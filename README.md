# Blockchain Data Indexing Project

## Project Overview
This project started with the goal of indexing blockchain data across multiple chains (Ethereum and Base) for various data points including:
- First Transaction timestamps
- ETH Balances
- Outgoing Transactions
- Active Smart Contracts
- Contracts Deployed (Mainnet)
- Contracts Deployed (Testnet)
- Primary ENS Domain
- ENS Account Age

## Current Scope (MVP)
For the MVP phase, we've narrowed down the scope to focus on:
- Single Chain: Ethereum Mainnet
- Single Data Point: Contract Deployments
- Time Range: Last 1000 blocks
- Output Format: CSV file

## Implementation
The project consists of one main component:

### 1. Contract Scanner (`contract_scanner.py`)
- Scans the last 1000 blocks on Ethereum
- Identifies contract creation transactions
- Stores relevant data in CSV format including:
  - Block Number
  - Transaction Hash
  - Contract Address
  - Creator Address
  - Timestamp
  - Gas Used

## How Contract Creation is Identified
A transaction is identified as a contract creation when:
1. The transaction's `to` address is `None`
2. The transaction receipt contains a `contractAddress`

## Setup and Requirements
1. Python 3.9+
2. Required packages (install via pip):
   ```
   pip install -r requirements.txt
   ```
3. Environment Variables:
   - Create a `.env` file
   - Add your Ethereum node provider API key:
     ```
     ALCHEMY_API_KEY=your_api_key_here
     ```

## Usage
To scan for contract creations:
```bash
python3 contract_scanner.py
```

The script will:
1. Connect to Ethereum mainnet
2. Scan the last 1000 blocks
3. Identify contract creation transactions
4. Save the results to `contract_creations.csv`

## Future Scope
Future iterations could include:
1. Adding Base chain support
2. Implementing ENS event tracking
3. Real-time indexing
4. Database storage (e.g., Supabase)
5. Additional data points from the original scope

## Notes
- The current implementation uses CSV for simplicity
- Rate limiting depends on your Ethereum node provider
- Block range (1000) was chosen for MVP testing purposes 