"""
Cryptocurrency Wallet Seed Finder Package

This package implements a parallel processing system to find cryptocurrency wallet seeds
by generating and testing permutations of seed phrases.
"""

from .core import WalletFinder
from .gui import WalletFinderGUI
from .utils import logger_config, load_wordlist, get_config, save_config, validate_device

__version__ = "1.0.0"
__all__ = ['WalletFinder', 'WalletFinderGUI', 'logger_config', 'load_wordlist', 
           'get_config', 'save_config', 'validate_device']
