#!/bin/bash
# ProStudio startup script - Direct Python execution
# =================================================

set -e

echo "Starting ProStudio Dynamic Memory Caching Service..."
echo "Environment: ${PROSTUDIO_ENV:-development}"
echo "Redis Host: ${REDIS_HOST:-localhost}"
echo "Workers: ${GUNICORN_WORKERS:-2}"

# Add user's local Python packages to PYTHONPATH
export PYTHONPATH=/home/prostudio/.local/lib/python3.9/site-packages:/app:$PYTHONPATH
export PATH=/home/prostudio/.local/bin:$PATH

# Simple wait for Redis
echo "Waiting for Redis to be ready..."
sleep 5
echo "Proceeding with startup..."

# Debug info
echo "Python version: $(python --version)"
echo "PYTHONPATH: $PYTHONPATH"

# Try to run directly with Python
echo "Starting application with Python gunicorn module..."
exec python -m gunicorn \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads ${GUNICORN_THREADS:-2} \
    --worker-class sync \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    api_server:app