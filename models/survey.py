from datetime import datetime
from bson import ObjectId

class Survey:
    def __init__(self, title, description, created_by, questions=None, is_active=True, end_date=None, _id=None):
        self.title = title
        self.description = description
        self.created_by = created_by  # User ID who created the survey
        self.questions = questions if questions else []
        self.is_active = is_active
        self.created_at = datetime.utcnow()
        self.end_date = end_date
        self._id = _id if _id else ObjectId()
    
    @staticmethod
    def from_mongo(survey_data):
        if not survey_data:
            return None
        return Survey(
            title=survey_data.get('title'),
            description=survey_data.get('description'),
            created_by=survey_data.get('created_by'),
            questions=survey_data.get('questions', []),
            is_active=survey_data.get('is_active', True),
            end_date=survey_data.get('end_date'),
            _id=survey_data.get('_id')
        )
    
    def to_mongo(self):
        return {
            '_id': self._id,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'questions': self.questions,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'end_date': self.end_date
        }

class Response:
    def __init__(self, survey_id, user_id, answers, submitted_at=None, _id=None):
        self.survey_id = survey_id
        self.user_id = user_id
        self.answers = answers  # List of answers to questions
        self.submitted_at = submitted_at if submitted_at else datetime.utcnow()
        self._id = _id if _id else ObjectId()
    
    @staticmethod
    def from_mongo(response_data):
        if not response_data:
            return None
        return Response(
            survey_id=response_data.get('survey_id'),
            user_id=response_data.get('user_id'),
            answers=response_data.get('answers', []),
            submitted_at=response_data.get('submitted_at'),
            _id=response_data.get('_id')
        )
    
    def to_mongo(self):
        return {
            '_id': self._id,
            'survey_id': self.survey_id,
            'user_id': self.user_id,
            'answers': self.answers,
            'submitted_at': self.submitted_at
        }