# Blockchain Data Indexing Project

## Background and Motivation
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
- [x] Implement contract creation detection and storage
- [x] Add duplicate transaction checking
- [x] Implement parallel processing with batching
- [x] Add performance monitoring and logging
- [x] Document process and results

# Project Status Board
- [x] Environment setup for Base Mainnet
- [x] RPC connection
- [x] Supabase integration
- [x] Block scanning
- [x] Contract creation detection
- [x] Data validation
- [x] Performance monitoring
- [x] Parallel processing
- [x] Documentation

# Latest Performance Metrics (as of latest run)
- Total Blocks Processed: 100 blocks (29862098 to 29862197)
- Total Processing Time: 3.14 seconds
- Blocks Processed per Second: 31.87
- Contract Creations Found: 6
- Contract Creations per Second: 1.91
- Average Time per Contract: 0.523 seconds
- RPC Request Rate: Up to 50 RPS

# Executor's Feedback or Assistance Requests
- Successfully implemented parallel processing with batching
- Added comprehensive logging with timestamp and block range
- Implemented proper duplicate handling for contract creations
- Optimized RPC request handling with rate limiting
- All contract creations being stored with proper validation
- Performance significantly improved with parallel processing

# Lessons
- Always include block_number in transaction data to maintain proper relationships
- Use proper column names in database schema (e.g., from_address instead of from)
- Implement validation to ensure data consistency
- Add performance metrics to monitor and optimize processing
- Use proper error handling and logging for debugging
- Configure RLS policies carefully to ensure proper access control
- Duplicate transactions are normal and should be handled gracefully
- Use tx_hash as primary key to prevent duplicate contract creations
- Include timestamp in log files for better tracking
- Monitor and log RPC request rates to stay within limits

---

## Implementation Details (for Base Mainnet)

### Contract Scanner (`contract_scanner.py`)
- Scans recent blocks on Base Mainnet in parallel
- Identifies contract creation transactions
- Stores data in Supabase with proper relationships
- Features:
  - Parallel block processing (up to 8 concurrent batches)
  - Transaction batching (25 transactions per batch)
  - RPC rate limiting (50 RPS)
  - Block data prefetching (5 blocks ahead)
  - Block data caching (20 blocks)
  - Comprehensive logging with timestamps
  - Performance metrics tracking
  - Duplicate transaction handling

### Database Schema (`database.py`)
- Contract Creations table:
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

### How Contract Creation is Identified
A transaction is identified as a contract creation when:
1. Initial check: transaction's `to` address is `None` OR input data matches creation patterns
2. Confirmation: transaction receipt contains a `contractAddress`

### Setup and Requirements
1. Python 3.9+
2. Required packages (install via pip):
   ```
   pip install -r requirements.txt
   ```
3. Environment Variables:
   ```
   BASE_MAINNET_RPC_URL=your_base_mainnet_rpc_url_here
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_key_here
   ```

### Usage
```bash
python3 contract_scanner.py
```

The script will:
1. Connect to Base Mainnet and Supabase
2. Process the latest 100 blocks in parallel
3. Identify and store contract creations
4. Log performance metrics and block range
5. Create timestamped log file

### Future Scope
- Add support for other data types (transfers, ENS, etc.)
- Move to real-time indexing (websockets or polling)
- Implement smart prefetching based on contract creation patterns
- Add more validation and error handling
- Expand to other chains as needed

### Notes
- Performance has been significantly improved with parallel processing
- Duplicate prevention is working as intended
- Logging provides clear visibility into processing status
- Block range can be adjusted based on needs
- RPC rate limiting ensures stable operation 