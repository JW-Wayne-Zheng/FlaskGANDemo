import os
import logging
import numpy as np
import requests
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from flask import current_app
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Import TensorFlow Addons for custom layers
try:
    import tensorflow_addons as tfa
    TFA_AVAILABLE = True
except ImportError:
    TFA_AVAILABLE = False
    logging.warning("TensorFlow Addons not available. Some models may not load correctly.")

logger = logging.getLogger(__name__)

class ModelService:
    """Service class for handling GAN model operations"""
    
    def __init__(self):
        self.models = {}
        self.model_loaded = False
        self.loading_status = {
            'is_loading': False,
            'current_artist': None,
            'progress': 0,
            'total_models': 5,
            'loaded_models': 0,
            'message': 'Ready'
        }
        # Cloud storage URLs for model files
        self.model_urls = {
            'monet': 'https://drive.usercontent.google.com/uc?id=1q0fz1r6zrh2r3j1IjZVMQN3NrcwVkgXb&export=download',
            'vangogh': 'https://drive.usercontent.google.com/uc?id=1hP2qKxGhjrtwvMbpbqXj9towUGWHUm_6&export=download',
            'degas': 'https://drive.usercontent.google.com/uc?id=19JSuqF3u_UDrju2jq1AsBI9hSGV3yozx&export=download',
            'picasso': 'https://drive.usercontent.google.com/uc?id=1a4PPlYBuaO8KaIYxDtz6JYv4vemkg-SM&export=download',
            'rembrandt': 'https://drive.usercontent.google.com/uc?id=1Lo6H982WkOWN-VNuZV-xw5GrN6TdZ9Hv&export=download'
        }
    
    def get_status(self):
        """Get current loading status"""
        return self.loading_status.copy()
    
    def update_status(self, **kwargs):
        """Update loading status"""
        self.loading_status.update(kwargs)
    
    def download_model(self, artist):
        """Download model from cloud storage if not present locally"""
        try:
            models_dir = current_app.config['MODELS_FOLDER']
            model_path = os.path.join(models_dir, f'{artist}_generator.h5')
            
            # If model already exists locally, skip download
            if os.path.exists(model_path):
                logger.info(f'Model for {artist} already exists locally')
                return model_path
            
            # Create models directory if it doesn't exist
            os.makedirs(models_dir, exist_ok=True)
            
            # Download model from cloud storage
            if artist in self.model_urls:
                url = self.model_urls[artist]
                logger.info(f'Downloading {artist} model from {url}')
                
                self.update_status(
                    current_artist=artist,
                    message=f'Downloading {artist.title()} model...'
                )
                
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                # Get file size for progress tracking
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                
                with open(model_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # Update progress if we know total size
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                self.update_status(progress=progress)
                
                logger.info(f'Successfully downloaded {artist} model to {model_path}')
                return model_path
            else:
                logger.warning(f'No download URL configured for {artist}')
                return None
                
        except Exception as e:
            logger.error(f'Error downloading {artist} model: {str(e)}')
            return None
    
    def load_models(self):
        """Load all artist models on demand"""
        if self.model_loaded:
            return
            
        try:
            self.update_status(
                is_loading=True,
                progress=0,
                loaded_models=0,
                message='Starting model initialization...'
            )
            
            models_dir = current_app.config['MODELS_FOLDER']
            artists = current_app.config['ARTISTS']
            
            for i, artist in enumerate(artists):
                model_path = os.path.join(models_dir, f'{artist}_generator.h5')
                
                # Update progress
                progress = (i / len(artists)) * 100
                self.update_status(
                    current_artist=artist,
                    progress=progress,
                    message=f'Processing {artist.title()} model...'
                )
                
                # If model doesn't exist locally, try to download it
                if not os.path.exists(model_path):
                    model_path = self.download_model(artist)
                    if not model_path:
                        logger.warning(f'Could not download model for {artist}')
                        continue
                
                if os.path.exists(model_path):
                    logger.info(f'Loading model for {artist}')
                    
                    self.update_status(
                        message=f'Loading {artist.title()} model into memory...'
                    )
                    
                    # Load model with custom objects for TensorFlow Addons
                    custom_objects = {}
                    if TFA_AVAILABLE:
                        custom_objects.update({
                            'InstanceNormalization': tfa.layers.InstanceNormalization,
                            'Addons>InstanceNormalization': tfa.layers.InstanceNormalization,
                        })
                    
                    self.models[artist] = load_model(
                        model_path, 
                        compile=False, 
                        custom_objects=custom_objects
                    )
                    
                    self.loading_status['loaded_models'] += 1
                    logger.info(f'Successfully loaded {artist} model')
                else:
                    logger.warning(f'Model file not found: {model_path}')
            
            self.model_loaded = True
            self.update_status(
                is_loading=False,
                progress=100,
                message=f'Ready! {len(self.models)} models loaded successfully'
            )
            logger.info(f'Loaded {len(self.models)} models')
            
        except Exception as e:
            self.update_status(
                is_loading=False,
                message=f'Error loading models: {str(e)}'
            )
            logger.error(f'Error loading models: {str(e)}')
            raise
    
    def get_available_artists(self):
        """Get list of available artists"""
        if not self.model_loaded:
            self.load_models()
        return list(self.models.keys())
    
    def preprocess_image(self, image_path, target_size=None):
        """Preprocess image for model input"""
        try:
            if target_size is None:
                target_size = current_app.config['IMAGE_SIZE']
            
            # Load and resize image
            pixels = load_img(image_path, target_size=target_size)
            pixels = img_to_array(pixels)
            pixels = np.expand_dims(pixels, 0)
            
            # Normalize to [-1, 1] range for GAN
            pixels = (pixels - 127.5) / 127.5
            
            return pixels
            
        except Exception as e:
            logger.error(f'Error preprocessing image {image_path}: {str(e)}')
            raise
    
    def generate_artwork(self, image_path, artist, output_path):
        """Generate artwork using specified artist model"""
        try:
            if not self.model_loaded:
                self.load_models()
            
            if artist not in self.models:
                raise ValueError(f'Artist {artist} not available. Available: {list(self.models.keys())}')
            
            # Preprocess input image
            input_image = self.preprocess_image(image_path)
            
            # Generate artwork
            logger.info(f'Generating artwork with {artist} style')
            generated_image = self.models[artist].predict(input_image, verbose=0)
            
            # Post-process output
            generated_image = (generated_image + 1) / 2.0  # Convert from [-1,1] to [0,1]
            generated_image = np.clip(generated_image[0], 0, 1)
            
            # Save generated image
            plt.figure(figsize=(8, 8))
            plt.imshow(generated_image)
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(output_path, bbox_inches='tight', pad_inches=0, dpi=150)
            plt.close()
            
            logger.info(f'Successfully generated artwork: {output_path}')
            return output_path
            
        except Exception as e:
            logger.error(f'Error generating artwork: {str(e)}')
            raise
    
    def get_model_info(self):
        """Get information about loaded models"""
        if not self.model_loaded:
            self.load_models()
        
        info = {}
        for artist, model in self.models.items():
            try:
                info[artist] = {
                    'name': artist.title(),
                    'input_shape': model.input_shape,
                    'output_shape': model.output_shape,
                    'total_params': model.count_params()
                }
            except Exception as e:
                logger.warning(f'Could not get info for {artist}: {str(e)}')
                info[artist] = {'name': artist.title(), 'error': str(e)}
        
        return info

# Global model service instance
model_service = ModelService() 