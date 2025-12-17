import sys
import os
import yaml
import logging
import pandas as pd
import time

# Add the project root to path so we can import from core/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.browser import BrowserManager
from core.actions import ActionEngine
from core.extractors import DataExtractor
from core.pagination import PaginationHandler

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("outputs/logs.txt"),
        logging.StreamHandler()
    ]
)

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def save_data(data, filepath):
    if not data:
        return
    
    df = pd.DataFrame(data)
    
    # Check if file exists to determine if header is needed
    header = not os.path.exists(filepath)
    
    df.to_csv(filepath, mode='a', header=header, index=False)
    logging.info(f"Saved {len(data)} records to {filepath}")

def run(config_path):
    config = load_config(config_path)
    logger = logging.getLogger(__name__)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(config['output_file']), exist_ok=True)
    
    # Initialize Core Modules
    browser_mgr = BrowserManager(headless=config.get('headless', False))
    driver = browser_mgr.start_browser()
    
    try:
        actions = ActionEngine(driver)
        extractor = DataExtractor(driver)
        paginator = PaginationHandler(driver, actions)
        
        # 1. Navigation
        actions.navigate(config['base_url'])
        
        # 2. Setup Steps (Login, Cookies, etc)
        if 'setup_steps' in config:
            actions.execute_steps(config['setup_steps'])
            
        current_page = 1
        total_records = 0
        
        while True:
            logger.info(f"--- Processing Page {current_page} ---")
            
            # 3. Extraction
            page_data = extractor.extract_data(config['extraction'])
            total_records += len(page_data)
            
            # 4. Save Data (Incremental Save)
            save_data(page_data, config['output_file'])
            
            # 5. Pagination
            if not paginator.handle_pagination(config['pagination'], current_page):
                break
                
            current_page += 1
            
        logger.info(f"Extraction complete. Total records: {total_records}")
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
    finally:
        browser_mgr.close_browser()

if __name__ == "__main__":
    # Default to the sample config if no arg provided
    conf = "config/books_config.yaml"
    if len(sys.argv) > 1:
        conf = sys.argv[1]
        
    run(conf)