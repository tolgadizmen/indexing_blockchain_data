# Blockchain Data Indexing Tool

A Python-based tool for collecting and analyzing blockchain data from Base network.

## Current Version
- Tag: v1.1.0
- Last Updated: May 5, 2024
- Features:
  - Collects data from latest blocks on Base network
  - Analyzes different transaction types (normal, contract creation)
  - Implements rate limiting and error handling
  - Stores data in Supabase for efficient querying
  - Includes data validation and duplicate checking
  - Provides performance metrics and detailed logging

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

### Blocks Table
- `block_number` (primary key)
- `block_hash`
- `timestamp`
- `tx_count`

### Transactions Table
- `tx_hash`
- `block_number` (foreign key)
- `from_address`
- `to_address`
- `status`
- `contract_address`
- `logs_count`
- `tx_type`

## Usage
Run the script:
```bash
python3 contract_scanner.py
```

The script will:
1. Connect to Base Mainnet
2. Connect to Supabase
3. Scan the three most recent blocks
4. Store block and transaction data
5. Validate transaction counts
6. Log performance metrics

## Performance Metrics
- Average processing time per transaction: ~0.31 seconds
- Block processing time: ~40-50 seconds per block
- Transaction count per block: ~100-160 transactions

## Important Notes
- The script uses rate limiting to avoid RPC endpoint restrictions
- Data is validated to ensure consistency
- Duplicate blocks are automatically skipped
- All changes are tracked in Git with version tags
- Performance metrics help identify bottlenecks

## To Return to This Version
```bash
git checkout v1.1.0
``` 