import os
import logging
from web3 import Web3
from dotenv import load_dotenv

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

def get_block_data(block_number: int) -> dict:
    """
    Fetch and process data for a specific block.
    
    Args:
        block_number (int): The block number to fetch
        
    Returns:
        dict: Block data including timestamp and transaction count
    """
    try:
        block = w3.eth.get_block(block_number)
        return {
            'block_number': block_number,
            'timestamp': block.timestamp,
            'tx_count': len(block.transactions)
        }
    except Exception as e:
        logger.error(f"Error fetching block {block_number}: {str(e)}")
        return None

def main():
    """
    Main function to scan recent blocks on Base Mainnet.
    Fetches the last 10 blocks and logs their details.
    """
    if not check_rpc_connection():
        exit(1)

    try:
        latest_block = w3.eth.get_block('latest').number
        logger.info(f"Fetching last 10 blocks from Base Mainnet (latest block: {latest_block})")
        
        for block_number in range(latest_block - 9, latest_block + 1):
            block_data = get_block_data(block_number)
            if block_data:
                logger.info(
                    f"Block {block_data['block_number']}: "
                    f"Timestamp={block_data['timestamp']}, "
                    f"TxCount={block_data['tx_count']}"
                )
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 