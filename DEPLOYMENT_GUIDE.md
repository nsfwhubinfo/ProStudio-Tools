# ProStudio Full Deployment Guide

## 🚀 Overview

ProStudio is a high-performance AI content generation platform capable of generating viral social media content in milliseconds. This guide covers deployment from local development to production scale.

## 📊 Performance Capabilities

With all optimizations enabled:
- **Single Generation**: 2-10ms
- **Throughput**: 400+ generations/second per instance
- **Concurrent Requests**: 1000+
- **Cache Hit Rate**: 70%+ 
- **Scale**: Horizontal scaling to millions of requests/day

## 🏃 Quick Start

### Option 1: Automated Deployment Script

```bash
# Run the full deployment script
./deploy_full.sh

# Choose:
# 1 - Local deployment with all optimizations
# 2 - Docker deployment (recommended)
# 3 - Cloud deployment guides
```

### Option 2: Docker Compose (Fastest)

```bash
# Start everything with one command
docker-compose up -d

# Access at http://localhost
# API at http://localhost:8000
# Redis at localhost:6379
```

## 📦 Local Development Setup

### 1. Prerequisites

- Python 3.8+
- 8GB RAM minimum
- NVIDIA GPU (optional, for acceleration)
- Redis (optional, for caching)

### 2. Full Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements-prod.txt

# Compile Cython extensions (5x speedup)
cd core/acceleration
python setup.py build_ext --inplace
cd ../..

# Start Redis (for caching)
docker run -d --name redis -p 6379:6379 redis:alpine

# Configure environment
export PROSTUDIO_ENV=production
export SECRET_KEY=$(openssl rand -hex 32)
export API_KEY=$(openssl rand -hex 32)
export REDIS_HOST=localhost
export ENABLE_GPU=true  # if GPU available

# Run production server
gunicorn -c gunicorn.conf.py api_server_prod:app
```

### 3. Verify Installation

```bash
# Test the API
python test_api_client.py

# Run benchmarks
python benchmark_suite.py

# Monitor performance
./monitor.sh
```

## 🐳 Docker Production Deployment

### 1. Build Production Image

```dockerfile
# Multi-stage Dockerfile for optimized image
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
WORKDIR /app
COPY requirements-prod.txt .
RUN pip install --user --no-cache-dir -r requirements-prod.txt

# Compile Cython extensions
COPY core/acceleration/*.pyx core/acceleration/*.py core/acceleration/
RUN cd core/acceleration && python setup.py build_ext --inplace

# Final stage
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/core/acceleration/*.so /app/core/acceleration/

# Copy application
WORKDIR /app
COPY . .

# Configure Python path
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Run with gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "api_server_prod:app"]
```

### 2. Docker Compose Stack

```yaml
version: '3.8'

services:
  prostudio:
    build: .
    image: prostudio:latest
    ports:
      - "8000:8000"
    environment:
      - PROSTUDIO_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - API_KEY=${API_KEY}
      - REDIS_HOST=redis
      - ENABLE_GPU=false
      - ENABLE_METRICS=true
    depends_on:
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          memory: 2G

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

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus

volumes:
  redis_data:
  prometheus_data:
```

### 3. Deploy with Docker

```bash
# Build and start
docker-compose up -d --build

# Scale up
docker-compose up -d --scale prostudio=5

# View logs
docker-compose logs -f prostudio

# Monitor health
watch 'docker-compose ps && echo && curl -s localhost:8000/stats | jq'
```

## ☁️ Cloud Deployments

### AWS ECS Deployment

```bash
# 1. Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URI
docker build -t prostudio .
docker tag prostudio:latest $ECR_URI/prostudio:latest
docker push $ECR_URI/prostudio:latest

# 2. Create task definition
cat > task-definition.json << EOF
{
  "family": "prostudio",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [{
    "name": "prostudio",
    "image": "$ECR_URI/prostudio:latest",
    "portMappings": [{
      "containerPort": 8000,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "PROSTUDIO_ENV", "value": "production"},
      {"name": "REDIS_HOST", "value": "prostudio-redis.abc123.ng.0001.use1.cache.amazonaws.com"}
    ],
    "secrets": [
      {"name": "SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:region:account:secret:prostudio/secret-key"},
      {"name": "API_KEY", "valueFrom": "arn:aws:secretsmanager:region:account:secret:prostudio/api-key"}
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/prostudio",
        "awslogs-region": "us-east-1",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }]
}
EOF

# 3. Create service with auto-scaling
aws ecs create-service \
  --cluster prostudio-cluster \
  --service-name prostudio-api \
  --task-definition prostudio:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --platform-version LATEST \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:region:account:targetgroup/prostudio/xxx,containerName=prostudio,containerPort=8000
```

### Google Cloud Run Deployment

```bash
# 1. Build and push to GCR
gcloud auth configure-docker
docker build -t prostudio .
docker tag prostudio gcr.io/$PROJECT_ID/prostudio
docker push gcr.io/$PROJECT_ID/prostudio

# 2. Deploy to Cloud Run
gcloud run deploy prostudio \
  --image gcr.io/$PROJECT_ID/prostudio \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 1000 \
  --max-instances 100 \
  --allow-unauthenticated \
  --set-env-vars="PROSTUDIO_ENV=production,REDIS_HOST=redis.prostudio.internal" \
  --set-secrets="SECRET_KEY=prostudio-secret-key:latest,API_KEY=prostudio-api-key:latest"

# 3. Set up Redis (Memorystore)
gcloud redis instances create prostudio-cache \
  --size=5 \
  --region=us-central1 \
  --redis-version=redis_6_x

# 4. Configure VPC connector for Redis access
gcloud compute networks vpc-access connectors create prostudio-connector \
  --region=us-central1 \
  --subnet=prostudio-subnet \
  --subnet-project=$PROJECT_ID \
  --min-instances=2 \
  --max-instances=10

# 5. Update Cloud Run service to use connector
gcloud run services update prostudio \
  --vpc-connector=prostudio-connector \
  --region=us-central1
```

### Kubernetes Deployment

```yaml
# prostudio-deployment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: prostudio
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prostudio-config
  namespace: prostudio
data:
  PROSTUDIO_ENV: "production"
  REDIS_HOST: "redis-service"
  ENABLE_GPU: "false"
  ENABLE_METRICS: "true"
---
apiVersion: v1
kind: Secret
metadata:
  name: prostudio-secrets
  namespace: prostudio
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret>
  API_KEY: <base64-encoded-api-key>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prostudio-api
  namespace: prostudio
spec:
  replicas: 3
  selector:
    matchLabels:
      app: prostudio-api
  template:
    metadata:
      labels:
        app: prostudio-api
    spec:
      containers:
      - name: prostudio
        image: your-registry/prostudio:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: prostudio-config
        - secretRef:
            name: prostudio-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "1"
          limits:
            memory: "2Gi"
            cpu: "2"
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
  namespace: prostudio
spec:
  selector:
    app: prostudio-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: prostudio-hpa
  namespace: prostudio
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: prostudio-api
  minReplicas: 3
  maxReplicas: 20
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
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

Deploy to Kubernetes:

```bash
# Apply configuration
kubectl apply -f prostudio-deployment.yaml

# Check status
kubectl get all -n prostudio

# View logs
kubectl logs -n prostudio -l app=prostudio-api -f

# Port forward for testing
kubectl port-forward -n prostudio svc/prostudio-service 8000:80
```

## 📊 Production Configuration

### Environment Variables

```bash
# Required
PROSTUDIO_ENV=production
SECRET_KEY=<random-secret-key>
API_KEY=<api-authentication-key>

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=<redis-password>
REDIS_MAX_CONNECTIONS=50
REDIS_TTL=3600

# Performance
ENABLE_GPU=true
ENABLE_CACHING=true
ENABLE_DISTRIBUTED=true
OPTIMIZATION_ITERATIONS=3
MAX_WORKERS=4

# API Configuration
API_WORKERS=4
API_THREADS=2
API_TIMEOUT=120
RATE_LIMIT_DEFAULT=1000/hour

# Monitoring
ENABLE_METRICS=true
SENTRY_DSN=<sentry-dsn>
LOG_LEVEL=INFO
```

### Gunicorn Configuration

```python
# gunicorn.conf.py
import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"
workers = int(os.getenv('API_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'gevent'
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'prostudio'

# Server mechanics
daemon = False
pidfile = '/tmp/prostudio.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Pre/Post fork hooks
def pre_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_int(worker):
    worker.log.info(f"Worker exiting (pid: {worker.pid})")
```

## 🔍 Monitoring & Operations

### 1. Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health with metrics
curl http://localhost:8000/health | jq

# Prometheus metrics
curl http://localhost:8000/metrics
```

### 2. Performance Monitoring

```bash
# Real-time monitoring
./monitor.sh

# Load testing
ab -n 10000 -c 100 -p request.json -T application/json http://localhost:8000/generate

# Stress testing
hey -n 10000 -c 200 -m POST -H "Content-Type: application/json" -d '{"concept":"test"}' http://localhost:8000/generate
```

### 3. Logging

```python
# Structured logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/prostudio/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}
```

### 4. Alerts & Dashboards

Prometheus alerts:

```yaml
groups:
- name: prostudio
  rules:
  - alert: HighErrorRate
    expr: rate(prostudio_errors_total[5m]) > 0.05
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: High error rate detected
      
  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(prostudio_request_duration_seconds_bucket[5m])) > 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: High API latency detected
      
  - alert: LowCacheHitRate
    expr: rate(prostudio_cache_hits_total[5m]) / (rate(prostudio_cache_hits_total[5m]) + rate(prostudio_cache_misses_total[5m])) < 0.5
    for: 10m
    labels:
      severity: info
    annotations:
      summary: Cache hit rate below 50%
```

## 🚀 Optimization Tips

### 1. Redis Optimization

```bash
# Redis configuration for production
maxmemory 4gb
maxmemory-policy allkeys-lru
save ""  # Disable persistence for cache-only use
tcp-keepalive 60
timeout 300
```

### 2. GPU Optimization

```python
# Enable GPU for maximum performance
export ENABLE_GPU=true
export CUDA_VISIBLE_DEVICES=0,1  # Use multiple GPUs

# In code
if torch.cuda.is_available():
    torch.cuda.set_device(0)
    torch.backends.cudnn.benchmark = True
```

### 3. Load Balancing

```nginx
upstream prostudio_backend {
    least_conn;
    server prostudio1:8000 weight=5;
    server prostudio2:8000 weight=5;
    server prostudio3:8000 weight=5;
    keepalive 32;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://prostudio_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## 📈 Scaling Strategy

### Horizontal Scaling

1. **API Servers**: Scale based on CPU/Memory
   - Target: 70% CPU utilization
   - Min: 3 instances
   - Max: 20 instances

2. **Redis**: Use Redis Cluster for sharding
   - 3 master nodes minimum
   - 1 replica per master

3. **Load Balancer**: Use cloud provider's LB
   - Health checks every 10s
   - Connection draining enabled

### Vertical Scaling

1. **Optimize instance types**:
   - CPU-optimized for API servers
   - Memory-optimized for Redis
   - GPU instances for AI acceleration

2. **Resource allocation**:
   - API: 2-4 vCPUs, 4-8GB RAM
   - Redis: 4-8GB RAM
   - GPU: T4 or better for acceleration

## 🔐 Security Best Practices

1. **API Security**:
   - Use API keys for authentication
   - Enable CORS with specific origins
   - Rate limiting per API key
   - Input validation and sanitization

2. **Network Security**:
   - Use VPC/private networks
   - Enable SSL/TLS everywhere
   - Firewall rules for Redis
   - Regular security updates

3. **Secrets Management**:
   - Use cloud provider's secret manager
   - Rotate keys regularly
   - Never commit secrets to git
   - Use environment variables

## 🎯 Performance Benchmarks

Expected performance in production:

| Metric | Value |
|--------|-------|
| Single Generation | 2-10ms |
| API Latency (P50) | <50ms |
| API Latency (P95) | <100ms |
| API Latency (P99) | <200ms |
| Throughput | 400+ req/s per instance |
| Cache Hit Rate | 70%+ |
| Error Rate | <0.1% |
| Availability | 99.9% |

## 🛠️ Troubleshooting

### Common Issues

1. **High Latency**:
   - Check Redis connection
   - Verify Cython compilation
   - Monitor CPU/Memory usage
   - Check network latency

2. **Memory Issues**:
   - Tune Redis maxmemory
   - Implement request queuing
   - Check for memory leaks
   - Use connection pooling

3. **GPU Not Detected**:
   - Verify CUDA installation
   - Check GPU drivers
   - Set CUDA_VISIBLE_DEVICES
   - Monitor GPU memory

## 📞 Support

- Documentation: See README.md
- Issues: GitHub Issues
- Monitoring: Prometheus + Grafana
- Logs: CloudWatch/Stackdriver/ELK

---

**Ready to scale to millions of users! 🚀**