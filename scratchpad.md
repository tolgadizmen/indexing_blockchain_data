# Background and Motivation

This project aims to index relevant blockchain data, with a primary focus on reducing dependency on third-party indexing platforms (such as Blockscout, Alchemy, etc.). The long-term goal is to build and maintain our own indexing infrastructure, starting with the most relevant data for our needs and expanding over time.

## Updated Project Goal
- Index only the blockchain data relevant to our project, not all data.
- Gradually decrease reliance on external indexing services by building our own indexers.
- Step-by-step approach: start with a single, high-impact data type and expand coverage iteratively.

## First Milestone
- **Indexing Smart Contract Creation on Base Mainnet**
- Use a Base Mainnet RPC URL as the data source (can be from a provider or self-hosted in the future).

# Key Challenges and Analysis
- Understanding and adapting to the Base Mainnet (an EVM-compatible L2 network)
- Efficiently scanning and processing large block ranges
- Identifying contract creation transactions accurately (to address is None, receipt has contractAddress)
- Handling rate limits and reliability of the Base RPC endpoint
- Ensuring data is saved reliably in a chosen format (CSV, database, etc.)
- Laying the groundwork for future expansion to other data types and chains

# High-level Task Breakdown
- [ ] Set up environment and dependencies for Base Mainnet
- [ ] Obtain and configure a Base Mainnet RPC URL
- [ ] Connect to Base Mainnet using web3.py (or similar)
- [ ] Scan a defined block range for contract creation transactions
- [ ] Identify contract creation transactions (to address is None, receipt has contractAddress)
- [ ] Extract and store relevant data (block number, tx hash, contract address, creator, timestamp, gas used, etc.)
- [ ] Save results to a CSV file (or other storage as needed)
- [ ] Document process and results

# Project Status Board
- [ ] Environment setup for Base Mainnet
- [ ] RPC connection
- [ ] Block scanning
- [ ] Transaction identification
- [ ] Data export
- [ ] Documentation

# Executor's Feedback or Assistance Requests
- (To be filled during execution: blockers, questions, or requests for user input)

# Lessons
- (To be filled as issues are encountered and solved, or as best practices are established)

---

## Implementation Details (for Base Mainnet)

### Contract Scanner (`contract_scanner.py`)
- Scans a defined block range on Base Mainnet
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
   - Add your Base Mainnet RPC URL:
     ```
     BASE_MAINNET_RPC_URL=your_base_mainnet_rpc_url_here
     ```

### Usage
To scan for contract creations:
```bash
python3 contract_scanner.py
```

The script will:
1. Connect to Base Mainnet
2. Scan the defined block range
3. Identify contract creation transactions
4. Save the results to `contract_creations.csv`

### Future Scope
- Add support for other data types (transfers, ENS, etc.)
- Move to real-time indexing (websockets or polling)
- Store data in a database for advanced querying
- Run our own Base node to eliminate all third-party dependencies
- Expand to other chains as needed

### Notes
- The current implementation uses CSV for simplicity
- Rate limiting and reliability depend on your Base Mainnet RPC provider
- Block range can be adjusted for testing or production use 