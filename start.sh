#!/bin/bash
set -e

echo "-> Starting ProStudio Application Server..."

# The PATH is already set by the Dockerfile, so venv is active.
# No need to source activate.sh here.

# Verify gunicorn is found in the venv path
echo "   Gunicorn path: $(which gunicorn)"
echo "   Python path:   $(which python)"
echo "   Environment:   ${PROSTUDIO_ENV:-production}"
echo "   API Workers:   ${API_WORKERS:-4}"

# Execute the Gunicorn server
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers ${API_WORKERS:-4} \
    --worker-class gevent \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --keep-alive 5 \
    --access-logfile '-' \
    --error-logfile '-' \
    --log-level info \
    api_server:app