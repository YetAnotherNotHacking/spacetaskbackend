from flask import Blueprint, request, jsonify
from services.database import DatabaseService
from services.auth import AuthService
import os

notifications_bp = Blueprint('notifications', __name__)

# Initialize services
db = DatabaseService()
auth_service = AuthService(os.getenv('JWT_SECRET', 'your-secret-key'))

def get_user_from_request():
    """Helper function to get user from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    return auth_service.get_user_from_token(token)

@notifications_bp.route('/register', methods=['POST'])
def register_device():
    """Register device for push notifications"""
    try:
        # Authenticate user
        user_data = get_user_from_request()
        if not user_data:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        if not data or 'device_token' not in data:
            return jsonify({'error': 'Device token required'}), 400
        
        device_token = data['device_token']
        platform = data.get('platform', 'unknown')
        
        # Register device
        success = db.register_device(user_data['user_id'], device_token, platform)
        
        if success:
            return jsonify({'message': 'Device registered successfully'}), 201
        else:
            return jsonify({'error': 'Failed to register device'}), 500
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500 