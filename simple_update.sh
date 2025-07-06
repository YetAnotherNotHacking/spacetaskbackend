#!/bin/bash

# Simple SpaceTask Update Script
# Usage: ./simple_update.sh

set -e

echo "🚀 Starting SpaceTask update..."

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Stop containers
echo "🛑 Stopping containers..."
docker-compose -f docker-compose.prod.yml down

# Rebuild and start
echo "🔨 Rebuilding and starting containers..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait a bit for startup
echo "⏳ Waiting for containers to start..."
sleep 15

# Check if it's working
echo "🔍 Checking if API is responding..."
if curl -f -s http://silverflag.net:8000/api/health > /dev/null; then
    echo "✅ Update completed successfully!"
    echo "🌐 API is available at: http://silverflag.net:8000"
else
    echo "❌ API health check failed"
    echo "📋 Container status:"
    docker-compose -f docker-compose.prod.yml ps
    echo "📋 Recent logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=20
fi 