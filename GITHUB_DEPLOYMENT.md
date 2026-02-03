# 🚀 GitHub Repository & EC2 Deployment Instructions

## Step 1: Create GitHub Repository

### Option A: Using GitHub CLI (Recommended)
```bash
# Install GitHub CLI if not already installed
brew install gh  # macOS
# or
sudo apt install gh  # Ubuntu
# or 
winget install GitHub.cli  # Windows

# Authenticate with GitHub
gh auth login

# Create repository and push
cd "/Users/manoj1.warpd.con/kpcl requests"
gh repo create kpcl-automation --public --description "Advanced KPCL automation system with robust alert handling and EC2 deployment"
git remote add origin https://github.com/YOUR_USERNAME/kpcl-automation.git
git push -u origin main
```

### Option B: Manual GitHub Creation
1. Go to https://github.com/new
2. Repository name: `kpcl-automation`
3. Description: `Advanced KPCL automation system with robust alert handling and EC2 deployment`
4. Make it Public
5. Don't initialize with README (we already have one)
6. Click "Create repository"

Then run:
```bash
cd "/Users/manoj1.warpd.con/kpcl requests"
git remote add origin https://github.com/themanojgowda/kpcl-automation.git
git push -u origin main
```

## Step 2: Deploy to EC2

### Launch EC2 Instance
1. **AWS Console** → EC2 → Launch Instance
2. **AMI**: Amazon Linux 2 AMI (HVM)
3. **Instance Type**: t3.small (minimum) or t3.medium (recommended)
4. **Storage**: 20 GB GP3
5. **Security Group**: Allow ports 22, 80, 443, 5001
6. **Key Pair**: Create/use existing key pair

### Deploy Application
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP

# Run automated deployment
wget https://raw.githubusercontent.com/themanojgowda/kpcl-automation/main/deploy-ec2.sh
chmod +x deploy-ec2.sh
./deploy-ec2.sh

# Configure credentials
nano .env
# Add your KPCL username and password

# Start the service
sudo systemctl start kpcl-automation
sudo systemctl status kpcl-automation
```

## Step 3: Access Your Application

🌐 **Web Interface**: `http://YOUR_EC2_PUBLIC_IP:5001`

### Setup Your Automation
1. Enter KPCL credentials
2. Configure form data (vehicle details, etc.)
3. Set schedule (default: 07:00:01 AM)
4. Monitor real-time status

## Step 4: Production Optimizations (Optional)

### 1. Domain & SSL
```bash
# Point your domain to EC2 IP
# Install SSL certificate
sudo certbot --nginx -d yourdomain.com
```

### 2. Monitoring
```bash
# View real-time logs
sudo journalctl -u kpcl-automation -f

# Check system resources
htop
```

### 3. Backup Configuration
```bash
# Backup your .env file
cp .env .env.backup
```

## Step 5: GitHub Actions Setup (Optional)

Add these secrets to your GitHub repository:
- `EC2_HOST`: Your EC2 public IP
- `EC2_USERNAME`: `ec2-user`
- `EC2_SSH_KEY`: Content of your private key file

Now every push to `main` branch will automatically deploy to EC2!

## 🎉 You're Live!

Your KPCL automation system is now:
- ✅ **Deployed on EC2** with automatic startup
- ✅ **Available 24/7** with systemd service
- ✅ **Robust and reliable** with comprehensive error handling
- ✅ **Monitored** with detailed logging
- ✅ **Scalable** with Docker support
- ✅ **Automated** with GitHub Actions CI/CD

### Quick Commands Reference

```bash
# Check service status
sudo systemctl status kpcl-automation

# View logs
sudo journalctl -u kpcl-automation -f

# Restart service
sudo systemctl restart kpcl-automation

# Update application
cd /root/kpcl-automation
git pull origin main
sudo systemctl restart kpcl-automation
```

## 🆘 Need Help?

1. **Check Logs**: `sudo journalctl -u kpcl-automation --no-pager`
2. **Verify Config**: `cat /root/kpcl-automation/.env`
3. **Test Manually**: Access `http://YOUR_EC2_IP:5001`
4. **GitHub Issues**: Create issue with logs

---

**🎯 Your automation is now production-ready and will reliably handle the 07:00:01 AM KPCL form submissions!**
