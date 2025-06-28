import os
import logging
from flask import Blueprint, request, jsonify, current_app
from app.services.model_service import model_service
from app.services.image_service import image_service
from app.utils.file_utils import get_directory_size, format_file_size

logger = logging.getLogger(__name__)
bp = Blueprint('api', __name__)

def api_response(data=None, error=None, status=200):
    """Standardized API response format"""
    response = {
        'success': error is None,
        'data': data,
        'error': error
    }
    return jsonify(response), status

@bp.route('/models/info')
def models_info():
    """Get information about available models"""
    try:
        model_info = model_service.get_model_info()
        return api_response(model_info)
    except Exception as e:
        logger.error(f'Error getting model info: {str(e)}')
        return api_response(error='Failed to get model information', status=500)

@bp.route('/models/artists')
def available_artists():
    """Get list of available artists"""
    try:
        artists = model_service.get_available_artists()
        return api_response(artists)
    except Exception as e:
        logger.error(f'Error getting artists: {str(e)}')
        return api_response(error='Failed to get artist list', status=500)

@bp.route('/image/analyze', methods=['POST'])
def analyze_image():
    """Analyze uploaded image for color histogram and metadata"""
    try:
        filename = request.json.get('filename')
        if not filename:
            return api_response(error='Filename required', status=400)
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        
        if not os.path.exists(filepath):
            return api_response(error='Image not found', status=404)
        
        # Get analysis data
        metadata = image_service.get_image_metadata(filepath)
        color_analysis = image_service.analyze_color_histogram(filepath)
        
        result = {
            'filename': filename,
            'metadata': metadata,
            'color_analysis': color_analysis
        }
        
        return api_response(result)
        
    except Exception as e:
        logger.error(f'Error analyzing image: {str(e)}')
        return api_response(error='Failed to analyze image', status=500)

@bp.route('/image/convert', methods=['POST'])
def convert_image_api():
    """Convert image using specified artist style (async endpoint)"""
    try:
        data = request.json
        filename = data.get('filename')
        artist = data.get('artist')
        
        if not filename or not artist:
            return api_response(error='Filename and artist required', status=400)
        
        # Validate input file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        input_path = os.path.join(upload_folder, filename)
        
        if not os.path.exists(input_path):
            return api_response(error='Input image not found', status=404)
        
        # Validate artist
        available_artists = model_service.get_available_artists()
        if artist not in available_artists:
            return api_response(error=f'Artist {artist} not available', status=400)
        
        # Generate output filename
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_{artist}{ext}"
        output_path = os.path.join(current_app.config['GENERATED_FOLDER'], output_filename)
        
        # Generate artwork
        model_service.generate_artwork(input_path, artist, output_path)
        
        result = {
            'original_filename': filename,
            'generated_filename': output_filename,
            'artist': artist,
            'message': f'Successfully generated artwork in {artist.title()} style'
        }
        
        return api_response(result)
        
    except Exception as e:
        logger.error(f'Error in API conversion: {str(e)}')
        return api_response(error=str(e), status=500)

@bp.route('/stats/storage')
def storage_stats():
    """Get storage usage statistics"""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        generated_folder = current_app.config['GENERATED_FOLDER']
        
        upload_size = get_directory_size(upload_folder)
        generated_size = get_directory_size(generated_folder)
        
        # Count files
        upload_files = len([f for f in os.listdir(upload_folder) 
                           if os.path.isfile(os.path.join(upload_folder, f))]) if os.path.exists(upload_folder) else 0
        generated_files = len([f for f in os.listdir(generated_folder) 
                              if os.path.isfile(os.path.join(generated_folder, f))]) if os.path.exists(generated_folder) else 0
        
        stats = {
            'uploads': {
                'size_bytes': upload_size,
                'size_formatted': format_file_size(upload_size),
                'file_count': upload_files
            },
            'generated': {
                'size_bytes': generated_size,
                'size_formatted': format_file_size(generated_size),
                'file_count': generated_files
            },
            'total': {
                'size_bytes': upload_size + generated_size,
                'size_formatted': format_file_size(upload_size + generated_size),
                'file_count': upload_files + generated_files
            }
        }
        
        return api_response(stats)
        
    except Exception as e:
        logger.error(f'Error getting storage stats: {str(e)}')
        return api_response(error='Failed to get storage statistics', status=500)

@bp.route('/gallery/recent')
def recent_gallery():
    """Get recent generated images"""
    try:
        limit = request.args.get('limit', 10, type=int)
        generated_folder = current_app.config['GENERATED_FOLDER']
        
        if not os.path.exists(generated_folder):
            return api_response([])
        
        # Get image files with metadata
        images = []
        for filename in os.listdir(generated_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(generated_folder, filename)
                stat = os.stat(filepath)
                
                # Extract artist from filename if possible
                artist = 'unknown'
                for a in current_app.config['ARTISTS']:
                    if f'_{a}' in filename:
                        artist = a
                        break
                
                images.append({
                    'filename': filename,
                    'artist': artist,
                    'created': stat.st_mtime,
                    'size': stat.st_size
                })
        
        # Sort by creation time (newest first) and limit
        images.sort(key=lambda x: x['created'], reverse=True)
        images = images[:limit]
        
        return api_response(images)
        
    except Exception as e:
        logger.error(f'Error getting recent gallery: {str(e)}')
        return api_response(error='Failed to get gallery images', status=500)

@bp.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check if models are loaded
        available_artists = model_service.get_available_artists()
        
        health_data = {
            'status': 'healthy',
            'models_loaded': len(available_artists),
            'available_artists': available_artists,
            'upload_folder_exists': os.path.exists(current_app.config['UPLOAD_FOLDER']),
            'generated_folder_exists': os.path.exists(current_app.config['GENERATED_FOLDER'])
        }
        
        return api_response(health_data)
        
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return api_response(error='Health check failed', status=500) 