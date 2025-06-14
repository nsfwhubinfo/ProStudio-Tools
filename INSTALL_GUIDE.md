# ProStudio Installation Guide

## Python Package Installation (PEP 668 Compliant)

Due to PEP 668, modern Linux distributions prevent system-wide pip installations. Here are your options:

### Option 1: Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv prostudio_env

# Activate it
source prostudio_env/bin/activate

# Install packages
pip install -r requirements_video.txt
```

### Option 2: User Installation
```bash
# Install for current user only
pip3 install --user -r requirements_video.txt

# You may need to add to PATH:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Option 3: pipx for CLI tools (if needed)
```bash
# Install pipx first
sudo apt install pipx
pipx ensurepath

# Then install tools
pipx install <package-name>
```

### Option 4: System Packages (Limited)
```bash
# Some packages available via apt
sudo apt update
sudo apt install python3-numpy python3-opencv python3-pil

# But most ML packages need pip
```

## Quick Start Commands

```bash
# Navigate to prostudio
cd ~/prostudio

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PyTorch (choose based on your CUDA version)
# For CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other requirements
pip install opencv-python Pillow imageio imageio-ffmpeg
pip install numpy scipy tqdm huggingface-hub
pip install librosa soundfile

# Test installation
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
```

## Troubleshooting

### 1. CUDA Not Available
```bash
# Check NVIDIA driver
nvidia-smi

# Install CUDA toolkit if needed
sudo apt install nvidia-cuda-toolkit
```

### 2. FFmpeg Missing
```bash
# Required for video processing
sudo apt install ffmpeg
```

### 3. Memory Issues
- Close other applications
- Use PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

### 4. Import Errors
- Make sure virtual environment is activated
- Check package versions compatibility

## Running ProStudio

```bash
# Always activate environment first
source venv/bin/activate

# Run tests
python test_framepack.py

# Start API server
python api_server.py
```

## Deactivate Environment
```bash
deactivate
```