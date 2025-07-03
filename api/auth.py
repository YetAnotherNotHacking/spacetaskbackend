from flask import Blueprint, request, jsonify
from services.database import DatabaseService
from services.auth import AuthService
import os

auth_bp = Blueprint('auth', __name__)

# Initialize services
db = DatabaseService()
auth_service = AuthService(os.getenv('JWT_SECRET', 'your-secret-key'))

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Create new user account with 200 starting coins"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        
        # Basic validation
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Hash password
        password_hash = auth_service.hash_password(password)
        
        # Create user
        user_id = db.create_user(username, email, password_hash)
        
        if user_id is None:
            return jsonify({'error': 'Username or email already exists'}), 409
        
        # Generate token
        token = auth_service.generate_token(user_id, username)
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {
                'id': user_id,
                'username': username,
                'email': email,
                'coin_balance': 200
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return token"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        email = data['email']
        password = data['password']
        
        # Get user by email
        user = db.get_user_by_email(email)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not auth_service.verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = auth_service.generate_token(user['id'], user['username'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'coin_balance': user['coin_balance']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token required'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        user_data = auth_service.get_user_from_token(token)
        if not user_data:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get full user info
        user = db.get_user_by_id(user_data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'coin_balance': user['coin_balance'],
                'created_at': user['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500 