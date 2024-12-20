"""
Core functionality for wallet finding operations.
"""

import os
import csv
import types
import itertools
import multiprocessing
from pathlib import Path
from more_itertools import chunked
from .crypto_wallet import CryptoWallet

from .utils import logger_config, get_config, save_config

logger = logger_config()
app_data_dir = Path.home() / '.wallet_finder'
csv_file = app_data_dir / "found_wallets.csv"
config_file = app_data_dir / "config.json"

class WalletFinder:
    """
    Core wallet finding implementation using parallel processing.

    This class handles the generation and testing of wallet seed phrases using
    multiprocessing for optimal performance. It processes permutations of seed
    phrases in parallel, checking each generated wallet address against a set
    of target addresses.

    The class is designed to:
        - Utilize all available CPU cores efficiently
        - Process seed phrases in optimized chunks
        - Save progress periodically
        - Report results through callback functions

    Note:
        All methods in this class are static as it serves as a utility class
        rather than maintaining instance state.
    """

    def __init__(self):
        """
        Initialize the wallet finder.

        This method initializes the wallet finder by creating the CSV file
        for storing found wallets if it does not exist.
        """
        if not os.path.exists(csv_file):
            with open(csv_file, mode="w", newline="", encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Seed Phrase", "TRX Address"])

    @staticmethod
    def process(seeds: list[str], target_address: set) -> tuple[bool, list]:
        """
        Generate a wallet address from the given seed phrase and check if it matches the target address.

        Args:
            seeds (list[str]): List of words forming the seed phrase
            target_address (set): Set of target wallet addresses to match against

        Returns:
            tuple[bool, list]: A tuple containing:
                - bool: True if the generated address matches any target address, False otherwise
                - list: [seed_phrase, address] if match found, [None, None] otherwise
        """
        seeds = " ".join(map(lambda x: x.lower().strip(), seeds))
        try:
            wallet = CryptoWallet(seeds)
            address = wallet.get_trx_address()
            if str(address) in target_address:
                return True, [seeds, address]
            
        except Exception as e:
            # Don't need to log the exception if exception is value error
            if not isinstance(e, ValueError):
                print(e)

        return False, [None, None]

    @staticmethod
    def start(wordlist: list[str], target_address: list[str], update_status_func: types.FunctionType, update_list_func: types.FunctionType, resume: bool = False) -> None:
        """
        Start the wallet finding process using multiprocessing.

        This function:
        1. Generates permutations of the wordlist
        2. Processes chunks of permutations in parallel
        3. Updates GUI with progress and found wallets
        4. Saves progress and found wallets to disk

        Args:
            update_status_func (types.FunctionType): Callback to update status in GUI
            update_list_func (types.FunctionType): Callback to update found wallets list in GUI
            resume (bool, optional): If True, resumes from last saved progress. Defaults to False.

        Note:
            - Uses multiprocessing for parallel processing
            - Saves progress every 10 chunks
            - Writes found wallets to CSV file immediately
        """
        num_processes = multiprocessing.cpu_count()
        config = get_config()

        combinations = itertools.permutations(wordlist, 12)
        start_from = config["progress"] if resume else 0

        logger.info('Starting Process...')
        update_status_func('Starting Process...')

        if not resume:
            # Delete the old csv file and create a new one
            with open(csv_file, mode="w", newline="", encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Seed Phrase", "TRX Address"])


        # Parallel processing
        with multiprocessing.Pool(processes=num_processes) as pool:
            chunk_size = num_processes * 1000  # Adjust as per system resources

            # Process in chunks
            for index, chunk in enumerate(chunked(itertools.islice(combinations, start_from, None), chunk_size), start=int(start_from / chunk_size) - 1):
                process_count = (index + 1) * chunk_size
                update_status_func(f'Checking Wallet: {"{:,}".format(process_count)}\t({num_processes} cores)')
                results: AsyncResult = pool.starmap_async(WalletFinder.process, [(seeds, target_address) for seeds in chunk])

                results.wait()
                process_results = results.get()
                for success, [seeds, address] in process_results:
                    if not success:
                        continue

                    logger.info(f"Found address: {address} with seed: {seeds}")
                    with open(csv_file, mode="a", newline="", encoding='utf-8') as file:
                        csv_writer = csv.writer(file)
                        csv_writer.writerow([seeds, address])
                    update_list_func(seeds, address)

                # Update config progress value
                if index % 10 == 0:
                    config["progress"] = (index + 1) * chunk_size
                    save_config(config)
