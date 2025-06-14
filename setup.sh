#!/bin/bash
# ProStudio Setup Script

echo "🚀 ProStudio SDK Setup"
echo "====================="
echo

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✓ Virtual environment created"
echo
echo "📥 Installing dependencies..."

# Activate and install
source venv/bin/activate

# Install basic requirements
pip install --upgrade pip
pip install numpy scipy scikit-learn
pip install flask flask-cors requests psutil

echo
echo "🔧 Optional components:"
echo "1. Install Cython extensions (5x performance boost)"
echo "2. Install Redis (for caching)"
echo "3. Install Ray (for distributed processing)"
echo "4. Install all optional components"
echo "5. Skip optional components"
echo

read -p "Select option (1-5): " option

case $option in
    1)
        echo "Installing Cython..."
        pip install cython
        cd core/acceleration
        python setup.py build_ext --inplace
        cd ../..
        ;;
    2)
        echo "Installing Redis client..."
        pip install redis
        echo "Note: You'll need to run Redis server separately"
        echo "  Docker: docker run -d -p 6379:6379 redis:alpine"
        ;;
    3)
        echo "Installing Ray..."
        pip install ray
        ;;
    4)
        echo "Installing all optional components..."
        pip install cython redis ray
        cd core/acceleration
        python setup.py build_ext --inplace
        cd ../..
        ;;
    5)
        echo "Skipping optional components"
        ;;
esac

echo
echo "✅ Setup complete!"
echo
echo "🎮 Quick Start Commands:"
echo "========================"
echo
echo "1. Activate environment:"
echo "   source venv/bin/activate"
echo
echo "2. Run quick demo:"
echo "   python quick_demo.py"
echo
echo "3. Start API server:"
echo "   python api_server.py"
echo
echo "4. Test API (in another terminal):"
echo "   python test_api_client.py"
echo
echo "5. Run performance benchmark:"
echo "   python run_benchmark_demo.py"
echo
echo "Happy creating! 🚀"