import sys
import os
import yaml
import threading
import logging
import pandas as pd
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

# Add project root to path to import runners and core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from runners.run_pipeline import run as run_pipeline

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Global State
SCRAPER_STATUS = {
    "is_running": False,
    "message": "Idle",
    "total_records": 0
}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/books_config.yaml')
LOG_PATH = os.path.join(os.path.dirname(__file__), '../outputs/logs.txt')

def run_scraper_thread(config_path):
    """Runs the scraper in a separate thread to not block the server."""
    global SCRAPER_STATUS
    SCRAPER_STATUS["is_running"] = True
    SCRAPER_STATUS["message"] = "Running..."
    
    try:
        # Clear previous logs
        open(LOG_PATH, 'w').close()
        
        # Run the pipeline
        run_pipeline(config_path)
        
        SCRAPER_STATUS["message"] = "Completed Successfully"
    except Exception as e:
        SCRAPER_STATUS["message"] = f"Failed: {str(e)}"
    finally:
        SCRAPER_STATUS["is_running"] = False

@app.route('/api/config', methods=['GET'])
def get_config():
    """Returns the current YAML configuration."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            content = f.read()
        return jsonify({"config": content})
    return jsonify({"config": ""}), 404

@app.route('/api/config', methods=['POST'])
def save_config():
    """Updates the YAML configuration."""
    data = request.json
    new_config = data.get('config')
    try:
        # Validate YAML
        yaml.safe_load(new_config)
        with open(CONFIG_PATH, 'w') as f:
            f.write(new_config)
        return jsonify({"status": "success", "message": "Configuration saved"})
    except yaml.YAMLError as e:
        return jsonify({"status": "error", "message": f"Invalid YAML: {e}"}), 400

@app.route('/api/run', methods=['POST'])
def trigger_run():
    """Starts the scraper if not already running."""
    if SCRAPER_STATUS["is_running"]:
        return jsonify({"status": "error", "message": "Scraper is already running"}), 409
    
    thread = threading.Thread(target=run_scraper_thread, args=(CONFIG_PATH,))
    thread.start()
    return jsonify({"status": "success", "message": "Scraper started"})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the current status of the scraper."""
    return jsonify(SCRAPER_STATUS)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Returns the content of the log file."""
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'r') as f:
            return jsonify({"logs": f.read()})
    return jsonify({"logs": "No logs yet."})

@app.route('/api/data', methods=['GET'])
def get_data():
    """Returns the scraped CSV data as JSON."""
    # Read config to find output path
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
        output_file = config.get('output_file', 'outputs/data.csv')
        
        full_path = os.path.join(os.path.dirname(__file__), '..', output_file)
        
        if os.path.exists(full_path):
            df = pd.read_csv(full_path)
            return jsonify({"data": df.to_dict(orient='records'), "columns": df.columns.tolist()})
        return jsonify({"data": [], "columns": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create outputs dir if not exists
    os.makedirs(os.path.join(os.path.dirname(__file__), '../outputs'), exist_ok=True)
    app.run(debug=True, port=5000)