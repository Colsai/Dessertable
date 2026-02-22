import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')  # Admin dashboard password
    INVITE_CODE = os.getenv('INVITE_CODE')  # Required for user registration

    # Flask config
    DEBUG = False
    TESTING = False

    # Session security
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Session expires after 7 days

    # Application config
    DEFAULT_SEARCH_RADIUS = 5000  # meters (about 3 miles)
    MAX_RESULTS = 20
    CACHE_TIMEOUT = 60  # seconds


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    # Security enhancements
    SESSION_COOKIE_SECURE = True  # Require HTTPS for cookies
    PREFERRED_URL_SCHEME = 'https'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
