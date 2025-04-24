from web3 import Web3
import csv
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Connect to Ethereum node
alchemy_url = f"https://eth-mainnet.g.alchemy.com/v2/{os.getenv('ALCHEMY_API_KEY')}"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

# Check connection
if not w3.is_connected():
    print("Failed to connect to Ethereum node")
    exit(1)

def scan_contract_creations(start_block, end_block):
    """Scan blocks for contract creation transactions"""
    contracts = []
    
    print(f"Scanning blocks from {start_block} to {end_block}")
    
    for block_number in range(start_block, end_block + 1):
        try:
            # Get block
            block = w3.eth.get_block(block_number, full_transactions=True)
            
            # Process each transaction in the block
            for tx in block.transactions:
                # Check if transaction creates a contract (to address is None)
                if tx.to is None:
                    # Get transaction receipt to get contract address
                    receipt = w3.eth.get_transaction_receipt(tx.hash)
                    if receipt.contractAddress:
                        contracts.append({
                            'block_number': block_number,
                            'tx_hash': tx.hash.hex(),
                            'contract_address': receipt.contractAddress,
                            'creator_address': tx['from'],
                            'timestamp': datetime.utcfromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                            'gas_used': receipt.gasUsed
                        })
            
            # Print progress every 100 blocks
            if (block_number - start_block) % 100 == 0:
                print(f"Processed block {block_number}")
                
        except Exception as e:
            print(f"Error processing block {block_number}: {str(e)}")
            continue
    
    return contracts

def save_to_csv(contracts, filename='contract_creations.csv'):
    """Save contract creation data to CSV"""
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Block Number', 'Transaction Hash', 'Contract Address', 
                        'Creator Address', 'Timestamp', 'Gas Used'])
        
        for contract in contracts:
            writer.writerow([
                contract['block_number'],
                contract['tx_hash'],
                contract['contract_address'],
                contract['creator_address'],
                contract['timestamp'],
                contract['gas_used']
            ])

def main():
    # Get latest block
    latest_block = w3.eth.get_block('latest').number
    start_block = latest_block - 1000
    
    print(f"Starting scan from block {start_block} to {latest_block}")
    
    # Scan for contract creations
    contracts = scan_contract_creations(start_block, latest_block)
    
    # Save to CSV
    save_to_csv(contracts)
    print(f"Found {len(contracts)} contract creations")
    print(f"Data saved to contract_creations.csv")

if __name__ == "__main__":
    main() 