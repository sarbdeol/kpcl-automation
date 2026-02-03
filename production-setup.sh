#!/usr/bin/env bash

# ==================================================
# KPCL Automation – Linux Setup Script
# Tested on: Ubuntu 20.04 / 22.04
# ==================================================

set -e  # Exit on any error

echo "🚀 Setting up KPCL Automation (Linux)..."
echo "----------------------------------------"

# --------- Helpers ----------
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --------- OS Check ----------
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This setup script is intended for Linux only."
    exit 1
fi

# --------- System Dependencies ----------
echo "📦 Checking system dependencies..."

sudo apt update -y

# Python
if ! command_exists python3; then
    echo "🐍 Installing Python3..."
    sudo apt install -y python3
fi

# Pip
if ! command_exists pip3; then
    echo "📥 Installing pip3..."
    sudo apt install -y python3-pip
fi

# venv
echo "🔧 Ensuring python3-venv is installed..."
sudo apt install -y python3-venv

# Build tools (often needed for pip packages)
sudo apt install -y build-essential

# --------- Virtual Environment ----------
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

echo "🔌 Activating virtual environment..."
source venv/bin/activate

# --------- Python Dependencies ----------
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# --------- App Directories ----------
echo "📁 Creating application directories..."
mkdir -p logs screenshots backups

# --------- Permissions ----------
echo "🔐 Setting executable permissions..."
chmod +x run.sh setup.sh

# --------- Chrome Installation ----------
echo "🌐 Checking Chrome / Chromium..."

if command_exists google-chrome; then
    echo "✅ Google Chrome found"
elif command_exists chromium-browser || command_exists chromium; then
    echo "✅ Chromium found"
else
    echo "⬇️ Installing Google Chrome..."
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main"
    sudo apt update -y
    sudo apt install -y google-chrome-stable
    echo "✅ Google Chrome installed"
fi

# --------- Selenium Test ----------
echo "🧪 Verifying Python dependencies..."
python - <<EOF
import selenium
import flask
import apscheduler
print("✅ Python dependencies OK")
EOF

# --------- Finish ----------
echo ""
echo "🎉 KPCL Automation setup completed successfully!"
echo ""
echo "📌 Next steps:"
echo "   1️⃣ Edit config/form_data.json"
echo "   2️⃣ Run the app: ./run.sh"
echo "   3️⃣ Open: http://localhost:5000"
echo "   4️⃣ Enter KPCL credentials and start automation"
echo ""
echo "📖 See README.md for full documentation"
