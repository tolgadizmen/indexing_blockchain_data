# Background and Motivation

This project aims to index blockchain data, focusing on Ethereum Mainnet contract deployments for the MVP. The goal is to provide a foundation for more advanced indexing and analytics across multiple chains and data points in the future.

## Original Project Overview
- Index blockchain data (Ethereum, Base)
- Data points: First Transaction timestamps, ETH Balances, Outgoing Transactions, Active Smart Contracts, Contracts Deployed (Mainnet/Testnet), Primary ENS Domain, ENS Account Age

## MVP Scope
- Single Chain: Ethereum Mainnet
- Single Data Point: Contract Deployments
- Time Range: Last 1000 blocks
- Output Format: CSV file

# Key Challenges and Analysis
- Efficiently scanning and processing large block ranges
- Identifying contract creation transactions accurately
- Handling rate limits from Ethereum node providers
- Ensuring data is saved reliably in CSV format

# High-level Task Breakdown
- [ ] Set up environment and dependencies
- [ ] Connect to Ethereum node
- [ ] Scan last 1000 blocks for contract creation transactions
- [ ] Identify contract creation transactions (to address is None, receipt has contractAddress)
- [ ] Save results to contract_creations.csv
- [ ] Document process and results

# Project Status Board
- [ ] Environment setup
- [ ] Node connection
- [ ] Block scanning
- [ ] Transaction identification
- [ ] Data export
- [ ] Documentation

# Executor's Feedback or Assistance Requests
- (To be filled during execution: blockers, questions, or requests for user input)

# Lessons
- (To be filled as issues are encountered and solved, or as best practices are established)

---

## Implementation Details (from original README)

### Contract Scanner (`contract_scanner.py`)
- Scans the last 1000 blocks on Ethereum
- Identifies contract creation transactions
- Stores relevant data in CSV format including:
  - Block Number
  - Transaction Hash
  - Contract Address
  - Creator Address
  - Timestamp
  - Gas Used

### How Contract Creation is Identified
A transaction is identified as a contract creation when:
1. The transaction's `to` address is `None`
2. The transaction receipt contains a `contractAddress`

### Setup and Requirements
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

### Usage
To scan for contract creations:
```bash
python3 contract_scanner.py
```

The script will:
1. Connect to Ethereum mainnet
2. Scan the last 1000 blocks
3. Identify contract creation transactions
4. Save the results to `contract_creations.csv`

### Future Scope
- Adding Base chain support
- Implementing ENS event tracking
- Real-time indexing
- Database storage (e.g., Supabase)
- Additional data points from the original scope

### Notes
- The current implementation uses CSV for simplicity
- Rate limiting depends on your Ethereum node provider
- Block range (1000) was chosen for MVP testing purposes 