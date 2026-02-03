#!/bin/bash

# KPCL Automation System - EC2 Deployment Script
# Run this script on your EC2 instance to deploy the application

set -e

echo "🚀 Starting KPCL Automation System deployment on EC2..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install required packages
echo "🔧 Installing required packages..."
sudo yum install -y python3 python3-pip git wget unzip

# Install Chrome
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo yum install -y google-chrome-stable

# Install ChromeDriver
echo "🚗 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Clone repository
echo "📥 Cloning repository..."
cd /home/ec2-user
git clone https://github.com/themanojgowda/kpcl-automation.git
cd kpcl-automation

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
echo "⚙️ Setting up environment variables..."
cp .env.example .env
echo "Please edit .env file with your KPCL credentials:"
echo "nano .env"

# Create directories
echo "📁 Creating necessary directories..."
mkdir -p screenshots logs

# Set permissions
echo "🔒 Setting permissions..."
chmod +x docker-entrypoint.sh
chmod +x deploy-ec2.sh
sudo chown -R ec2-user:ec2-user /root/kpcl-automation

# Install systemd service
echo "🔧 Installing systemd service..."
sudo cp kpcl-automation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kpcl-automation

# Configure firewall
echo "🔥 Configuring firewall..."
sudo yum install -y firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your KPCL credentials: nano .env"
echo "2. Start the service: sudo systemctl start kpcl-automation"
echo "3. Check status: sudo systemctl status kpcl-automation"
echo "4. View logs: sudo journalctl -u kpcl-automation -f"
echo "5. Access application: http://YOUR_EC2_PUBLIC_IP:5001"
echo ""
echo "🔧 Optional Docker deployment:"
echo "1. Install Docker: sudo yum install -y docker && sudo service docker start"
echo "2. Run: sudo docker-compose up -d"
echo ""
echo "🌐 For production, consider:"
echo "- Setting up SSL/TLS certificates"
echo "- Configuring a reverse proxy (nginx)"
echo "- Setting up log rotation"
echo "- Implementing monitoring and alerting"
