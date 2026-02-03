#!/usr/bin/env python3
"""
KPCL Automation Application
Main Flask application for automated form submission
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import json
import logging
import os
from datetime import datetime, time
import threading
from automation.scheduler import AutomationScheduler
from automation.session_manager import SessionManager
from automation.form_filler import FormFiller
import secrets

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global instances
scheduler = None
session_manager = None
form_filler = None

# Application state
app_state = {
    'status': 'idle',
    'last_run': None,
    'next_run': None,
    'attempts': 0,
    'success': False,
    'error_message': None,
    'logged_in': False,
    'otp_required': False
}

def load_config():
    """Load application configuration"""
    try:
        with open('config/settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'schedule_time': '07:00:01',
            'retry_interval': 10,
            'max_retries': 3,
            'headless': True,
            'browser': 'chrome'
        }

def save_config(config):
    """Save application configuration"""
    os.makedirs('config', exist_ok=True)
    with open('config/settings.json', 'w') as f:
        json.dump(config, f, indent=2)

def load_form_data():
    """Load static form data"""
    try:
        with open('config/form_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
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

@app.route('/')
def index():
    """Main dashboard page"""
    config = load_config()
    form_data = load_form_data()
    return render_template('index.html', 
                         config=config, 
                         form_data=form_data, 
                         app_state=app_state)

@app.route('/config')
def config_page():
    """Configuration page"""
    config = load_config()
    form_data = load_form_data()
    return render_template('config.html', config=config, form_data=form_data)

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login credentials"""
    global session_manager, app_state
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'})
        
        # Store credentials in session
        session['username'] = username
        session['password'] = password
        
        # Initialize session manager
        config = load_config()
        session_manager = SessionManager(config)
        
        # Attempt login
        success, message = session_manager.login(username, password)
        
        if success:
            app_state['logged_in'] = True
            app_state['otp_required'] = session_manager.otp_required
            socketio.emit('status_update', app_state)
            
        return jsonify({
            'success': success, 
            'message': message,
            'otp_required': app_state['otp_required']
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/verify_otp', methods=['POST'])
def api_verify_otp():
    """Handle OTP verification"""
    global session_manager, app_state
    
    try:
        data = request.get_json()
        otp = data.get('otp')
        
        if not otp:
            return jsonify({'success': False, 'message': 'OTP required'})
        
        if not session_manager:
            return jsonify({'success': False, 'message': 'Please login first'})
        
        success, message = session_manager.verify_otp(otp)
        
        if success:
            app_state['otp_required'] = False
            app_state['logged_in'] = True
            socketio.emit('status_update', app_state)
            
            
        return jsonify({'success': success, 'message': message})
        
    except Exception as e:
        logger.error(f"OTP verification error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/start_automation', methods=['POST'])
def api_start_automation():
    """Start the automation scheduler"""
    global scheduler, app_state
    
    try:
        if not session_manager or not session_manager.check_session_valid():
            app_state['logged_in'] = False
            return jsonify({'success': False, 'message': 'Please login first'})

        
        config = load_config()
        
        # Initialize scheduler
        scheduler = AutomationScheduler(config, socketio)
        
        # Set credentials
        scheduler.set_credentials(
            session.get('username'),
            session.get('password')
        )
        
        # Start scheduler
        success = scheduler.start()
        
        if success:
            app_state['status'] = 'scheduled'
            app_state['next_run'] = scheduler.get_next_run_time()
            socketio.emit('status_update', app_state)
            
        return jsonify({
            'success': success,
            'message': 'Automation started successfully' if success else 'Failed to start automation',
            'next_run': app_state['next_run']
        })
        
    except Exception as e:
        logger.error(f"Start automation error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stop_automation', methods=['POST'])
def api_stop_automation():
    """Stop the automation scheduler"""
    global scheduler, app_state
    
    try:
        if scheduler:
            scheduler.stop()
            
        app_state['status'] = 'idle'
        app_state['next_run'] = None
        socketio.emit('status_update', app_state)
        
        return jsonify({'success': True, 'message': 'Automation stopped'})
        
    except Exception as e:
        logger.error(f"Stop automation error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/manual_submit', methods=['POST'])
def api_manual_submit():
    """Manual form submission for testing"""
    global form_filler, app_state
    
    try:
        if not app_state['logged_in']:
            return jsonify({'success': False, 'message': 'Please login first'})
        
        config = load_config()
        form_data = load_form_data()
        
        # Initialize form filler
        form_filler = FormFiller(config, socketio)
        
        # Set credentials
        form_filler.set_credentials(
            session.get('username'),
            session.get('password')
        )
        
        # Run in background thread
        def run_submission():
            try:
                app_state['status'] = 'running'
                app_state['attempts'] = 1
                socketio.emit('status_update', app_state)
                
                success, message = form_filler.submit_form(form_data)
                
                app_state['status'] = 'completed'
                app_state['success'] = success
                app_state['error_message'] = None if success else message
                app_state['last_run'] = datetime.now().isoformat()
                
                socketio.emit('status_update', app_state)
                socketio.emit('submission_complete', {
                    'success': success,
                    'message': message
                })
                
            except Exception as e:
                logger.error(f"Manual submission error: {e}")
                app_state['status'] = 'error'
                app_state['error_message'] = str(e)
                socketio.emit('status_update', app_state)
        
        thread = threading.Thread(target=run_submission)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Manual submission started'})
        
    except Exception as e:
        logger.error(f"Manual submit error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/save_config', methods=['POST'])
def api_save_config():
    """Save configuration"""
    try:
        data = request.get_json()
        config = data.get('config', {})
        form_data = data.get('form_data', {})
        
        save_config(config)
        
        os.makedirs('config', exist_ok=True)
        with open('config/form_data.json', 'w') as f:
            json.dump(form_data, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Configuration saved'})
        
    except Exception as e:
        logger.error(f"Save config error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/status')
def api_status():
    """Get current application status"""
    return jsonify(app_state)

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('status_update', app_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info('Client disconnected')

@app.route('/api/session/status')
def api_session_status():
    global session_manager

    # 1️⃣ Ensure session manager exists
    if not session_manager:
        from automation.session_manager import SessionManager
        config = load_config()
        session_manager = SessionManager(config)

    selenium_alive = False
    selenium_logged_in = False

    # 2️⃣ Ensure Selenium is attached to Chrome (9222)
    if not session_manager.selenium.driver:
        try:
            session_manager.start_session()  # attach to :9222
        except Exception as e:
            return jsonify({
                "selenium_alive": False,
                "logged_in": False,
                "automation_running": app_state['status'] in ['running', 'scheduled'],
                "error": "Chrome not reachable on port 9222"
            })

    # 3️⃣ Now Selenium exists
    selenium_alive = True

    try:
        selenium_logged_in = session_manager.check_session_valid()
    except Exception:
        selenium_logged_in = False

    # 4️⃣ Sync Flask state
    app_state['logged_in'] = selenium_logged_in
    app_state['otp_required'] = session_manager.otp_required

    return jsonify({
        "selenium_alive": selenium_alive,
        "logged_in": selenium_logged_in,
        "automation_running": app_state['status'] in ['running', 'scheduled']
    })

def restore_session_state():
    global session_manager, app_state

    config = load_config()
    session_manager = SessionManager(config)

    if session_manager.selenium.driver:
        if session_manager.check_session_valid():
            app_state['logged_in'] = True
            app_state['otp_required'] = False
            logger.info("Recovered existing Selenium login session")
        else:
            logger.info("Selenium exists but session invalid")
if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    os.makedirs('screenshots', exist_ok=True)
    
    # Initialize default config files
    if not os.path.exists('config/settings.json'):
        save_config(load_config())
    
    if not os.path.exists('config/form_data.json'):
        form_data = load_form_data()
        with open('config/form_data.json', 'w') as f:
            json.dump(form_data, f, indent=2)
    
    logger.info("Starting KPCL Automation Application")
    restore_session_state()
    # Run the application
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)


