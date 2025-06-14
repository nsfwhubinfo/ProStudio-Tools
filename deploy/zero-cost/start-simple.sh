#!/bin/bash
# ProStudio startup script - Simplified version
# =============================================

set -e

echo "Starting ProStudio Dynamic Memory Caching Service..."
echo "Environment: ${PROSTUDIO_ENV:-development}"
echo "Redis Host: ${REDIS_HOST:-localhost}"
echo "Workers: ${GUNICORN_WORKERS:-2}"

# Simple wait for Redis - just sleep a bit since Redis container is marked as healthy
echo "Waiting for Redis to be ready..."
sleep 5
echo "Proceeding with startup..."

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