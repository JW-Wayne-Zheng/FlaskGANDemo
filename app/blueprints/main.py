import os
import logging
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, session
from app.services.model_service import model_service
from app.services.image_service import image_service
from app.utils.file_utils import cleanup_old_files, cleanup_old_sessions

logger = logging.getLogger(__name__)
bp = Blueprint('main', __name__)

def get_session_folder():
    """Get or create session-specific folder"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    session_folder = os.path.join(current_app.config['GENERATED_FOLDER'], session['session_id'])
    os.makedirs(session_folder, exist_ok=True)
    return session_folder

@bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', artists=current_app.config['ARTISTS'])

@bp.route('/about')
def about():
    """About page with project information"""
    model_info = model_service.get_model_info()
    return render_template('about.html', model_info=model_info)

@bp.route('/gallery')
def gallery():
    """Gallery of generated artworks for current session only"""
    session_folder = get_session_folder()
    images = []
    
    if os.path.exists(session_folder):
        for filename in os.listdir(session_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                images.append(filename)
    
    # Sort by modification time (newest first)
    images.sort(key=lambda x: os.path.getmtime(os.path.join(session_folder, x)), reverse=True)
    
    return render_template('gallery.html', images=images[:20])  # Show last 20 images

@bp.route('/upload', methods=['GET', 'POST'])
def upload_image():
    """Handle image upload"""
    if request.method == 'GET':
        return redirect(url_for('main.index'))
    
    try:
        file = request.files.get('file')
        
        if not file:
            flash('No file selected', 'error')
            return redirect(url_for('main.index'))
        
        # Validate image
        is_valid, message = image_service.validate_image(file)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('main.index'))
        
        # Process and save upload
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filename, filepath = image_service.process_upload(file, upload_folder)
        
        # Clean up old files periodically
        cleanup_old_files(upload_folder, max_age_hours=24)
        cleanup_old_sessions(current_app.config['GENERATED_FOLDER'], max_age_hours=24)
        
        flash('Image uploaded successfully!', 'success')
        return redirect(url_for('main.process_image', filename=filename))
        
    except Exception as e:
        logger.error(f'Upload error: {str(e)}')
        flash('Error uploading image. Please try again.', 'error')
        return redirect(url_for('main.index'))

@bp.route('/process/<filename>')
def process_image(filename):
    """Process uploaded image - show analysis and conversion options"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    filepath = os.path.join(upload_folder, filename)
    
    if not os.path.exists(filepath):
        flash('Image not found', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Get image metadata and analysis
        metadata = image_service.get_image_metadata(filepath)
        color_analysis = image_service.analyze_color_histogram(filepath)
        
        # Get available artists
        available_artists = model_service.get_available_artists()
        
        return render_template('process.html', 
                             filename=filename,
                             metadata=metadata,
                             color_analysis=color_analysis,
                             artists=available_artists)
    
    except Exception as e:
        logger.error(f'Error processing image {filename}: {str(e)}')
        flash('Error analyzing image', 'error')
        return redirect(url_for('main.index'))

@bp.route('/convert', methods=['POST'])
def convert_image():
    """Convert image using selected artist style"""
    try:
        filename = request.form.get('filename')
        artist = request.form.get('artist')
        
        if not filename or not artist:
            flash('Missing filename or artist selection', 'error')
            return redirect(url_for('main.index'))
        
        # Validate files exist
        upload_folder = current_app.config['UPLOAD_FOLDER']
        input_path = os.path.join(upload_folder, filename)
        
        if not os.path.exists(input_path):
            flash('Original image not found', 'error')
            return redirect(url_for('main.index'))
        
        # Generate output filename in session folder
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_{artist}{ext}"
        session_folder = get_session_folder()
        output_path = os.path.join(session_folder, output_filename)
        
        # Generate artwork
        model_service.generate_artwork(input_path, artist, output_path)
        
        flash(f'Artwork generated in {artist.title()} style!', 'success')
        return redirect(url_for('main.view_result', 
                               original=filename, 
                               generated=output_filename,
                               artist=artist))
        
    except Exception as e:
        logger.error(f'Conversion error: {str(e)}')
        flash(f'Error generating artwork: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@bp.route('/result')
def view_result():
    """View conversion results"""
    original = request.args.get('original')
    generated = request.args.get('generated')
    artist = request.args.get('artist')
    
    if not all([original, generated, artist]):
        flash('Invalid result parameters', 'error')
        return redirect(url_for('main.index'))
    
    # Verify files exist
    upload_folder = current_app.config['UPLOAD_FOLDER']
    session_folder = get_session_folder()
    
    original_path = os.path.join(upload_folder, original)
    generated_path = os.path.join(session_folder, generated)
    
    if not os.path.exists(original_path) or not os.path.exists(generated_path):
        flash('Result files not found', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('result.html',
                         original=original,
                         generated=generated,
                         artist=artist)

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/generated/<filename>')
def generated_file(filename):
    """Serve generated files from session folder"""
    session_folder = get_session_folder()
    return send_from_directory(session_folder, filename)

@bp.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('main.index'))

@bp.errorhandler(Exception)
def handle_error(e):
    """Global error handler for this blueprint"""
    logger.error(f'Unhandled error: {str(e)}', exc_info=True)
    flash('An unexpected error occurred. Please try again.', 'error')
    return redirect(url_for('main.index')) 