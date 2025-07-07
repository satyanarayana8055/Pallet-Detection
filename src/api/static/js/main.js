class PalletDetectionApp {
    constructor() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.uploadBtn = document.getElementById('upload-btn');
        this.progressSection = document.getElementById('progress-section');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.progressPercentage = document.getElementById('progress-percentage');
        this.resultsSection = document.getElementById('results-section');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.errorModal = document.getElementById('error-modal');
        this.errorMessage = document.getElementById('error-message');
        
        this.totalProcessed = 0;
        this.totalPallets = 0;
        this.currentFile = null;
        
        this.initializeEventListeners();
        this.initializeAnimations();
    }
    
    initializeEventListeners() {
        // File input events
        this.uploadBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        
        // Action buttons
        document.getElementById('new-detection-btn')?.addEventListener('click', () => this.resetToUpload());
        document.getElementById('download-results-btn')?.addEventListener('click', () => this.downloadResults());
        document.getElementById('share-results-btn')?.addEventListener('click', () => this.shareResults());
        
        // View toggle
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.toggleView(e));
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }
    
    initializeAnimations() {
        // Add entrance animations to elements
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        });
        
        document.querySelectorAll('.upload-card, .comparison-card, .detection-details').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }
    
    processFile(file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showError('Please select a valid image file (JPG, PNG, WEBP, BMP).');
            return;
        }
        
        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            this.showError('File size must be less than 16MB. Please choose a smaller image.');
            return;
        }
        
        this.currentFile = file;
        this.uploadAndDetect(file);
    }
    
    async uploadAndDetect(file) {
        try {
            this.showLoading();
            this.showProgress();
            
            const formData = new FormData();
            formData.append('file', file);
            
            // Progress simulation
            this.updateProgress(10, 'Uploading image...');
            await this.delay(500);
            
            this.updateProgress(30, 'Preprocessing image...');
            await this.delay(500);
            
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });
            
            this.updateProgress(70, 'Running AI detection...');
            await this.delay(800);
            
            const result = await response.json();
            
            this.updateProgress(90, 'Processing results...');
            await this.delay(500);
            
            if (result.success) {
                this.updateProgress(100, 'Complete!');
                await this.delay(500);
                
                this.displayResults(result, file);
                this.hideLoading();
                this.hideProgress();
            } else {
                throw new Error(result.error || 'Detection failed');
            }
            
        } catch (error) {
            this.hideLoading();
            this.hideProgress();
            this.showError(error.message || 'An error occurred during detection. Please try again.');
        }
    }
    
    displayResults(result, originalFile) {
        // Update stats
        this.totalProcessed++;
        this.totalPallets += result.total_pallets;
        this.updateStats();
        
        // Display images
        const originalImage = document.getElementById('original-image');
        const processedImage = document.getElementById('processed-image');
        
        originalImage.src = result.original_image;
        processedImage.src = result.processed_image;
        
        // Update detection count and confidence
        const detectionCount = document.getElementById('detection-count');
        const avgConfidence = document.getElementById('avg-confidence');
        
        detectionCount.textContent = result.total_pallets;
        
        if (result.detections.length > 0) {
            const avgConf = result.detections.reduce((sum, det) => sum + det.confidence, 0) / result.detections.length;
            avgConfidence.textContent = `${(avgConf * 100).toFixed(1)}%`;
        } else {
            avgConfidence.textContent = '0%';
        }
        
        // Display detection details
        this.displayDetectionDetails(result.detections);
        
        // Show results section with animation
        this.resultsSection.style.display = 'block';
        setTimeout(() => {
            this.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }
    
    displayDetectionDetails(detections) {
        const detailsGrid = document.getElementById('details-grid');
        detailsGrid.innerHTML = '';
        
        if (detections.length === 0) {
            detailsGrid.innerHTML = `
                <div class="no-detections">
                    <i class="fas fa-search"></i>
                    <h4>No Pallets Detected</h4>
                    <p>No pallets were found in this image. Try uploading a different image with visible pallets.</p>
                </div>
            `;
            return;
        }
        
        detections.forEach((detection, index) => {
            const detectionItem = document.createElement('div');
            detectionItem.className = 'detection-item';
            
            const confidence = (detection.confidence * 100).toFixed(1);
            const bbox = detection.bbox;
            
            // Generate a unique color for each detection
            const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];
            const color = colors[index % colors.length];
            detectionItem.style.borderLeftColor = color;
            
            detectionItem.innerHTML = `
                <h4><i class="fas fa-cube" style="color: ${color}"></i> Pallet ${index + 1}</h4>
                <div class="detection-property">
                    <span>Confidence Score:</span>
                    <span>${confidence}%</span>
                </div>
                <div class="detection-property">
                    <span>Position (X, Y):</span>
                    <span>${bbox[0]}, ${bbox[1]}</span>
                </div>
                <div class="detection-property">
                    <span>Dimensions (W × H):</span>
                    <span>${bbox[2]} × ${bbox[3]}</span>
                </div>
                <div class="detection-property">
                    <span>Classification:</span>
                    <span>${detection.class}</span>
                </div>
            `;
            
            // Add hover effect
            detectionItem.addEventListener('mouseenter', () => {
                detectionItem.style.transform = 'translateY(-4px) scale(1.02)';
                detectionItem.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.2)';
            });
            
            detectionItem.addEventListener('mouseleave', () => {
                detectionItem.style.transform = 'translateY(0) scale(1)';
                detectionItem.style.boxShadow = 'none';
            });
            
            detailsGrid.appendChild(detectionItem);
        });
    }
    
    updateStats() {
        const processedElement = document.getElementById('total-processed');
        const palletsElement = document.getElementById('total-pallets');
        
        this.animateNumber(processedElement, this.totalProcessed);
        this.animateNumber(palletsElement, this.totalPallets);
    }
    
    animateNumber(element, targetValue) {
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            element.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
    
    hideLoading() {
        this.loadingOverlay.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    showProgress() {
        this.progressSection.style.display = 'block';
        this.updateProgress(0, 'Initializing...');
    }
    
    hideProgress() {
        this.progressSection.style.display = 'none';
    }
    
    updateProgress(percent, text) {
        this.progressFill.style.width = `${percent}%`;
        this.progressText.textContent = text;
        this.progressPercentage.textContent = `${percent}%`;
    }
    
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
    
    hideErrorModal() {
        this.errorModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    resetToUpload() {
        this.resultsSection.style.display = 'none';
        this.fileInput.value = '';
        this.currentFile = null;
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    downloadResults() {
        if (!this.currentFile) return;
        
        const originalImage = document.getElementById('original-image');
        const processedImage = document.getElementById('processed-image');
        const detectionCount = document.getElementById('detection-count');
        const avgConfidence = document.getElementById('avg-confidence');
        
        const results = {
            timestamp: new Date().toISOString(),
            filename: this.currentFile.name,
            total_pallets: detectionCount.textContent,
            average_confidence: avgConfidence.textContent,
            processing_info: {
                file_size: this.formatFileSize(this.currentFile.size),
                file_type: this.currentFile.type,
                processed_at: new Date().toLocaleString()
            }
        };
        
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(results, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `pallet_detection_${Date.now()}.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
        
        this.showNotification('Results downloaded successfully!', 'success');
    }
    
    shareResults() {
        if (navigator.share) {
            navigator.share({
                title: 'Pallet Detection Results',
                text: `Found ${document.getElementById('detection-count').textContent} pallets with ${document.getElementById('avg-confidence').textContent} average confidence`,
                url: window.location.href
            });
        } else {
            // Fallback: copy to clipboard
            const text = `Pallet Detection Results: Found ${document.getElementById('detection-count').textContent} pallets with ${document.getElementById('avg-confidence').textContent} average confidence`;
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('Results copied to clipboard!', 'success');
            });
        }
    }
    
    toggleView(e) {
        const viewType = e.target.closest('.toggle-btn').dataset.view;
        const detailsGrid = document.getElementById('details-grid');
        
        // Update active button
        document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
        e.target.closest('.toggle-btn').classList.add('active');
        
        // Update grid layout
        if (viewType === 'list') {
            detailsGrid.style.gridTemplateColumns = '1fr';
        } else {
            detailsGrid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(300px, 1fr))';
        }
    }
    
    handleKeyboard(e) {
        // ESC to close modals
        if (e.key === 'Escape') {
            this.hideErrorModal();
            closeImageModal();
        }
        
        // Ctrl+N for new detection
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            this.resetToUpload();
        }
        
        // Ctrl+D for download
        if (e.ctrlKey && e.key === 'd') {
            e.preventDefault();
            this.downloadResults();
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Global functions for modal handling
function openImageModal(imageId) {
    const modal = document.getElementById('image-modal');
    const modalImage = document.getElementById('modal-image');
    const modalTitle = document.getElementById('modal-title');
    const sourceImage = document.getElementById(imageId);
    
    modalImage.src = sourceImage.src;
    modalTitle.textContent = imageId.includes('original') ? 'Original Image' : 'Detection Results';
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeImageModal() {
    const modal = document.getElementById('image-modal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function closeErrorModal() {
    app.hideErrorModal();
}

function retryDetection() {
    closeErrorModal();
    if (app.currentFile) {
        app.uploadAndDetect(app.currentFile);
    }
}

// Initialize the app when DOM is loaded
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new PalletDetectionApp();
});

// Add notification styles
const notificationStyles = `
.notification {
    position: fixed;
    top: 100px;
    right: 20px;
    background: var(--bg-card);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-md);
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-primary);
    backdrop-filter: blur(20px);
    box-shadow: var(--shadow-lg);
    transform: translateX(100%);
    transition: transform 0.3s ease;
    z-index: 4000;
}

.notification.show {
    transform: translateX(0);
}

.notification.success {
    border-left: 4px solid #4facfe;
}

.notification.error {
    border-left: 4px solid #fa709a;
}

.notification i {
    font-size: 1.25rem;
}

.no-detections {
    grid-column: 1 / -1;
    text-align: center;
    padding: 3rem;
    color: var(--text-secondary);
}

.no-detections i {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

.no-detections h4 {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
    color: var(--text-primary);
}
`;

// Inject notification styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);
