from flask import Blueprint, request, jsonify
from services.upload import UploadService
from services.auth import AuthService
import os

upload_bp = Blueprint('upload', __name__)

# Initialize services
upload_service = UploadService()
auth_service = AuthService(os.getenv('JWT_SECRET', 'your-secret-key'))

def get_user_from_request():
    """Helper function to get user from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return auth_service.get_user_from_token(token)

@upload_bp.route('', methods=['POST'])
def upload_image():
    """Upload an image file"""
    try:
        # Authenticate user
        user_data = get_user_from_request()
        if not user_data:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not upload_service.allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Read file data
        file_data = file.read()
        
        # Save file
        filename = upload_service.save_image(file_data, file.filename)
        
        if filename:
            # Get base URL from environment or request
            base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
            file_url = upload_service.get_file_url(filename, base_url)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'url': file_url
            }), 201
        else:
            return jsonify({'error': 'Failed to upload file'}), 500
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500 