import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class ActionEngine:
    """
    Handles generic interactions with the webpage (Click, Input, Wait).
    """
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)

    def execute_steps(self, steps):
        """Iterates through a list of steps from config and executes them."""
        if not steps:
            return

        for step in steps:
            action_type = step.get('action')
            target_type = step.get('target', 'css_selector')
            selector = step.get('selector')
            value = step.get('value', None)
            timeout = step.get('timeout', 10)

            try:
                if action_type == 'navigate':
                    self.navigate(value)
                elif action_type == 'click':
                    self.click(target_type, selector, timeout)
                elif action_type == 'input':
                    self.input_text(target_type, selector, value, timeout)
                elif action_type == 'wait':
                    self.wait_for_element(target_type, selector, timeout)
                else:
                    self.logger.warning(f"Unknown action: {action_type}")
            except Exception as e:
                self.logger.error(f"Error executing step {step}: {e}")

    def _get_by_strategy(self, strategy):
        strategies = {
            'css_selector': By.CSS_SELECTOR,
            'xpath': By.XPATH,
            'id': By.ID,
            'name': By.NAME,
            'class_name': By.CLASS_NAME
        }
        return strategies.get(strategy, By.CSS_SELECTOR)

    def navigate(self, url):
        self.logger.info(f"Navigating to {url}")
        self.driver.get(url)

    def click(self, target_type, selector, timeout=10):
        by = self._get_by_strategy(target_type)
        self.logger.info(f"Clicking element: {selector}")
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        element.click()

    def input_text(self, target_type, selector, text, timeout=10):
        by = self._get_by_strategy(target_type)
        self.logger.info(f"Inputting text into: {selector}")
        element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((by, selector))
        )
        element.clear()
        element.send_keys(text)

    def wait_for_element(self, target_type, selector, timeout=10):
        by = self._get_by_strategy(target_type)
        self.logger.info(f"Waiting for element: {selector}")
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )