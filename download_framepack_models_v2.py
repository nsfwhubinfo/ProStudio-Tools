#!/usr/bin/env python3
"""
Download Frame Pack models (Community Version)
"""

import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download
import torch

print("=" * 60)
print("Frame Pack Model Downloader (Community Edition)")
print("=" * 60)

# Model repository IDs - Using community versions that don't require auth
MODELS = {
    "hunyuan_video_community": "hunyuanvideo-community/HunyuanVideo",
    "framepack_i2v": "lllyasviel/FramePackI2V_HY",
    "flux_redux": "lllyasviel/flux_redux_bfl"
}

# Base cache directory
cache_dir = Path.home() / ".cache/huggingface"
cache_dir.mkdir(parents=True, exist_ok=True)

print(f"\nModels will be cached in: {cache_dir}")
print("\nNote: This will download ~30GB of data")
print("Using community models (no authentication required)")
print("=" * 60)

total_models = len(MODELS)
completed = 0

for model_name, repo_id in MODELS.items():
    print(f"\n[{completed + 1}/{total_models}] Downloading {model_name}")
    print(f"Repository: {repo_id}")
    
    try:
        # Download model with progress
        local_path = snapshot_download(
            repo_id=repo_id,
            cache_dir=cache_dir,
            resume_download=True,
            max_workers=4,
            ignore_patterns=["*.md", "*.txt"]  # Skip docs to save space
        )
        
        print(f"✓ {model_name} downloaded to: {local_path}")
        completed += 1
        
    except Exception as e:
        print(f"✗ Error downloading {model_name}: {e}")
        print(f"  Try manually: https://huggingface.co/{repo_id}")

print("\n" + "=" * 60)
print(f"Download summary: {completed}/{total_models} models downloaded")

if completed == total_models:
    print("\n✓ All models downloaded successfully!")
    print("\nFrame Pack is ready to use:")
    print("1. cd ~/.cache/prostudio/models/FramePack")
    print("2. python demo_gradio.py")
else:
    print("\n⚠ Some models failed to download")
    print("You may need to manually download or check your internet connection")

# Check GPU memory
if torch.cuda.is_available():
    gpu_mem = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"\nDetected GPU memory: {gpu_mem:.1f} GB")
    if gpu_mem >= 6:
        print("✓ Your GPU has sufficient memory for Frame Pack")
    else:
        print("⚠ Frame Pack requires at least 6GB VRAM")
else:
    print("\n⚠ No CUDA GPU detected")

print("=" * 60)