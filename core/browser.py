import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class BrowserManager:
    """
    Manages the lifecycle of the Selenium WebDriver.
    """
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.logger = logging.getLogger(__name__)

    def start_browser(self):
        """Initializes and returns the Chrome WebDriver."""
        self.logger.info("Initializing Browser...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
        
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Browser initialized successfully.")
            return self.driver
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise

    def close_browser(self):
        """Safely closes the browser session."""
        if self.driver:
            self.logger.info("Closing browser...")
            self.driver.quit()