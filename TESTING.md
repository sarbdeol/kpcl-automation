# KPCL Automation Testing Guide

This document provides comprehensive testing procedures for the KPCL automation application.

## Pre-Testing Setup

### 1. **Environment Validation**
```bash
# Verify Python installation
python --version  # Should be 3.8+

# Check virtual environment
source venv/bin/activate
pip list | grep -E "(selenium|flask|apscheduler)"

# Test browser access
google-chrome --version  # Or chromium-browser --version
```

### 2. **Configuration Check**
```bash
# Verify config files exist
ls config/settings.json config/form_data.json

# Check permissions
ls -la *.sh  # setup.sh and run.sh should be executable
```

## Testing Procedures

### **Phase 1: Component Testing**

#### **1.1 Logger Testing**
```python
# Test in Python console
from automation.logger import setup_logger, log_automation_step
logger = setup_logger()
log_automation_step("TEST", "SUCCESS", "Logger test completed")
```

#### **1.2 Selenium Handler Testing**
```python
# Test WebDriver initialization
from automation.selenium_handler import SeleniumHandler
handler = SeleniumHandler()
driver = handler.get_driver()
print(f"Driver initialized: {driver.title}")
handler.cleanup()
```

#### **1.3 Session Manager Testing**
```python
# Test website connectivity
from automation.session_manager import SessionManager
session_mgr = SessionManager()
# Note: Requires valid credentials for full test
```

### **Phase 2: Integration Testing**

#### **2.1 Flask Application Testing**
```bash
# Start application in test mode
export FLASK_ENV=testing
python app.py

# Test endpoints (in another terminal)
curl http://localhost:5000/api/status
curl -X POST http://localhost:5000/api/test_connection
```

#### **2.2 WebSocket Testing**
```javascript
// Test in browser console
const socket = io();
socket.on('connect', () => console.log('Connected'));
socket.on('status_update', (data) => console.log('Status:', data));
```

### **Phase 3: End-to-End Testing**

#### **3.1 Manual Form Submission**
1. Start application: `./run.sh`
2. Open `http://localhost:5000`
3. Enter test credentials (use test account)
4. Click "Manual Submit" to test immediate execution
5. Monitor logs in `logs/` directory

#### **3.2 Scheduled Automation**
1. Set test schedule time (2-3 minutes in future)
2. Update `config/settings.json`:
   ```json
   {
     "schedule_time": "14:35:00",  // Current time + 2 minutes
     "retry_interval": 10,
     "max_retries": 3
   }
   ```
3. Click "Start Automation"
4. Wait for scheduled execution
5. Verify logs and screenshots

### **Phase 4: Error Testing**

#### **4.1 Network Failure Simulation**
```bash
# Block KPCL website (requires admin/sudo)
echo "127.0.0.1 kpcl-ams.com" >> /etc/hosts

# Test application behavior
# Remember to remove the line after testing
```

#### **4.2 Invalid Credentials Testing**
1. Use incorrect username/password
2. Verify error handling and logging
3. Check retry mechanism activation

#### **4.3 Session Timeout Testing**
1. Login successfully
2. Wait 30+ minutes (session timeout)
3. Trigger form submission
4. Verify session refresh mechanism

## Test Cases Checklist

### **✅ Basic Functionality**
- [ ] Application starts without errors
- [ ] Web interface loads correctly
- [ ] Configuration files are read properly
- [ ] Logging system captures events
- [ ] Screenshots are saved on errors

### **✅ Authentication Flow**
- [ ] Login form accepts credentials
- [ ] OTP generation triggers correctly
- [ ] OTP verification works
- [ ] Session validation functions
- [ ] Invalid credentials are handled gracefully

### **✅ Form Automation**
- [ ] KPCL website loads in browser
- [ ] Form fields are populated correctly
- [ ] Static data is applied from config
- [ ] Dynamic data is extracted from website
- [ ] Form submission completes successfully

### **✅ Scheduling System**
- [ ] Jobs are scheduled at correct time
- [ ] Retry mechanism activates on failure
- [ ] Multiple retries work with intervals
- [ ] Scheduler can be stopped/started
- [ ] Background execution functions properly

### **✅ Real-time Communication**
- [ ] WebSocket connection establishes
- [ ] Status updates are broadcasted
- [ ] Multiple clients receive updates
- [ ] Connection recovery works
- [ ] Error notifications are sent

### **✅ Error Handling**
- [ ] Network errors are caught and logged
- [ ] Browser crashes are handled
- [ ] Session timeouts trigger re-login
- [ ] Form submission failures retry
- [ ] Configuration errors are reported

### **✅ Performance**
- [ ] Application starts within 10 seconds
- [ ] Form submission completes within 60 seconds
- [ ] Memory usage remains stable
- [ ] Browser resources are cleaned up
- [ ] Log files don't grow excessively

## Test Data

### **Valid Test Credentials**
```json
{
  "username": "test_user",
  "password": "test_password",
  "note": "Use actual test account for KPCL"
}
```

### **Form Test Data**
```json
{
  "ash_utilization": "Test_Products",
  "pickup_time": "10.00AM - 11.00AM",
  "vehicle_type": "Test Vehicle",
  "quantity_limit": "10",
  "expected_elements": [
    "ash_utilization_dropdown",
    "pickup_time_dropdown",
    "vehicle_type_input"
  ]
}
```

## Expected Results

### **Successful Execution Logs**
```
2024-01-20 07:00:01 - INFO - SCHEDULER: Daily automation job started
2024-01-20 07:00:02 - INFO - SESSION: Login initiated for user: test_user
2024-01-20 07:00:05 - INFO - SESSION: OTP verification successful
2024-01-20 07:00:08 - INFO - FORM: Form populated with static data
2024-01-20 07:00:12 - INFO - FORM: Dynamic data extracted successfully
2024-01-20 07:00:15 - INFO - FORM: Form submission completed successfully
2024-01-20 07:00:16 - INFO - AUTOMATION: Daily task completed successfully
```

### **Error Scenario Logs**
```
2024-01-20 07:00:01 - INFO - SCHEDULER: Daily automation job started
2024-01-20 07:00:05 - ERROR - SESSION: Login failed - Invalid credentials
2024-01-20 07:00:15 - INFO - SCHEDULER: Retry attempt 1/3 in 10 seconds
2024-01-20 07:00:25 - ERROR - SESSION: Login failed - Invalid credentials
2024-01-20 07:00:35 - INFO - SCHEDULER: Retry attempt 2/3 in 10 seconds
```

## Troubleshooting Test Issues

### **Common Test Problems**

**❌ Browser Won't Start**
- Check Chrome/Chromium installation
- Verify ChromeDriver compatibility
- Try headless=false for debugging
- Check system resources (RAM/CPU)

**❌ Website Access Fails**
- Verify internet connection
- Check KPCL website availability
- Test manual browser access
- Review firewall/proxy settings

**❌ Form Elements Not Found**
- KPCL website structure may have changed
- Update element selectors in code
- Check for CAPTCHAs or new security measures
- Verify page load timing

**❌ Scheduling Doesn't Work**
- Check system timezone settings
- Verify APScheduler configuration
- Test with near-future time first
- Check application permissions

### **Debug Mode Testing**
```python
# Enable debug mode in config/settings.json
{
  "headless": false,
  "debug_mode": true,
  "verbose_logging": true
}
```

### **Test Log Analysis**
```bash
# View real-time logs
tail -f logs/automation_$(date +%Y%m%d).log

# Search for specific errors
grep -i "error\|failed" logs/automation_*.log

# Check performance metrics
grep "PERFORMANCE" logs/automation_*.log
```

## Test Environment Cleanup

### **After Testing**
```bash
# Stop application
Ctrl+C

# Deactivate virtual environment
deactivate

# Clean up test files
rm -rf screenshots/test_*
rm -rf logs/test_*

# Reset configuration to production values
```

### **Reset Test Data**
```bash
# Restore original configuration
cp config/settings.json.backup config/settings.json
cp config/form_data.json.backup config/form_data.json
```

---

**⚡ Following this testing guide ensures the KPCL automation application works reliably in production!**
