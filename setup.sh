#!/bin/bash

# KPCL Automation Setup Script
# This script will set up the KPCL automation environment

echo "🚀 Setting up KPCL Automation Application..."

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python packages
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating application directories..."
mkdir -p logs
mkdir -p screenshots
mkdir -p backups

# Set permissions
echo "🔐 Setting file permissions..."
chmod +x run.sh
chmod +x setup.sh

# Check if Chrome is installed
echo "🌐 Checking browser installation..."
if command -v google-chrome >/dev/null 2>&1; then
    echo "✅ Chrome browser found"
elif command -v chromium-browser >/dev/null 2>&1; then
    echo "✅ Chromium browser found"
else
    echo "⚠️  Chrome/Chromium not found. Please install Chrome browser."
    echo "   Download from: https://www.google.com/chrome/"
fi

# Test Python installation
echo "🧪 Testing Python setup..."
python -c "import selenium, flask, apscheduler; print('✅ All dependencies installed successfully')" 2>/dev/null || {
    echo "❌ Dependency installation failed. Please check errors above."
    exit 1
}

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Configure your form data in config/form_data.json"
echo "   2. Run the application: ./run.sh"
echo "   3. Open http://localhost:5000 in your browser"
echo "   4. Enter your KPCL credentials and start automation"
echo ""
echo "📖 For detailed instructions, see README.md"
