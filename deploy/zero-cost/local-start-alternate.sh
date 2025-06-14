#!/bin/bash
# Alternative Local Start Script (uses docker compose plugin syntax)
# ==================================================================

set -e

echo "🚀 ProStudio Local Development Setup (Alternative)"
echo "================================================="
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please run ./install-docker.sh first"
    exit 1
fi

# Check which compose command to use
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
    echo "✅ Using Docker Compose plugin"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "✅ Using standalone Docker Compose"
else
    echo "❌ Docker Compose not found"
    echo "Please run ./install-docker.sh first"
    exit 1
fi

# Navigate to zero-cost directory
cd "$(dirname "$0")"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs cache ssl monitoring

# Create self-signed SSL certificate for local HTTPS testing
if [ ! -f ssl/cert.pem ]; then
    echo "🔐 Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=ProStudio/CN=localhost" 2>/dev/null
fi

# Create example prometheus config if not exists
if [ ! -f monitoring/prometheus.yml ]; then
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prostudio'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
EOF
fi

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# ProStudio Local Development Environment Variables
REDIS_PASSWORD=local_dev_redis_password_change_in_prod
API_KEY=local_dev_api_key_change_in_prod
SECRET_KEY=local_dev_secret_key_change_in_prod
GRAFANA_PASSWORD=admin
EOF
    echo "⚠️  Created .env file with default values. Please update for production!"
fi

# Check if Docker daemon is running
if ! docker ps &> /dev/null 2>&1; then
    echo "❌ Docker daemon is not running"
    echo
    echo "Please start Docker:"
    echo "  - If using Docker Desktop: Start Docker Desktop on Windows"
    echo "  - If using Docker in WSL: sudo service docker start"
    exit 1
fi

# Build images
echo "🏗️  Building Docker images..."
$COMPOSE_CMD build

# Start services
echo "🚀 Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
echo

# Function to check service
check_service() {
    local service=$1
    local url=$2
    local name=$3
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo "✅ $name is running at $url"
    else
        echo "⚠️  $name is not responding at $url (may still be starting)"
    fi
}

# Check each service
check_service "nginx" "http://localhost/health" "Nginx (Load Balancer)"
check_service "app" "http://localhost:8000/health" "ProStudio API"

# Check Redis separately
if $COMPOSE_CMD exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis Cache is running"
else
    echo "⚠️  Redis is not responding (may still be starting)"
fi

# Display logs command
echo
echo "📋 Quick Commands:"
echo "=================="
echo
echo "View logs:"
echo "  $COMPOSE_CMD logs -f"
echo
echo "Stop services:"
echo "  $COMPOSE_CMD down"
echo
echo "Start with monitoring:"
echo "  $COMPOSE_CMD --profile monitoring up -d"
echo
echo "Access services:"
echo "  API:        http://localhost"
echo "  Health:     http://localhost/health"
echo "  Metrics:    http://localhost/metrics"
echo
echo "Test API:"
echo "  curl -X POST http://localhost/api/cache/set \\"
echo "    -H 'X-API-Key: local_dev_api_key_change_in_prod' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"key\": \"test\", \"value\": \"Hello ProStudio!\"}'"
echo
echo "Container status:"
$COMPOSE_CMD ps
echo
echo "✨ Local development environment is ready!"
echo
echo "If services are not responding, wait a moment and check logs:"
echo "  $COMPOSE_CMD logs app"