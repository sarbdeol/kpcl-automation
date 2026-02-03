// KPCL Automation Dashboard JavaScript

class KPCLApp {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.currentStatus = 'idle';
        this.logEntries = [];
        this.maxLogEntries = 100;
        
        this.init();
    }
    
    init() {
        this.initializeSocket();
        this.bindEvents();
        this.updateUI();
        this.addLogEntry('System initialized', 'info');
    }
    
    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.updateConnectionStatus();
            this.addLogEntry('Connected to server', 'success');
        });
        
        this.socket.on('disconnect', () => {
            this.isConnected = false;
            this.updateConnectionStatus();
            this.addLogEntry('Disconnected from server', 'error');
        });
        
        this.socket.on('status_update', (data) => {
            this.handleStatusUpdate(data);
        });
        
        this.socket.on('form_status', (data) => {
            this.handleFormStatus(data);
        });
        
        this.socket.on('automation_started', (data) => {
            this.addLogEntry(`Automation started (${data.type})`, 'info');
        });
        
        this.socket.on('automation_attempt', (data) => {
            this.addLogEntry(`Attempt ${data.attempt}/${data.max_attempts}`, 'info');
        });
        
        this.socket.on('automation_success', (data) => {
            this.addLogEntry(`✓ Success: ${data.message}`, 'success');
            this.showNotification('Form submitted successfully!', 'success');
        });
        
        this.socket.on('automation_attempt_failed', (data) => {
            this.addLogEntry(`⚠ Attempt ${data.attempt} failed: ${data.message}`, 'warning');
        });
        
        this.socket.on('automation_error', (data) => {
            this.addLogEntry(`✗ Error: ${data.error}`, 'error');
        });
        
        this.socket.on('automation_final_failure', (data) => {
            this.addLogEntry(`✗ Final failure after ${data.total_attempts} attempts`, 'error');
            this.showNotification('Automation failed after all retries', 'error');
        });
        
        this.socket.on('automation_completed', (data) => {
            const status = data.success ? 'success' : 'error';
            const message = data.success ? 'Automation completed successfully' : 'Automation completed with errors';
            this.addLogEntry(message, status);
            this.currentStatus = 'idle';
            this.updateUI();
        });
        
        this.socket.on('scheduler_status', (data) => {
            this.handleSchedulerStatus(data);
        });
        
        this.socket.on('submission_complete', (data) => {
            const status = data.success ? 'success' : 'error';
            this.showNotification(data.message, status);
        });
    }
    
    bindEvents() {
        // Login form
        document.getElementById('login-btn').addEventListener('click', () => {
            this.handleLogin();
        });
        
        // OTP verification
        document.getElementById('verify-otp-btn').addEventListener('click', () => {
            this.handleOTPVerification();
        });
        
        // Control buttons
        document.getElementById('start-automation-btn').addEventListener('click', () => {
            this.startAutomation();
        });
        
        document.getElementById('stop-automation-btn').addEventListener('click', () => {
            this.stopAutomation();
        });
        
        document.getElementById('manual-submit-btn').addEventListener('click', () => {
            this.manualSubmit();
        });
        
        // Quick settings
        document.getElementById('save-quick-settings-btn').addEventListener('click', () => {
            this.saveQuickSettings();
        });
        
        // Clear log
        document.getElementById('clear-log-btn').addEventListener('click', () => {
            this.clearLog();
        });
        
        // Enter key handlers
        document.getElementById('username').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleLogin();
        });
        
        document.getElementById('password').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleLogin();
        });
        
        document.getElementById('otp').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleOTPVerification();
        });
    }
    
    async handleLogin() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        
        if (!username || !password) {
            this.showNotification('Please enter username and password', 'warning');
            return;
        }
        
        const loginBtn = document.getElementById('login-btn');
        const originalText = loginBtn.innerHTML;
        
        try {
            loginBtn.disabled = true;
            loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Logging in...';
            
            this.addLogEntry('Attempting login...', 'info');
            
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                if (data.otp_required) {
                    this.addLogEntry('OTP required for login', 'info');
                    this.showOTPSection();
                } else {
                    this.addLogEntry('Login successful', 'success');
                    this.showControlSection();
                }
                this.showNotification(data.message, 'success');
            } else {
                this.addLogEntry(`Login failed: ${data.message}`, 'error');
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.addLogEntry(`Login error: ${error.message}`, 'error');
            this.showNotification('Login failed', 'error');
        } finally {
            loginBtn.disabled = false;
            loginBtn.innerHTML = originalText;
        }
    }
    
    async handleOTPVerification() {
        const otp = document.getElementById('otp').value.trim();
        
        if (!otp) {
            this.showNotification('Please enter OTP', 'warning');
            return;
        }
        
        const verifyBtn = document.getElementById('verify-otp-btn');
        const originalText = verifyBtn.innerHTML;
        
        try {
            verifyBtn.disabled = true;
            verifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Verifying...';
            
            this.addLogEntry('Verifying OTP...', 'info');
            
            const response = await fetch('/api/verify_otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ otp })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addLogEntry('OTP verified successfully', 'success');
                this.showControlSection();
                this.showNotification(data.message, 'success');
            } else {
                this.addLogEntry(`OTP verification failed: ${data.message}`, 'error');
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.addLogEntry(`OTP verification error: ${error.message}`, 'error');
            this.showNotification('OTP verification failed', 'error');
        } finally {
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = originalText;
        }
    }
    
    async startAutomation() {
        const startBtn = document.getElementById('start-automation-btn');
        const stopBtn = document.getElementById('stop-automation-btn');
        
        try {
            startBtn.disabled = true;
            startBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Starting...';
            
            this.addLogEntry('Starting automation scheduler...', 'info');
            
            const response = await fetch('/api/start_automation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addLogEntry('Automation scheduler started', 'success');
                this.showNotification(`Automation scheduled. Next run: ${data.next_run}`, 'success');
                startBtn.style.display = 'none';
                stopBtn.style.display = 'block';
                stopBtn.disabled = false;
                this.currentStatus = 'scheduled';
                this.updateUI();
            } else {
                this.addLogEntry(`Failed to start automation: ${data.message}`, 'error');
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.addLogEntry(`Start automation error: ${error.message}`, 'error');
            this.showNotification('Failed to start automation', 'error');
        } finally {
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Automation';
        }
    }
    
    async stopAutomation() {
        const startBtn = document.getElementById('start-automation-btn');
        const stopBtn = document.getElementById('stop-automation-btn');
        
        try {
            stopBtn.disabled = true;
            stopBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Stopping...';
            
            this.addLogEntry('Stopping automation scheduler...', 'info');
            
            const response = await fetch('/api/stop_automation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addLogEntry('Automation scheduler stopped', 'success');
                this.showNotification('Automation stopped', 'info');
                stopBtn.style.display = 'none';
                startBtn.style.display = 'block';
                this.currentStatus = 'idle';
                this.updateUI();
            } else {
                this.addLogEntry(`Failed to stop automation: ${data.message}`, 'error');
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.addLogEntry(`Stop automation error: ${error.message}`, 'error');
            this.showNotification('Failed to stop automation', 'error');
        } finally {
            stopBtn.disabled = false;
            stopBtn.innerHTML = '<i class="fas fa-stop me-2"></i>Stop Automation';
        }
    }
    
    async manualSubmit() {
        const submitBtn = document.getElementById('manual-submit-btn');
        const originalText = submitBtn.innerHTML;
        
        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
            
            this.addLogEntry('Starting manual form submission...', 'info');
            this.currentStatus = 'running';
            this.updateUI();
            
            const response = await fetch('/api/manual_submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addLogEntry('Manual submission started', 'info');
                this.showNotification('Manual submission started', 'info');
            } else {
                this.addLogEntry(`Failed to start manual submission: ${data.message}`, 'error');
                this.showNotification(data.message, 'error');
                this.currentStatus = 'idle';
                this.updateUI();
            }
        } catch (error) {
            this.addLogEntry(`Manual submit error: ${error.message}`, 'error');
            this.showNotification('Failed to start manual submission', 'error');
            this.currentStatus = 'idle';
            this.updateUI();
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }
    
    async saveQuickSettings() {
        const scheduleTime = document.getElementById('schedule-time').value + ':01';
        const maxRetries = parseInt(document.getElementById('max-retries').value);
        const retryInterval = parseInt(document.getElementById('retry-interval').value);
        
        const config = {
            schedule_time: scheduleTime,
            max_retries: maxRetries,
            retry_interval: retryInterval
        };
        
        try {
            const response = await fetch('/api/save_config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ config })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addLogEntry('Quick settings saved', 'success');
                this.showNotification('Settings saved successfully', 'success');
            } else {
                this.addLogEntry(`Failed to save settings: ${data.message}`, 'error');
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.addLogEntry(`Save settings error: ${error.message}`, 'error');
            this.showNotification('Failed to save settings', 'error');
        }
    }
    
    clearLog() {
        this.logEntries = [];
        const logContainer = document.getElementById('activity-log');
        logContainer.innerHTML = '<div class="log-entry text-muted"><small>Log cleared</small></div>';
        this.addLogEntry('Log cleared', 'info');
    }
    
    showOTPSection() {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('otp-section').style.display = 'block';
    }
    
    showControlSection() {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('otp-section').style.display = 'none';
        document.getElementById('control-section').style.display = 'block';
    }
    
    handleStatusUpdate(data) {
        this.currentStatus = data.status;
        this.updateUI();
        
        if (data.error_message) {
            this.addLogEntry(`Error: ${data.error_message}`, 'error');
        }
    }
    
    handleFormStatus(data) {
        if (data.message) {
            const logType = data.status === 'success' ? 'success' : 
                           data.status === 'error' ? 'error' : 'info';
            this.addLogEntry(data.message, logType);
        }
    }
    
    handleSchedulerStatus(data) {
        if (data.running) {
            this.currentStatus = 'scheduled';
            document.getElementById('next-run-time').textContent = 
                data.next_run ? new Date(data.next_run).toLocaleString() : 'Not scheduled';
        } else {
            this.currentStatus = 'idle';
            document.getElementById('next-run-time').textContent = 'Not scheduled';
        }
        this.updateUI();
    }
    
    updateUI() {
        this.updateStatusIndicator();
        this.updateConnectionStatus();
    }
    
    updateStatusIndicator() {
        const statusIcon = document.getElementById('status-icon');
        const statusText = document.getElementById('status-text');
        
        statusIcon.className = 'status-icon me-2';
        
        switch (this.currentStatus) {
            case 'idle':
                statusIcon.classList.add('status-idle');
                statusIcon.innerHTML = '<i class="fas fa-circle"></i>';
                statusText.textContent = 'Idle';
                break;
            case 'scheduled':
                statusIcon.classList.add('status-scheduled');
                statusIcon.innerHTML = '<i class="fas fa-clock"></i>';
                statusText.textContent = 'Scheduled';
                break;
            case 'running':
                statusIcon.classList.add('status-running');
                statusIcon.innerHTML = '<i class="fas fa-play-circle"></i>';
                statusText.textContent = 'Running';
                break;
            case 'success':
                statusIcon.classList.add('status-success');
                statusIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
                statusText.textContent = 'Success';
                break;
            case 'error':
                statusIcon.classList.add('status-error');
                statusIcon.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
                statusText.textContent = 'Error';
                break;
        }
    }
    
    updateConnectionStatus() {
        let statusElement = document.getElementById('connection-status');
        
        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.id = 'connection-status';
            statusElement.className = 'connection-status';
            document.body.appendChild(statusElement);
        }
        
        if (this.isConnected) {
            statusElement.className = 'connection-status connected';
            statusElement.innerHTML = '<i class="fas fa-wifi me-1"></i>Connected';
        } else {
            statusElement.className = 'connection-status disconnected';
            statusElement.innerHTML = '<i class="fas fa-wifi me-1"></i>Disconnected';
        }
    }
    
    addLogEntry(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const entry = {
            message,
            type,
            timestamp,
            id: Date.now()
        };
        
        this.logEntries.unshift(entry);
        
        // Limit log entries
        if (this.logEntries.length > this.maxLogEntries) {
            this.logEntries = this.logEntries.slice(0, this.maxLogEntries);
        }
        
        this.renderLogEntry(entry);
    }
    
    renderLogEntry(entry) {
        const logContainer = document.getElementById('activity-log');
        
        const logElement = document.createElement('div');
        logElement.className = `log-entry log-${entry.type} new-entry`;
        logElement.innerHTML = `
            <div class="log-message">
                <i class="fas ${this.getLogIcon(entry.type)} log-icon"></i>
                ${entry.message}
                <span class="log-time">${entry.timestamp}</span>
            </div>
        `;
        
        // Insert at the beginning
        if (logContainer.firstChild) {
            logContainer.insertBefore(logElement, logContainer.firstChild);
        } else {
            logContainer.appendChild(logElement);
        }
        
        // Remove animation class after animation completes
        setTimeout(() => {
            logElement.classList.remove('new-entry');
        }, 300);
    }
    
    getLogIcon(type) {
        switch (type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            case 'info': return 'fa-info-circle';
            default: return 'fa-circle';
        }
    }
    
    showNotification(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        const toastBody = toast.querySelector('.toast-body');
        
        // Set message and type
        toastBody.textContent = message;
        
        // Update toast styling based on type
        toast.className = 'toast';
        switch (type) {
            case 'success':
                toast.classList.add('border-success');
                toastBody.className = 'toast-body text-success';
                break;
            case 'error':
                toast.classList.add('border-danger');
                toastBody.className = 'toast-body text-danger';
                break;
            case 'warning':
                toast.classList.add('border-warning');
                toastBody.className = 'toast-body text-warning';
                break;
            default:
                toast.classList.add('border-info');
                toastBody.className = 'toast-body text-info';
        }
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
    
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.kpclApp = new KPCLApp();
});

window.addEventListener("load", async () => {
    try {
        window.kpclApp.addLogEntry(
                "checking login session status...",
                "success"
            );
        const res = await fetch("/api/session/status");
        const data = await res.json();
        
        if (!window.kpclApp) return;

        if (data.logged_in) {
            window.kpclApp.showControlSection();
            window.kpclApp.addLogEntry(
                "Recovered active KPCL session",
                "success"
            );
        } else {
            // explicit login view
            document.getElementById("login-section").style.display = "block";
            document.getElementById("otp-section").style.display = "none";
            document.getElementById("control-section").style.display = "none";
        }
    } catch (err) {
        console.error("Session restore failed", err);
    }
});
