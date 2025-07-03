from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Enable CORS
    CORS(app)
    
    # Import blueprints here to avoid circular imports
    from .auth import auth_bp
    from .tasks import tasks_bp
    from .submissions import submissions_bp
    from .upload import upload_bp
    from .notifications import notifications_bp
    from .users import users_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
    app.register_blueprint(submissions_bp, url_prefix='/api/tasks')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # Serve uploaded files
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory('uploads', filename)
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'SpaceTask API is running'}
    
    # Root API status endpoint
    @app.route('/')
    @app.route('/api')
    def api_status():
        return {
            'name': 'SpaceTask API',
            'version': '1.0.0',
            'status': 'running',
            'message': 'Welcome to SpaceTask - Location-based task completion with rewards!',
            'endpoints': {
                'auth': '/api/signup, /api/login, /api/me',
                'tasks': '/api/tasks (CRUD operations)',
                'submissions': '/api/tasks/:id/submit, /api/tasks/:id/submissions',
                'users': '/api/users/:id (profile, tasks, completions)',
                'upload': '/api/upload (image upload)',
                'notifications': '/api/notifications/register',
                'health': '/api/health'
            },
            'features': [
                'JWT Authentication',
                'Location-based Tasks',
                'Coin Reward System',
                'Image Upload for Proof',
                'Task Bounties'
            ]
        }
    
    return app

# Create the app instance
app = create_app()
