# Crypto Wallet Finder

A Python package for finding cryptocurrency wallet seeds by generating and testing permutations of seed phrases. This tool uses parallel processing to efficiently search through possible combinations while providing a user-friendly GUI interface for monitoring progress.

## Features

- **Parallel Processing**: Utilizes all available CPU cores for efficient processing
- **User-Friendly GUI**: Monitor progress and results in real-time
- **Progress Management**: Automatic saving and resumption of search progress
- **Export Functionality**: Export found wallets to CSV format
- **Device Validation**: Secure API-based device validation system

## Installation

You can install the package directly from PyPI:

```bash
pip install crypto-wallet-finder
```

Or install from source:

```bash
git clone https://github.com/yourusername/wallet_finder.git
cd wallet_finder/package
pip install -e .
```

## Requirements

- Python 3.6 or higher
- Required packages (automatically installed):
  - requests>=2.25.0
  - more-itertools>=8.0.0
  - crypto-wallet>=1.0.0

## Usage

### GUI Application

Run the GUI application:

```bash
wallet-finder
```

Or use it in your Python code:

```python
from wallet_finder import WalletFinderGUI
import tkinter as tk

def main():
    root = tk.Tk()
    app = WalletFinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
```

### Core Functionality

Use the core functionality in your own code:

```python
from wallet_finder import WalletFinder

# Initialize with your wordlist and target addresses
wordlist = ["word1", "word2", ...]
target_addresses = {"address1", "address2"}

# Define callback functions
def status_callback(message):
    print(f"Status: {message}")

def result_callback(seed, address):
    print(f"Found: {address} with seed: {seed}")

# Start the search
WalletFinder.start(
    wordlist=wordlist,
    target_address=target_addresses,
    update_status_func=status_callback,
    update_list_func=result_callback
)
```

## Configuration

The package creates a configuration directory at `~/.wallet_finder` with:

- `config.json`: Stores progress and settings
- `found_wallets.csv`: Stores found wallet addresses
- `wallet_finder.log`: Application logs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

This tool is for educational purposes only. Always ensure you have the right to search for specific wallet addresses before using this tool.
