"""
Form Filler for automated KPCL gatepass form submission
"""

import logging
import time
import json
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from automation.selenium_handler import SeleniumHandler
from automation.session_manager import SessionManager

logger = logging.getLogger(__name__)

class FormFiller:
    """Handles automated form filling and submission"""
    
    def __init__(self, config, socketio=None):
        """
        Initialize Form Filler
        
        Args:
            config (dict): Configuration dictionary
            socketio: SocketIO instance for real-time updates
        """
        self.config = config
        self.socketio = socketio
        self.session_manager = SessionManager(config)
        self.username = None
        self.password = None
        
        # Form field mappings
        self.field_mappings = {
            'ash_utilization': 'ash_utilization',
            'pickup_time': 'pickup_time',
            'vehicle_type': 'vehicle_type',
            'quantity_limit': 'quantity_limit',
            'vehicle_classification': 'vehicle_classification',
            'authorised_person': 'authorised_person',
            'vehicle_no': 'vehicle_no1',
            'dl_no': 'dl_no',
            'driver_mob_no': 'driver_mob_no1'
        }
    
    def set_credentials(self, username, password):
        """Set login credentials"""
        self.username = username
        self.password = password
    
    def emit_status(self, status, message=None, data=None):
        """Emit status update via SocketIO"""
        if self.socketio:
            update = {
                'status': status,
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'data': data
            }
            self.socketio.emit('form_status', update)
    
    def submit_form(self, form_data, max_retries=3):
        """
        Submit the gatepass form with retry mechanism
        
        Args:
            form_data (dict): Form data to submit
            max_retries (int): Maximum number of retries
            
        Returns:
            tuple: (success, message)
        """
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                retry_count += 1
                logger.info(f"Form submission attempt {retry_count}/{max_retries}")
                
                self.emit_status('starting', f'Starting submission attempt {retry_count}')
                
                # Ensure session is valid
                success, message = self._ensure_valid_session()
                if not success:
                    if retry_count < max_retries:
                        logger.warning(f"Session setup failed, retrying in 10 seconds: {message}")
                        time.sleep(10)
                        continue
                    else:
                        return False, f"Session setup failed: {message}"
                
                # Navigate to gatepass page
                self.emit_status('navigating', 'Navigating to gatepass page')
                if not self.session_manager.navigate_to_gatepass():
                    if retry_count < max_retries:
                        logger.warning("Failed to navigate to gatepass page, retrying")
                        time.sleep(10)
                        continue
                    else:
                        return False, "Failed to navigate to gatepass page"
                
                # Extract dynamic data
                self.emit_status('extracting', 'Extracting dynamic data from page')
                dynamic_data = self._extract_dynamic_data()
                
                # Merge static and dynamic data
                complete_form_data = {**form_data, **dynamic_data}
                
                # Fill and submit form
                self.emit_status('filling', 'Filling form fields')
                success, message = self._fill_and_submit_form(complete_form_data)
                
                if success:
                    self.emit_status('success', 'Form submitted successfully')
                    logger.info("Form submission successful")
                    return True, "Form submitted successfully"
                else:
                    if retry_count < max_retries:
                        logger.warning(f"Form submission failed, retrying in 10 seconds: {message}")
                        self.emit_status('retrying', f'Retry {retry_count}: {message}')
                        time.sleep(10)
                    else:
                        self.emit_status('failed', f'All retries failed: {message}')
                        return False, f"Form submission failed after {max_retries} attempts: {message}"
                
            except Exception as e:
                error_msg = f"Error in submission attempt {retry_count}: {str(e)}"
                logger.error(error_msg)
                
                if retry_count < max_retries:
                    self.emit_status('error', f'Error, retrying: {str(e)}')
                    time.sleep(10)
                else:
                    self.emit_status('failed', f'Fatal error: {str(e)}')
                    return False, error_msg
        
        return False, "Maximum retries exceeded"
    
    def _ensure_valid_session(self):
        """Ensure we have a valid logged-in session"""
        try:
            # Start session if not already started
            if not self.session_manager.selenium.driver:
                if not self.session_manager.start_session():
                    return False, "Failed to start browser session"
            
            # Check if session is valid
            if not self.session_manager.check_session_valid():
                logger.info("Session invalid, attempting login")
                
                # Attempt login
                success, message = self.session_manager.login(self.username, self.password)
                if not success:
                    return False, f"Login failed: {message}"
                
                # If OTP is required, we can't proceed automatically
                if self.session_manager.otp_required:
                    return False, "OTP required for login. Please complete login manually."
            
            return True, "Session is valid"
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False, f"Session validation error: {str(e)}"
    
    def _extract_dynamic_data(self):
        """Extract dynamic data from the gatepass page"""
        dynamic_data = {}
        
        try:
            # Extract current ash price
            ash_price_element = self.session_manager.selenium.find_element(By.NAME, "ash_price")
            if ash_price_element:
                ash_price = ash_price_element.get_attribute("value") or "150"
                dynamic_data['ash_price'] = ash_price
                logger.info(f"Extracted ash price: {ash_price}")
            
            # Extract balance amount
            balance_element = self.session_manager.selenium.find_element(By.NAME, "balance_amount")
            if balance_element:
                balance = balance_element.get_attribute("value") or "0"
                dynamic_data['balance_amount'] = balance
                logger.info(f"Extracted balance amount: {balance}")
            
            # Extract gatepass token
            token_element = self.session_manager.selenium.find_element(By.NAME, "gatepass_token")
            if token_element:
                token = token_element.get_attribute("value")
                dynamic_data['gatepass_token'] = token
                logger.info(f"Extracted gatepass token: {token[:20]}...")
            
            # Extract other dynamic fields that might be present
            dynamic_fields = [
                'total_extra', 'full_flyash', 'extra_flyash'
            ]
            
            for field in dynamic_fields:
                element = self.session_manager.selenium.find_element(By.NAME, field)
                if element:
                    value = element.get_attribute("value")
                    if value:
                        dynamic_data[field] = value
                        logger.debug(f"Extracted {field}: {value}")
            
        except Exception as e:
            logger.warning(f"Error extracting dynamic data: {e}")
        
        return dynamic_data
    
    def _fill_and_submit_form(self, form_data):
        """Fill and submit the form with robust element handling"""
        try:
            selenium = self.session_manager.selenium
            
            # Handle any initial alerts
            selenium.handle_possible_alerts(timeout=10)
            
            # Fill ash utilization dropdown
            if 'ash_utilization' in form_data:
                ash_dropdown = selenium.wait_for_element_robust(By.NAME, 'ash_utilization', timeout=30)
                if ash_dropdown:
                    try:
                        select = Select(ash_dropdown)
                        select.select_by_visible_text(form_data['ash_utilization'])
                        logger.info(f"Selected ash utilization: {form_data['ash_utilization']}")
                        selenium.handle_possible_alerts(timeout=5)
                    except Exception as e:
                        logger.warning(f"Failed to select ash utilization: {e}")
                else:
                    logger.warning("Ash utilization dropdown not found")
            
            # Fill pickup time dropdown
            if 'pickup_time' in form_data:
                pickup_dropdown = selenium.wait_for_element_robust(By.NAME, 'pickup_time', timeout=30)
                if pickup_dropdown:
                    try:
                        select = Select(pickup_dropdown)
                        select.select_by_visible_text(form_data['pickup_time'])
                        logger.info(f"Selected pickup time: {form_data['pickup_time']}")
                        selenium.handle_possible_alerts(timeout=5)
                    except Exception as e:
                        logger.warning(f"Failed to select pickup time: {e}")
                else:
                    logger.warning("Pickup time dropdown not found")
            
            # Fill vehicle information
            vehicle_fields = [
                ('vehicle_no', 'vehicle_no1'),
                ('dl_no', 'dl_no'),
                ('driver_mob_no', 'driver_mob_no1')
            ]
            
            for form_key, field_name in vehicle_fields:
                if form_key in form_data:
                    field_element = selenium.wait_for_element_robust(By.NAME, field_name, timeout=30)
                    if field_element:
                        try:
                            field_element.clear()
                            field_element.send_keys(form_data[form_key])
                            logger.info(f"Filled {field_name}: {form_data[form_key]}")
                            selenium.handle_possible_alerts(timeout=5)
                        except Exception as e:
                            logger.warning(f"Failed to fill {field_name}: {e}")
                    else:
                        logger.warning(f"Field {field_name} not found")
            
            # Select authorised person dropdown
            if 'authorised_person' in form_data:
                auth_dropdown = selenium.wait_for_element_robust(By.NAME, 'authorised_person', timeout=30)
                if auth_dropdown:
                    try:
                        select = Select(auth_dropdown)
                        select.select_by_visible_text(form_data['authorised_person'])
                        logger.info(f"Selected authorised person: {form_data['authorised_person']}")
                        selenium.handle_possible_alerts(timeout=5)
                    except Exception as e:
                        logger.warning(f"Failed to select authorised person: {e}")
                else:
                    logger.warning("Authorised person dropdown not found")
            
            # Wait for form to update
            time.sleep(3)
            
            # Handle any alerts before submission
            selenium.handle_possible_alerts(timeout=10)
            
            # Submit the form
            logger.info("Submitting the form")
            submit_button = selenium.wait_for_element_robust(By.NAME, "generate_flyash_gatepass", timeout=30)
            
            if submit_button:
                # Scroll to submit button
                selenium.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(1)
                
                # Take screenshot before submission
                selenium.take_screenshot("before_submission.png")
                
                # Click submit button
                logger.info("Clicking submit button")
                submit_button.click()
                
                # Handle alerts immediately after submission
                selenium.handle_possible_alerts(timeout=15)
                
                # Wait for response
                time.sleep(5)
                
                # Take screenshot after submission
                selenium.take_screenshot("after_submission.png")
                
                # Check current URL for success/error indicators
                current_url = selenium.get_current_url()
                logger.info(f"Current URL after submission: {current_url}")
                
                # Check for success/error messages on page
                success_found = False
                error_found = False
                
                # Look for success indicators in page content
                page_body = selenium.wait_for_element_robust(By.TAG_NAME, "body", timeout=10)
                if page_body:
                    page_text = page_body.text.lower()
                    
                    success_indicators = [
                        "success", "generated", "gatepass", "complete", "submitted"
                    ]
                    
                    error_indicators = [
                        "invalid session", "exhausted", "failed", "error", "expired"
                    ]
                    
                    for indicator in success_indicators:
                        if indicator in page_text:
                            success_found = True
                            logger.info(f"Success indicator found: {indicator}")
                            break
                    
                    for indicator in error_indicators:
                        if indicator in page_text:
                            error_found = True
                            logger.warning(f"Error indicator found: {indicator}")
                            break
                
                if success_found:
                    return True, "Form submitted successfully"
                elif error_found:
                    return False, "Form submission failed - check page for details"
                else:
                    # If no clear indicators, assume success if no obvious errors
                    logger.info("No clear success/error indicators - assuming success")
                    return True, "Form submission completed"
            else:
                return False, "Submit button not found"
            
        except Exception as e:
            logger.error(f"Form submission error: {e}")
            try:
                self.session_manager.selenium.take_screenshot("form_submission_error.png")
            except:
                pass
            return False, f"Form submission error: {str(e)}"
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session_manager:
                self.session_manager.stop_session()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def test_form_access(self):
        """Test if we can access the gatepass form"""
        try:
            # Ensure session is valid
            success, message = self._ensure_valid_session()
            if not success:
                return False, message
            
            # Navigate to gatepass page
            if not self.session_manager.navigate_to_gatepass():
                return False, "Cannot access gatepass page"
            
            # Check if form is present
            form_element = self.session_manager.selenium.find_element(
                By.NAME, "generate_flyash_gatepass"
            )
            
            if form_element:
                return True, "Gatepass form is accessible"
            else:
                return False, "Gatepass form not found on page"
            
        except Exception as e:
            logger.error(f"Form access test error: {e}")
            return False, f"Form access test error: {str(e)}"
