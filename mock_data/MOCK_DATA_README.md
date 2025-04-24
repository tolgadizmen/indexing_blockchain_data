# Mock Blockchain Data Generator

## Overview
This project generates mock blockchain data for two main types of transactions:
1. Smart Contract Creations
2. ENS (Ethereum Name Service) Transactions

## Data Structure

### Smart Contract Creations
Each contract creation record includes:
- Block Number
- Transaction Hash
- Contract Address
- Creator Address
- Timestamp
- Gas Used
- Deployment Cost (in ETH)
- Constructor Arguments
- Bytecode
- Verification Status
- Contract Type (ERC20, ERC721, ERC1155, or Custom)

### ENS Transactions
Four types of ENS transactions are generated:
1. **Domain Registration**
   - Domain Name
   - Registrant Address
   - Duration (in years)
   - Expiration Date
   - Gas Used
   - Transaction Cost

2. **Domain Transfer**
   - Domain Name
   - From Address
   - To Address
   - Gas Used
   - Transaction Cost

3. **Domain Renewal**
   - Domain Name
   - Owner Address
   - Duration (in years)
   - New Expiration Date
   - Gas Used
   - Transaction Cost

4. **Resolver Update**
   - Domain Name
   - Owner Address
   - Old Resolver Address
   - New Resolver Address
   - Gas Used
   - Transaction Cost

## Data Relationships
- 30% of ENS transactions are randomly linked to contract addresses
- Block numbers are sequential with random increments
- Timestamps are within the last 30 days
- Gas prices and costs follow realistic ranges

## Database Implementation
We implemented a SQLite database (`mock_ens.db`) to store and query the mock data. This was done to:
1. Demonstrate real-world data relationships
2. Enable complex queries across different data types
3. Provide a foundation for future data analysis tools

### Database Structure
The database consists of two main tables:
1. **contracts** - Stores all contract creation data
2. **ens_transactions** - Stores all ENS-related transactions

The tables are linked through the `linked_contract` field in the `ens_transactions` table, which references the `contract_address` in the `contracts` table.

### Example Queries
The `query_data.py` script demonstrates several useful queries:
1. Contract type distribution
2. Contracts with linked ENS domains
3. Most active ENS registrants
4. Gas usage statistics
5. Recent ENS transactions

## Usage
1. Generate mock data:
   ```bash
   python mock_data_generator.py
   ```
   This creates `mock_ens_data.json`

2. Create and query the database:
   ```bash
   python query_data.py
   ```
   This:
   - Creates `mock_ens.db`
   - Imports data from JSON
   - Runs example queries

## Future Improvements
- Add more contract types
- Include more ENS transaction types
- Add more realistic data patterns
- Implement data validation
- Add data querying capabilities
- Create visualization tools
- Add more complex queries and analysis
- Implement a web interface for data exploration 