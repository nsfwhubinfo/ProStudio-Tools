#!/bin/bash
# Local Development Quick Start Script
# ====================================

set -e

echo "🚀 ProStudio Local Development Setup"
echo "==================================="
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
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
        -subj "/C=US/ST=State/L=City/O=ProStudio/CN=localhost"
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

# Build images
echo "🏗️  Building Docker images..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

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
    
    if curl -f -s "$url" > /dev/null; then
        echo "✅ $name is running at $url"
    else
        echo "❌ $name is not responding at $url"
    fi
}

# Check each service
check_service "nginx" "http://localhost/health" "Nginx (Load Balancer)"
check_service "app" "http://localhost:8000/health" "ProStudio API"
check_service "redis" "redis://localhost:6379" "Redis Cache"

# Optional monitoring services
if docker-compose ps | grep -q prometheus; then
    check_service "prometheus" "http://localhost:9090" "Prometheus"
    check_service "grafana" "http://localhost:3000" "Grafana"
fi

# Display logs command
echo
echo "📋 Quick Commands:"
echo "=================="
echo
echo "View logs:"
echo "  docker-compose logs -f"
echo
echo "Stop services:"
echo "  docker-compose down"
echo
echo "Start with monitoring:"
echo "  docker-compose --profile monitoring up -d"
echo
echo "Access services:"
echo "  API:        http://localhost"
echo "  Health:     http://localhost/health"
echo "  Metrics:    http://localhost/metrics"
echo "  Prometheus: http://localhost:9090 (if enabled)"
echo "  Grafana:    http://localhost:3000 (if enabled)"
echo
echo "Test API:"
echo "  curl -X POST http://localhost/api/cache/set \\"
echo "    -H 'X-API-Key: local_dev_api_key_change_in_prod' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"key\": \"test\", \"value\": \"Hello ProStudio!\"}'"
echo
echo "✨ Local development environment is ready!"