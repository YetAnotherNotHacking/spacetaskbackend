from flask import Blueprint, request, jsonify
from services.database import DatabaseService
from services.auth import AuthService
import os

users_bp = Blueprint('users', __name__)

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

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    """Get user profile"""
    try:
        user = db.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Return public profile info only
        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    """Get tasks created by user"""
    try:
        tasks = db.get_user_tasks(user_id, 'created')
        
        return jsonify({
            'tasks': tasks,
            'count': len(tasks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@users_bp.route('/<int:user_id>/completions', methods=['GET'])
def get_user_completions(user_id):
    """Get tasks completed by user"""
    try:
        tasks = db.get_user_tasks(user_id, 'completed')
        
        return jsonify({
            'completions': tasks,
            'count': len(tasks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500 