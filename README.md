# ArtGAN - AI Art Generator

Transform your photos into artistic masterpieces using cutting-edge CycleGAN technology. Create stunning artworks in the style of famous artists like Monet, Van Gogh, Picasso, Degas, and Rembrandt.

## 🎨 Features

- **Multiple Artist Styles**: Transform images using 5 different pre-trained GAN models
- **Real-time Processing**: Fast image conversion with modern web technologies
- **Interactive Gallery**: Browse and manage generated artworks
- **Color Analysis**: Advanced color histogram visualization with D3.js
- **AI Classification**: Client-side image classification using TensorFlow.js
- **Modern UI**: Responsive design with Bootstrap 5 and custom CSS
- **RESTful API**: Clean API endpoints for programmatic access

## 🛠️ Technology Stack

### Backend

- **Python 3.11.6** - Modern Python runtime
- **Flask 3.0.0** - Lightweight web framework
- **TensorFlow 2.15.0** - ML model inference
- **Pillow 10.1.0** - Image processing
- **NumPy 1.24.3** - Numerical computations
- **Matplotlib 3.8.2** - Visualization

### Frontend

- **Bootstrap 5.3.2** - Modern CSS framework
- **D3.js 7.0** - Data visualization
- **TensorFlow.js 4.15.0** - Client-side AI
- **Modern JavaScript** - ES6+ features

### Infrastructure

- **Heroku** - Cloud deployment
- **Gunicorn** - Production WSGI server

## 🏗️ Architecture

The application follows a modern Flask architecture with:

```
app/
├── __init__.py              # Application factory
├── config.py               # Configuration management
├── blueprints/             # Route organization
│   ├── main.py            # Main user routes
│   └── api.py             # RESTful API endpoints
├── services/              # Business logic
│   ├── model_service.py   # GAN model operations
│   └── image_service.py   # Image processing
├── utils/                 # Helper functions
│   └── file_utils.py      # File operations
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── index.html        # Homepage
│   ├── process.html      # Image processing
│   ├── result.html       # Results display
│   ├── gallery.html      # Gallery view
│   └── about.html        # Project information
└── static/               # Static assets
    ├── css/style.css     # Custom styling
    ├── js/app.js         # JavaScript functionality
    └── images/           # Image assets
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd FlaskGANDemo
   ```

2. **Set up Python environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the application**

   ```bash
   python main.py
   ```

4. **Access the application**
   - Open http://localhost:5000 in your browser

### Heroku Deployment

The application is configured for Heroku deployment with:

- `Procfile` - Gunicorn configuration
- `runtime.txt` - Python version specification
- `requirements.txt` - Dependencies

Deploy with:

```bash
git push heroku main
```

## 📊 AI Models

The application includes pre-trained CycleGAN models for:

- **Monet** - Impressionist landscape style
- **Van Gogh** - Post-impressionist with bold colors
- **Picasso** - Cubist geometric abstractions
- **Degas** - Classical figure painting
- **Rembrandt** - Dutch Golden Age portraits

Each model file (~31MB) contains a complete generator network trained on artist-specific datasets.

## 🎯 Usage

1. **Upload Image**: Select a photo using the file picker
2. **Analyze**: View color histogram and AI classification
3. **Transform**: Choose an artist style for conversion
4. **Download**: Save your generated artwork
5. **Gallery**: Browse all created artworks

## 🔧 API Endpoints

### Core Endpoints

- `GET /` - Homepage
- `POST /upload` - Image upload
- `GET /process/<filename>` - Image processing interface
- `POST /convert` - Style transfer
- `GET /gallery` - Artwork gallery

### API Endpoints

- `GET /api/models/info` - Model information
- `GET /api/gallery/recent` - Recent artworks
- `GET /api/stats/storage` - Storage statistics
- `GET /api/health` - Health check

## 🎨 Features in Detail

### Color Analysis

- RGB histogram visualization
- Dominant color extraction
- Statistical color analysis
- Interactive D3.js charts

### Image Processing

- Automatic image resizing
- Format standardization
- EXIF data preservation
- Secure file handling

### Gallery Management

- Artwork filtering by artist
- Multiple view modes
- Lightbox image viewing
- Social sharing capabilities

## 🔒 Security Features

- File type validation
- File size limits (16MB)
- Secure filename generation
- Input sanitization
- Error handling

## 📱 Responsive Design

- Mobile-first approach
- Touch-friendly interfaces
- Adaptive image scaling
- Progressive enhancement

## 🌟 Advanced Features

- **Before/After Slider**: Interactive image comparison
- **Batch Processing**: Multiple image support (API)
- **Theme Toggle**: Light/dark mode support
- **Progressive Loading**: Lazy image loading
- **Error Recovery**: Graceful error handling

## 🐛 Troubleshooting

### Common Issues

1. **Model Loading Errors**

   - Ensure model files exist in `models/` directory
   - Check file permissions and size

2. **Memory Issues**

   - Reduce image size before upload
   - Monitor system memory usage

3. **Slow Processing**
   - Use smaller input images
   - Consider model optimization

### Development

- Enable debug mode: `export FLASK_DEBUG=1`
- View logs: Check console output
- API testing: Use `/api/health` endpoint
