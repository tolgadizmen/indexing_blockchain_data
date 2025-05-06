# Blockchain Data Indexing Tool

A Python-based tool for collecting and analyzing blockchain data from Base network.

## Current Version
- Tag: v1.2.0
- Last Updated: May 5, 2024
- Features:
  - Collects data from latest blocks on Base network
  - Analyzes different transaction types (normal, contract creation)
  - Implements rate limiting and error handling
  - Stores data in Supabase for efficient querying
  - Includes data validation and duplicate checking
  - Provides performance metrics and detailed logging
  - Parallel processing with batching
  - Block data prefetching and caching
  - Quick contract creation detection
  - Comprehensive logging with timestamps

## Setup
1. Clone the repository:
```bash
git clone https://github.com/tolgadizmen/indexing_blockchain_data.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Create a `.env` file with:
```
BASE_MAINNET_RPC_URL=your_rpc_url_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

## Database Schema

### Contract Creations Table
- `tx_hash` (TEXT, primary key) - Transaction hash of the contract creation
- `block_number` (BIGINT) - Block number where the contract was created
- `creator_address` (TEXT) - Address of the contract creator
- `contract_address` (TEXT) - Address of the created contract
- `creation_timestamp` (TIMESTAMP) - When the contract was created
- `init_code_hash` (TEXT) - Hash of the contract's initialization code
- `gas_used` (BIGINT) - Amount of gas used for contract creation
- `status` (BOOLEAN) - Whether the transaction was successful
- `logs_count` (INTEGER) - Number of event logs emitted
- `metadata` (JSONB) - Additional metadata for future extensibility

## Usage
Run the script:
```bash
python3 contract_scanner.py
```

The script will:
1. Connect to Base Mainnet
2. Connect to Supabase
3. Scan the latest blocks in parallel
4. Store block and transaction data
5. Validate transaction counts
6. Log performance metrics

## Performance Metrics
- Average processing time per block: ~0.35 seconds
- Blocks processed per second: ~31.87
- Contract creations found: 6 per 100 blocks
- Contract creations per second: 1.91
- Average time per contract: 0.523 seconds
- RPC request rate: Up to 50 RPS
- Memory usage: Optimized for efficient processing
- Parallel processing: Up to 8 concurrent batches
- Transaction batching: 25 transactions per batch
- Block data prefetching: 5 blocks ahead
- Block data caching: 20 blocks

## Important Notes
- The script uses rate limiting to avoid RPC endpoint restrictions
- Data is validated to ensure consistency
- Duplicate blocks are automatically skipped
- All changes are tracked in Git with version tags
- Performance metrics help identify bottlenecks
- Parallel processing significantly improves performance
- Quick contract detection reduces processing time
- Comprehensive logging provides clear visibility

## To Return to This Version
```bash
git checkout v1.2.0
``` 