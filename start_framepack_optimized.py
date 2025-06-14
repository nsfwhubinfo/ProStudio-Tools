#!/usr/bin/env python3
"""
Start Frame Pack with optimized settings for RTX 4060
"""

import os
import sys

# Set environment variables for better performance
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
os.environ['CUDA_LAUNCH_BLOCKING'] = '0'  # Set to 0 for better performance
os.environ['TORCH_CUDA_ARCH_LIST'] = '8.9'  # RTX 4060 architecture

print("=" * 60)
print("Starting Frame Pack with Optimized Settings")
print("=" * 60)
print("\nRecommended settings for RTX 4060:")
print("- Video Length: 5-10 seconds (start small)")
print("- GPU Memory Preservation: 8 GB")
print("- Steps: 25 (default)")
print("- Enable TeaCache: Yes (faster)")
print("- Image size: 512x512 or 768x512")
print("\nStarting Frame Pack GUI...")
print("=" * 60)

# Change to Frame Pack directory
framepack_dir = os.path.expanduser("~/.cache/prostudio/models/FramePack")
os.chdir(framepack_dir)

# Import and run
sys.path.insert(0, framepack_dir)
import demo_gradio

# The demo_gradio script will handle the rest