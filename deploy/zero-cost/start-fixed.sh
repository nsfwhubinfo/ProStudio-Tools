#!/bin/bash
# ProStudio startup script for zero-cost deployment (Fixed)
# =========================================================

set -e

echo "Starting ProStudio Dynamic Memory Caching Service..."
echo "Environment: ${PROSTUDIO_ENV:-development}"
echo "Redis Host: ${REDIS_HOST:-localhost}"
echo "Workers: ${GUNICORN_WORKERS:-2}"

# Wait for Redis to be ready using Python
echo "Waiting for Redis..."
python -c "
import redis
import time
import os

redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', '6379'))
redis_password = os.environ.get('REDIS_PASSWORD', '')

print(f'Connecting to Redis at {redis_host}:{redis_port}...')

connected = False
for i in range(30):
    try:
        r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)
        r.ping()
        connected = True
        print('Redis is ready!')
        break
    except:
        time.sleep(1)
        print(f'Waiting for Redis... ({i+1}/30)')

if not connected:
    print('Failed to connect to Redis after 30 seconds')
    exit(1)
"

# Run any initialization if needed
if [ -f "init.py" ]; then
    echo "Running initialization..."
    python init.py
fi

# Start the application with Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads ${GUNICORN_THREADS:-2} \
    --worker-class gevent \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload \
    api_server:app