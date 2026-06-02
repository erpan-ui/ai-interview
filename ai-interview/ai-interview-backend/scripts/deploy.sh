#!/bin/bash

# Prepwise Production Environment Deployment Script
# This script handles the deployment process on the production server

set -e  # Exit on any error

# Configuration
COMPOSE_FILES="${COMPOSE_FILES:-"-f docker-compose.yml -f docker-compose.prod.yml"}"
API_PORT="${API_PORT:-8001}"
HEALTH_ENDPOINT="http://localhost:${API_PORT}/api/v1/config/health"
TIMEOUT=120

echo "🚀 Starting Prepwise deployment..."

# Check if IMAGE_TAG is set when using production compose files
if [[ "$COMPOSE_FILES" == *"docker-compose.prod.yml"* ]] && [[ -z "$IMAGE_TAG" ]]; then
    echo "⚠️  Warning: IMAGE_TAG not set, using default image tag"
    export IMAGE_TAG="ghcr.io/dev-zetos/prepwise-app:latest"
fi

echo "📋 Using compose files: $COMPOSE_FILES"
echo "🐳 Using Docker image: $IMAGE_TAG"
echo "🔌 Using API port: $API_PORT"
echo "🏥 Health endpoint: $HEALTH_ENDPOINT"

# Function to check application health
check_health() {
    local timeout=$1
    echo "⏳ Waiting for application to be ready..."

    while [ $timeout -gt 0 ]; do
        if curl -f $HEALTH_ENDPOINT >/dev/null 2>&1; then
            echo "✅ Application is ready!"
            return 0
        fi
        echo "Waiting... ($timeout seconds left)"
        sleep 5
        timeout=$((timeout - 5))
    done

    echo "❌ Application failed to start within timeout"
    return 1
}

# Function to show service logs on failure
show_logs() {
    echo "📋 Service logs:"
    docker compose $COMPOSE_FILES logs --tail=50
}

# Main deployment process
main() {
    echo "🔍 Environment check:"
    echo "  - API_PORT: $API_PORT"
    echo "  - IMAGE_TAG: $IMAGE_TAG"
    echo "  - COMPOSE_FILES: $COMPOSE_FILES"
    echo "  - HEALTH_ENDPOINT: $HEALTH_ENDPOINT"

    # Pull latest images
    echo "📥 Pulling latest images..."
    docker compose $COMPOSE_FILES pull

    # Stop existing containers gracefully
    echo "🛑 Stopping existing services..."
    docker compose $COMPOSE_FILES down --timeout 30

    # Clean up unused images to free space
    echo "🧹 Cleaning up unused images..."
    docker image prune -f

    # Start services
    echo "🏃 Starting services..."
    docker compose $COMPOSE_FILES up -d

    # Show running containers and their ports
    echo "📊 Container status:"
    docker compose $COMPOSE_FILES ps
    echo "🔌 Port mapping:"
    docker ps --format "table {{.Names}}\t{{.Ports}}"

    # Wait for application to be ready
    if ! check_health $TIMEOUT; then
        show_logs
        exit 1
    fi

    # Run database migrations
    echo "🗄️ Running database migrations..."
    docker compose $COMPOSE_FILES exec -T app alembic upgrade head

    # Show service status
    echo "📊 Service status:"
    docker compose $COMPOSE_FILES ps

    # Final health check
    echo "🏥 Final health check..."
    if curl -f $HEALTH_ENDPOINT; then
        echo "✅ Deployment completed successfully!"
        echo "🔗 Application is available at: $HEALTH_ENDPOINT"
    else
        echo "⚠️ Health check failed after deployment"
        show_logs
        exit 1
    fi
}

# Error handling
trap 'echo "❌ Deployment failed. Check logs above."; show_logs; exit 1' ERR

# Run main deployment
main "$@"