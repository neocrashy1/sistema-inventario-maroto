#!/bin/bash

# Levitiis Production Deployment Script
# This script handles the deployment of the Levitiis application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="levitiis"
BACKUP_DIR="/backup/levitiis"
LOG_FILE="/var/log/levitiis/deploy.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
    fi
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    command -v docker >/dev/null 2>&1 || error "Docker is not installed"
    command -v docker-compose >/dev/null 2>&1 || error "Docker Compose is not installed"
    command -v git >/dev/null 2>&1 || error "Git is not installed"
    
    success "All dependencies are installed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    sudo mkdir -p /var/log/levitiis
    sudo mkdir -p "$BACKUP_DIR"
    sudo mkdir -p /etc/ssl/levitiis
    
    # Set permissions
    sudo chown -R $USER:$USER /var/log/levitiis
    sudo chown -R $USER:$USER "$BACKUP_DIR"
    
    success "Directories created successfully"
}

# Backup database
backup_database() {
    if [ "$1" = "--skip-backup" ]; then
        warning "Skipping database backup"
        return
    fi
    
    log "Creating database backup..."
    
    BACKUP_FILE="$BACKUP_DIR/levitiis_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    if docker-compose ps postgres | grep -q "Up"; then
        docker-compose exec -T postgres pg_dump -U levitiis_user levitiis_prod > "$BACKUP_FILE"
        success "Database backup created: $BACKUP_FILE"
    else
        warning "PostgreSQL container is not running, skipping backup"
    fi
}

# Pull latest code
update_code() {
    log "Updating code from repository..."
    
    git fetch origin
    git pull origin main
    
    success "Code updated successfully"
}

# Build and deploy
deploy() {
    log "Starting deployment..."
    
    # Stop existing containers
    log "Stopping existing containers..."
    docker-compose down
    
    # Build new images
    log "Building new images..."
    docker-compose build --no-cache
    
    # Start services
    log "Starting services..."
    docker-compose up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30
    
    # Check health
    check_health
    
    success "Deployment completed successfully"
}

# Health check
check_health() {
    log "Performing health checks..."
    
    # Check backend health
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        success "Backend is healthy"
    else
        error "Backend health check failed"
    fi
    
    # Check frontend
    if curl -f http://localhost >/dev/null 2>&1; then
        success "Frontend is healthy"
    else
        error "Frontend health check failed"
    fi
    
    # Check database
    if docker-compose exec -T postgres pg_isready -U levitiis_user -d levitiis_prod >/dev/null 2>&1; then
        success "Database is healthy"
    else
        error "Database health check failed"
    fi
}

# Rollback function
rollback() {
    log "Rolling back to previous version..."
    
    # Stop current containers
    docker-compose down
    
    # Restore from backup if available
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/*.sql 2>/dev/null | head -n1)
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restoring database from backup: $LATEST_BACKUP"
        docker-compose up -d postgres
        sleep 10
        docker-compose exec -T postgres psql -U levitiis_user -d levitiis_prod < "$LATEST_BACKUP"
    fi
    
    # Start previous version
    git checkout HEAD~1
    docker-compose up -d
    
    warning "Rollback completed. Please check the application"
}

# Show logs
show_logs() {
    log "Showing application logs..."
    docker-compose logs -f --tail=100
}

# Main script
main() {
    case "$1" in
        "deploy")
            check_root
            check_dependencies
            create_directories
            backup_database "$2"
            update_code
            deploy
            ;;
        "rollback")
            check_root
            rollback
            ;;
        "health")
            check_health
            ;;
        "logs")
            show_logs
            ;;
        "backup")
            backup_database
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|health|logs|backup} [--skip-backup]"
            echo ""
            echo "Commands:"
            echo "  deploy [--skip-backup]  - Deploy the application"
            echo "  rollback               - Rollback to previous version"
            echo "  health                 - Check application health"
            echo "  logs                   - Show application logs"
            echo "  backup                 - Create database backup"
            exit 1
            ;;
    esac
}

# Create log directory if it doesn't exist
sudo mkdir -p "$(dirname "$LOG_FILE")"
sudo touch "$LOG_FILE"
sudo chown $USER:$USER "$LOG_FILE"

# Run main function
main "$@"