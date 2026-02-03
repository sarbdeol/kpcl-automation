"""
Session Manager for handling KPCL login and authentication
"""

import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from automation.selenium_handler import SeleniumHandler

logger = logging.getLogger(__name__)
import json,os

def save_cookies(driver, path="cookies.json"):
    with open(path, "w") as f:
        json.dump(driver.get_cookies(), f)
def load_cookies(driver, base_url, path="cookies.json"):
    if not os.path.exists(path):
        return False

    driver.get(base_url)  # must be same domain

    with open(path, "r") as f:
        cookies = json.load(f)

    for cookie in cookies:
        cookie.pop("sameSite", None)  # Selenium compatibility
        try:
            driver.add_cookie(cookie)
        except Exception:
            pass

    driver.refresh()
    return True
class SessionManager:
    """Manages KPCL website sessions and authentication"""
    
    def __init__(self, config):
        """
        Initialize Session Manager
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.selenium = SeleniumHandler(config)
        self.username = None
        self.password = None
        self.otp_required = False
        self.logged_in = False
        
        # KPCL URLs
        self.base_url = "https://kpcl-ams.com"
        self.login_url = f"{self.base_url}/signin_page.php"
        self.dashboard_url = f"{self.base_url}/user/dashboard.php"
        self.gatepass_url = f"{self.base_url}/user/gatepass.php"
    
    def start_session(self):
        try:
            success = self.selenium.start_driver()
            if not success:
                logger.error("Failed to start browser session")
                return False

            logger.info("Browser session started")

            # 🔥 TRY COOKIE RESTORE HERE
            restored = load_cookies(self.selenium.driver, self.base_url)
            if restored:
                logger.info("Cookies loaded, checking session validity")
                if self.check_session_valid():
                    self.logged_in = True
                    self.otp_required = False
                    logger.info("Session restored from cookies")
                else:
                    logger.info("Cookies present but session invalid")

            return True
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return False
    
    def stop_session(self):
        """Stop the browser session"""
        try:
            self.selenium.stop_driver()
            self.logged_in = False
            logger.info("Browser session stopped")
        except Exception as e:
            logger.error(f"Error stopping session: {e}")
    
    def login(self, username, password):
        """
        Login to KPCL website with robust element handling
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            tuple: (success, message)
        """
        try:
            self.username = username
            self.password = password
            
            # Start browser if not already started
            if not self.selenium.driver:
                if not self.start_session():
                    return False, "Failed to start browser session"
            
            # Navigate to login page
            logger.info("Navigating to login page")
            page_start_time = time.time()
            if not self.selenium.navigate_to(self.login_url):
                return False, "Failed to navigate to login page"
            
            # Handle any initial alerts
            self.selenium.handle_possible_alerts(timeout=3)
            
            # Wait for username field to be available (reduce timeout for immediate elements)
            logger.info("Waiting for username field...")
            username_start_time = time.time()
            username_element = self.selenium.wait_for_element_robust(By.ID, "username", timeout=15)
            if not username_element:
                return False, "Username field not found"
            
            username_wait_time = time.time() - username_start_time
            logger.info(f"Username field found after {username_wait_time:.2f} seconds")
            
            # Fill username
            logger.info("Filling username")
            username_fill_start = time.time()
            username_element.clear()
            username_element.send_keys(username)
            username_fill_time = time.time() - username_fill_start
            logger.info(f"Username filled in {username_fill_time:.2f} seconds")
            
            # Reduce alert handling after username (field typing shouldn't trigger alerts)
            # self.selenium.handle_possible_alerts(timeout=5)  # Commented out to reduce delay
            
            # Wait for password field (should be immediate after username)
            logger.info("Waiting for password field...")
            password_start_time = time.time()
            password_element = self.selenium.wait_for_element_robust(By.ID, "password", timeout=10)
            if not password_element:
                return False, "Password field not found"
            
            password_wait_time = time.time() - password_start_time
            logger.info(f"Password field found after {password_wait_time:.2f} seconds")
            
            # Fill password
            logger.info("Filling password")
            password_fill_start = time.time()
            password_element.clear()
            password_element.send_keys(password)
            password_fill_time = time.time() - password_fill_start
            logger.info(f"Password filled in {password_fill_time:.2f} seconds")
            
            # Only handle alerts if OTP button click might trigger them
            
            # Wait for Generate OTP button (should be immediate after password)
            logger.info("Waiting for Generate OTP button...")
            otp_button_start_time = time.time()
            otp_button = self.selenium.wait_for_element_robust(By.ID, "generateOtpBtn", timeout=15)
            if not otp_button:
                return False, "Generate OTP button not found"
            
            otp_button_wait_time = time.time() - otp_button_start_time
            logger.info(f"Generate OTP button found after {otp_button_wait_time:.2f} seconds")
            
            # Click Generate OTP button
            logger.info("Clicking Generate OTP button")
            otp_start_time = time.time()
            otp_button.click()
            
            # Handle any alerts after clicking OTP button
            self.selenium.handle_possible_alerts(timeout=10)
            
            # Wait for OTP section to appear with more aggressive timeout
            logger.info("Waiting for OTP section to become available...")
            otp_section = self.selenium.wait_for_element_robust(By.ID, "otpSection", timeout=45)
            if otp_section and otp_section.is_displayed():
                otp_wait_time = time.time() - otp_start_time
                logger.info(f"OTP section appeared after {otp_wait_time:.2f} seconds")
                self.otp_required = True
                logger.info("OTP required for login")
                return True, "OTP sent. Please enter OTP to continue."
            else:
                # Check for error messages
                error_element = self.selenium.find_element(By.ID, "otpStatus")
                if error_element:
                    error_text = error_element.text
                    if error_text:
                        return False, f"Login failed: {error_text}"
                
                return False, "Failed to generate OTP. Please check credentials."
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, f"Login error: {str(e)}"
    
    def verify_otp(self, otp):
        """
        Verify OTP and complete login with robust element handling
        
        Args:
            otp (str): OTP code
            
        Returns:
            tuple: (success, message)
        """
        try:
            if not self.otp_required:
                return False, "OTP not required"
            
            # Wait for OTP field to be available
            otp_element = self.selenium.wait_for_element_robust(By.ID, "otp_code", timeout=30)
            if not otp_element:
                return False, "OTP field not found"
            
            # Fill OTP
            logger.info("Filling OTP")
            otp_element.clear()
            otp_element.send_keys(otp)
            
            # Handle any alerts after OTP entry
            self.selenium.handle_possible_alerts(timeout=5)
            
            # Wait for Verify OTP button
            verify_button = self.selenium.wait_for_element_robust(By.ID, "verifyOtpBtn", timeout=30)
            if not verify_button:
                return False, "Verify OTP button not found"
            
            # Click Verify OTP button
            logger.info("Clicking Verify OTP button")
            verify_button.click()
            
            # Handle alerts immediately after OTP verification
            self.selenium.handle_possible_alerts(timeout=15)
            
            # Wait for page processing with dynamic check instead of fixed sleep
            wait_time = 0
            max_wait = 10
            while wait_time < max_wait:
                current_url = self.selenium.get_current_url()
                if current_url and ("dashboard" in current_url or "user" in current_url):
                    break
                time.sleep(1)
                wait_time += 1
            
            # Check current URL for successful redirect
            current_url = self.selenium.get_current_url()
            logger.info(f"Current URL after OTP verification: {current_url}")
            
            if current_url:
                if "dashboard" in current_url or "user" in current_url:
                    self.logged_in = True
                    self.otp_required = False
                    logger.info("Login successful - already on dashboard")
                    return True, "Login successful"
                elif "signin" in current_url:
                    logger.info("Still on signin page - checking for additional steps")
                    
                    # Look for Sign In button and click if present
                    signin_btn = self.selenium.wait_for_element_robust(By.ID, "signInBtn", timeout=15)
                    if signin_btn and signin_btn.is_displayed():
                        logger.info("Clicking Sign In button after OTP verification")
                        signin_btn.click()
                        
                        # Handle any alerts after signin button click
                        self.selenium.handle_possible_alerts(timeout=10)
                        
                        # Wait for redirect
                        time.sleep(5)
                        
                        current_url = self.selenium.get_current_url()
                        if current_url and ("dashboard" in current_url or "user" in current_url):
                            self.logged_in = True
                            self.otp_required = False

                            # 🔥 SAVE COOKIES HERE
                            save_cookies(self.selenium.driver)
                            logger.info("Cookies saved after OTP login")

                            return True, "Login successful"
            
            # Check for success/error status messages
            status_element = self.selenium.wait_for_element_robust(By.ID, "otpStatus", timeout=10)
            if status_element:
                status_text = status_element.text
                logger.info(f"OTP Status: {status_text}")
                
                if "verified successfully" in status_text.lower():
                    self.logged_in = True
                    self.otp_required = False

                    # 🔥 SAVE COOKIES HERE
                    save_cookies(self.selenium.driver)
                    logger.info("Cookies saved after OTP verified")

                    return True, "OTP verified successfully"
                elif "invalid" in status_text.lower() or "expired" in status_text.lower():
                    return False, f"OTP verification failed: {status_text}"
            
            # If we reach here, assume successful verification
            self.logged_in = True
            self.otp_required = False
            save_cookies(self.selenium.driver)
            logger.info("Cookies saved (assumed success)")
            logger.info("OTP verification completed (assumed successful)")
            
            return True, "OTP verification completed"
        
        except Exception as e:
            logger.error(f"OTP verification failed: {e}")
            self.selenium.take_screenshot("otp_verification_error.png")
            return False, f"OTP verification error: {e}"
          
        except Exception as e:
            logger.error(f"OTP verification error: {e}")
            return False, f"OTP verification error: {str(e)}"
        
    def check_session_valid(self):
        """
        Check if current session is still valid
        
        Returns:
            bool: True if session is valid
        """
        try:
            if not self.selenium.driver:
                return False
            
            current_url = self.selenium.get_current_url()
            print(f"Checking session validity, current URL: {current_url}")
            self.selenium.driver.save_screenshot("current_url.png")
            # If we're on login page, session is not valid
            if current_url and ("signin" in current_url or "login" in current_url or "data" in current_url):
                return False
            
            # Try to navigate to dashboard
            self.selenium.navigate_to(self.dashboard_url)
            time.sleep(2)
            self.selenium.driver.save_screenshot("session_check.png")
            
            # Check if we're redirected to login
            current_url = self.selenium.get_current_url()
            if current_url and ("signin" in current_url or "login" in current_url):
                self.logged_in = False
                return False
            
            # Check for session invalid alerts
            alert_text = self.selenium.handle_alert(accept=True)
            if alert_text and "invalid session" in alert_text.lower():
                self.logged_in = False
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Session check error: {e}")
            return False
    
    def refresh_session(self):
        """
        Refresh the current session
        
        Returns:
            tuple: (success, message)
        """
        try:
            if not self.check_session_valid():
                logger.info("Session invalid, attempting re-login")
                
                # Re-login
                success, message = self.login(self.username, self.password)
                if not success:
                    return False, f"Re-login failed: {message}"
                
                if self.otp_required:
                    return False, "OTP required for re-login"
            
            # Navigate to gatepass page to refresh tokens
            logger.info("Refreshing session by visiting gatepass page")
            self.selenium.navigate_to(self.gatepass_url)
            time.sleep(3)
            
            # Check for session invalid alerts
            alert_text = self.selenium.handle_alert(accept=True)
            if alert_text and "invalid session" in alert_text.lower():
                return False, "Session expired"
            
            # Check if we're on the right page
            current_url = self.selenium.get_current_url()
            if current_url and "gatepass" in current_url:
                return True, "Session refreshed successfully"
            
            return False, "Failed to refresh session"
            
        except Exception as e:
            logger.error(f"Session refresh error: {e}")
            return False, f"Session refresh error: {str(e)}"
    
    def navigate_to_gatepass(self):
        """
        Navigate to gatepass page
        
        Returns:
            bool: True if successful
        """
        try:
            if not self.check_session_valid():
                logger.warning("Session not valid, cannot navigate to gatepass")
                return False
            
            logger.info("Navigating to gatepass page")
            success = self.selenium.navigate_to(self.gatepass_url)
            
            if success:
                time.sleep(3)
                
                # Check for alerts (like "invalid session")
                alert_text = self.selenium.handle_alert(accept=True)
                if alert_text:
                    logger.warning(f"Alert detected: {alert_text}")
                    if "invalid session" in alert_text.lower():
                        self.logged_in = False
                        return False
                
                # Verify we're on the gatepass page
                current_url = self.selenium.get_current_url()
                if current_url and "gatepass" in current_url:
                    logger.info("Successfully navigated to gatepass page")
                    return True
                else:
                    logger.warning(f"Unexpected URL after navigation: {current_url}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False
    
    def close_session(self):
        """Close the browser session"""
        try:
            if self.selenium:
                self.selenium.stop_driver()
                logger.info("Browser session closed")
            self.logged_in = False
            self.otp_required = False
        except Exception as e:
            logger.error(f"Error closing session: {e}")
    
    def get_csrf_token(self):
        """
        Extract CSRF token from the current page
        
        Returns:
            str: CSRF token or None
        """
        try:
            # Look for gatepass_token input field
            token_element = self.selenium.find_element(By.NAME, "gatepass_token")
            if token_element:
                token_value = token_element.get_attribute("value")
                logger.info(f"Found CSRF token: {token_value[:20]}...")
                return token_value
            
            logger.warning("CSRF token not found")
            return None
            
        except Exception as e:
            logger.error(f"Error getting CSRF token: {e}")
            return None
    
    def logout(self):
        """Logout from the system"""
        try:
            if self.selenium.driver:
                logout_url = f"{self.base_url}/logout.php"
                self.selenium.navigate_to(logout_url)
                time.sleep(2)
            
            self.logged_in = False
            logger.info("Logged out successfully")
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
