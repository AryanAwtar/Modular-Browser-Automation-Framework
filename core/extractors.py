import logging
from bs4 import BeautifulSoup

class DataExtractor:
    """
    Parses HTML content to extract structured data based on configuration.
    Uses BeautifulSoup for speed and flexibility after the page is loaded.
    """
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)

    def extract_data(self, config):
        """
        Extracts data from the current page source.
        
        Args:
            config (dict): The 'extraction' part of the yaml config.
        Returns:
            list[dict]: A list of dictionaries containing extracted data.
        """
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        container_selector = config.get('container')
        fields = config.get('fields', {})
        
        results = []
        
        # Find all container elements (e.g., rows in a table, cards in a grid)
        containers = soup.select(container_selector)
        self.logger.info(f"Found {len(containers)} items on current page.")

        for item in containers:
            row_data = {}
            for field_name, rules in fields.items():
                selector = rules.get('selector')
                attr = rules.get('attribute', 'text')
                
                try:
                    element = item.select_one(selector)
                    if element:
                        if attr == 'text':
                            row_data[field_name] = element.get_text(strip=True)
                        elif attr == 'href':
                            row_data[field_name] = element.get('href')
                        else:
                            row_data[field_name] = element.get(attr)
                    else:
                        row_data[field_name] = None
                except Exception as e:
                    self.logger.warning(f"Error extracting field {field_name}: {e}")
                    row_data[field_name] = None
            
            results.append(row_data)
            
        return results