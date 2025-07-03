from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import blueprints
from api.auth import auth_bp
from api.tasks import tasks_bp
from api.submissions import submissions_bp
from api.upload import upload_bp
from api.notifications import notifications_bp
from api.users import users_bp

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Enable CORS
    CORS(app)
    
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
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
