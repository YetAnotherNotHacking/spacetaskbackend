#!/bin/bash
set -e

# Create data directory if it doesn't exist
mkdir -p /app/data

# Create uploads directory if it doesn't exist
mkdir -p /app/uploads

# Set proper permissions (as root, before switching to appuser)
if [ "$(whoami)" = "root" ]; then
    chown -R appuser:appuser /app/data /app/uploads
    chmod 755 /app/data /app/uploads
    exec gosu appuser "$0" "$@"
fi

# Now running as appuser
# Set database path to the mounted volume
export DATABASE_PATH="/app/data/spacetask.db"

# Run database initialization (will create tables if they don't exist)
echo "Initializing database at $DATABASE_PATH..."
python -c "from services.database import DatabaseService; db = DatabaseService('$DATABASE_PATH'); print('Database initialized successfully')"

# Start the application
echo "Starting SpaceTask Backend on port $PORT..."
exec python main.py 