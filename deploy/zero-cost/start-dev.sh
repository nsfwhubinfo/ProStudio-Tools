#!/bin/bash
# ProStudio startup script - Development mode
# ===========================================

set -e

echo "Starting ProStudio Dynamic Memory Caching Service (Dev Mode)..."
echo "Environment: ${PROSTUDIO_ENV:-development}"
echo "Redis Host: ${REDIS_HOST:-localhost}"

# Simple wait for Redis
echo "Waiting for Redis to be ready..."
sleep 5

# Add local packages to Python path
export PYTHONPATH=/home/prostudio/.local/lib/python3.9/site-packages:$PYTHONPATH

# Check what we have
echo "Checking Python environment..."
python --version

# Try to start the Flask app directly
echo "Starting Flask development server..."
cd /app

# First, let's check if we have Flask
python -c "import sys; print('Python path:', sys.path)"
python -c "
try:
    import flask
    print('Flask is available')
except ImportError:
    print('Flask not found in Python path')
"

# Start the app with Flask's built-in server
exec python api_server.py