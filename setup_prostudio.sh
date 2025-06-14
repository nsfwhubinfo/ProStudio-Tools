#!/bin/bash
# ProStudio Setup Script

echo "==================================="
echo "ProStudio Environment Setup"
echo "==================================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Virtual environment already exists."
    echo "To activate it, run: source venv/bin/activate"
    exit 0
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install basic requirements first
echo "Installing basic requirements..."
pip install numpy pillow tqdm

# Check CUDA availability
echo "Checking CUDA..."
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU detected"
    # Install PyTorch with CUDA support
    echo "Installing PyTorch with CUDA support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    echo "No NVIDIA GPU detected, installing CPU-only PyTorch..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install remaining packages
echo "Installing remaining packages..."
pip install opencv-python imageio imageio-ffmpeg
pip install scipy huggingface-hub
pip install librosa soundfile matplotlib

# Test installation
echo ""
echo "Testing installation..."
python3 -c "
import torch
import cv2
import PIL
print('✓ PyTorch:', torch.__version__)
print('✓ CUDA available:', torch.cuda.is_available())
if torch.cuda.is_available():
    print('✓ CUDA device:', torch.cuda.get_device_name(0))
print('✓ OpenCV installed')
print('✓ PIL/Pillow installed')
"

echo ""
echo "==================================="
echo "Setup complete!"
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  python test_framepack.py"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo "==================================="