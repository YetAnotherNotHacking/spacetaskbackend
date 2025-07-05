#!/bin/bash

# SpaceTask Backend Update Script
# This script pulls the latest code from GitHub and updates the running Docker containers

set -e  # Exit on any error

# Configuration
REPO_DIR="/path/to/your/spacetaskbackend"  # Update this path
BRANCH="main"
BACKUP_DIR="/tmp/spacetask_backup_$(date +%i4%m%d_%H%M%S)"
LOG_FILE="/var/log/spacetask_update.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root or with sudo
check_permissions() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root or with sudo"
        exit 1
    fi
}

# Check if Docker and Docker Compose are available
check_dependencies() {
    log "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        error "Git is not installed or not in PATH"
        exit 1
    fi
    
    success "All dependencies are available"
}

# Create backup of current state
create_backup() {
    log "Creating backup of current deployment..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup current code
    if [ -d "$REPO_DIR" ]; then
        cp -r "$REPO_DIR" "$BACKUP_DIR/code"
        success "Code backup created at $BACKUP_DIR/code"
    fi
    
    # Backup database and uploads if they exist
    if docker volume ls | grep -q "spacetaskbackend_spacetask_data"; then
        docker run --rm -v spacetaskbackend_spacetask_data:/source -v "$BACKUP_DIR":/backup alpine tar czf /backup/database_backup.tar.gz -C /source .
        success "Database backup created at $BACKUP_DIR/database_backup.tar.gz"
    fi
    
    if docker volume ls | grep -q "spacetaskbackend_spacetask_uploads"; then
        docker run --rm -v spacetaskbackend_spacetask_uploads:/source -v "$BACKUP_DIR":/backup alpine tar czf /backup/uploads_backup.tar.gz -C /source .
        success "Uploads backup created at $BACKUP_DIR/uploads_backup.tar.gz"
    fi
}

# Pull latest code from GitHub
pull_updates() {
    log "Pulling latest code from GitHub..."
    
    cd "$REPO_DIR"
    
    # Stash any local changes
    if ! git diff --quiet; then
        warning "Local changes detected, stashing them..."
        git stash push -m "Auto-stash before update $(date)"
    fi
    
    # Pull latest changes
    git fetch origin
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
    
    success "Code updated successfully"
}

# Check if containers are running
check_containers() {
    log "Checking current container status..."
    
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log "Containers are currently running"
        return 0
    else
        log "No containers are currently running"
        return 1
    fi
}

# Stop running containers
stop_containers() {
    log "Stopping running containers..."
    
    cd "$REPO_DIR"
    docker-compose -f docker-compose.prod.yml down
    
    success "Containers stopped"
}

# Build new images
build_images() {
    log "Building new Docker images..."
    
    cd "$REPO_DIR"
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    success "Images built successfully"
}

# Start containers
start_containers() {
    log "Starting updated containers..."
    
    cd "$REPO_DIR"
    docker-compose -f docker-compose.prod.yml up -d
    
    success "Containers started"
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Wait for containers to be ready
    sleep 10
    
    # Check if containers are running
    if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        error "Containers failed to start properly"
        return 1
    fi
    
    # Check if API is responding
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost/api/health > /dev/null 2>&1; then
            success "API health check passed"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, retrying in 5 seconds..."
        sleep 5
        ((attempt++))
    done
    
    error "Health check failed after $max_attempts attempts"
    return 1
}

# Rollback function
rollback() {
    error "Update failed, initiating rollback..."
    
    # Stop current containers
    cd "$REPO_DIR"
    docker-compose -f docker-compose.prod.yml down
    
    # Restore code backup
    if [ -d "$BACKUP_DIR/code" ]; then
        rm -rf "$REPO_DIR"
        mv "$BACKUP_DIR/code" "$REPO_DIR"
        log "Code restored from backup"
    fi
    
    # Rebuild and restart with old code
    cd "$REPO_DIR"
    docker-compose -f docker-compose.prod.yml build --no-cache
    docker-compose -f docker-compose.prod.yml up -d
    
    warning "Rollback completed. Please check the application status."
}

# Cleanup old images
cleanup() {
    log "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove old backups (keep last 5)
    find /tmp -name "spacetask_backup_*" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
    
    success "Cleanup completed"
}

# Main execution
main() {
    log "Starting SpaceTask Backend update process..."
    
    # Pre-flight checks
    check_permissions
    check_dependencies
    
    # Check if repo directory exists
    if [ ! -d "$REPO_DIR" ]; then
        error "Repository directory $REPO_DIR does not exist"
        error "Please update the REPO_DIR variable in this script"
        exit 1
    fi
    
    # Create backup
    create_backup
    
    # Pull updates
    if ! pull_updates; then
        error "Failed to pull updates"
        exit 1
    fi
    
    # Check if containers were running
    containers_were_running=false
    if check_containers; then
        containers_were_running=true
        stop_containers
    fi
    
    # Build new images
    if ! build_images; then
        error "Failed to build images"
        if [ "$containers_were_running" = true ]; then
            rollback
        fi
        exit 1
    fi
    
    # Start containers
    if ! start_containers; then
        error "Failed to start containers"
        rollback
        exit 1
    fi
    
    # Health check
    if ! health_check; then
        rollback
        exit 1
    fi
    
    # Cleanup
    cleanup
    
    success "Update completed successfully!"
    log "Backup created at: $BACKUP_DIR"
    log "Application is running at: http://localhost"
    log "API health endpoint: http://localhost/api/health"
}

# Handle script interruption
trap 'error "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@" 