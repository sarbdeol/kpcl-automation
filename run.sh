#!/bin/bash

# KPCL Automation Run Script
# This script starts the automation application

echo "🚀 Starting KPCL Automation Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Please ensure you're in the correct directory."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the application
echo "🌐 Starting Flask application on http://localhost:5001"
echo "📱 Press Ctrl+C to stop the application"
echo ""

export FLASK_ENV=development
export FLASK_DEBUG=1

python app.py
