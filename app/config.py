import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    GENERATED_FOLDER = os.path.join(basedir, 'static', 'generated')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Model settings
    MODELS_FOLDER = os.path.join(basedir, '..', 'models')
    IMAGE_SIZE = (256, 256)
    
    # Artists supported
    ARTISTS = ['monet', 'vangogh', 'degas', 'picasso', 'rembrandt']
    
    @staticmethod
    def init_app(app):
        # Ensure upload directories exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.GENERATED_FOLDER, exist_ok=True) 