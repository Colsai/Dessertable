from flask import Flask
from config import config
import os


def create_app(config_name=None):
    """Flask application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Register template filters
    from app.utils.filters import register_filters
    register_filters(app)

    return app
