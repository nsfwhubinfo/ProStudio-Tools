#!/bin/bash
# ProStudio startup script - Test mode
# ====================================

set -e

echo "Starting ProStudio Test API Server..."
echo "Environment: ${PROSTUDIO_ENV:-development}"
echo "Redis Host: ${REDIS_HOST:-localhost}"

# Simple wait
echo "Waiting for services to initialize..."
sleep 3

# Copy test script if it exists
if [ -f "/app/deploy/zero-cost/test_api.py" ]; then
    cp /app/deploy/zero-cost/test_api.py /app/test_api.py
fi

# Start the test server
echo "Starting test server on port 8000..."
cd /app
exec python test_api.py