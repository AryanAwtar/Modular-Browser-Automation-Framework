import logging
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class PaginationHandler:
    """
    Handles logic for moving to the next page.
    """
    def __init__(self, driver, action_engine):
        self.driver = driver
        self.actions = action_engine
        self.logger = logging.getLogger(__name__)

    def handle_pagination(self, config, current_page):
        """
        Attempts to go to the next page.
        
        Returns:
            bool: True if navigation was successful, False otherwise.
        """
        if not config.get('enabled', False):
            return False

        max_pages = config.get('max_pages', 1)
        if current_page >= max_pages:
            self.logger.info("Max pages reached.")
            return False

        next_selector = config.get('next_button_selector')
        
        try:
            # Check if button exists
            self.logger.info(f"Attempting to go to page {current_page + 1}...")
            
            # Using the ActionEngine to click safely
            self.actions.click('css_selector', next_selector)
            
            # Simple wait for stale element or load (can be improved with implicit waits)
            time.sleep(2) 
            return True

        except (NoSuchElementException, TimeoutException):
            self.logger.info("Pagination button not found or not clickable. Stopping.")
            return False
        except Exception as e:
            self.logger.error(f"Pagination error: {e}")
            return False