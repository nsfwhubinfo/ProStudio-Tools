# ProStudio SDK Quick Start Guide

## 🚀 Getting Started

ProStudio is an AI-powered content generation SDK that creates viral social media content in milliseconds. This guide will help you run it locally and deploy to the cloud.

## 📋 Prerequisites

### Required
- Python 3.8+
- 4GB+ RAM
- pip or conda

### Optional (for full performance)
- NVIDIA GPU with CUDA support
- Redis server
- Docker (for easy Redis setup)

## 🏠 Local Installation

### 1. Basic Setup

```bash
# Clone or navigate to ProStudio directory
cd /home/golde/prostudio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt
```

### 2. Install Performance Dependencies (Optional)

```bash
# For GPU acceleration
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For Cython compilation
pip install cython numpy

# For distributed processing
pip install ray

# For Redis caching
pip install redis

# Compile Cython extensions
cd core/acceleration
python setup.py build_ext --inplace
cd ../..
```

### 3. Quick Test

```bash
# Run the demo
python demo.py

# Run performance benchmark demo
python run_benchmark_demo.py

# Run full benchmarks (requires all dependencies)
python benchmark_suite.py
```

## 🐳 Docker Setup (Recommended)

### 1. Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir cython numpy redis ray

# Compile Cython extensions
RUN cd core/acceleration && python setup.py build_ext --inplace

# Expose API port
EXPOSE 8000

# Run API server
CMD ["python", "api_server.py"]
```

### 2. Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  prostudio:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - ENABLE_GPU=false
    depends_on:
      - redis
    volumes:
      - ./output:/app/output
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### 3. Run with Docker

```bash
# Build and start
docker-compose up --build

# Access API at http://localhost:8000
```

## 🔧 Basic Usage

### Python SDK

```python
from core.content_engine import ContentEngine
from core.content_types import Platform, ContentType

# Initialize engine
engine = ContentEngine({
    'enable_performance_mode': True,
    'enable_fa_cms': True
})
engine.initialize()

# Generate content
content = engine.generate_content(
    concept="How to grow on social media",
    content_type=ContentType.VIDEO_SHORT,
    platform=Platform.TIKTOK
)

print(f"Generated in {content.generation_time_ms}ms")
print(f"Predicted engagement: {content.optimization.predicted_engagement}%")
print(f"Script: {content.metadata['script']}")
```

### REST API

```python
import requests

# Generate content via API
response = requests.post('http://localhost:8000/generate', json={
    'concept': 'AI productivity hacks',
    'platform': 'TIKTOK',
    'content_type': 'VIDEO_SHORT'
})

result = response.json()
print(f"Content ID: {result['id']}")
print(f"Generation time: {result['generation_time_ms']}ms")
```

## ☁️ Cloud Deployment

### Option 1: AWS EC2

```bash
# 1. Launch EC2 instance (recommended: t3.medium or better)
# 2. SSH into instance
# 3. Install Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start

# 4. Clone and run ProStudio
git clone <your-repo-url>
cd prostudio
docker-compose up -d
```

### Option 2: Google Cloud Run

```bash
# 1. Build container
gcloud builds submit --tag gcr.io/YOUR_PROJECT/prostudio

# 2. Deploy to Cloud Run
gcloud run deploy prostudio \
  --image gcr.io/YOUR_PROJECT/prostudio \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

### Option 3: Heroku

```bash
# 1. Create Heroku app
heroku create your-prostudio-app

# 2. Add Redis
heroku addons:create heroku-redis:hobby-dev

# 3. Deploy
git push heroku main

# 4. Scale
heroku ps:scale web=1 worker=2
```

### Option 4: DigitalOcean App Platform

```yaml
# app.yaml
name: prostudio
services:
- name: web
  github:
    repo: your-username/prostudio
    branch: main
  build_command: pip install -r requirements.txt
  run_command: python api_server.py
  environment_slug: python
  instance_size_slug: professional-xs
  instance_count: 1
  http_port: 8000
  
- name: redis
  image:
    registry_type: DOCKER_HUB
    registry: library
    repository: redis
    tag: alpine
```

## 🎮 Testing the Deployment

### 1. Health Check
```bash
curl http://your-deployment-url/health
```

### 2. Generate Content
```bash
curl -X POST http://your-deployment-url/generate \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "5 AI tools for creators",
    "platform": "TIKTOK",
    "content_type": "VIDEO_SHORT"
  }'
```

### 3. Batch Generation
```bash
curl -X POST http://your-deployment-url/batch \
  -H "Content-Type: application/json" \
  -d '{
    "concepts": ["AI tips", "Growth hacks", "Viral secrets"],
    "platforms": ["TIKTOK", "INSTAGRAM"],
    "count": 10
  }'
```

## 📊 Performance Testing

### Local Performance Test
```bash
# Simple test
python -c "
from core.content_engine import ContentEngine
from core.content_types import Platform, ContentType
import time

engine = ContentEngine({'enable_performance_mode': True})
engine.initialize()

times = []
for i in range(10):
    start = time.time()
    content = engine.generate_content(
        concept=f'Test concept {i}',
        content_type=ContentType.VIDEO_SHORT,
        platform=Platform.TIKTOK
    )
    times.append((time.time() - start) * 1000)

print(f'Average: {sum(times)/len(times):.1f}ms')
print(f'Min: {min(times):.1f}ms')
print(f'Max: {max(times):.1f}ms')
"
```

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API performance
ab -n 1000 -c 10 -p request.json -T application/json \
  http://localhost:8000/generate
```

## 🔍 Monitoring & Debugging

### Check Logs
```bash
# Docker logs
docker-compose logs -f

# Heroku logs
heroku logs --tail

# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision"
```

### Performance Metrics
```python
# Check cache stats
from core.acceleration.redis_cache import RedisContentCache
cache = RedisContentCache()
print(cache.get_stats())

# Check GPU usage
nvidia-smi

# Check Redis
redis-cli ping
redis-cli info stats
```

## 💡 Optimization Tips

### 1. Enable All Optimizations
```python
engine = ContentEngine({
    'enable_performance_mode': True,
    'enable_gpu': True,  # If GPU available
    'enable_caching': True,  # If Redis available
    'enable_distributed': True,
    'optimization_iterations': 2  # Reduce for speed
})
```

### 2. Use Batch Processing
```python
# More efficient than individual requests
contents = engine.batch_generate(
    concepts=['concept1', 'concept2', 'concept3'],
    platforms=[Platform.TIKTOK, Platform.INSTAGRAM]
)
```

### 3. Pre-warm Cache
```python
# Cache popular concepts
from core.acceleration.redis_cache import RedisContentCache
cache = RedisContentCache()
cache.warm_cache(
    popular_concepts=['AI tips', 'Growth hacks', 'Viral content'],
    platforms=['TIKTOK', 'INSTAGRAM']
)
```

## 🚨 Troubleshooting

### Common Issues

1. **ImportError: No module named 'core'**
   ```bash
   export PYTHONPATH=/path/to/prostudio:$PYTHONPATH
   ```

2. **Redis connection refused**
   ```bash
   # Start Redis
   docker run -d -p 6379:6379 redis:alpine
   ```

3. **GPU not detected**
   ```bash
   # Check CUDA
   python -c "import torch; print(torch.cuda.is_available())"
   ```

4. **Slow performance**
   - Compile Cython extensions
   - Enable Redis caching
   - Use GPU if available
   - Reduce optimization_iterations

## 📚 Next Steps

1. **API Documentation**: See `API_DOCUMENTATION.md`
2. **Advanced Features**: Check `docs/advanced_usage.md`
3. **Contributing**: Read `CONTRIBUTING.md`
4. **Support**: Open an issue on GitHub

## 🎉 Quick Win

Try this one-liner to see ProStudio in action:

```bash
python -c "from demo import main; main()" | head -20
```

You should see content generated in milliseconds!

---

**Happy Creating! 🚀**

For more help, visit: [ProStudio Documentation](https://github.com/your-username/prostudio)