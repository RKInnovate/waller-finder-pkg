"""Tests for utility functions."""

import os
import json
import pytest
from pathlib import Path
from wallet_finder.utils import (
    logger_config,
    load_wordlist,
    get_config,
    save_config,
    validate_device
)

@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file."""
    config_file = tmp_path / "config.json"
    original_config_file = Path.home() / '.wallet_finder' / "config.json"
    
    # Store original path
    old_path = os.environ.get('CONFIG_FILE')
    os.environ['CONFIG_FILE'] = str(config_file)
    
    yield config_file
    
    # Restore original path
    if old_path:
        os.environ['CONFIG_FILE'] = old_path
    else:
        del os.environ['CONFIG_FILE']

def test_logger_config():
    """Test logger configuration."""
    logger = logger_config()
    assert logger.name == "WalletFinder"
    assert logger.level == 20  # INFO level

def test_load_wordlist(tmp_path):
    """Test wordlist loading."""
    # Create a temporary wordlist file
    wordlist_file = tmp_path / "test_wordlist.txt"
    words = ["word1", "word2", "word3"]
    wordlist_file.write_text("\n".join(words))
    
    loaded_words = load_wordlist(str(wordlist_file))
    assert loaded_words == words

def test_get_config(temp_config_file):
    """Test config retrieval."""
    config = get_config()
    assert isinstance(config, dict)
    assert "progress" in config
    assert "api_key" in config
    assert "device_id" in config

def test_save_config(temp_config_file):
    """Test config saving."""
    test_config = {
        "progress": 100,
        "api_key": "test_key",
        "device_id": "test_id"
    }
    save_config(test_config)
    
    # Read the saved config
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
    
    assert saved_config == test_config

def test_validate_device(monkeypatch):
    """Test device validation with mocked API response."""
    class MockResponse:
        status_code = 200
    
    def mock_post(*args, **kwargs):
        return MockResponse()
    
    # Mock the requests.post function
    monkeypatch.setattr("requests.post", mock_post)
    
    assert validate_device() is True
