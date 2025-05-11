from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app, jsonify, abort
from flask_login import login_required, current_user
from models.survey import Survey, Response
from bson import ObjectId
import json
from datetime import datetime

survey_bp = Blueprint('survey', __name__)

@survey_bp.route('/dashboard')
@login_required
def dashboard():
    mongo = current_app.mongo
    
    if current_user.is_admin:
        # Admin sees all surveys they created
        surveys = list(mongo.db.surveys.find({'created_by': current_user.get_id()}))
    else:
        # Regular users see active surveys they can take and their responses
        active_surveys = list(mongo.db.surveys.find({'is_active': True}))
        
        # Get surveys the user has already responded to
        responses = list(mongo.db.responses.find({'user_id': current_user.get_id()}))
        responded_survey_ids = [str(response['survey_id']) for response in responses]
        
        # Filter surveys that the user has not responded to yet
        surveys_to_take = []
        responded_surveys = []
        
        for survey in active_surveys:
            survey_id_str = str(survey['_id'])
            if survey_id_str in responded_survey_ids:
                responded_surveys.append(survey)
            else:
                surveys_to_take.append(survey)
        
        return render_template('dashboard.html', 
                              surveys_to_take=surveys_to_take, 
                              responded_surveys=responded_surveys)
    
    return render_template('dashboard.html', surveys=surveys)

@survey_bp.route('/create_survey', methods=['GET', 'POST'])
@login_required
def create_survey():
    if not current_user.is_admin:
        flash('Only administrators can create surveys', 'error')
        return redirect(url_for('survey.dashboard'))
    
    if request.method == 'POST':
        data = request.form
        title = data.get('title')
        description = data.get('description')
        end_date_str = data.get('end_date')
        
        questions_json = data.get('questions_json', '[]')
        questions = json.loads(questions_json)
        
        if not title or not description or not questions:
            flash('Please provide all required fields', 'error')
            return render_template('create_survey.html')
        
        end_date = None
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format', 'error')
                return render_template('create_survey.html')
        
        survey = Survey(
            title=title,
            description=description,
            created_by=current_user.get_id(),
            questions=questions,
            end_date=end_date
        )
        
        mongo = current_app.mongo
        result = mongo.db.surveys.insert_one(survey.to_mongo())
        
        if result.inserted_id:
            flash('Survey created successfully!', 'success')
            return redirect(url_for('survey.dashboard'))
        else:
            flash('Error creating survey', 'error')
    
    return render_template('create_survey.html')

@survey_bp.route('/edit_survey/<survey_id>', methods=['GET', 'POST'])
@login_required
def edit_survey(survey_id):
    if not current_user.is_admin:
        flash('Only administrators can edit surveys', 'error')
        return redirect(url_for('survey.dashboard'))
    
    mongo = current_app.mongo
    survey_data = mongo.db.surveys.find_one({'_id': ObjectId(survey_id)})
    
    if not survey_data:
        flash('Survey not found', 'error')
        return redirect(url_for('survey.dashboard'))
    
    survey = Survey.from_mongo(survey_data)
    
    if survey.created_by != current_user.get_id():
        flash('You do not have permission to edit this survey', 'error')
        return redirect(url_for('survey.dashboard'))
    
    if request.method == 'POST':
        data = request.form
        title = data.get('title')
        description = data.get('description')
        end_date_str = data.get('end_date')
        is_active = 'is_active' in data
        
        questions_json = data.get('questions_json', '[]')
        questions = json.loads(questions_json)
        
        if not title or not description or not questions:
            flash('Please provide all required fields', 'error')
            return render_template('edit_survey.html', survey=survey)
        
        end_date = None
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format', 'error')
                return render_template('edit_survey.html', survey=survey)
        
        # Update survey details
        mongo.db.surveys.update_one(
            {'_id': ObjectId(survey_id)},
            {
                '$set': {
                    'title': title,
                    'description': description,
                    'questions': questions,
                    'is_active': is_active,
                    'end_date': end_date
                }
            }
        )
        
        flash('Survey updated successfully!', 'success')
        return redirect(url_for('survey.dashboard'))
    
    # Format end_date for HTML date input if it exists
    end_date_str = ''
    if survey.end_date:
        end_date_str = survey.end_date.strftime('%Y-%m-%d')
    
    return render_template('edit_survey.html', survey=survey, end_date=end_date_str)

@survey_bp.route('/take_survey/<survey_id>', methods=['GET', 'POST'])
@login_required
def take_survey(survey_id):
    mongo = current_app.mongo
    survey_data = mongo.db.surveys.find_one({'_id': ObjectId(survey_id)})
    
    if not survey_data:
        flash('Survey not found', 'error')
        return redirect(url_for('survey.dashboard'))
    
    survey = Survey.from_mongo(survey_data)
    
    # Check if the survey is active
    if not survey.is_active:
        flash('This survey is no longer active', 'error')
        return redirect(url_for('survey.dashboard'))
    
    # Check if the end date has passed
    if survey.end_date and survey.end_date < datetime.utcnow():
        flash('This survey has expired', 'error')
        return redirect(url_for('survey.dashboard'))
    
    # Check if the user has already responded to this survey
    existing_response = mongo.db.responses.find_one({
        'survey_id': ObjectId(survey_id),
        'user_id': current_user.get_id()
    })
    
    if existing_response:
        flash('You have already responded to this survey', 'info')
        return redirect(url_for('survey.dashboard'))
    
    if request.method == 'POST':
        answers = []
        for question in survey.questions:
            question_id = question['id']
            question_type = question['type']
            
            if question_type == 'multiple_choice':
                # Get selected option
                answer = request.form.get(f'question_{question_id}')
                answers.append({
                    'question_id': question_id,
                    'answer': answer
                })
            elif question_type == 'checkbox':
                # Get all selected options as a list
                selected_options = request.form.getlist(f'question_{question_id}')
                answers.append({
                    'question_id': question_id,
                    'answer': selected_options
                })
            elif question_type == 'text':
                # Get text input
                answer = request.form.get(f'question_{question_id}')
                answers.append({
                    'question_id': question_id,
                    'answer': answer
                })
        
        # Save the response
        response = Response(
            survey_id=ObjectId(survey_id),
            user_id=current_user.get_id(),
            answers=answers
        )
        
        mongo.db.responses.insert_one(response.to_mongo())
        
        flash('Thank you for completing the survey!', 'success')
        return redirect(url_for('survey.dashboard'))
    
    return render_template('take_survey.html', survey=survey)

@survey_bp.route('/survey_results/<survey_id>')
@login_required
def survey_results(survey_id):
    mongo = current_app.mongo
    survey_data = mongo.db.surveys.find_one({'_id': ObjectId(survey_id)})
    
    if not survey_data:
        flash('Survey not found', 'error')
        return redirect(url_for('survey.dashboard'))
    
    survey = Survey.from_mongo(survey_data)
    
    # If user is not admin and not the creator of the survey, they cannot see results
    if not current_user.is_admin and survey.created_by != current_user.get_id():
        flash('You do not have permission to view these results', 'error')
        return redirect(url_for('survey.dashboard'))
    
    # Get all responses for this survey
    responses = list(mongo.db.responses.find({'survey_id': ObjectId(survey_id)}))
    
    # Process responses for analysis
    results = {}
    for question in survey.questions:
        question_id = question['id']
        question_type = question['type']
        question_text = question['text']
        
        if question_type in ['multiple_choice', 'checkbox']:
            options = question.get('options', [])
            option_counts = {option: 0 for option in options}
            
            for response in responses:
                for answer in response['answers']:
                    if answer['question_id'] == question_id:
                        if question_type == 'multiple_choice':
                            selected_option = answer['answer']
                            if selected_option in option_counts:
                                option_counts[selected_option] += 1
                        elif question_type == 'checkbox':
                            selected_options = answer['answer']
                            for option in selected_options:
                                if option in option_counts:
                                    option_counts[option] += 1
            
            results[question_id] = {
                'text': question_text,
                'type': question_type,
                'options': options,
                'counts': option_counts
            }
        elif question_type == 'text':
            text_answers = []
            for response in responses:
                for answer in response['answers']:
                    if answer['question_id'] == question_id:
                        text_answers.append(answer['answer'])
            
            results[question_id] = {
                'text': question_text,
                'type': question_type,
                'answers': text_answers
            }
    
    return render_template('survey_results.html', survey=survey, results=results, total_responses=len(responses))