"""
Configuration Management for PV Testing LIMS-QMS
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""

    # Application Settings
    APP_NAME = "PV Testing LIMS-QMS"
    VERSION = "1.0.0"
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')

    # Flask Settings
    FLASK_APP = os.getenv('FLASK_APP', 'genspark_app.app')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    TESTING = False

    # Database Settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://lims_user:lims_password@localhost:5432/pv_lims')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG

    # Redis & Celery Settings
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Email Settings
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@pvlims.com')

    # File Storage Settings
    BASE_DIR = Path(__file__).resolve().parent.parent
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 104857600))  # 100MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls', 'csv', 'dat', 'json'}
    STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')

    # S3/MinIO Settings
    S3_BUCKET = os.getenv('S3_BUCKET', 'pv-lims-data')
    S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', '')
    S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', '')
    S3_ENDPOINT = os.getenv('S3_ENDPOINT', '')

    # Security Settings
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('SESSION_TIMEOUT', 3600))
    JWT_REFRESH_TOKEN_EXPIRES = 86400  # 24 hours
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8080').split(',')

    # Laboratory Settings
    LAB_NAME = os.getenv('LAB_NAME', 'PV Testing Laboratory')
    LAB_ADDRESS = os.getenv('LAB_ADDRESS', '123 Solar Street, Tech City')
    LAB_PHONE = os.getenv('LAB_PHONE', '+1-555-123-4567')
    LAB_EMAIL = os.getenv('LAB_EMAIL', 'lab@pvtesting.com')
    LAB_ACCREDITATION = os.getenv('LAB_ACCREDITATION', 'ISO/IEC 17025:2017')

    # Application Settings
    TIMEZONE = os.getenv('TIMEZONE', 'UTC')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))

    # Protocol Settings
    PROTOCOLS_DIR = BASE_DIR / 'genspark_app' / 'templates' / 'protocols'
    TOTAL_PROTOCOLS = 54

    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create upload directory if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

        # Create protocols directory if it doesn't exist
        os.makedirs(Config.PROTOCOLS_DIR, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler

        if not app.debug:
            file_handler = RotatingFileHandler(
                'logs/pv_lims.log',
                maxBytes=10240000,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('PV LIMS startup')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://lims_user:lims_password@localhost:5432/pv_lims_test'
    WTF_CSRF_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration object by name"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    return config.get(config_name, DevelopmentConfig)
