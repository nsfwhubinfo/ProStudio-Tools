#!/bin/bash
# ProStudio startup script - Final version
# ========================================

set -e

echo "Starting ProStudio Dynamic Memory Caching Service..."
echo "Environment: ${PROSTUDIO_ENV:-development}"
echo "Redis Host: ${REDIS_HOST:-localhost}"
echo "Workers: ${GUNICORN_WORKERS:-2}"

# Add user's local Python packages to PATH
export PATH=/home/prostudio/.local/bin:$PATH
export PYTHONPATH=/app:$PYTHONPATH

# Simple wait for Redis - just sleep a bit since Redis container is marked as healthy
echo "Waiting for Redis to be ready..."
sleep 5
echo "Proceeding with startup..."

# Check if gunicorn is available
echo "Python path: $(which python)"
echo "Gunicorn path: $(which gunicorn || echo 'Not in PATH')"

# Start the application
echo "Starting Gunicorn server..."
if [ -f "/home/prostudio/.local/bin/gunicorn" ]; then
    echo "Using gunicorn from user installation"
    exec /home/prostudio/.local/bin/gunicorn \
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
else
    echo "Gunicorn not found, falling back to Python direct execution"
    exec python -m gunicorn \
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
fi