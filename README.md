# KPCL Automation System

An advanced web automation system for KPCL (Karnataka Power Corporation Limited) gatepass form submission with robust alert handling, session management, and scheduling capabilities.

## 🚀 Features

- **Automated KPCL Login**: Handles OTP-based authentication with robust alert management
- **Smart Form Submission**: Automated gatepass form filling and submission
- **Robust Alert Handling**: Comprehensive JavaScript alert management
- **Session Management**: Intelligent session validation and recovery
- **Scheduling System**: Precise 07:00:01 AM execution with retry logic
- **Real-time Dashboard**: Web interface with WebSocket updates
- **Error Recovery**: Automatic screenshots and detailed logging

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, Flask, Flask-SocketIO
- **Automation**: Selenium WebDriver with Chrome/ChromeDriver
- **Scheduling**: APScheduler for precise timing
- **Frontend**: HTML5, CSS3, JavaScript with WebSocket
- **Deployment**: Docker, AWS EC2

### 🎯 **Precise Timing Control**
- **07:00:01 AM** automatic execution
- **10-second intervals** for 3 retry attempts
- **Background scheduling** with APScheduler

### 🔐 **Smart Authentication**
- **Local credential input** (Username/Password/OTP)
- **Session management** with automatic refresh
- **CSRF token** handling

### 🤖 **Advanced Automation**
- **Selenium WebDriver** automation
- **Dynamic data extraction** from website
- **Static form pre-filling**
- **Multi-browser support** (Chrome/Firefox)

### 📊 **Real-time Monitoring**
- **Live dashboard** with WebSocket updates
- **Activity logging** with timestamps
- **Status indicators** and notifications
- **Screenshot capture** for debugging

### ⚙️ **Configuration Management**
- **Web-based settings** interface
- **Export/Import** configuration
- **Backup and restore** functionality

## Quick Start

### 1. **Install Dependencies**

```bash
# Install Python packages
pip install -r requirements.txt

# Install Chrome WebDriver (automatic via webdriver-manager)
# Or manually download from: https://chromedriver.chromium.org/
```

### 2. **Configure Settings**

Edit `config/form_data.json` with your static data:
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

### 3. **Run Application**

```bash
python app.py
```

### 4. **Access Dashboard**

Open your browser and go to: `http://localhost:5000`

## Usage Workflow

### **Step 1: Authentication**
1. Enter your KPCL username and password
2. Click "Login" to generate OTP
3. Enter the OTP received on your mobile
4. Click "Verify OTP" to complete login

### **Step 2: Schedule Automation**
1. Click "Start Automation" to schedule daily execution
2. System will automatically run at **07:00:01 AM**
3. Monitor status in real-time via dashboard

### **Step 3: Monitor Execution**
- **Live status updates** via WebSocket
- **Activity log** with detailed timestamps
- **Success/failure notifications**
- **Automatic retry** on failures (3 attempts, 10-second intervals)

## Application Architecture

```
kpcl-automation/
├── app.py                     # Main Flask application
├── automation/                # Core automation modules
│   ├── selenium_handler.py    # WebDriver management
│   ├── session_manager.py     # Login/session handling  
│   ├── form_filler.py         # Form automation logic
│   └── scheduler.py           # Timing control
├── templates/                 # HTML templates
│   ├── index.html            # Main dashboard
│   └── config.html           # Settings page
├── static/                   # CSS/JS assets
│   ├── css/style.css         # Custom styles
│   └── js/app.js             # Dashboard JavaScript
├── config/                   # Configuration files
│   ├── settings.json         # App configuration
│   └── form_data.json        # Static form values
├── logs/                     # Application logs
├── screenshots/              # Debug screenshots
└── requirements.txt          # Python dependencies
```

## Configuration Options

### **Application Settings** (`config/settings.json`)
```json
{
  "schedule_time": "07:00:01",    // Daily execution time
  "retry_interval": 10,           // Seconds between retries
  "max_retries": 3,              // Maximum retry attempts
  "headless": true,              // Run browser in background
  "browser": "chrome"            // Browser choice (chrome/firefox)
}
```

### **Form Data** (`config/form_data.json`)
Pre-configured static values that will be automatically filled:
- Purpose of Fly Ash Utilization
- Pickup Timing Slot
- Vehicle Type & Classification  
- Authorized Person Details
- Vehicle & Driver Information

## Advanced Features

### **🔄 Retry Mechanism**
- **Automatic retries** on failure
- **Intelligent session refresh**
- **CSRF token regeneration**
- **Screenshot capture** on errors

### **📡 Real-time Updates**
- **WebSocket communication** for live updates
- **Status broadcasting** to all connected clients
- **Progress tracking** during execution
- **Error reporting** with details

### **🛡️ Security Features**
- **Local storage only** - no cloud dependencies
- **Session validation** before each attempt
- **CSRF protection** handling
- **Secure credential management**

### **🔧 Debugging Tools**
- **Detailed logging** with timestamps
- **Screenshot capture** at key moments
- **Error stack traces** for troubleshooting
- **Browser console** access in non-headless mode

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/login` | POST | Authenticate user credentials |
| `/api/verify_otp` | POST | Verify OTP for login |
| `/api/start_automation` | POST | Start scheduled automation |
| `/api/stop_automation` | POST | Stop automation scheduler |
| `/api/manual_submit` | POST | Trigger immediate form submission |
| `/api/save_config` | POST | Save configuration settings |
| `/api/status` | GET | Get current application status |

## Troubleshooting

### **Common Issues**

**❌ Login Fails**
- Verify username/password are correct
- Ensure KPCL website is accessible
- Check for CAPTCHA requirements

**❌ OTP Not Received** 
- Verify mobile number in KPCL account
- Check network connectivity
- Try manual login to test

**❌ Form Submission Fails**
- Check session validity
- Verify form data configuration
- Review screenshots in `/screenshots` folder

**❌ Browser Issues**
- Install/update Chrome browser
- Check ChromeDriver compatibility
- Try Firefox as alternative browser

### **Debug Mode**
Set `headless: false` in configuration to see browser actions in real-time.

### **Log Analysis**
Check `logs/automation.log` for detailed execution logs with timestamps.

## System Requirements

- **Python 3.8+**
- **Chrome/Firefox** browser
- **Network access** to kpcl-ams.com
- **5GB+ RAM** recommended
- **macOS/Windows/Linux** supported

## License

This application is for educational and automation purposes. Please ensure compliance with KPCL website terms of service.

## Support

For issues and feature requests, check the application logs and screenshots for debugging information.

---

**⚡ Ready to automate your KPCL form submissions with precision timing and intelligent retry mechanisms!**
