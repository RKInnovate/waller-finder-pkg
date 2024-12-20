"""
Utility functions for the wallet finder application.
"""

import json
import uuid
import shutil
import logging
import requests
import platform
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Constants
app_data_dir = Path.home() / '.wallet_finder'
csv_file = app_data_dir / "found_wallets.csv"
config_file = app_data_dir / "config.json"
download_dir = Path.home() / 'Downloads'

def logger_config() -> logging.Logger:
    """Configure and return the application logger."""
    Path.mkdir(app_data_dir, exist_ok=True)
    log_file = app_data_dir / "wallet_finder.log"
    
    logger = logging.getLogger("WalletFinder")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def load_wordlist(filename: str = 'bip39_wordlist.txt') -> list:
    """Load wordlist from file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [word.strip() for word in file.readlines() if word.strip()]
    except Exception as e:
        raise ValueError(f"Failed to load wordlist: {str(e)}")

def get_config() -> dict:
    """Get or create configuration."""
    if not config_file.exists():
        default_config = {
            "device_id": str(uuid.uuid4()),
            "device_mac": hex(uuid.getnode()),
            "device_name": platform.node(),
            "progress": 0,
            "wordlist_file": "",
            "api_key": ""
        }
        save_config(default_config)
        return default_config
        
    try:
        with open(config_file, 'r') as file:
            return json.load(file)
    except Exception as e:
        raise ValueError(f"Failed to load config: {str(e)}")

def save_config(config_data: dict = None) -> None:
    """Save configuration to file."""
    if config_data is None:
        config_data = get_config()
        
    try:
        with open(config_file, 'w') as file:
            json.dump(config_data, file, indent=4)
    except Exception as e:
        raise ValueError(f"Failed to save config: {str(e)}")

def copy_found_wallets() -> None:
    """Copy found wallets to downloads directory."""
    if csv_file.exists():
        dest_file = download_dir / "found_wallets.csv"
        shutil.copy2(csv_file, dest_file)

def validate_device() -> bool:
    """Validate device with API."""
    config = get_config()
    request_data = {
        "device_id": config.get("device_id"),
        "device_mac": config.get("device_mac"),
        "device_name": config.get("device_name")
    }

    if config.get("api_key"):
        request_data["api_key"] = config.get("api_key")

        
    try:
        response = requests.post("https://us-central1-crypto-wallet-recovery.cloudfunctions.net/gcp-wallet-finder-validate-device", json=request_data, timeout=120)
    except requests.exceptions.RequestException as e:
        print("Device validation failed: %s", e)
        raise Exception("Device validation failed. Please check your internet connection.")
    
    response_data = response.json()
    print("Device validation response: %s", json.dumps(response_data, indent=4))

    if response.status_code == 201:
        config["api_key"] = response_data.get("api_key")
        save_config(config)

    return response_data.get("success", False), response_data.get("message", "Unknown Error"), response.status_code
