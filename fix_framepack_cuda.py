#!/usr/bin/env python3
"""
Fix Frame Pack CUDA issues
"""

import os
import torch

print("=" * 60)
print("Frame Pack CUDA Troubleshooting")
print("=" * 60)

# Check CUDA configuration
print("\n1. CUDA Configuration:")
print(f"   PyTorch version: {torch.__version__}")
print(f"   CUDA available: {torch.cuda.is_available()}")
print(f"   CUDA version (PyTorch): {torch.version.cuda}")
print(f"   GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")
print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

# Set environment variables for better compatibility
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

print("\n2. Recommended Settings for RTX 4060:")
print("   - Steps: 25 (default)")
print("   - Video Length: Start with 5 seconds, not 30")
print("   - GPU Memory Preservation: Try 8GB instead of 6GB")
print("   - Use TeaCache: Yes (faster)")
print("   - MP4 Compression: 16 (default)")

print("\n3. Quick Fixes to Try:")
print("   a) Reduce video length to 5 seconds")
print("   b) Increase GPU Memory Preservation to 8GB")
print("   c) Enable TeaCache for faster generation")
print("   d) Use a smaller/simpler image")

print("\n4. CUDA Version Mismatch:")
print("   System CUDA: 12.8")
print("   PyTorch CUDA: 11.8")
print("   This mismatch might cause issues.")

print("\n5. To reinstall PyTorch with CUDA 12.1:")
print("   pip uninstall torch torchvision torchaudio")
print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")

print("\n6. Alternative: Use CPU mode (very slow but works):")
print("   Set device='cpu' in the code")

print("=" * 60)