# Blockchain Data Indexing Tool

A Python-based tool for collecting and analyzing blockchain data from Base network.

## Current Version
- Tag: v1.0.0
- Last Updated: May 1, 2024
- Features:
  - Collects data from latest block on Base network
  - Analyzes different transaction types (normal, bundled, sequencer, contract creation)
  - Implements rate limiting and error handling
  - Saves data to CSV files

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
```

## Usage
Run the script:
```bash
python3 contract_scanner.py
```

## Output Files
- `block_data.csv`: Contains block-level statistics
- `transaction_details.csv`: Contains detailed transaction information
- `contract_scanner.log`: Contains execution logs

## Important Notes
- The script uses rate limiting to avoid RPC endpoint restrictions
- Data is collected in batches to manage memory usage
- All changes are tracked in Git with version tags

## To Return to This Version
```bash
git checkout v1.0.0
``` 