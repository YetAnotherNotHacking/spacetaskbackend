from flask import Blueprint, request, jsonify
from services.database import DatabaseService
from services.auth import AuthService
import os

submissions_bp = Blueprint('submissions', __name__)

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

@submissions_bp.route('/<int:task_id>/submit', methods=['POST'])
def submit_task(task_id):
    """Submit proof for task completion"""
    try:
        # Authenticate user
        user_data = get_user_from_request()
        if not user_data:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Get task
        task = db.get_task_by_id(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if task is active
        if task['status'] != 'active':
            return jsonify({'error': 'Task is not active'}), 400
        
        # Check if user is not the creator
        if task['creator_id'] == user_data['user_id']:
            return jsonify({'error': 'Cannot submit to your own task'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data or 'image_url' not in data:
            return jsonify({'error': 'Image URL required'}), 400
        
        # Create submission
        submission_id = db.create_submission(
            task_id=task_id,
            submitter_id=user_data['user_id'],
            image_url=data['image_url'],
            note=data.get('note')
        )
        
        if submission_id:
            return jsonify({
                'message': 'Submission created successfully',
                'submission_id': submission_id
            }), 201
        else:
            return jsonify({'error': 'Failed to create submission'}), 500
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@submissions_bp.route('/<int:task_id>/submissions', methods=['GET'])
def get_task_submissions(task_id):
    """Get all submissions for a task (owner only)"""
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
            return jsonify({'error': 'Not authorized to view submissions'}), 403
        
        submissions = db.get_task_submissions(task_id)
        
        return jsonify({
            'submissions': submissions,
            'count': len(submissions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@submissions_bp.route('/<int:task_id>/images', methods=['GET'])
def get_task_images(task_id):
    """Get all uploaded images for a task with submission IDs (owner only)"""
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
            return jsonify({'error': 'Not authorized to view task images'}), 403
        
        # Get all submissions for this task
        submissions = db.get_task_submissions(task_id)
        
        # Extract image information
        images = []
        for submission in submissions:
            images.append({
                'submission_id': submission['id'],
                'image_url': submission['image_url'],
                'submitter_id': submission['submitter_id'],
                'submitter_username': submission['submitter_username'],
                'status': submission['status'],
                'submitted_at': submission['submitted_at'],
                'note': submission.get('note', '')
            })
        
        return jsonify({
            'task_id': task_id,
            'task_title': task['title'],
            'images': images,
            'count': len(images)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@submissions_bp.route('/<int:task_id>/submissions/<int:submission_id>/accept', methods=['POST'])
def accept_submission(task_id, submission_id):
    """Accept a submission and transfer coins"""
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
            return jsonify({'error': 'Not authorized to accept submissions'}), 403
        
        # Accept submission
        success = db.accept_submission(submission_id)
        
        if success:
            return jsonify({
                'message': 'Submission accepted successfully',
                'coins_transferred': task['bounty_amount'] + 10  # bounty + base reward
            }), 200
        else:
            return jsonify({'error': 'Failed to accept submission or insufficient coins'}), 400
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500 