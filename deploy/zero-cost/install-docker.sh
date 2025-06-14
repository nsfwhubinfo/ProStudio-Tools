#!/bin/bash
# Docker Installation Script for WSL2/Linux
# =========================================

set -e

echo "🐳 Docker Installation for ProStudio"
echo "===================================="
echo

# Detect OS
if grep -q Microsoft /proc/version; then
    echo "Detected WSL environment"
    IS_WSL=true
else
    IS_WSL=false
fi

# Function to install Docker
install_docker() {
    echo "📦 Installing Docker..."
    
    # Update package index
    sudo apt-get update
    
    # Install prerequisites
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Set up the stable repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    echo "✅ Docker installed successfully!"
}

# Function to install Docker Compose standalone
install_docker_compose() {
    echo "📦 Installing Docker Compose..."
    
    # Download Docker Compose
    COMPOSE_VERSION="v2.24.0"
    sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # Make executable
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Create symbolic link
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    echo "✅ Docker Compose installed successfully!"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found"
    
    if [ "$IS_WSL" = true ]; then
        echo
        echo "For WSL2, you have two options:"
        echo
        echo "Option 1: Docker Desktop (Recommended)"
        echo "  1. Install Docker Desktop on Windows"
        echo "  2. Enable WSL2 integration in Docker Desktop settings"
        echo "  3. Restart WSL2"
        echo "  Download: https://www.docker.com/products/docker-desktop"
        echo
        echo "Option 2: Docker in WSL2 (Advanced)"
        echo "  Install Docker directly in WSL2 (requires systemd)"
        echo
        read -p "Install Docker in WSL2 directly? (y/n) " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_docker
        else
            echo "Please install Docker Desktop and enable WSL2 integration"
            exit 1
        fi
    else
        install_docker
    fi
else
    echo "✅ Docker is already installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found"
    
    # Check if docker compose (plugin) works
    if docker compose version &> /dev/null; then
        echo "✅ Docker Compose plugin is available"
        echo "Creating docker-compose alias..."
        
        # Create alias for docker-compose
        echo 'alias docker-compose="docker compose"' >> ~/.bashrc
        echo "Please run: source ~/.bashrc"
    else
        install_docker_compose
    fi
else
    echo "✅ Docker Compose is already installed"
fi

# For WSL2, check if Docker daemon is running
if [ "$IS_WSL" = true ]; then
    if ! docker ps &> /dev/null; then
        echo
        echo "⚠️  Docker daemon is not running"
        echo
        echo "If using Docker Desktop:"
        echo "  1. Start Docker Desktop on Windows"
        echo "  2. Ensure WSL2 integration is enabled"
        echo
        echo "If using Docker in WSL2:"
        echo "  sudo service docker start"
    else
        echo "✅ Docker daemon is running"
    fi
fi

echo
echo "🎉 Docker setup complete!"
echo
echo "Next steps:"
echo "1. If you installed Docker, log out and back in for group changes"
echo "2. Or run: newgrp docker"
echo "3. Then run: ./local-start.sh"