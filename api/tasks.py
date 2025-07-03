from flask import Blueprint, request, jsonify
from services.database import DatabaseService
from services.auth import AuthService
import os

tasks_bp = Blueprint('tasks', __name__)

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

@tasks_bp.route('', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        # Authenticate user
        user_data = get_user_from_request()
        if not user_data:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'completion_criteria', 'bounty_amount', 'latitude', 'longitude']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate bounty amount
        bounty_amount = data['bounty_amount']
        if not isinstance(bounty_amount, int) or bounty_amount <= 0:
            return jsonify({'error': 'Bounty amount must be a positive integer'}), 400
        
        # Check if user has enough coins
        user = db.get_user_by_id(user_data['user_id'])
        if user['coin_balance'] < bounty_amount:
            return jsonify({'error': 'Insufficient coins for bounty'}), 400
        
        # Create task
        task_id = db.create_task(
            creator_id=user_data['user_id'],
            title=data['title'],
            description=data['description'],
            label=data.get('label', ''),
            completion_criteria=data['completion_criteria'],
            bounty_amount=bounty_amount,
            latitude=data['latitude'],
            longitude=data['longitude'],
            location_name=data.get('location_name')
        )
        
        if task_id:
            return jsonify({
                'message': 'Task created successfully',
                'task_id': task_id
            }), 201
        else:
            return jsonify({'error': 'Failed to create task'}), 500
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('', methods=['GET'])
def get_tasks():
    """Get list of tasks"""
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        status = request.args.get('status', 'active')
        
        tasks = db.get_tasks(limit=limit, offset=offset, status=status)
        
        return jsonify({
            'tasks': tasks,
            'count': len(tasks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get task details"""
    try:
        task = db.get_task_by_id(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({'task': task}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/<int:task_id>', methods=['PATCH'])
def update_task(task_id):
    """Update task (owner only)"""
    try:
        # Authenticate user
        user_data = get_user_from_request()
        if not user_data:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get task
        task = db.get_task_by_id(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if user is the creator
        if task['creator_id'] != user_data['user_id']:
            return jsonify({'error': 'Not authorized to update this task'}), 403
        
        # Check if task is still active
        if task['status'] != 'active':
            return jsonify({'error': 'Cannot update completed or cancelled tasks'}), 400
        
        data = request.get_json()
        
        # Update task fields
        update_fields = {}
        allowed_fields = ['title', 'description', 'completion_criteria', 'bounty_amount', 'label']
        
        for field in allowed_fields:
            if field in data:
                update_fields[field] = data[field]
        
        if update_fields:
            success = db.update_task(task_id, **update_fields)
            if success:
                return jsonify({'message': 'Task updated successfully'}), 200
            else:
                return jsonify({'error': 'Failed to update task'}), 500
        else:
            return jsonify({'error': 'No valid fields to update'}), 400
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete task (owner only, if no submissions)"""
    try:
        # Authenticate user
        user_data = get_user_from_request()
        if not user_data:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get task
        task = db.get_task_by_id(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if user is the creator
        if task['creator_id'] != user_data['user_id']:
            return jsonify({'error': 'Not authorized to delete this task'}), 403
        
        # Try to delete task
        success = db.delete_task(task_id)
        if success:
            return jsonify({'message': 'Task deleted successfully'}), 200
        else:
            return jsonify({'error': 'Cannot delete task with submissions'}), 400
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/nearby', methods=['GET'])
def get_nearby_tasks():
    """Get tasks near a location"""
    try:
        # Get query parameters
        latitude = request.args.get('lat', type=float)
        longitude = request.args.get('lng', type=float)
        radius = request.args.get('radius', 5.0, type=float)
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'Latitude and longitude required'}), 400
        
        tasks = db.get_nearby_tasks(latitude, longitude, radius)
        
        return jsonify({
            'tasks': tasks,
            'count': len(tasks),
            'center': {'lat': latitude, 'lng': longitude},
            'radius_km': radius
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500 