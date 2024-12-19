"""
GUI implementation for the wallet finder application.
"""

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
config = get_config()

class WalletFinderGUI:
    """
    Graphical user interface for the wallet finder application.
    """
    def __init__(self, tk_root: Tk) -> None:
        """Initialize the GUI with the given Tkinter root."""
        logger.info('TKInter Version: %s', tk.TkVersion)

        self.root = tk_root
        self.root.title("Wallet Finder")
        self.root.geometry("1000x500")
        
        self.addresses = set()
        self.result_list = []
        self.wordlist = []
        
        self._create_widgets()
        self._create_menu()
        
    def _create_widgets(self):
        """Create and arrange GUI widgets."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create and configure grid
        for i in range(4):
            main_frame.grid_columnconfigure(i, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        
        # Add widgets
        self._add_address_entry(main_frame)
        self._add_buttons(main_frame)
        self._add_status_display(main_frame)
        self._add_result_display(main_frame)
        
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Wordlist", command=self._load_wordlist)
        file_menu.add_command(label="Export Results", command=self._export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
    def _add_address_entry(self, parent):
        """Add address entry widgets."""
        ttk.Label(parent, text="Enter Target Address:").grid(row=0, column=0, sticky=tk.W)
        self.address_entry = ttk.Entry(parent)
        self.address_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E))
        ttk.Button(parent, text="Add", command=self._add_address).grid(row=0, column=3)
        
    def _add_buttons(self, parent):
        """Add control buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=1, column=0, columnspan=4, pady=5)
        
        ttk.Button(button_frame, text="Start", command=self._start_processing).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Resume", command=self._resume_processing).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Stop", command=self._stop_processing).pack(side=tk.LEFT, padx=5)
        
    def _add_status_display(self, parent):
        """Add status display widgets."""
        ttk.Label(parent, text="Status:").grid(row=2, column=0, sticky=tk.W)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(parent, textvariable=self.status_var).grid(row=2, column=1, columnspan=3, sticky=tk.W)
        
    def _add_result_display(self, parent):
        """Add result display widgets."""
        self.result_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=10)
        self.result_text.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def _add_address(self):
        """Add a new target address."""
        address = self.address_entry.get().strip()
        if address:
            self.addresses.add(address)
            self.address_entry.delete(0, tk.END)
            self._update_result_display(f"Added address: {address}")
            
    def _load_wordlist(self):
        """Load wordlist from file."""
        filename = filedialog.askopenfilename(
            title="Select Wordlist File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.wordlist = load_wordlist(filename)
                self._update_status(f"Loaded wordlist from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load wordlist: {str(e)}")
                
    def _export_results(self):
        """Export results to CSV file."""
        try:
            copy_found_wallets()
            messagebox.showinfo("Success", "Results exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export results: {str(e)}")
            
    def _start_processing(self):
        """Start wallet finding process."""
        if not self.addresses:
            messagebox.showerror("Error", "Please add at least one target address.")
            return
            
        if not self.wordlist:
            messagebox.showerror("Error", "Please load a wordlist first.")
            return
            
        if not validate_device():
            messagebox.showerror("Error", "Device validation failed.")
            return
            
        threading.Thread(target=self._process_wallets, args=(False,), daemon=True).start()
        
    def _resume_processing(self):
        """Resume wallet finding process."""
        if not validate_device():
            messagebox.showerror("Error", "Device validation failed.")
            return
            
        threading.Thread(target=self._process_wallets, args=(True,), daemon=True).start()
        
    def _process_wallets(self, resume: bool):
        """Process wallet addresses in a separate thread."""
        try:
            WalletFinder.start(
                self.wordlist,
                self.addresses,
                self._update_status,
                self._update_result_display,
                resume
            )
        except Exception as e:
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
            
    def _stop_processing(self):
        """Stop wallet finding process."""
        # Implementation depends on how we want to handle process termination
        pass
        
    def _update_status(self, message: str):
        """Update status display."""
        self.status_var.set(message)
        
    def _update_result_display(self, message: str):
        """Update result display."""
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
