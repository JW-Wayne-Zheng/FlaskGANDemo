// Main JavaScript file for ArtGAN

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeTooltips();
    initializeImagePreview();
    initializeFormValidation();
    startModelStatusCheck();
    successToastShown = false;
});

// Tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Image preview functionality
function initializeImagePreview() {
    const fileInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            handleImagePreview(e.target);
        });
    });
}

function handleImagePreview(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        
        // Validate file size (16MB limit)
        if (file.size > 16 * 1024 * 1024) {
            showNotification('File size must be less than 16MB', 'error');
            input.value = '';
            return;
        }
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showNotification('Please select a valid image file', 'error');
            input.value = '';
            return;
        }
        
        // Create preview
        const reader = new FileReader();
        reader.onload = function(e) {
            createImagePreview(e.target.result, file.name);
        };
        reader.readAsDataURL(file);
    }
}

function createImagePreview(src, filename) {
    // Remove existing preview
    const existingPreview = document.getElementById('imagePreview');
    if (existingPreview) {
        existingPreview.remove();
    }
    
    // Create new preview
    const preview = document.createElement('div');
    preview.id = 'imagePreview';
    preview.className = 'mt-3 text-center';
    preview.innerHTML = `
        <div class="card" style="max-width: 300px; margin: 0 auto;">
            <img src="${src}" class="card-img-top" alt="Preview" style="height: 200px; object-fit: cover;">
            <div class="card-body">
                <p class="card-text small text-muted">${filename}</p>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removePreview()">
                    <i class="bi bi-trash me-1"></i>Remove
                </button>
            </div>
        </div>
    `;
    
    // Insert after file input
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.parentNode.appendChild(preview);
    }
}

function removePreview() {
    const preview = document.getElementById('imagePreview');
    if (preview) {
        preview.remove();
    }
    
    // Clear file input
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.value = '';
    }
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Loading overlay
function showLoading(message = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.querySelector('h5').textContent = message;
        overlay.classList.remove('d-none');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('d-none');
    }
}

// Notifications
function showNotification(message, type = 'info') {
    const alertClass = type === 'error' ? 'danger' : type;
    const iconClass = type === 'error' ? 'exclamation-triangle' : 
                     type === 'success' ? 'check-circle' : 'info-circle';
    
    const notification = document.createElement('div');
    notification.className = `alert alert-${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    notification.innerHTML = `
        <i class="bi bi-${iconClass} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Image utilities
function downloadImage(url, filename) {
    fetch(url)
        .then(response => response.blob())
        .then(blob => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            link.click();
            URL.revokeObjectURL(link.href);
        })
        .catch(error => {
            console.error('Download failed:', error);
            showNotification('Download failed. Please try again.', 'error');
        });
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        const success = document.execCommand('copy');
        document.body.removeChild(textArea);
        return Promise.resolve(success);
    }
}

// API utilities
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Intersection Observer for animations
function initializeAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Lazy loading for images
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Don't show error notifications for every JS error in production
    if (window.location.hostname === 'localhost') {
        showNotification(`JavaScript error: ${e.error.message}`, 'error');
    }
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    // Don't show error notifications for every promise rejection in production
    if (window.location.hostname === 'localhost') {
        showNotification(`Promise rejection: ${e.reason}`, 'error');
    }
});

// Performance monitoring
function logPerformance() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
            }, 0);
        });
    }
}

// Initialize performance monitoring in development
if (window.location.hostname === 'localhost') {
    logPerformance();
}

// Service Worker registration (for PWA capabilities)
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js')
                .then(function(registration) {
                    console.log('SW registered: ', registration);
                })
                .catch(function(registrationError) {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }
}

// Model loading status management
let modelStatusInterval = null;
let statusCheckStarted = false;
let successToastShown = false;
let wasLoading = false; // Track if we were actually loading

function checkModelStatus() {
    fetch('/api/models/status')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateModelLoadingUI(data.data);
            }
        })
        .catch(error => {
            console.error('Error checking model status:', error);
        });
}

function updateModelLoadingUI(status) {
    const overlay = document.getElementById('modelLoadingOverlay');
    const title = document.getElementById('modelLoadingTitle');
    const message = document.getElementById('modelLoadingMessage');
    const progressBar = document.getElementById('modelProgressBar');
    const currentArtist = document.getElementById('currentArtist');
    const loadedCount = document.getElementById('loadedCount');
    
    // Update homepage status indicator (only on homepage)
    const statusIndicator = document.getElementById('modelStatusIndicator');
    const statusText = document.getElementById('modelStatusText');
    const isHomepage = window.location.pathname === '/' || window.location.pathname === '/index';
    
    if (status.is_loading) {
        // Mark that we were loading
        wasLoading = true;
        
        // Show loading overlay
        if (overlay) overlay.classList.remove('d-none');
        
        // Show homepage status indicator only on homepage
        if (statusIndicator && isHomepage) {
            statusIndicator.classList.remove('d-none');
            statusIndicator.className = 'alert alert-info d-flex align-items-center mb-4';
        }
        
        // Update content
        if (title) title.textContent = 'Loading AI Models...';
        if (message) message.textContent = status.message;
        if (statusText && isHomepage) statusText.textContent = status.message;
        
        // Update progress bar
        if (progressBar) {
            const progress = Math.round(status.progress);
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
        
        // Update status details
        if (currentArtist && status.current_artist) {
            currentArtist.textContent = `Current: ${status.current_artist.charAt(0).toUpperCase() + status.current_artist.slice(1)}`;
        }
        if (loadedCount) {
            loadedCount.textContent = `Loaded: ${status.loaded_models}/${status.total_models} models`;
        }
        
    } else {
        // Hide loading overlay
        if (overlay) overlay.classList.add('d-none');
        
        // Update homepage status indicator only on homepage
        if (statusIndicator && isHomepage) {
            if (status.message.includes('Ready') || status.loaded_models === status.total_models) {
                statusIndicator.className = 'alert alert-success d-flex align-items-center mb-4';
                if (statusText) statusText.textContent = 'AI Models ready! You can now upload photos.';
                
                // Remove spinner when ready
                const spinner = statusIndicator.querySelector('.spinner-border');
                if (spinner) {
                    spinner.remove();
                }
                
                // Add checkmark icon
                if (!statusIndicator.querySelector('.bi-check-circle')) {
                    const checkIcon = document.createElement('i');
                    checkIcon.className = 'bi bi-check-circle me-2';
                    statusIndicator.querySelector('.d-flex').insertBefore(checkIcon, statusIndicator.querySelector('.d-flex').firstChild);
                }
                
                // Hide indicator after 5 seconds
                setTimeout(() => {
                    if (statusIndicator) {
                        statusIndicator.classList.add('d-none');
                    }
                }, 5000);
                
            } else {
                statusIndicator.classList.add('d-none');
            }
        }
        
        // Stop checking status when models are ready
        if (status.message.includes('Ready') || status.loaded_models === status.total_models) {
            if (modelStatusInterval) {
                clearInterval(modelStatusInterval);
                modelStatusInterval = null;
            }
            
            // Show success message only if we were actually loading and haven't shown it yet
            if (wasLoading && !successToastShown && status.loaded_models > 0) {
                showToast('AI Models loaded successfully!', 'success');
                successToastShown = true;
            }
        }
    }
}

function startModelStatusCheck() {
    // Don't start multiple intervals
    if (statusCheckStarted) {
        return;
    }
    
    statusCheckStarted = true;
    
    // Check immediately
    checkModelStatus();
    
    // Then check every 2 seconds
    modelStatusInterval = setInterval(checkModelStatus, 2000);
}

function resetModelStatusCheck() {
    if (modelStatusInterval) {
        clearInterval(modelStatusInterval);
        modelStatusInterval = null;
    }
    statusCheckStarted = false;
    successToastShown = false;
    wasLoading = false;
}

function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert">
            <div class="toast-header">
                <strong class="me-auto">ArtGAN</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Show toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Export functions for use in other scripts
window.ArtGAN = {
    showLoading,
    hideLoading,
    showNotification,
    downloadImage,
    copyToClipboard,
    apiRequest,
    toggleTheme
}; 