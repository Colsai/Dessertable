from flask import Flask
from flask_login import LoginManager
from config import config
import os

# Initialize Flask-Login
login_manager = LoginManager()


def create_app(config_name=None):
    """Flask application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page'
    login_manager.login_message_category = 'info'

    # User loader callback for Flask-Login
    from app.models.database import Database
    db = Database()

    @login_manager.user_loader
    def load_user(user_id):
        return db.get_user_by_id(int(user_id))

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Register template filters
    from app.utils.filters import register_filters
    register_filters(app)

    # Production security headers
    if config_name == 'production':
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
            return response

    return app
