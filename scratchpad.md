# Background and Motivation

This project aims to index relevant blockchain data, with a primary focus on reducing dependency on third-party indexing platforms (such as Blockscout, Alchemy, etc.). The long-term goal is to build and maintain our own indexing infrastructure, starting with the most relevant data for our needs and expanding over time.

## Updated Project Goal
- Index only the blockchain data relevant to our project, not all data.
- Gradually decrease reliance on external indexing services by building our own indexers.
- Step-by-step approach: start with a single, high-impact data type and expand coverage iteratively.

## First Milestone
- **Indexing Smart Contract Creation on Base Mainnet**
- Use a Base Mainnet RPC URL as the data source (can be from a provider or self-hosted in the future).
- Store data in Supabase for efficient querying and scalability.

# Key Challenges and Analysis
- Understanding and adapting to the Base Mainnet (an EVM-compatible L2 network)
- Efficiently scanning and processing large block ranges
- Identifying contract creation transactions accurately (to address is None, receipt has contractAddress)
- Handling rate limits and reliability of the Base RPC endpoint
- Ensuring data is saved reliably in Supabase
- Maintaining data consistency and preventing duplicates
- Laying the groundwork for future expansion to other data types and chains

# High-level Task Breakdown
- [x] Set up environment and dependencies for Base Mainnet
- [x] Obtain and configure a Base Mainnet RPC URL
- [x] Connect to Base Mainnet using web3.py
- [x] Set up Supabase database and tables
- [x] Configure Row Level Security (RLS) policies
- [x] Implement block and transaction data storage
- [x] Add duplicate block checking
- [x] Add transaction count validation
- [x] Implement performance monitoring
- [ ] Document process and results

# Project Status Board
- [x] Environment setup for Base Mainnet
- [x] RPC connection
- [x] Supabase integration
- [x] Block scanning
- [x] Transaction identification
- [x] Data validation
- [x] Performance monitoring
- [ ] Documentation

# Executor's Feedback or Assistance Requests
- Successfully implemented Supabase integration
- Added validation for transaction counts
- Implemented duplicate block checking
- Added performance metrics tracking
- All HTTP requests returning 201 Created status codes
- Average processing time: ~0.31 seconds per transaction

# Lessons
- Always include block_number in transaction data to maintain proper relationships
- Use proper column names in database schema (e.g., from_address instead of from)
- Implement validation to ensure data consistency
- Add performance metrics to monitor and optimize processing
- Use proper error handling and logging for debugging
- Configure RLS policies carefully to ensure proper access control

---

## Implementation Details (for Base Mainnet)

### Contract Scanner (`contract_scanner.py`)
- Scans recent blocks on Base Mainnet
- Identifies contract creation transactions
- Stores data in Supabase with proper relationships
- Includes validation and performance monitoring
- Features:
  - Duplicate block checking
  - Transaction count validation
  - Performance metrics
  - Detailed logging

### Database Schema (`database.py`)
- Blocks table:
  - block_number (primary key)
  - block_hash
  - timestamp
  - tx_count
- Transactions table:
  - tx_hash
  - block_number (foreign key)
  - from_address
  - to_address
  - status
  - contract_address
  - logs_count
  - tx_type

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
   - Add your Base Mainnet RPC URL and Supabase credentials:
     ```
     BASE_MAINNET_RPC_URL=your_base_mainnet_rpc_url_here
     SUPABASE_URL=your_supabase_url_here
     SUPABASE_KEY=your_supabase_key_here
     ```

### Usage
To scan for contract creations:
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

### Performance Metrics
- Average processing time per transaction: ~0.31 seconds
- Block processing time: ~40-50 seconds per block
- Transaction count per block: ~100-160 transactions

### Future Scope
- Add support for other data types (transfers, ENS, etc.)
- Move to real-time indexing (websockets or polling)
- Implement batch processing for better performance
- Add more validation and error handling
- Expand to other chains as needed

### Notes
- The current implementation uses Supabase for efficient data storage and querying
- Rate limiting and reliability depend on your Base Mainnet RPC provider
- Block range can be adjusted for testing or production use
- Performance metrics help identify bottlenecks and optimize processing 