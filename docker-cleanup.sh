#!/bin/bash
# Docker Cleanup Script for AI OS
# This script ensures complete cleanup of Docker containers, volumes, and networks
# to prevent conflicts on subsequent runs.

set -e

echo "🧹 Starting Docker cleanup for AI OS..."

# Function to cleanup a compose file
cleanup_compose() {
    local compose_file=$1
    if [ -f "$compose_file" ]; then
        echo "Cleaning up: $compose_file"
        docker compose -f "$compose_file" down -v --remove-orphans 2>/dev/null || true
    fi
}

# Stop and remove all containers, volumes, and networks
echo "Stopping and removing containers..."

# Main compose file
cleanup_compose "docker-compose.yml"

# Environment-specific compose files
cleanup_compose "docker-compose.dev.yml"
cleanup_compose "docker-compose.alpha.yml"
cleanup_compose "docker-compose.beta.yml"
cleanup_compose "docker-compose.preprod.yml"
cleanup_compose "docker-compose.prod.yml"

# Remove any orphaned containers
echo "Removing orphaned containers..."
docker ps -a --filter "name=osdash-" --filter "name=os-dashboard-" -q | xargs -r docker rm -f 2>/dev/null || true

# Remove any orphaned volumes
echo "Removing orphaned volumes..."
docker volume ls --filter "name=osdash-" --filter "name=os-dashboard-" -q | xargs -r docker volume rm 2>/dev/null || true

# Remove any orphaned networks
echo "Removing orphaned networks..."
docker network ls --filter "name=osdash-" --filter "name=os-dashboard-" -q | xargs -r docker network rm 2>/dev/null || true

# Prune system (optional, uncomment if needed)
# echo "Pruning Docker system..."
# docker system prune -f

echo "✅ Docker cleanup complete!"
echo ""
echo "To start fresh, run:"
echo "  docker compose up -d"
echo "  docker compose -f docker-compose.dev.yml up -d"
echo "  docker compose --profile full up -d"
echo "  docker compose --profile gui up -d"







