# KPCL Automation System - Deployment Guide

## 🚀 Quick Deployment Options

### Option 1: Automated EC2 Deployment (Recommended)

```bash
# On your EC2 instance (Amazon Linux 2)
wget https://raw.githubusercontent.com/yourusername/kpcl-automation/main/deploy-ec2.sh
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

### Option 2: Manual EC2 Deployment

#### Step 1: Prepare EC2 Instance
```bash
# Update system
sudo yum update -y

# Install Python and Git
sudo yum install -y python3 python3-pip git

# Install Chrome browser
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo rpm --import -
sudo yum install -y google-chrome-stable
```

#### Step 2: Clone and Setup
```bash
# Clone repository
cd /home/ec2-user
git clone https://github.com/yourusername/kpcl-automation.git
cd kpcl-automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

#### Step 4: Install as Service
```bash
# Install systemd service
sudo cp kpcl-automation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable kpcl-automation
sudo systemctl start kpcl-automation
```

### Option 3: Docker Deployment

```bash
# Clone repository
git clone https://github.com/yourusername/kpcl-automation.git
cd kpcl-automation

# Copy environment file
cp .env.example .env
# Edit .env with your credentials

# Deploy with Docker Compose
docker-compose up -d
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# KPCL Credentials
KPCL_USERNAME=your_username
KPCL_PASSWORD=your_password

# Application Settings
FLASK_ENV=production
SECRET_KEY=generate_secure_key
PORT=5001
HOST=0.0.0.0

# Browser Settings
BROWSER=chrome
HEADLESS=true
TIMEOUT=60

# Scheduling
SCHEDULE_TIME=07:00:01
SCHEDULE_TIMEZONE=Asia/Kolkata
MAX_RETRIES=3
```

### EC2 Security Group Settings

| Type | Protocol | Port Range | Source |
|------|----------|------------|--------|
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |
| Custom TCP | TCP | 5001 | 0.0.0.0/0 |
| SSH | TCP | 22 | Your IP |

## 📊 Monitoring

### Check Service Status
```bash
sudo systemctl status kpcl-automation
```

### View Logs
```bash
# System logs
sudo journalctl -u kpcl-automation -f

# Application logs
tail -f /root/kpcl-automation/logs/app.log
```

### Health Check
```bash
curl http://localhost:5001/health
```

## 🔒 Security Considerations

### 1. Secure Environment Variables
- Never commit `.env` file to repository
- Use AWS Systems Manager Parameter Store for production
- Rotate credentials regularly

### 2. Network Security
- Configure Security Groups properly
- Use VPC for internal communication
- Enable CloudTrail for monitoring

### 3. Application Security
- Keep dependencies updated
- Enable HTTPS in production
- Implement proper authentication

## 🌐 Production Recommendations

### 1. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. SSL/TLS Certificate
```bash
# Install Certbot
sudo amazon-linux-extras install epel
sudo yum install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Process Management
```bash
# Use supervisor for better process management
sudo pip install supervisor

# Configure supervisor
sudo cp supervisor.conf /etc/supervisor/conf.d/kpcl-automation.conf
sudo supervisorctl reread
sudo supervisorctl update
```

## 🔄 CI/CD with GitHub Actions

### Setup Repository Secrets

In your GitHub repository, add these secrets:

| Secret Name | Description |
|-------------|-------------|
| `EC2_HOST` | Your EC2 public IP |
| `EC2_USERNAME` | SSH username (ec2-user) |
| `EC2_SSH_KEY` | Private SSH key content |

### Automatic Deployment

Push to `main` branch triggers automatic deployment to EC2.

## 🆘 Troubleshooting

### Common Issues

#### Chrome/ChromeDriver Issues
```bash
# Check Chrome version
google-chrome --version

# Check ChromeDriver version
chromedriver --version

# Reinstall ChromeDriver
sudo rm /usr/local/bin/chromedriver
# Run deployment script again
```

#### Permission Issues
```bash
# Fix permissions
sudo chown -R ec2-user:ec2-user /root/kpcl-automation
chmod +x /root/kpcl-automation/docker-entrypoint.sh
```

#### Service Won't Start
```bash
# Check service logs
sudo journalctl -u kpcl-automation --no-pager

# Check if port is in use
sudo netstat -tlnp | grep 5001

# Restart service
sudo systemctl restart kpcl-automation
```

## 📞 Support

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Ensure all dependencies are installed
4. Create an issue on GitHub with logs

## 🔄 Updates

### Manual Update
```bash
cd /root/kpcl-automation
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart kpcl-automation
```

### Automated Updates
Updates are automatically deployed via GitHub Actions when pushing to `main` branch.

---

**Note**: Always test deployments in a staging environment before production deployment.
