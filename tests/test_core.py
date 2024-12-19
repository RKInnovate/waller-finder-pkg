"""Tests for the core wallet finder functionality."""

import pytest
from wallet_finder import WalletFinder

def test_process():
    """Test the process method with a sample seed phrase."""
    seeds = ["word1", "word2", "word3"]
    target_address = {"sample_address"}
    
    # Test with non-matching address
    success, result = WalletFinder.process(seeds, target_address)
    assert not success
    assert result == [None, None]

def test_start(monkeypatch):
    """Test the start method with mocked dependencies."""
    def mock_status(msg):
        assert isinstance(msg, str)
    
    def mock_list(seed, addr):
        assert isinstance(seed, str)
        assert isinstance(addr, str)
    
    # Mock process method to avoid actual crypto operations
    monkeypatch.setattr(
        WalletFinder,
        "process",
        lambda seeds, target: (False, [None, None])
    )
    
    wordlist = ["word1", "word2", "word3"]
    target_address = {"sample_address"}
    
    # Should not raise any exceptions
    WalletFinder.start(
        wordlist=wordlist,
        target_address=target_address,
        update_status_func=mock_status,
        update_list_func=mock_list,
        resume=False
    )
