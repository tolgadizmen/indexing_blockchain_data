import os
import time
import logging
import asyncio
from web3 import Web3
from dotenv import load_dotenv
from database import store_transactions_batch, test_connection
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
log_filename = f"contract_scanner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_filename, mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Initialize Web3 with RPC URL from environment variables
rpc_url = os.getenv("BASE_MAINNET_RPC_URL")
if not rpc_url:
    logger.error("BASE_MAINNET_RPC_URL not found in environment variables")
    exit(1)

logger.info(f"Using RPC URL: {rpc_url}")
w3 = Web3(Web3.HTTPProvider(rpc_url))

# Configuration
BATCH_SIZE = 25  # Optimal batch size based on testing
RPC_LIMIT = 50  # Maximum requests per second allowed
RATE_LIMIT_DELAY = 1/RPC_LIMIT  # seconds between requests (0.02s for 50 RPS)
MAX_RETRIES = 3
INITIAL_BACKOFF = 1  # seconds
MAX_CONCURRENT_BATCHES = 8  # Number of transaction batches to process in parallel
PREFETCH_BLOCKS = 5  # Number of blocks to prefetch
RPC_BATCH_SIZE = 10  # Number of RPC requests to process in parallel

# RPC request tracking
last_request_time = 0
request_times = []  # Rolling window of request timestamps
REQUEST_WINDOW = 1.0  # 1 second window for rate limiting

# Block data cache
block_cache = {}
CACHE_SIZE = 20  # Maximum number of blocks to cache

async def track_request():
    """
    Track RPC request timing and ensure we don't exceed rate limits
    """
    global request_times
    current_time = time.time()
    
    # Remove old requests from the window
    request_times = [t for t in request_times if current_time - t < REQUEST_WINDOW]
    
    # If we're at the limit, wait until we have capacity
    while len(request_times) >= RPC_LIMIT:
        oldest_request = min(request_times)
        wait_time = REQUEST_WINDOW - (current_time - oldest_request)
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        current_time = time.time()
        request_times = [t for t in request_times if current_time - t < REQUEST_WINDOW]
    
    # Add current request
    request_times.append(current_time)
    return current_time

async def batch_rpc_requests(requests):
    """
    Process multiple RPC requests in parallel batches
    """
    results = []
    # Group requests into batches
    batches = [requests[i:i + RPC_BATCH_SIZE] for i in range(0, len(requests), RPC_BATCH_SIZE)]
    
    # Process batches concurrently
    for batch in batches:
        batch_results = await asyncio.gather(*batch)
        results.extend(batch_results)
    return results

async def get_transaction_receipts_batch(tx_hashes):
    """
    Get transaction receipts for multiple transactions using batch processing
    """
    async def get_receipt(tx_hash):
        retries = 0
        backoff = INITIAL_BACKOFF
        while retries < MAX_RETRIES:
            try:
                await track_request()
                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                receipt = await loop.run_in_executor(None, lambda: w3.eth.get_transaction_receipt(tx_hash))
                return receipt
            except Exception as e:
                retries += 1
                if retries == MAX_RETRIES:
                    logger.error(f"Failed to get receipt for {tx_hash} after {MAX_RETRIES} retries: {str(e)}")
                    return None
                else:
                    await asyncio.sleep(backoff)
                    backoff *= 2
    
    # Create tasks for all receipts
    receipt_tasks = [get_receipt(tx_hash) for tx_hash in tx_hashes]
    return await batch_rpc_requests(receipt_tasks)

async def prefetch_block_data(block_number):
    """
    Prefetch block data for upcoming blocks
    """
    if block_number in block_cache:
        return block_cache[block_number]
    
    await track_request()
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    block = await loop.run_in_executor(None, lambda: w3.eth.get_block(block_number, full_transactions=True))
    
    # Update cache
    if len(block_cache) >= CACHE_SIZE:
        # Remove oldest block from cache
        oldest_block = min(block_cache.keys())
        del block_cache[oldest_block]
    
    block_cache[block_number] = block
    return block

async def get_block_data(block_number):
    """
    Get block data with caching
    """
    if block_number in block_cache:
        return block_cache[block_number].transactions
    
    block = await prefetch_block_data(block_number)
    return block.transactions

def is_potential_contract_creation(tx):
    """
    Check if a transaction is potentially a contract creation
    """
    # Direct contract creation (to_address is null)
    if tx['to'] is None:
        return True
        
    # Check input data for contract creation patterns
    input_data = tx['input']
    if input_data and len(input_data) > 2:  # Ensure input exists and has content
        # Convert input to string if it's bytes
        if isinstance(input_data, bytes):
            input_data = input_data.hex()
        elif not input_data.startswith('0x'):
            input_data = '0x' + input_data
            
        # Common contract creation bytecode patterns
        creation_patterns = [
            '0x60806040',  # Common constructor bytecode
            '0x60606040',  # Another common pattern
        ]
        return any(input_data.startswith(pattern) for pattern in creation_patterns)
    
    return False

def confirm_contract_creation(receipt):
    """
    Confirm if a transaction actually created a contract
    """
    return receipt.contractAddress is not None

async def process_transactions_batch(transactions, block_number, block_timestamp):
    """
    Process a batch of transactions, but only for potential contract creations
    """
    batch_start_time = time.time()
    
    # Filter for potential contract creations
    potential_creations = [
        tx for tx in transactions 
        if is_potential_contract_creation(tx)
    ]
    
    if not potential_creations:
        return [], 0
    
    # Get receipts only for potential creations
    tx_hashes = [tx.hash for tx in potential_creations]
    receipts = await get_transaction_receipts_batch(tx_hashes)
    
    # Process only confirmed contract creations
    contract_data_list = []
    for tx, receipt in zip(potential_creations, receipts):
        if receipt and confirm_contract_creation(receipt):
            # Convert HexBytes to strings
            tx_hash = tx.hash.hex() if isinstance(tx.hash, (bytes, bytearray)) else str(tx.hash)
            # Convert Unix timestamp to ISO format
            creation_time = datetime.fromtimestamp(block_timestamp).isoformat()
            
            contract_data = {
                "tx_hash": f"0x{tx_hash}",
                "block_number": block_number,
                "creator_address": tx["from"],
                "contract_address": receipt.contractAddress,
                "creation_timestamp": creation_time,
                "init_code_hash": tx["input"].hex() if isinstance(tx["input"], (bytes, bytearray)) else str(tx["input"]),
                "gas_used": receipt.gasUsed,
                "status": receipt.status == 1,
                "logs_count": len(receipt.logs),
                "metadata": {}  # For future extensibility
            }
            contract_data_list.append(contract_data)
    
    batch_time = time.time() - batch_start_time
    return contract_data_list, batch_time

async def process_block(block_number):
    """
    Process a single block for contract creations
    """
    logger.info(f"Processing block {block_number}")
    block_start_time = time.time()
    
    # Get block data with prefetching
    block = await prefetch_block_data(block_number)
    transactions = block.transactions
    block_timestamp = block.timestamp
    
    # Quick pre-check for potential contract creations
    potential_creations = [tx for tx in transactions if is_potential_contract_creation(tx)]
    if not potential_creations:
        logger.info(f"Block {block_number} has no potential contract creations, skipping batch processing")
        block_time = time.time() - block_start_time
        logger.info(f"Block {block_number} processed in {block_time:.2f} seconds")
        return 0
    
    logger.info(f"Block {block_number} has {len(potential_creations)} potential contract creations")
    
    # Process transactions in parallel batches
    stored_contracts = 0
    total_batch_time = 0
    
    # Create batches
    batches = []
    for i in range(0, len(transactions), BATCH_SIZE):
        batches.append(transactions[i:i + BATCH_SIZE])
    
    # Process batches in parallel with a limit
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_BATCHES)
    async def process_batch_with_semaphore(batch):
        async with semaphore:
            return await process_transactions_batch(batch, block_number, block_timestamp)
    
    # Process all batches concurrently
    tasks = [process_batch_with_semaphore(batch) for batch in batches]
    results = await asyncio.gather(*tasks)
    
    # Combine all contract data
    all_contract_data = []
    for contract_data_list, batch_time in results:
        all_contract_data.extend(contract_data_list)
        total_batch_time += batch_time
    
    # Store all contract creations in a single bulk operation
    if all_contract_data:
        try:
            batch_result = store_transactions_batch(all_contract_data)
            if batch_result:
                stored_contracts = len(all_contract_data)
                logger.info(f"Successfully stored {stored_contracts} new contract creations from block {block_number}")
            else:
                # Check if it's a duplicate key error
                if "duplicate key value" in str(batch_result):
                    logger.info(f"Block {block_number} contract creations already exist in database - skipping")
                else:
                    logger.error(f"Failed to store contract creations for block {block_number}: {str(batch_result)}")
        except Exception as e:
            if "23505" in str(e):  # PostgreSQL duplicate key error
                logger.info(f"Block {block_number} contract creations already exist in database - skipping")
            else:
                logger.error(f"Error storing contract creations for block {block_number}: {str(e)}")
    
    block_time = time.time() - block_start_time
    avg_batch_time = total_batch_time / len(batches) if batches else 0
    
    logger.info(f"Block {block_number} processed in {block_time:.2f} seconds")
    logger.info(f"Average batch processing time: {avg_batch_time:.2f} seconds")
    logger.info(f"Contract creations found: {stored_contracts}")
    logger.info(f"Current RPC request rate: {len(request_times)} requests in last second")
    
    return stored_contracts

async def main():
    """
    Main function to process blocks and store contract creation data
    """
    # Test database connection
    if not test_connection():
        logger.error("Failed to connect to Supabase. Exiting...")
        return
    
    # Get latest block number
    await track_request()
    latest_block = w3.eth.block_number
    logger.info(f"Latest block number: {latest_block}")
    
    # Process blocks
    total_contracts = 0
    start_time = time.time()
    
    # Create tasks for processing blocks
    tasks = []
    BLOCKS_TO_PROCESS = 100
    first_block = latest_block - BLOCKS_TO_PROCESS + 1
    last_block = latest_block
    logger.info(f"Processing blocks from {first_block} to {last_block}")
    
    # Prefetch initial blocks
    prefetch_tasks = []
    for i in range(PREFETCH_BLOCKS):
        block_number = latest_block - i
        prefetch_tasks.append(prefetch_block_data(block_number))
    await asyncio.gather(*prefetch_tasks)
    
    for i in range(BLOCKS_TO_PROCESS):
        block_number = latest_block - i
        tasks.append(process_block(block_number))
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    total_contracts = sum(results)
    
    # Calculate and log performance metrics
    total_time = time.time() - start_time
    avg_time_per_contract = total_time / total_contracts if total_contracts > 0 else 0
    blocks_per_second = BLOCKS_TO_PROCESS / total_time
    contracts_per_second = total_contracts / total_time if total_contracts > 0 else 0
    
    # Log performance summary
    summary = [
        "=" * 50,
        "PERFORMANCE SUMMARY",
        "=" * 50,
        f"Block Range: {first_block} to {last_block}",
        f"Total Blocks Processed: {BLOCKS_TO_PROCESS}",
        f"Total Contract Creations: {total_contracts}",
        f"Total Processing Time: {total_time:.2f} seconds",
        f"Average Time per Contract: {avg_time_per_contract:.4f} seconds",
        f"Blocks Processed per Second: {blocks_per_second:.2f}",
        f"Contract Creations per Second: {contracts_per_second:.2f}",
        f"Log file created: {log_filename}",
        "=" * 50
    ]
    
    for line in summary:
        logger.info(line)
    
    # Ensure all logs are written to file
    for handler in logger.handlers:
        handler.flush()

if __name__ == "__main__":
    asyncio.run(main()) 