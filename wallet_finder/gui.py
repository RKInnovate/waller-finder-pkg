"""
GUI implementation for the wallet finder application.
"""

import re
import os
import sys
import threading
import tkinter as tk
from tkinter import Tk, ttk, scrolledtext, filedialog, messagebox
from pathlib import Path

from .core import WalletFinder
from .utils import logger_config, load_wordlist, get_config, save_config, copy_found_wallets, validate_device

logger = logger_config()
app_data_dir = Path.home() / '.wallet_finder'

class WalletFinderGUI:
    """
    Graphical user interface for the wallet finder application.

    This class provides a Tkinter-based GUI that allows users to:
        - Input target wallet addresses
        - Select wordlist files
        - Monitor processing progress
        - View found wallet addresses in real-time
        - Save and resume progress

    The GUI is designed to remain responsive during intensive processing by
    using separate threads for UI updates and background processing.

    Attributes:
        root (Tk): The main Tkinter window
        addresses (set): Set of target wallet addresses to search for
        result_list (list): List to store found wallet results
    """
    def __init__(self, tk_root: Tk) -> None:
        """
        Initializes the WalletFinderGUI with the given Tkinter root and config.

        Args:
            root (Tk): The Tkinter root window.
        """
        global target_address, wordlist

        logger.info('TKInter Version: %s', tk.TkVersion)

        self.root = tk_root
        self.root.title("Wallet Finder")
        self.root.geometry("1000x500")
        self.config = get_config()

        # Set window icon
        try:
            # For packaged app
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, 'icon.png')
            if os.path.exists(icon_path):
                icon_img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon_img)
        except Exception as e:
            logger.error(f"Failed to set window icon: {e}")

        self.result_list = []  # List to store results (seed, address)
        
        self.addresses = set(self.config.get("addresses", []))
        target_address = self.addresses

        wordlist = load_wordlist(self.config.get("wordlist_file")) if self.config.get("wordlist_file") else []
        self.create_widgets()

    def create_widgets(self):
        """
        Creates the UI widgets for the application, including buttons for adding
        addresses, selecting the wordlist file, displaying the listbox for results,
        and status bar.
        """

        # Add Address Button
        self.add_address_button = tk.Button(self.root, text="Edit Addresses" if len(self.addresses) > 0 else "Add Addresses", command=self.add_addresses)
        self.add_address_button.pack(pady=10)

        wordlist_file = self.config.get("wordlist_file")

        # Select Wordlist File Button
        self.select_wordlist_button = tk.Button(self.root, text="Select Wordlist File" if not wordlist_file else "Change Wordlist File", command=self.select_wordlist_file)
        self.select_wordlist_button.pack(pady=10)

        # Status Bar
        self.status_label = tk.Label(self.root, text="Status: Idle", anchor="w", relief="sunken", bd=1)
        self.status_label.pack(fill=tk.X, padx=10, pady=(5, 0))
        
        # Listbox to display results (seed, address)
        self.result_listbox = ttk.Treeview(self.root, columns=("Seed", "Address"), show="headings")
        self.result_listbox.heading("Seed", text="Seed Phrase")
        self.result_listbox.heading("Address", text="TRX Address")
        self.result_listbox.pack(pady=(0, 20), padx=10, fill=tk.BOTH, expand=True)
        
        # Start and Stop Buttons
        self.start_button = tk.Button(self.root, text="Start", command=self.start_process)
        self.start_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.stop_button = tk.Button(self.root, text="Quit", command=self.quit)
        self.stop_button.pack(side=tk.RIGHT, padx=20, pady=10)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def add_addresses(self):
        """
        Opens a new window where the user can input wallet addresses manually.
        These addresses are converted into a list and displayed in the main window.
        """
        # Create a new window to input addresses
        address_window = tk.Toplevel(self.root)
        address_window.title("Enter TRX Addresses")
        address_window.geometry("300x400")

        # Create a scrolled text box for addresses input
        address_textbox = scrolledtext.ScrolledText(address_window, wrap=tk.WORD, width=35, height=25)
        address_textbox.pack(pady=10)

        if self.addresses:
            address_textbox.insert(tk.INSERT, "\n".join(self.addresses))

        # Create a button to convert addresses to list
        def convert_addresses():
            """
            Converts the addresses entered in the textbox into a list and
            updates the main window's result listbox.
            """
            global target_address

            addresses_str = address_textbox.get("1.0", tk.END).strip()
            
            if ',' in addresses_str:
                addresses = addresses_str.split(',')
            else:
                addresses = addresses_str.splitlines()

            addresses = [re.sub(r'[,"\'\s]', '', address) for address in addresses if address.strip()]  # Clean and split
            self.addresses = set(addresses)
            self.config["addresses"] = list(self.addresses)
            save_config(self.config)
            target_address = self.addresses
            self.add_address_button.config(text="Edit Addresses")
            address_window.destroy()

        convert_button = tk.Button(address_window, text="Add", command=convert_addresses)
        convert_button.pack(pady=10)

    def safe_update_listbox(self, seed, address):
        """
        Safely updates the listbox in the main thread using the `after` method.
        This ensures thread-safety when updating the GUI from a background thread.

        Args:
            seed (str): The seed phrase corresponding to the address.
            address (str): The wallet address to be displayed.
        """
        self.root.after(0, self._update_listbox, seed, address)

    def _update_listbox(self, seed, address):
        """
        Updates the listbox widget with a new seed phrase and address.

        Args:
            seed (str): The seed phrase to be inserted into the listbox.
            address (str): The wallet address to be inserted into the listbox.
        """
        self.result_listbox.insert("", "end", values=(seed, address))

    def select_wordlist_file(self):
        """
        Opens a file dialog to allow the user to select a wordlist file for wallet recovery.
        The selected file path is stored in the config instance.

        Raises:
            messagebox: Displays an informational message if a file is selected, or a warning if no file is selected.
        """
        global wordlist
        # Open a file dialog to select the wordlist file
        file_path = filedialog.askopenfilename(title="Select Wordlist File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))

        if file_path:
            wordlist = load_wordlist(file_path)
            self.config["wordlist_file"] = file_path
            save_config(self.config)
        else:
            messagebox.showwarning("No File", "No file was selected!")

    def start_process(self):
        """
        Starts the wallet recovery process in a new thread. This simulates a long-running process
        and updates the status bar and result listbox as new addresses are found.

        This method creates a new thread to run the `run_process` method, allowing the GUI to remain responsive.
        """
        self.update_status("Processing...")
        thread = threading.Thread(target=self.run_process, daemon=True)
        thread.start()

    def run_process(self):
        """
        Simulates a long-running process (e.g., wallet recovery). This is a placeholder method
        and should be replaced with actual wallet recovery logic.

        The method runs in a separate thread to avoid freezing the UI, and updates the status
        and result listbox during the process.
        """
        global wordlist, target_address
        resume = False

        try:
            # Validate the device with the API key
            success, status, status_code = validate_device()
            self.config = get_config()
            if not success or status_code != 200:
                messagebox.showerror("Device Validation Failed", f"Device validation failed with status: {status}")
                self.update_status(f"Device validation failed with status: {status}")
                return
        
        except Exception as e:
            messagebox.showerror("Device Validation Error", f"Device validation failed: {e}")
            self.update_status(f"Device validation failed: {e}")
            return

        if not wordlist and self.config.get("wordlist_file"):
            wordlist = load_wordlist(self.config.get("wordlist_file"))

        if not wordlist:
            messagebox.showerror("No Wordlist", "No wordlist file selected!")
            self.update_status("No wordlist file selected!")
            return

        if not target_address:
            messagebox.showwarning("No Address", "No TRX address added! Please add an address.")
            self.update_status("No TRX address added! Please add an address.")
            return
        
        if self.config["progress"] > 0:
            resume = messagebox.askyesno("Progress", "Do you want to continue from the last progress?")

        # Initialize the WalletFinder instance
        finder = WalletFinder()

        finder.start(wordlist, self.addresses, self.update_status, self.safe_update_listbox, resume)

    def quit(self):
        """
        Exits the application gracefully by destroying the root window and quitting the main loop.
        """

        # copy the found wallets to the main csv file in download folder
        try:
            copy_found_wallets()
            messagebox.showinfo("Success", "Found wallets file has been saved to the download folder.")
        except ValueError:
            pass

        self.root.destroy()
        self.root.quit()
        exit(0)

    def update_status(self, status):
        """
        Updates the status bar with the provided status text. This method is thread-safe
        and ensures the GUI remains responsive during background processes.

        Args:
            status (str): The status message to be displayed on the status bar.
        """
        self.root.after(0, self._update_status, status)

    def _update_status(self, status):
        """
        Helper method that updates the status label widget with the given status text.

        Args:
            status (str): The status message to be displayed on the status label.
        """
        self.status_label.config(text=f"Status: {status}")
