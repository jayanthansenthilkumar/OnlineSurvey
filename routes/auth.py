from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app, session
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
import pymongo

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate data
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        mongo = current_app.mongo
        existing_user = mongo.db.users.find_one({'$or': [{'username': username}, {'email': email}]})
        
        if existing_user:
            flash('Username or Email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        is_admin = False
        
        # If this is the first user, make them an admin
        if mongo.db.users.count_documents({}) == 0:
            is_admin = True
        
        user = User(username=username, email=email, password=password, is_admin=is_admin)
        mongo.db.users.insert_one(user.to_mongo())
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        mongo = current_app.mongo
        user_data = mongo.db.users.find_one({'username': username})
        
        if not user_data:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
        user = User.from_mongo(user_data)
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('survey.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate data
        if not username or not email or not current_password:
            flash('Username, email, and current password are required', 'error')
            return render_template('edit_profile.html')
        
        # Verify current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'error')
            return render_template('edit_profile.html')
        
        mongo = current_app.mongo
          # If username or email has changed, check if it already exists
        if username != current_user.username or email != current_user.email:
            existing_user = mongo.db.users.find_one({
                '$and': [
                    {'_id': {'$ne': current_user._id}},
                    {'$or': [{'username': username}, {'email': email}]}
                ]
            })
            
            if existing_user:
                flash('Username or Email already exists', 'error')
                return render_template('edit_profile.html')
        
        # Update user data
        update_data = {
            'username': username,
            'email': email
        }
        
        # If new password is provided, update it
        if new_password:
            if not confirm_password:
                flash('Please confirm your new password', 'error')
                return render_template('edit_profile.html')
            
            if new_password != confirm_password:
                flash('New passwords do not match', 'error')
                return render_template('edit_profile.html')
            
            # Update password hash
            update_data['password_hash'] = generate_password_hash(new_password)
          # Update user in database
        mongo.db.users.update_one({'_id': current_user._id}, {'$set': update_data})
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('survey.dashboard'))
    
    return render_template('edit_profile.html')