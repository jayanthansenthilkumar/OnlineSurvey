from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId

class User(UserMixin):
    def __init__(self, username, email, password, is_admin=False, _id=None):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.is_admin = is_admin
        self.created_at = datetime.utcnow()
        self._id = _id if _id else ObjectId()
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self._id)
    
    @staticmethod
    def from_mongo(user_data):
        if not user_data:
            return None
        user = User(
            username=user_data.get('username'),
            email=user_data.get('email'),
            password='',  # No need to store password as we already have password_hash
            is_admin=user_data.get('is_admin', False),
            _id=user_data.get('_id')
        )
        # Set password_hash directly
        user.password_hash = user_data.get('password_hash')
        return user
    
    def to_mongo(self):
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'is_admin': self.is_admin,
            'created_at': self.created_at
        }