# KPCL Automation - Quick Start Guide

## 🚀 Getting Started (5 Minutes)

### **Step 1: Setup** (2 minutes)
```bash
cd "/Users/manoj1.warpd.con/kpcl requests"
./setup.sh
```

### **Step 2: Configure** (1 minute)
Edit your vehicle and pickup details in `config/form_data.json`

### **Step 3: Run** (1 minute)
```bash
./run.sh
```

### **Step 4: Use** (1 minute)
1. Open: `http://localhost:5000`
2. Enter your KPCL username/password
3. Click "Start Automation" for 07:00:01 AM daily execution

## 📱 Dashboard Features

### **🔐 Authentication**
- Login with KPCL credentials
- OTP verification support
- Session management

### **⏰ Automation Control**
- **"Start Automation"** - Schedule daily 07:00:01 AM execution
- **"Manual Submit"** - Test immediate form submission
- **"Stop Automation"** - Cancel scheduled jobs

### **📊 Live Monitoring**
- Real-time status updates
- Activity log with timestamps
- Success/failure notifications
- Screenshot capture on errors

## ⚙️ Configuration

### **Form Data** (`config/form_data.json`)
```json
{
  "ash_utilization": "Ash_based_Products",
  "pickup_time": "10.00AM - 11.00AM",
  "vehicle_type": "Bluker 16 Wheeler",
  "quantity_limit": "36",
  "vehicle_classification": "Hired",
  "authorised_person": "POTHALINGAPPA C",
  "vehicle_no": "KA28AB2222",
  "dl_no": "7634",
  "driver_mob_no": "9768453423"
}
```

### **App Settings** (`config/settings.json`)
```json
{
  "schedule_time": "07:00:01",
  "retry_interval": 10,
  "max_retries": 3,
  "headless": true,
  "browser": "chrome"
}
```

## 🔧 Troubleshooting

### **❌ Setup Issues**
```bash
# If setup fails, try manual installation:
python3 -m venv venv
source venv/bin/activate
pip install selenium flask flask-socketio apscheduler webdriver-manager
```

### **❌ Browser Issues**
- Install Chrome: `https://www.google.com/chrome/`
- For debugging, set `"headless": false` in settings.json

### **❌ Login Problems**
- Verify KPCL website is accessible
- Check username/password spelling
- Ensure mobile number is correct for OTP

### **❌ Form Submission Fails**
- Check internet connection
- Verify form data is correct
- Review logs in `logs/` folder
- Check screenshots in `screenshots/` folder

## 📋 Daily Usage Workflow

### **Evening Setup** (Day Before)
1. Run the application: `./run.sh`
2. Test your credentials with "Manual Submit"
3. Verify form data is correct
4. Click "Start Automation" for next day

### **Morning Execution** (07:00:01 AM)
- Application automatically logs in
- Fills and submits the form
- Retries 3 times if needed (10-second intervals)
- Sends notifications on completion

### **Result Verification**
- Check dashboard for success status
- Review logs for detailed execution info
- Check screenshots if there were any issues

## 📁 Important Directories

```
📂 logs/           # Execution logs with timestamps
📂 screenshots/    # Debug screenshots on errors  
📂 config/         # Your settings and form data
📂 automation/     # Core automation modules
📂 templates/      # Web interface files
```

## 🛡️ Security Notes

- **All data stays local** - no cloud storage
- **Credentials not saved** - enter each session
- **HTTPS not required** - runs on localhost only
- **No external dependencies** - works offline after setup

## 📞 Quick Help

### **Can't access dashboard?**
- Ensure application is running: `./run.sh`
- Try: `http://localhost:5000`
- Check terminal for error messages

### **Automation not working?**
- Verify time schedule is correct
- Check KPCL website accessibility
- Review logs for error details
- Try "Manual Submit" first to test

### **Need to change settings?**
- Stop application (Ctrl+C)
- Edit `config/settings.json` or `config/form_data.json`
- Restart application: `./run.sh`

---

**🎯 Your KPCL form will be automatically submitted at 07:00:01 AM daily with intelligent retry mechanisms!**

For detailed information, see `README.md` and `TESTING.md`.
