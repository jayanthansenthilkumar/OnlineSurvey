import os
from flask import Flask, render_template, url_for, redirect, flash, current_app
from flask_pymongo import PyMongo
from flask_login import LoginManager, current_user
from config.config import config
from models.user import User
from routes.auth import auth_bp
from routes.survey import survey_bp
from bson import ObjectId

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    if not user_id:
        return None
    mongo = current_app.mongo
    user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User.from_mongo(user_data)
    return None

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    mongo = PyMongo(app)
    app.mongo = mongo
    
    login_manager.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(survey_bp)
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('survey.dashboard'))
        return render_template('index.html')
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(debug=True)