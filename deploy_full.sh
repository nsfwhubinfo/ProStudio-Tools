#!/bin/bash
# ProStudio Full Deployment Script

echo "🚀 PROSTUDIO FULL DEPLOYMENT"
echo "============================"
echo
echo "This script will set up ProStudio with all optimizations enabled."
echo "Choose your deployment target:"
echo
echo "1. Local Development (Full Setup)"
echo "2. Docker (Recommended for Cloud)"
echo "3. Cloud Deployment Guide"
echo
read -p "Select option (1-3): " deploy_option

case $deploy_option in
    1)
        echo
        echo "📦 LOCAL FULL DEPLOYMENT"
        echo "========================"
        
        # Check system requirements
        echo
        echo "🔍 Checking system requirements..."
        
        # Python version
        if command -v python3 &> /dev/null; then
            python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
            echo "✓ Python $python_version found"
        else
            echo "❌ Python 3 not found. Please install Python 3.8+"
            exit 1
        fi
        
        # Check for GPU
        gpu_available="false"
        if command -v nvidia-smi &> /dev/null; then
            echo "✓ NVIDIA GPU detected"
            gpu_available="true"
        else
            echo "⚠ No NVIDIA GPU detected (CPU mode will be used)"
        fi
        
        # Create virtual environment
        echo
        echo "📦 Setting up virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        
        # Upgrade pip
        pip install --upgrade pip wheel setuptools
        
        # Install core dependencies
        echo
        echo "📥 Installing core dependencies..."
        pip install numpy scipy scikit-learn
        pip install flask flask-cors requests psutil
        
        # Install performance dependencies
        echo
        echo "⚡ Installing performance optimizations..."
        
        # Cython
        echo "  • Installing Cython..."
        pip install cython
        
        # Compile Cython extensions
        echo "  • Compiling Cython extensions..."
        cd core/acceleration
        python setup.py build_ext --inplace
        cd ../..
        
        # Redis
        echo "  • Installing Redis client..."
        pip install redis
        
        # Ray for distributed processing
        echo "  • Installing Ray..."
        pip install ray
        
        # GPU support (if available)
        if [ "$gpu_available" = "true" ]; then
            echo "  • Installing PyTorch with CUDA..."
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
            pip install GPUtil
        fi
        
        # Start Redis using Docker
        echo
        echo "🔴 Starting Redis server..."
        if command -v docker &> /dev/null; then
            docker run -d --name prostudio-redis -p 6379:6379 redis:alpine
            echo "✓ Redis started in Docker"
        else
            echo "⚠ Docker not found. Please install Redis manually or use Docker"
        fi
        
        # Create startup script
        cat > start_local.sh << 'EOF'
#!/bin/bash
# Start ProStudio locally

echo "Starting ProStudio..."

# Activate virtual environment
source venv/bin/activate

# Export environment variables
export ENABLE_GPU=$(command -v nvidia-smi &> /dev/null && echo "true" || echo "false")
export REDIS_HOST=localhost
export RAY_ENABLED=true

# Start API server
echo "🚀 Starting API server on http://localhost:8000"
python api_server.py
EOF
        chmod +x start_local.sh
        
        # Create test script
        cat > test_deployment.sh << 'EOF'
#!/bin/bash
# Test ProStudio deployment

source venv/bin/activate

echo "🧪 Testing ProStudio Deployment"
echo "==============================="

# Test 1: Import test
echo
echo "1️⃣ Testing imports..."
python -c "
try:
    from core.content_engine import ContentEngine
    print('✓ Core engine imported')
    from core.acceleration.redis_cache import RedisContentCache
    print('✓ Redis cache imported')
    from core.acceleration.distributed_engine import DistributedContentEngine
    print('✓ Distributed engine imported')
    print('✅ All imports successful!')
except Exception as e:
    print(f'❌ Import error: {e}')
"

# Test 2: Engine initialization
echo
echo "2️⃣ Testing engine initialization..."
python test_minimal.py

# Test 3: Performance test
echo
echo "3️⃣ Running performance benchmark..."
python run_benchmark_demo.py

echo
echo "✅ Deployment tests complete!"
EOF
        chmod +x test_deployment.sh
        
        echo
        echo "✅ LOCAL DEPLOYMENT COMPLETE!"
        echo
        echo "📋 Next steps:"
        echo "1. Start the server:    ./start_local.sh"
        echo "2. Test deployment:     ./test_deployment.sh"
        echo "3. Access API:          http://localhost:8000"
        echo "4. Test with client:    python test_api_client.py"
        ;;
        
    2)
        echo
        echo "🐳 DOCKER DEPLOYMENT"
        echo "===================="
        
        # Create optimized Dockerfile
        cat > Dockerfile << 'EOF'
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies
RUN pip install --no-cache-dir \
    cython numpy scipy scikit-learn \
    flask flask-cors \
    redis ray psutil \
    gunicorn

# Copy application code
COPY . .

# Compile Cython extensions
RUN cd core/acceleration && \
    python setup.py build_ext --inplace && \
    cd ../..

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV ENABLE_GPU=false
ENV REDIS_HOST=redis

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120", "api_server:app"]
EOF

        # Create docker-compose.yml
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  prostudio:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - ENABLE_GPU=false
      - RAY_ENABLED=true
      - PYTHONUNBUFFERED=1
    depends_on:
      - redis
    volumes:
      - ./output:/app/output
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - prostudio-net
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    networks:
      - prostudio-net
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - prostudio
    restart: unless-stopped
    networks:
      - prostudio-net

volumes:
  redis_data:

networks:
  prostudio-net:
    driver: bridge
EOF

        # Create nginx.conf for load balancing
        cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream prostudio {
        server prostudio:8000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://prostudio;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
        
        location /health {
            proxy_pass http://prostudio/health;
            access_log off;
        }
    }
}
EOF

        # Create production docker-compose
        cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  prostudio:
    image: prostudio:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - REDIS_HOST=redis
      - ENABLE_GPU=false
      - RAY_ENABLED=true
    networks:
      - prostudio-net

  redis:
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
EOF

        # Create build script
        cat > build_docker.sh << 'EOF'
#!/bin/bash
echo "🏗️ Building ProStudio Docker image..."

# Build the image
docker build -t prostudio:latest .

# Tag for registry (update with your registry)
# docker tag prostudio:latest your-registry.com/prostudio:latest

echo "✅ Build complete!"
echo
echo "📋 Next steps:"
echo "1. Start locally:     docker-compose up -d"
echo "2. View logs:         docker-compose logs -f"
echo "3. Scale up:          docker-compose up -d --scale prostudio=3"
echo "4. Push to registry:  docker push your-registry/prostudio:latest"
EOF
        chmod +x build_docker.sh
        
        echo
        echo "✅ DOCKER DEPLOYMENT READY!"
        echo
        echo "📋 Quick start:"
        echo "1. Build:     ./build_docker.sh"
        echo "2. Run:       docker-compose up -d"
        echo "3. Access:    http://localhost"
        echo "4. Monitor:   docker-compose logs -f"
        ;;
        
    3)
        echo
        echo "☁️ CLOUD DEPLOYMENT GUIDES"
        echo "========================="
        
        # Create AWS deployment script
        cat > deploy_aws.sh << 'EOF'
#!/bin/bash
# AWS ECS Deployment Script

echo "🚀 Deploying to AWS ECS..."

# Variables
REGION="us-east-1"
CLUSTER_NAME="prostudio-cluster"
SERVICE_NAME="prostudio-service"
TASK_FAMILY="prostudio-task"

# Create ECS cluster
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $REGION

# Register task definition
cat > task-definition.json << EOT
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "prostudio",
      "image": "prostudio:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "REDIS_HOST", "value": "redis.prostudio.local"},
        {"name": "ENABLE_GPU", "value": "false"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/prostudio",
          "awslogs-region": "$REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOT

aws ecs register-task-definition --cli-input-json file://task-definition.json --region $REGION

# Create service
aws ecs create-service \
  --cluster $CLUSTER_NAME \
  --service-name $SERVICE_NAME \
  --task-definition $TASK_FAMILY:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --region $REGION

echo "✅ Deployed to AWS ECS!"
EOF
        chmod +x deploy_aws.sh
        
        # Create GCP deployment script
        cat > deploy_gcp.sh << 'EOF'
#!/bin/bash
# Google Cloud Run Deployment

echo "🚀 Deploying to Google Cloud Run..."

PROJECT_ID="your-project-id"
SERVICE_NAME="prostudio"
REGION="us-central1"

# Build and push image
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 100 \
  --allow-unauthenticated \
  --set-env-vars="ENABLE_GPU=false,REDIS_HOST=redis.prostudio.internal"

echo "✅ Deployed to Google Cloud Run!"
echo "URL: $(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')"
EOF
        chmod +x deploy_gcp.sh
        
        # Create Kubernetes deployment
        cat > k8s-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prostudio
spec:
  replicas: 3
  selector:
    matchLabels:
      app: prostudio
  template:
    metadata:
      labels:
        app: prostudio
    spec:
      containers:
      - name: prostudio
        image: prostudio:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: redis-service
        - name: ENABLE_GPU
          value: "false"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: prostudio-service
spec:
  selector:
    app: prostudio
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-storage
          mountPath: /data
      volumes:
      - name: redis-storage
        emptyDir: {}
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: prostudio-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: prostudio
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
EOF

        echo
        echo "✅ CLOUD DEPLOYMENT GUIDES CREATED!"
        echo
        echo "📋 Available deployment options:"
        echo
        echo "1. AWS ECS:"
        echo "   ./deploy_aws.sh"
        echo
        echo "2. Google Cloud Run:"
        echo "   ./deploy_gcp.sh"
        echo
        echo "3. Kubernetes:"
        echo "   kubectl apply -f k8s-deployment.yaml"
        echo
        echo "4. Docker Swarm:"
        echo "   docker stack deploy -c docker-compose.prod.yml prostudio"
        echo
        echo "📚 See QUICKSTART_GUIDE.md for detailed instructions"
        ;;
esac

# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
# ProStudio Monitoring Script

echo "📊 ProStudio Monitoring Dashboard"
echo "================================"

while true; do
    clear
    echo "📊 ProStudio Monitoring - $(date)"
    echo "================================"
    
    # API Health
    echo
    echo "🏥 API Health:"
    curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ API not responding"
    
    # Redis Status
    echo
    echo "🔴 Redis Status:"
    redis-cli ping 2>/dev/null && echo "✓ Redis connected" || echo "❌ Redis not connected"
    
    # Docker Status (if using Docker)
    if command -v docker &> /dev/null; then
        echo
        echo "🐳 Docker Containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep prostudio
    fi
    
    # Performance Stats
    echo
    echo "📈 Performance Stats:"
    curl -s http://localhost:8000/stats | python3 -m json.tool 2>/dev/null || echo "No stats available"
    
    echo
    echo "Press Ctrl+C to exit | Refreshing in 5s..."
    sleep 5
done
EOF
chmod +x monitor.sh

echo
echo "🎉 DEPLOYMENT SETUP COMPLETE!"
echo
echo "📋 Quick Reference:"
echo "==================="
echo
echo "Local Development:"
echo "  ./start_local.sh      - Start local server"
echo "  ./test_deployment.sh  - Test deployment"
echo
echo "Docker:"
echo "  ./build_docker.sh     - Build Docker image"
echo "  docker-compose up     - Start with Docker"
echo
echo "Monitoring:"
echo "  ./monitor.sh          - Live monitoring dashboard"
echo
echo "🚀 Ready to deploy ProStudio at scale!"