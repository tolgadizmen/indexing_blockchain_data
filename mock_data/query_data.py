import sqlite3
import json
from typing import List, Dict
import os

def create_database(data: Dict) -> sqlite3.Connection:
    """Create SQLite database and tables from mock data"""
    # Remove existing database if it exists
    if os.path.exists('mock_data/mock_ens.db'):
        os.remove('mock_data/mock_ens.db')
    
    conn = sqlite3.connect('mock_data/mock_ens.db')
    cursor = conn.cursor()
    
    # Create contracts table
    cursor.execute('''
    CREATE TABLE contracts (
        block_number INTEGER,
        tx_hash TEXT,
        contract_address TEXT PRIMARY KEY,
        creator_address TEXT,
        timestamp TEXT,
        gas_used INTEGER,
        deployment_cost_eth REAL,
        constructor_args TEXT,
        bytecode TEXT,
        is_verified INTEGER,
        contract_type TEXT
    )
    ''')
    
    # Create ens_transactions table
    cursor.execute('''
    CREATE TABLE ens_transactions (
        type TEXT,
        block_number INTEGER,
        tx_hash TEXT PRIMARY KEY,
        timestamp TEXT,
        gas_used INTEGER,
        gas_price REAL,
        cost_eth REAL,
        domain TEXT,
        registrant TEXT,
        from_address TEXT,
        to_address TEXT,
        owner TEXT,
        duration_years INTEGER,
        expiration_date TEXT,
        old_resolver TEXT,
        new_resolver TEXT,
        linked_contract TEXT,
        FOREIGN KEY (linked_contract) REFERENCES contracts(contract_address)
    )
    ''')
    
    # Insert contract data
    for contract in data['contracts']:
        cursor.execute('''
        INSERT INTO contracts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contract['block_number'],
            contract['tx_hash'],
            contract['contract_address'],
            contract['creator_address'],
            contract['timestamp'],
            contract['gas_used'],
            contract['deployment_cost_eth'],
            json.dumps(contract['constructor_args']),
            contract['bytecode'],
            1 if contract['is_verified'] else 0,
            contract['contract_type']
        ))
    
    # Insert ENS transaction data
    for tx in data['ens_transactions']:
        cursor.execute('''
        INSERT INTO ens_transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            tx['type'],
            tx['block_number'],
            tx['tx_hash'],
            tx['timestamp'],
            tx['gas_used'],
            tx['gas_price'],
            tx['cost_eth'],
            tx.get('domain'),
            tx.get('registrant'),
            tx.get('from_address'),
            tx.get('to_address'),
            tx.get('owner'),
            tx.get('duration_years'),
            tx.get('expiration_date'),
            tx.get('old_resolver'),
            tx.get('new_resolver'),
            tx.get('linked_contract')
        ))
    
    conn.commit()
    return conn

def run_example_queries(conn: sqlite3.Connection):
    """Run and display example queries"""
    cursor = conn.cursor()
    
    # Query 1: Count contracts by type
    print("\n1. Contract Types Distribution:")
    cursor.execute('''
    SELECT contract_type, COUNT(*) as count 
    FROM contracts 
    GROUP BY contract_type
    ''')
    for row in cursor.fetchall():
        print(f"{row[0]}: {row[1]} contracts")
    
    # Query 2: Find contracts with linked ENS domains
    print("\n2. Contracts with Linked ENS Domains:")
    cursor.execute('''
    SELECT c.contract_address, c.contract_type, e.domain
    FROM contracts c
    JOIN ens_transactions e ON c.contract_address = e.linked_contract
    ''')
    for row in cursor.fetchall():
        print(f"Contract: {row[0]} ({row[1]}) -> ENS: {row[2]}")
    
    # Query 3: Most active ENS registrants
    print("\n3. Top ENS Registrants:")
    cursor.execute('''
    SELECT registrant, COUNT(*) as count
    FROM ens_transactions
    WHERE type = 'registration'
    GROUP BY registrant
    ORDER BY count DESC
    LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f"Registrant: {row[0]} -> {row[1]} domains")
    
    # Query 4: Gas usage statistics
    print("\n4. Gas Usage Statistics:")
    cursor.execute('''
    SELECT 
        AVG(gas_used) as avg_gas,
        MAX(gas_used) as max_gas,
        MIN(gas_used) as min_gas
    FROM contracts
    ''')
    stats = cursor.fetchone()
    print(f"Average Gas: {stats[0]:.2f}")
    print(f"Maximum Gas: {stats[1]}")
    print(f"Minimum Gas: {stats[2]}")
    
    # Query 5: Recent ENS transactions
    print("\n5. Recent ENS Transactions:")
    cursor.execute('''
    SELECT type, domain, timestamp
    FROM ens_transactions
    ORDER BY timestamp DESC
    LIMIT 5
    ''')
    for row in cursor.fetchall():
        print(f"{row[2]} - {row[0]} for {row[1]}")

def main():
    # Load mock data
    with open('mock_data/mock_ens_data.json', 'r') as f:
        data = json.load(f)
    
    # Create database and run queries
    conn = create_database(data)
    run_example_queries(conn)
    conn.close()

if __name__ == "__main__":
    main() 