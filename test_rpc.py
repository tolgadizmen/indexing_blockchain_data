import os
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
base_rpc_url = os.getenv("BASE_MAINNET_RPC_URL")

if not base_rpc_url:
    print("Error: BASE_MAINNET_RPC_URL not found in environment variables")
    exit(1)

print(f"Testing RPC URL: {base_rpc_url}")

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(base_rpc_url))

# Test connection
if w3.is_connected():
    print("Successfully connected to Base Mainnet RPC")
    
    # Get latest block number
    try:
        block_number = w3.eth.block_number
        print(f"Latest block number: {block_number}")
        
        # Get block details
        block = w3.eth.get_block(block_number)
        print(f"Block timestamp: {block.timestamp}")
        print(f"Number of transactions: {len(block.transactions)}")
        
    except Exception as e:
        print(f"Error getting block data: {str(e)}")
else:
    print("Failed to connect to Base Mainnet RPC") 