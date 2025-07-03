#!/usr/bin/env python3
"""
SpaceTask Backend - Main Entry Point
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from api import app

def main():
    """Main function to run the SpaceTask API server"""
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"Starting SpaceTask API server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"Database: {os.getenv('DATABASE_PATH', 'spacetask.db')}")
    
    # Create uploads directory if it doesn't exist
    uploads_dir = os.getenv('UPLOAD_FOLDER', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Run the Flask app
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main() 