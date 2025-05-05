import os
import time
import logging
from web3 import Web3
from dotenv import load_dotenv
from database import store_block_data, store_transaction_data, test_connection, get_existing_block

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Web3 with RPC URL from environment variables
rpc_url = os.getenv("BASE_MAINNET_RPC_URL")
if not rpc_url:
    logger.error("BASE_MAINNET_RPC_URL not found in environment variables")
    exit(1)

logger.info(f"Using RPC URL: {rpc_url}")
w3 = Web3(Web3.HTTPProvider(rpc_url))

def get_block_data(block_number):
    """
    Get block data and format it for database storage
    """
    block = w3.eth.get_block(block_number, full_transactions=True)
    
    # Format block data
    block_data = {
        "block_number": block.number,
        "block_hash": f"0x{block.hash.hex()}",
        "timestamp": block.timestamp,
        "tx_count": len(block.transactions)
    }
    
    return block_data, block.transactions

def analyze_transaction(tx, block_number):
    """
    Analyze transaction and format it for database storage
    """
    tx_hash = f"0x{tx.hash.hex()}"
    
    # Get transaction receipt
    receipt = w3.eth.get_transaction_receipt(tx_hash)
    
    # Format transaction data
    tx_data = {
        "tx_hash": tx_hash,
        "block_number": block_number,
        "from_address": tx["from"],
        "to_address": tx["to"],
        "status": receipt.status,
        "contract_address": receipt.contractAddress,
        "logs_count": len(receipt.logs),
        "tx_type": "contract_creation" if receipt.contractAddress else "normal"
    }
    
    return tx_data

def validate_block_data(block_number, expected_tx_count, actual_tx_count):
    """
    Validate that the number of transactions stored matches the block's transaction count
    """
    if expected_tx_count != actual_tx_count:
        logger.warning(f"Transaction count mismatch for block {block_number}: expected {expected_tx_count}, got {actual_tx_count}")
        return False
    return True

def main():
    """
    Main function to process blocks and store data in Supabase
    """
    # Test database connection
    if not test_connection():
        logger.error("Failed to connect to Supabase. Exiting...")
        return
    
    # Get latest block number
    latest_block = w3.eth.block_number
    logger.info(f"Latest block number: {latest_block}")
    
    # Process 3 blocks
    total_transactions = 0
    start_time = time.time()
    
    for i in range(3):
        block_number = latest_block - i
        block_start_time = time.time()
        
        # Check if block already exists
        if get_existing_block(block_number):
            logger.info(f"Block {block_number} already exists in database, skipping...")
            continue
        
        logger.info(f"Processing block {block_number}")
        
        # Get block data
        block_data, transactions = get_block_data(block_number)
        expected_tx_count = len(transactions)
        
        # Store block data
        block_result = store_block_data(block_data)
        if not block_result:
            logger.error(f"Failed to store block {block_number}")
            continue
        
        # Process transactions
        stored_tx_count = 0
        for tx in transactions:
            tx_data = analyze_transaction(tx, block_number)
            tx_result = store_transaction_data(tx_data)
            if tx_result:
                stored_tx_count += 1
            else:
                logger.error(f"Failed to store transaction {tx_data['tx_hash']}")
        
        # Validate transaction count
        if not validate_block_data(block_number, expected_tx_count, stored_tx_count):
            logger.error(f"Transaction count validation failed for block {block_number}")
        
        total_transactions += stored_tx_count
        block_time = time.time() - block_start_time
        logger.info(f"Block {block_number} processed in {block_time:.2f} seconds")
        logger.info(f"Transactions in block: {stored_tx_count}")
    
    # Calculate and log performance metrics
    total_time = time.time() - start_time
    avg_time_per_tx = total_time / total_transactions if total_transactions > 0 else 0
    
    logger.info(f"Total processing time: {total_time:.2f} seconds")
    logger.info(f"Total transactions processed: {total_transactions}")
    logger.info(f"Average time per transaction: {avg_time_per_tx:.4f} seconds")

if __name__ == "__main__":
    main() 