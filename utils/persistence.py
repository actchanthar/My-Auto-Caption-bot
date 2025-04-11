import json
import os
from utils.logger import setup_logger

# Set up logger
logger = setup_logger(__name__)

# Path to settings file
SETTINGS_FILE = 'data/settings.json'

def _ensure_data_dir():
    """Ensure the data directory exists"""
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)

def load_settings():
    """Load settings from file"""
    _ensure_data_dir()
    
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        else:
            # If file doesn't exist, create it with default empty settings
            default_settings = {}
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(default_settings, f, indent=2)
            return default_settings
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return {}

def save_settings(settings):
    """Save settings to file"""
    _ensure_data_dir()
    
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return False

def get_setting(key, default=None):
    """Get a specific setting"""
    settings = load_settings()
    return settings.get(key, default)

def save_setting(key, value):
    """Save a specific setting"""
    settings = load_settings()
    settings[key] = value
    return save_settings(settings)

def delete_setting(key):
    """Delete a specific setting"""
    settings = load_settings()
    if key in settings:
        del settings[key]
        return save_settings(settings)
    return True