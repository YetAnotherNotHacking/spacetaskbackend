#!/bin/bash
set -e

# Create data directory if it doesn't exist
mkdir -p /app/data

# Create uploads directory if it doesn't exist
mkdir -p /app/uploads

# Set proper permissions
chmod 755 /app/data
chmod 755 /app/uploads

# Run database initialization (will create tables if they don't exist)
echo "Initializing database..."
python -c "from services.database import DatabaseService; db = DatabaseService(); print('Database initialized successfully')"

# Start the application
echo "Starting SpaceTask Backend on port $PORT..."
exec python main.py 