#!/bin/bash
# Start Frame Pack model download in background

echo "Starting Frame Pack model download..."
echo "This will download ~30GB in the background"
echo "Check progress in: download_framepack.log"

cd ~/prostudio
source venv/bin/activate

# Run download in background
nohup python download_framepack_models.py > download_framepack.log 2>&1 &
PID=$!

echo "Download started with PID: $PID"
echo "Monitor progress: tail -f download_framepack.log"
echo "Check if complete: ps -p $PID"