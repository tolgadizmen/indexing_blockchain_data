import os
import csv
import time
import logging
from web3 import Web3
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('contract_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
base_rpc_url = os.getenv("BASE_MAINNET_RPC_URL")

if not base_rpc_url:
    logger.error("BASE_MAINNET_RPC_URL not found in environment variables")
    exit(1)

w3 = Web3(Web3.HTTPProvider(base_rpc_url))

# Rate limiting configuration
RATE_LIMIT_DELAY = 0.5  # 500ms between requests
MAX_RETRIES = 5
INITIAL_BACKOFF = 2  # Initial backoff time in seconds
MAX_BACKOFF = 32  # Maximum backoff time in seconds

# Base-specific addresses
BASE_BUNDLER = '0x4200000000000000000000000000000000000015'
BASE_SEQUENCER = '0x4200000000000000000000000000000000000010'

def check_rpc_connection() -> bool:
    """
    Check if the connection to Base Mainnet RPC is successful.
    
    Returns:
        bool: True if connected successfully, False otherwise
    """
    try:
        if not w3.is_connected():
            logger.error("Failed to connect to Base Mainnet RPC")
            return False
        logger.info("Successfully connected to Base Mainnet RPC")
        return True
    except Exception as e:
        logger.error(f"Error connecting to Base Mainnet RPC: {str(e)}")
        return False

def make_rpc_request(func, *args, **kwargs):
    """
    Make an RPC request with rate limiting and exponential backoff.
    
    Args:
        func: The RPC function to call
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        The result of the RPC call
    """
    backoff_time = INITIAL_BACKOFF
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(RATE_LIMIT_DELAY)
            return func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"Rate limit hit (attempt {attempt + 1}/{MAX_RETRIES}), waiting {backoff_time} seconds...")
                    time.sleep(backoff_time)
                    backoff_time = min(backoff_time * 2, MAX_BACKOFF)  # Exponential backoff with cap
                    continue
            elif "Connection" in str(e):
                logger.warning(f"Connection error (attempt {attempt + 1}/{MAX_RETRIES}), retrying...")
                time.sleep(backoff_time)
                backoff_time = min(backoff_time * 2, MAX_BACKOFF)
                continue
            logger.error(f"RPC request failed: {str(e)}")
            return None
    logger.error(f"Max retries ({MAX_RETRIES}) exceeded")
    return None

def analyze_transaction(tx_hash: str) -> Dict[str, Any]:
    """
    Analyze a single transaction.
    
    Args:
        tx_hash (str): Transaction hash
        
    Returns:
        dict: Transaction details
    """
    try:
        tx = make_rpc_request(w3.eth.get_transaction, tx_hash)
        if not tx:
            return None
            
        tx_receipt = make_rpc_request(w3.eth.get_transaction_receipt, tx_hash)
        if not tx_receipt:
            return None
        
        # Determine transaction type
        tx_type = "normal"
        if tx['to'] == BASE_BUNDLER:
            tx_type = "bundled"
        elif tx['to'] == BASE_SEQUENCER:
            tx_type = "sequencer"
        elif not tx['to']:
            tx_type = "contract_creation"
        
        return {
            'tx_hash': tx_hash,
            'from': tx['from'],
            'to': tx['to'] if tx['to'] else 'Contract Creation',
            'value': tx['value'],
            'gas_price': tx['gasPrice'],
            'gas_used': tx_receipt['gasUsed'],
            'status': tx_receipt['status'],
            'contract_address': tx_receipt['contractAddress'] if tx_receipt['contractAddress'] else None,
            'logs_count': len(tx_receipt['logs']),
            'tx_type': tx_type
        }
    except Exception as e:
        logger.error(f"Error analyzing transaction {tx_hash}: {str(e)}")
        return None

def get_block_data(block_number: int) -> Dict[str, Any]:
    """
    Fetch and process data for a specific block.
    
    Args:
        block_number (int): The block number to fetch
        
    Returns:
        dict: Block data including timestamp and transaction count
    """
    try:
        block = make_rpc_request(w3.eth.get_block, block_number, full_transactions=True)
        if not block:
            logger.error(f"Failed to fetch block {block_number}")
            return None
        
        # Analyze transactions
        transactions = []
        tx_type_counts = {
            'normal': 0,
            'bundled': 0,
            'sequencer': 0,
            'contract_creation': 0
        }
        
        # Process transactions in batches to avoid overwhelming the RPC
        batch_size = 10
        for i in range(0, len(block.transactions), batch_size):
            batch = block.transactions[i:i + batch_size]
            for tx in batch:
                tx_data = analyze_transaction(tx.hash.hex())
                if tx_data:
                    transactions.append(tx_data)
                    tx_type_counts[tx_data['tx_type']] += 1
            # Add a small delay between batches
            time.sleep(RATE_LIMIT_DELAY * 2)
        
        return {
            'block_number': block_number,
            'timestamp': block.timestamp,
            'datetime': datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            'tx_count': len(block.transactions),
            'normal_tx_count': tx_type_counts['normal'],
            'bundled_tx_count': tx_type_counts['bundled'],
            'sequencer_tx_count': tx_type_counts['sequencer'],
            'contract_creation_count': tx_type_counts['contract_creation'],
            'gas_used': block.gasUsed,
            'gas_limit': block.gasLimit,
            'base_fee_per_gas': block.baseFeePerGas if hasattr(block, 'baseFeePerGas') else None,
            'hash': block.hash.hex(),
            'transactions': transactions
        }
    except Exception as e:
        logger.error(f"Error fetching block {block_number}: {str(e)}")
        return None

def save_to_csv(data: List[Dict[str, Any]], filename: str = 'block_data.csv'):
    """
    Save block data to a CSV file.
    
    Args:
        data (list): List of block data dictionaries
        filename (str): Name of the output CSV file
    """
    try:
        if not data:
            logger.warning("No data to save to CSV")
            return

        # Prepare data for CSV (excluding full transaction details)
        csv_data = []
        for block in data:
            csv_block = {
                'block_number': block['block_number'],
                'timestamp': block['timestamp'],
                'datetime': block['datetime'],
                'tx_count': block['tx_count'],
                'normal_tx_count': block['normal_tx_count'],
                'bundled_tx_count': block['bundled_tx_count'],
                'sequencer_tx_count': block['sequencer_tx_count'],
                'contract_creation_count': block['contract_creation_count'],
                'gas_used': block['gas_used'],
                'gas_limit': block['gas_limit'],
                'base_fee_per_gas': block['base_fee_per_gas'],
                'hash': block['hash']
            }
            csv_data.append(csv_block)

        fieldnames = csv_data[0].keys()
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.isfile(filename)
        
        mode = 'a' if file_exists else 'w'
        with open(filename, mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write headers only if creating a new file
            if not file_exists:
                writer.writeheader()
            
            writer.writerows(csv_data)
            
        logger.info(f"Successfully saved {len(data)} blocks to {filename}")
        
        # Save detailed transaction data to a separate file
        tx_filename = 'transaction_details.csv'
        if data[0]['transactions']:
            tx_fieldnames = data[0]['transactions'][0].keys()
            tx_file_exists = os.path.isfile(tx_filename)
            
            with open(tx_filename, 'a' if tx_file_exists else 'w', newline='') as txfile:
                writer = csv.DictWriter(txfile, fieldnames=tx_fieldnames)
                if not tx_file_exists:
                    writer.writeheader()
                
                for block in data:
                    writer.writerows(block['transactions'])
            
            logger.info(f"Successfully saved transaction details to {tx_filename}")
            
    except Exception as e:
        logger.error(f"Error saving to CSV: {str(e)}")

def main():
    """
    Main function to scan the latest block on Base Mainnet.
    Fetches the most recent block and saves its details to CSV files.
    """
    if not check_rpc_connection():
        exit(1)

    try:
        latest_block = make_rpc_request(w3.eth.get_block, 'latest').number
        logger.info(f"Fetching latest block from Base Mainnet (block number: {latest_block})")
        
        block_data = get_block_data(latest_block)
        if block_data:
            logger.info(
                f"Block {block_data['block_number']}: "
                f"Timestamp={block_data['datetime']}, "
                f"TotalTx={block_data['tx_count']}, "
                f"NormalTx={block_data['normal_tx_count']}, "
                f"BundledTx={block_data['bundled_tx_count']}, "
                f"SequencerTx={block_data['sequencer_tx_count']}, "
                f"ContractCreations={block_data['contract_creation_count']}, "
                f"GasUsed={block_data['gas_used']}"
            )
            # Save the collected data to CSV
            save_to_csv([block_data])
        else:
            logger.error("Failed to fetch block data")
            exit(1)
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 