import os
import logging
import numpy as np
from PIL import Image, ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from flask import current_app

logger = logging.getLogger(__name__)

class ImageService:
    """Service class for image processing operations"""
    
    @staticmethod
    def validate_image(file):
        """Validate uploaded image file"""
        if not file or file.filename == '':
            return False, "No file selected"
        
        # Check file extension
        filename = file.filename.lower()
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        
        if not any(filename.endswith(f'.{ext}') for ext in allowed_extensions):
            return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        
        # Check file size (Flask handles MAX_CONTENT_LENGTH automatically)
        try:
            # Try to open as image to validate
            file.seek(0)  # Reset file pointer
            Image.open(file).verify()
            file.seek(0)  # Reset again for actual use
            return True, "Valid image"
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    @staticmethod
    def process_upload(file, upload_folder):
        """Process and save uploaded image"""
        try:
            # Generate secure filename
            original_filename = file.filename
            filename = ImageService.secure_filename(original_filename)
            
            # Ensure unique filename
            filepath = os.path.join(upload_folder, filename)
            counter = 1
            base_name, ext = os.path.splitext(filename)
            
            while os.path.exists(filepath):
                filename = f"{base_name}_{counter}{ext}"
                filepath = os.path.join(upload_folder, filename)
                counter += 1
            
            # Open and process image
            image = Image.open(file)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Auto-orient image
            image = ImageOps.exif_transpose(image)
            
            # Resize if too large (maintain aspect ratio)
            max_size = (2048, 2048)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save processed image
            image.save(filepath, 'JPEG', quality=95, optimize=True)
            
            logger.info(f'Successfully processed and saved image: {filename}')
            return filename, filepath
            
        except Exception as e:
            logger.error(f'Error processing upload: {str(e)}')
            raise
    
    @staticmethod
    def secure_filename(filename):
        """Create a secure filename"""
        # Remove any path components
        filename = os.path.basename(filename)
        
        # Replace spaces and special characters
        import re
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Ensure we have an extension
        if '.' not in filename:
            filename += '.jpg'
        
        return filename
    
    @staticmethod
    def analyze_color_histogram(image_path):
        """Analyze color histogram of an image"""
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(image)
            
            # Calculate histograms for each channel
            hist_r = np.histogram(img_array[:,:,0], bins=256, range=(0, 256))[0]
            hist_g = np.histogram(img_array[:,:,1], bins=256, range=(0, 256))[0]
            hist_b = np.histogram(img_array[:,:,2], bins=256, range=(0, 256))[0]
            
            # Calculate color statistics
            stats = {
                'red': {
                    'mean': float(np.mean(img_array[:,:,0])),
                    'std': float(np.std(img_array[:,:,0])),
                    'histogram': hist_r.tolist()
                },
                'green': {
                    'mean': float(np.mean(img_array[:,:,1])),
                    'std': float(np.std(img_array[:,:,1])),
                    'histogram': hist_g.tolist()
                },
                'blue': {
                    'mean': float(np.mean(img_array[:,:,2])),
                    'std': float(np.std(img_array[:,:,2])),
                    'histogram': hist_b.tolist()
                }
            }
            
            # Dominant colors
            stats['dominant_colors'] = ImageService._get_dominant_colors(image)
            
            return stats
            
        except Exception as e:
            logger.error(f'Error analyzing color histogram: {str(e)}')
            raise
    
    @staticmethod
    def _get_dominant_colors(image, num_colors=5):
        """Get dominant colors from image"""
        try:
            # Resize image for faster processing
            image_small = image.resize((150, 150))
            
            # Convert to numpy array and reshape
            data = np.array(image_small)
            data = data.reshape((-1, 3))
            
            # Use k-means clustering to find dominant colors
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
            kmeans.fit(data)
            
            colors = kmeans.cluster_centers_.astype(int)
            percentages = np.bincount(kmeans.labels_) / len(kmeans.labels_)
            
            # Sort by percentage
            sorted_indices = np.argsort(percentages)[::-1]
            
            dominant_colors = []
            for i in sorted_indices:
                color = colors[i]
                percentage = percentages[i]
                dominant_colors.append({
                    'rgb': color.tolist(),
                    'hex': f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}",
                    'percentage': float(percentage)
                })
            
            return dominant_colors
            
        except ImportError:
            # Fallback if sklearn is not available
            logger.warning('sklearn not available, using simple color analysis')
            return []
        except Exception as e:
            logger.error(f'Error getting dominant colors: {str(e)}')
            return []
    
    @staticmethod
    def get_image_metadata(image_path):
        """Get metadata information about an image"""
        try:
            with Image.open(image_path) as image:
                metadata = {
                    'filename': os.path.basename(image_path),
                    'format': image.format,
                    'mode': image.mode,
                    'size': image.size,
                    'width': image.width,
                    'height': image.height,
                    'file_size': os.path.getsize(image_path)
                }
                
                # Get EXIF data if available
                if hasattr(image, '_getexif') and image._getexif():
                    exif = image._getexif()
                    metadata['exif'] = exif
                
                return metadata
                
        except Exception as e:
            logger.error(f'Error getting image metadata: {str(e)}')
            return {}

# Global image service instance
image_service = ImageService() 