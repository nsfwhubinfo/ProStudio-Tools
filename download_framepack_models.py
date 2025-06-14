#!/usr/bin/env python3
"""
Download Frame Pack models for offline use
"""

import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download

# Add Frame Pack to path
framepack_path = Path.home() / ".cache/prostudio/models/FramePack"
sys.path.insert(0, str(framepack_path))

print("=" * 60)
print("Frame Pack Model Downloader")
print("=" * 60)

# Model repository IDs
MODELS = {
    "hunyuan_video": "Tencent-Hunyuan/HunyuanVideo",
    "text_encoder": "lllyasviel/FramePack_text_encoder",
    "vae": "lllyasviel/FramePack_vae"
}

# Base cache directory
cache_dir = Path.home() / ".cache/huggingface"
cache_dir.mkdir(parents=True, exist_ok=True)

print(f"\nModels will be cached in: {cache_dir}")
print("\nNote: This will download ~30GB of data")
print("=" * 60)

for model_name, repo_id in MODELS.items():
    print(f"\nDownloading {model_name} from {repo_id}...")
    try:
        local_dir = cache_dir / "hub" / repo_id.replace("/", "--")
        
        # Download model
        snapshot_download(
            repo_id=repo_id,
            cache_dir=cache_dir,
            local_dir_use_symlinks=True,
            resume_download=True,
            max_workers=4
        )
        
        print(f"✓ {model_name} downloaded successfully")
        
    except Exception as e:
        print(f"✗ Error downloading {model_name}: {e}")
        print("  You can manually download from: https://huggingface.co/" + repo_id)

print("\n" + "=" * 60)
print("Download complete!")
print("\nTo use Frame Pack:")
print("1. cd ~/.cache/prostudio/models/FramePack")
print("2. python demo_gradio.py")
print("=" * 60)