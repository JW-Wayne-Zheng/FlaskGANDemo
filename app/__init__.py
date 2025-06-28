import os
import logging
from flask import Flask
from app.config import Config
from app.utils.file_utils import cleanup_old_sessions

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/artgan.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('ArtGAN startup')

    # Clean up old session folders on startup
    with app.app_context():
        try:
            generated_folder = app.config['GENERATED_FOLDER']
            if os.path.exists(generated_folder):
                sessions_cleaned = cleanup_old_sessions(generated_folder, max_age_hours=24)
                if sessions_cleaned > 0:
                    app.logger.info(f'Cleaned up {sessions_cleaned} old session folders on startup')
        except Exception as e:
            app.logger.warning(f'Failed to cleanup old sessions on startup: {str(e)}')

    # Register blueprints
    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.blueprints.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app 