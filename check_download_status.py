#!/usr/bin/env python3
"""
Check Frame Pack download status
"""

import os
from pathlib import Path
import subprocess

print("=" * 60)
print("Frame Pack Download Status")
print("=" * 60)

# Check cache directory size
cache_dir = Path.home() / ".cache/huggingface"
if cache_dir.exists():
    try:
        result = subprocess.run(['du', '-sh', str(cache_dir)], capture_output=True, text=True)
        if result.returncode == 0:
            size = result.stdout.strip().split('\t')[0]
            print(f"\nCache directory size: {size}")
    except:
        pass

# Check for model directories
models_to_check = [
    "models--hunyuanvideo-community--HunyuanVideo",
    "models--lllyasviel--FramePackI2V_HY",
    "models--lllyasviel--flux_redux_bfl"
]

print("\nModel status:")
for model in models_to_check:
    model_path = cache_dir / "hub" / model
    if model_path.exists():
        model_name = model.replace("models--", "").replace("--", "/")
        # Check if download is complete by looking for key files
        snapshots = model_path / "snapshots"
        if snapshots.exists() and any(snapshots.iterdir()):
            print(f"✓ {model_name} - Downloaded")
        else:
            print(f"⏳ {model_name} - In progress")
    else:
        model_name = model.replace("models--", "").replace("--", "/")
        print(f"✗ {model_name} - Not started")

# Check if download log exists
log_file = Path("download_framepack_v2.log")
if log_file.exists():
    print(f"\n📄 Download log: {log_file}")
    # Get last few lines
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                print("\nLast status:")
                for line in lines[-5:]:
                    print(f"  {line.strip()}")
    except:
        pass

# Check for running download processes
try:
    result = subprocess.run(['pgrep', '-f', 'download_framepack'], capture_output=True, text=True)
    if result.stdout.strip():
        print(f"\n🔄 Download process running (PID: {result.stdout.strip()})")
    else:
        print("\n⏹ No active download process")
except:
    pass

print("\n" + "=" * 60)
print("Tips:")
print("- Downloads resume automatically if interrupted")
print("- Full download is ~30GB")
print("- Once complete, run: cd ~/.cache/prostudio/models/FramePack && python demo_gradio.py")
print("=" * 60)