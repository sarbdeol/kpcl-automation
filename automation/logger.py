import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

def setup_logger():
    """Setup application logger with file and console handlers"""
    
    # Create logger
    logger = logging.getLogger('kpcl_automation')
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler for detailed logs
    log_filename = f"logs/automation_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler for important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_session_activity(activity, details=None, level='info'):
    """Log session-related activities with context"""
    logger = logging.getLogger('kpcl_automation')
    
    message = f"SESSION: {activity}"
    if details:
        message += f" - {details}"
    
    if level.lower() == 'error':
        logger.error(message)
    elif level.lower() == 'warning':
        logger.warning(message)
    elif level.lower() == 'debug':
        logger.debug(message)
    else:
        logger.info(message)

def log_form_activity(activity, details=None, level='info'):
    """Log form submission activities with context"""
    logger = logging.getLogger('kpcl_automation')
    
    message = f"FORM: {activity}"
    if details:
        message += f" - {details}"
    
    if level.lower() == 'error':
        logger.error(message)
    elif level.lower() == 'warning':
        logger.warning(message)
    elif level.lower() == 'debug':
        logger.debug(message)
    else:
        logger.info(message)

def log_scheduler_activity(activity, details=None, level='info'):
    """Log scheduler activities with context"""
    logger = logging.getLogger('kpcl_automation')
    
    message = f"SCHEDULER: {activity}"
    if details:
        message += f" - {details}"
    
    if level.lower() == 'error':
        logger.error(message)
    elif level.lower() == 'warning':
        logger.warning(message)
    elif level.lower() == 'debug':
        logger.debug(message)
    else:
        logger.info(message)

def log_automation_step(step, status, details=None):
    """Log automation execution steps with standardized format"""
    logger = logging.getLogger('kpcl_automation')
    
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    message = f"AUTOMATION [{timestamp}] Step: {step} | Status: {status}"
    
    if details:
        message += f" | Details: {details}"
    
    if status.upper() in ['SUCCESS', 'COMPLETED']:
        logger.info(message)
    elif status.upper() in ['FAILED', 'ERROR']:
        logger.error(message)
    elif status.upper() in ['WARNING', 'RETRY']:
        logger.warning(message)
    else:
        logger.info(message)

def log_debug_info(component, info):
    """Log debug information for troubleshooting"""
    logger = logging.getLogger('kpcl_automation')
    logger.debug(f"DEBUG [{component}]: {info}")

def log_performance_metric(operation, duration, details=None):
    """Log performance metrics for optimization"""
    logger = logging.getLogger('kpcl_automation')
    
    message = f"PERFORMANCE: {operation} took {duration:.2f}s"
    if details:
        message += f" - {details}"
    
    logger.info(message)

def get_log_summary():
    """Get recent log entries for dashboard display"""
    try:
        log_filename = f"logs/automation_{datetime.now().strftime('%Y%m%d')}.log"
        
        if not os.path.exists(log_filename):
            return []
        
        with open(log_filename, 'r') as f:
            lines = f.readlines()
        
        # Return last 50 lines
        recent_lines = lines[-50:] if len(lines) > 50 else lines
        
        # Clean and format lines
        cleaned_lines = []
        for line in recent_lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return cleaned_lines
        
    except Exception as e:
        logger = logging.getLogger('kpcl_automation')
        logger.error(f"Error reading log summary: {str(e)}")
        return []

# Initialize logger when module is imported
logger = setup_logger()
logger.info("KPCL Automation logging system initialized")
