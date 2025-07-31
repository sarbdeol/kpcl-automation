"""
Selenium WebDriver handler for browser automation
"""

import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

logger = logging.getLogger(__name__)

class SeleniumHandler:
    """Handles Selenium WebDriver operations"""
    
    def __init__(self, config):
        """
        Initialize Selenium handler
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.driver = None
        self.wait = None
        
    def start_driver(self):
        """Start the WebDriver with retry logic"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                browser = self.config.get('browser', 'chrome').lower()
                headless = self.config.get('headless', True)
                
                logger.info(f"Starting WebDriver attempt {retry_count + 1}/{max_retries}")
                
                if browser == 'chrome':
                    self.driver = self._create_chrome_driver(headless)
                elif browser == 'firefox':
                    self.driver = self._create_firefox_driver(headless)
                else:
                    raise ValueError(f"Unsupported browser: {browser}")
                
                if self.driver is None:
                    raise Exception("WebDriver creation returned None")
                
                # Set up WebDriverWait
                self.wait = WebDriverWait(self.driver, 30)
                
                # Configure driver settings
                self.driver.implicitly_wait(10)
                self.driver.maximize_window()
                
                logger.info(f"WebDriver started successfully: {browser}")
                return True
                
            except Exception as e:
                retry_count += 1
                logger.error(f"WebDriver start attempt {retry_count} failed: {e}")
                
                # Clean up failed driver
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                
                if retry_count < max_retries:
                    logger.info(f"Retrying WebDriver start in 2 seconds...")
                    time.sleep(2)
                else:
                    logger.error("All WebDriver start attempts failed")
                    return False
    
    def _create_chrome_driver(self, headless=True):
        """Create Chrome WebDriver with robust error handling"""
        options = ChromeOptions()
        
        if headless:
            options.add_argument('--headless')
        
        # Additional Chrome options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36')
        
        # Disable notifications and popups
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2
        }
        options.add_experimental_option("prefs", prefs)
        
        # Try multiple approaches to get ChromeDriver
        try:
            # Method 1: Try local project chromedriver first
            local_chromedriver = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chromedriver')
            if os.path.exists(local_chromedriver):
                logger.info("Using local project ChromeDriver...")
                service = ChromeService(local_chromedriver)
                return webdriver.Chrome(service=service, options=options)
            
            # Method 2: Use webdriver-manager with timeout
            logger.info("Attempting to download ChromeDriver...")
            service = ChromeService(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
            
        except Exception as e1:
            logger.warning(f"WebDriver Manager failed: {e1}")
            
            # Method 2: Try system Chrome with default driver
            try:
                logger.info("Trying system Chrome installation...")
                # Check if chromedriver is in system PATH
                import shutil
                if shutil.which('chromedriver'):
                    service = ChromeService('chromedriver')
                    return webdriver.Chrome(service=service, options=options)
                    
            except Exception as e2:
                logger.warning(f"System chromedriver failed: {e2}")
                
                # Method 3: Try Chrome app directly (macOS)
                try:
                    logger.info("Trying Chrome app binary directly...")
                    chrome_binary = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                    if os.path.exists(chrome_binary):
                        options.binary_location = chrome_binary
                        # Try with a manual chromedriver path
                        chromedriver_paths = [
                            "/usr/local/bin/chromedriver",
                            "/opt/homebrew/bin/chromedriver",
                            os.path.expanduser("~/chromedriver")
                        ]
                        
                        for path in chromedriver_paths:
                            if os.path.exists(path):
                                service = ChromeService(path)
                                return webdriver.Chrome(service=service, options=options)
                        
                        # If no chromedriver found, try without service
                        return webdriver.Chrome(options=options)
                        
                except Exception as e3:
                    logger.error(f"All Chrome driver methods failed: {e3}")
                    raise Exception(f"Could not initialize Chrome WebDriver. Tried: WebDriver Manager ({e1}), System Path ({e2}), Chrome App ({e3})")
    
    def _create_firefox_driver(self, headless=True):
        """Create Firefox WebDriver"""
        options = FirefoxOptions()
        
        if headless:
            options.add_argument('--headless')
        
        # Additional Firefox options
        options.add_argument('--width=1920')
        options.add_argument('--height=1080')
        
        # Install and use GeckoDriver
        service = FirefoxService(GeckoDriverManager().install())
        return webdriver.Firefox(service=service, options=options)
    
    def stop_driver(self):
        """Stop the WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
                logger.info("WebDriver stopped")
        except Exception as e:
            logger.error(f"Error stopping WebDriver: {e}")
    
    def navigate_to(self, url):
        """Navigate to a URL"""
        try:
            if not self.driver:
                raise Exception("WebDriver not started")
            
            self.driver.get(url)
            logger.info(f"Navigated to: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def find_element(self, by, value, timeout=10):
        """Find an element with timeout"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            logger.warning(f"Element not found: {by}={value}")
            return None
    
    def find_elements(self, by, value):
        """Find multiple elements"""
        try:
            return self.driver.find_elements(by, value)
        except Exception as e:
            logger.error(f"Error finding elements: {e}")
            return []
    
    def click_element(self, by, value, timeout=10):
        """Click an element"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((by, value)))
            element.click()
            logger.debug(f"Clicked element: {by}={value}")
            return True
        except Exception as e:
            logger.error(f"Failed to click element {by}={value}: {e}")
            return False
    
    def send_keys(self, by, value, text, timeout=10, clear=True):
        """Send keys to an element"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            
            if clear:
                element.clear()
            
            element.send_keys(text)
            logger.debug(f"Sent keys to element: {by}={value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send keys to {by}={value}: {e}")
            return False
    
    def select_dropdown(self, by, value, text, timeout=10):
        """Select from dropdown by visible text"""
        try:
            from selenium.webdriver.support.ui import Select
            
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            
            select = Select(element)
            select.select_by_visible_text(text)
            logger.debug(f"Selected dropdown option: {text}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to select dropdown option: {e}")
            return False
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((by, value)))
            return True
        except TimeoutException:
            return False
    
    def wait_for_url_contains(self, text, timeout=10):
        """Wait for URL to contain specific text"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.url_contains(text))
            return True
        except TimeoutException:
            return False
    
    def get_text(self, by, value, timeout=10):
        """Get text from an element"""
        try:
            element = self.find_element(by, value, timeout)
            if element:
                return element.text
            return None
        except Exception as e:
            logger.error(f"Failed to get text from {by}={value}: {e}")
            return None
    
    def get_attribute(self, by, value, attribute, timeout=10):
        """Get attribute value from an element"""
        try:
            element = self.find_element(by, value, timeout)
            if element:
                return element.get_attribute(attribute)
            return None
        except Exception as e:
            logger.error(f"Failed to get attribute {attribute} from {by}={value}: {e}")
            return None
    
    def execute_script(self, script):
        """Execute JavaScript"""
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            logger.error(f"Failed to execute script: {e}")
            return None
    
    def take_screenshot(self, filename=None):
        """Take a screenshot"""
        try:
            if not filename:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshots/screenshot_{timestamp}.png"
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def switch_to_frame(self, frame_reference):
        """Switch to a frame"""
        try:
            self.driver.switch_to.frame(frame_reference)
            return True
        except Exception as e:
            logger.error(f"Failed to switch to frame: {e}")
            return False
    
    def switch_to_default_content(self):
        """Switch back to default content"""
        try:
            self.driver.switch_to.default_content()
            return True
        except Exception as e:
            logger.error(f"Failed to switch to default content: {e}")
            return False
    
    def handle_alert(self, accept=True, timeout=10):
        """Handle JavaScript alert with timeout and robust error handling"""
        try:
            from selenium.common.exceptions import TimeoutException, NoAlertPresentException
            
            # Wait for alert to appear
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            
            alert = self.driver.switch_to.alert
            text = alert.text
            
            if accept:
                alert.accept()
            else:
                alert.dismiss()
            
            logger.info(f"Alert handled successfully: {text}")
            return text
            
        except TimeoutException:
            logger.debug("No alert appeared within timeout")
            return None
        except NoAlertPresentException:
            logger.debug("No alert present")
            return None
        except Exception as e:
            logger.warning(f"Alert handling error: {e}")
            # Try to dismiss any alert that might exist
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                logger.info("Forced alert dismissal successful")
                return "Alert dismissed (forced)"
            except:
                pass
            return None
    
    def handle_possible_alerts(self, timeout=2):
        """Handle any possible alerts with reduced timeout and fewer attempts"""
        try:
            # Reduce to single attempt instead of 3 attempts to speed up
            alert_text = self.handle_alert(accept=True, timeout=timeout)
            if alert_text:
                logger.info(f"Alert handled: {alert_text}")
            # Remove the loop and sleep that was causing delays
        except Exception as e:
            logger.debug(f"Alert handling completed: {e}")
    
    def wait_for_element_robust(self, by, value, timeout=30):
        """Wait for element with optimized timeout and minimal alert handling"""
        try:
            # Quick alert check without long timeout
            self.handle_possible_alerts(timeout=1)
            
            # Then wait for element
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            
            # Only handle alerts again if this is a clickable element that might trigger them
            if by == By.ID and ("btn" in value.lower() or "button" in value.lower()):
                self.handle_possible_alerts(timeout=1)
            
            return element
            
        except Exception as e:
            logger.error(f"Failed to find element {by}={value}: {e}")
            # Take screenshot for debugging
            self.take_screenshot(f"element_not_found_{by}_{value}.png")
            return None
    
    def scroll_to_element(self, by, value):
        """Scroll to an element"""
        try:
            element = self.find_element(by, value)
            if element:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)  # Wait for scroll to complete
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to scroll to element: {e}")
            return False
    
    def wait_for_page_load(self, timeout=30):
        """Wait for page to load completely"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            return True
        except TimeoutException:
            logger.warning("Page load timeout")
            return False
    
    def get_current_url(self):
        """Get current URL"""
        try:
            return self.driver.current_url
        except Exception as e:
            logger.error(f"Failed to get current URL: {e}")
            return None
    
    def refresh_page(self):
        """Refresh the current page"""
        try:
            self.driver.refresh()
            self.wait_for_page_load()
            return True
        except Exception as e:
            logger.error(f"Failed to refresh page: {e}")
            return False
        