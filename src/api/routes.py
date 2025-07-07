from flask import Blueprint, render_template, request, jsonify, send_from_directory, current_app
import os
import base64
import io
from werkzeug.utils import secure_filename
from PIL import Image
from services.model_service import ModelService
from services.data_service import ImageService
from config.config import Config
# Initialize services
model_service = ModelService()
image_service = ImageService()

# Blueprint instance
routes_bp = Blueprint('routes_bp', __name__)

# Allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@routes_bp.route('/')
def index():
    return render_template('index.html')


@routes_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'pallet-detection-api'})

@routes_bp.route('/detect', methods=['POST'])
def detect_pallets():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if file and allowed_file(file.filename):
            
            # Read file from memory instead of saving to disk
            file_stream = io.BytesIO()
            file.save(file_stream)     
            file_stream.seek(0)     
            processed_image = image_service.preprocess_image_from_file(file_stream)

            # Run YOLO detection
            results = model_service.detect_pallets(processed_image)

            # Draw detections
            result_image = model_service.draw_detections(processed_image, results)

            # Format detections
            detections = [{
                'bbox': result['bbox'],
                'confidence': float(result['confidence']),
                'class': result['class']
            } for result in results]

            # Convert images to base64
            original_buffer = io.BytesIO()
            processed_image.save(original_buffer, format='PNG')
            original_str = base64.b64encode(original_buffer.getvalue()).decode()

            result_buffer = io.BytesIO()
            result_image.save(result_buffer, format='PNG')
            result_str = base64.b64encode(result_buffer.getvalue()).decode()

            return jsonify({
                'success': True,
                'detections': detections,
                'original_image': f'data:image/png;base64,{original_str}',
                'processed_image': f'data:image/png;base64,{result_str}',
                'total_pallets': len(detections)
            })

        return jsonify({'error': 'Invalid file format'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@routes_bp.route('/model/info', methods=['GET'])
def model_info():
    try:
        info = model_service.get_model_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
