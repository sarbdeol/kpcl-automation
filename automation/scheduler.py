"""
Scheduler for automated form submission at specific times
"""

import logging
import threading
import time
from datetime import datetime, time as dt_time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from automation.form_filler import FormFiller
import json

logger = logging.getLogger(__name__)

class AutomationScheduler:
    """Handles scheduling of automated form submissions"""
    
    def __init__(self, config, socketio=None):
        """
        Initialize Automation Scheduler
        
        Args:
            config (dict): Configuration dictionary
            socketio: SocketIO instance for real-time updates
        """
        self.config = config
        self.socketio = socketio
        self.scheduler = BackgroundScheduler()
        self.form_filler = None
        self.username = None
        self.password = None
        self.running = False
        
        # Load form data
        self.form_data = self._load_form_data()
        
        # Parse schedule time
        self.schedule_time = self._parse_schedule_time(
            config.get('schedule_time', '07:00:01')
        )
        
    def _load_form_data(self):
        """Load static form data"""
        try:
            with open('config/form_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Form data file not found, using defaults")
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
    
    def _parse_schedule_time(self, time_str):
        """Parse schedule time string into hour, minute, second"""
        try:
            time_parts = time_str.split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            second = int(time_parts[2]) if len(time_parts) > 2 else 0
            
            return dt_time(hour, minute, second)
        except Exception as e:
            logger.error(f"Invalid schedule time format: {time_str}, using default 07:00:01")
            return dt_time(7, 0, 1)
    
    def set_credentials(self, username, password):
        """Set login credentials"""
        self.username = username
        self.password = password
    
    def start(self):
        """Start the scheduler"""
        try:
            if self.running:
                logger.warning("Scheduler already running")
                return True
            
            if not self.username or not self.password:
                logger.error("Credentials not set")
                return False
            
            # Schedule the job
            self.scheduler.add_job(
                func=self._run_automation,
                trigger=CronTrigger(
                    hour=self.schedule_time.hour,
                    minute=self.schedule_time.minute,
                    second=self.schedule_time.second
                ),
                id='form_submission',
                name='KPCL Form Submission',
                replace_existing=True
            )
            
            # Start the scheduler
            self.scheduler.start()
            self.running = True
            
            logger.info(f"Scheduler started. Next run at {self.schedule_time}")
            
            # Emit status update
            if self.socketio:
                self.socketio.emit('scheduler_status', {
                    'running': True,
                    'next_run': self.get_next_run_time(),
                    'schedule_time': str(self.schedule_time)
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            return False
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
            
            self.running = False
            logger.info("Scheduler stopped")
            
            # Emit status update
            if self.socketio:
                self.socketio.emit('scheduler_status', {
                    'running': False,
                    'next_run': None
                })
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        try:
            if self.scheduler.running:
                jobs = self.scheduler.get_jobs()
                if jobs:
                    next_run = jobs[0].next_run_time
                    if next_run:
                        return next_run.isoformat()
            return None
        except Exception as e:
            logger.error(f"Error getting next run time: {e}")
            return None
    
    def _run_automation(self):
        """Run the automation process"""
        logger.info("Starting scheduled automation run")
        
        try:
            # Emit start event
            if self.socketio:
                self.socketio.emit('automation_started', {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'scheduled'
                })
            
            # Initialize form filler
            self.form_filler = FormFiller(self.config, self.socketio)
            self.form_filler.set_credentials(self.username, self.password)
            
            # Run the automation with retry logic
            max_retries = self.config.get('max_retries', 3)
            retry_interval = self.config.get('retry_interval', 10)
            
            success = False
            attempt = 0
            
            while attempt < max_retries and not success:
                attempt += 1
                logger.info(f"Automation attempt {attempt}/{max_retries}")
                
                try:
                    # Emit attempt status
                    if self.socketio:
                        self.socketio.emit('automation_attempt', {
                            'attempt': attempt,
                            'max_attempts': max_retries,
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    # Submit form
                    success, message = self.form_filler.submit_form(self.form_data, max_retries=1)
                    
                    if success:
                        logger.info(f"Automation successful on attempt {attempt}")
                        
                        # Emit success event
                        if self.socketio:
                            self.socketio.emit('automation_success', {
                                'attempt': attempt,
                                'message': message,
                                'timestamp': datetime.now().isoformat()
                            })
                        break
                    else:
                        logger.warning(f"Automation attempt {attempt} failed: {message}")
                        
                        # Emit failure event
                        if self.socketio:
                            self.socketio.emit('automation_attempt_failed', {
                                'attempt': attempt,
                                'message': message,
                                'timestamp': datetime.now().isoformat()
                            })
                        
                        # Wait before retry (except on last attempt)
                        if attempt < max_retries:
                            logger.info(f"Waiting {retry_interval} seconds before retry")
                            time.sleep(retry_interval)
                
                except Exception as e:
                    error_msg = f"Error in automation attempt {attempt}: {str(e)}"
                    logger.error(error_msg)
                    
                    # Emit error event
                    if self.socketio:
                        self.socketio.emit('automation_error', {
                            'attempt': attempt,
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    # Wait before retry (except on last attempt)
                    if attempt < max_retries:
                        time.sleep(retry_interval)
            
            # Final result
            if not success:
                final_message = f"Automation failed after {max_retries} attempts"
                logger.error(final_message)
                
                # Emit final failure event
                if self.socketio:
                    self.socketio.emit('automation_final_failure', {
                        'total_attempts': max_retries,
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Cleanup
            if self.form_filler:
                self.form_filler.cleanup()
                self.form_filler = None
            
            # Emit completion event
            if self.socketio:
                self.socketio.emit('automation_completed', {
                    'success': success,
                    'total_attempts': attempt,
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info("Scheduled automation run completed")
            
        except Exception as e:
            error_msg = f"Fatal error in scheduled automation: {str(e)}"
            logger.error(error_msg)
            
            # Emit fatal error event
            if self.socketio:
                self.socketio.emit('automation_fatal_error', {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            
            # Cleanup
            try:
                if self.form_filler:
                    self.form_filler.cleanup()
                    self.form_filler = None
            except:
                pass
    
    def run_manual(self):
        """Run automation manually (not scheduled)"""
        logger.info("Starting manual automation run")
        
        # Run in a separate thread to avoid blocking
        thread = threading.Thread(target=self._run_manual_automation)
        thread.daemon = True
        thread.start()
    
    def _run_manual_automation(self):
        """Manual automation run in separate thread"""
        try:
            # Emit start event
            if self.socketio:
                self.socketio.emit('automation_started', {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'manual'
                })
            
            # Initialize form filler
            form_filler = FormFiller(self.config, self.socketio)
            form_filler.set_credentials(self.username, self.password)
            
            # Submit form
            success, message = form_filler.submit_form(self.form_data)
            
            # Emit result
            if self.socketio:
                if success:
                    self.socketio.emit('automation_success', {
                        'attempt': 1,
                        'message': message,
                        'timestamp': datetime.now().isoformat(),
                        'type': 'manual'
                    })
                else:
                    self.socketio.emit('automation_failure', {
                        'message': message,
                        'timestamp': datetime.now().isoformat(),
                        'type': 'manual'
                    })
            
            # Cleanup
            form_filler.cleanup()
            
            logger.info(f"Manual automation completed: {'Success' if success else 'Failed'}")
            
        except Exception as e:
            error_msg = f"Error in manual automation: {str(e)}"
            logger.error(error_msg)
            
            if self.socketio:
                self.socketio.emit('automation_error', {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat(),
                    'type': 'manual'
                })
    
    def update_schedule(self, new_time):
        """Update the schedule time"""
        try:
            self.schedule_time = self._parse_schedule_time(new_time)
            
            if self.running:
                # Remove existing job
                self.scheduler.remove_job('form_submission')
                
                # Add new job with updated time
                self.scheduler.add_job(
                    func=self._run_automation,
                    trigger=CronTrigger(
                        hour=self.schedule_time.hour,
                        minute=self.schedule_time.minute,
                        second=self.schedule_time.second
                    ),
                    id='form_submission',
                    name='KPCL Form Submission',
                    replace_existing=True
                )
                
                logger.info(f"Schedule updated to {self.schedule_time}")
                
                # Emit status update
                if self.socketio:
                    self.socketio.emit('scheduler_status', {
                        'running': True,
                        'next_run': self.get_next_run_time(),
                        'schedule_time': str(self.schedule_time)
                    })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update schedule: {e}")
            return False
    
    def get_status(self):
        """Get scheduler status"""
        return {
            'running': self.running,
            'schedule_time': str(self.schedule_time),
            'next_run': self.get_next_run_time(),
            'credentials_set': bool(self.username and self.password)
        }
