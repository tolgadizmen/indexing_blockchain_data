import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import os

def generate_ethereum_address() -> str:
    """Generate a mock Ethereum address"""
    return f"0x{''.join(random.choices('0123456789abcdef', k=40))}"

def generate_tx_hash() -> str:
    """Generate a mock transaction hash"""
    return f"0x{''.join(random.choices('0123456789abcdef', k=64))}"

def generate_contract_type() -> str:
    """Generate a random contract type"""
    contract_types = ["ERC20", "ERC721", "ERC1155", "Custom"]
    return random.choice(contract_types)

def generate_constructor_args(contract_type: str) -> List[str]:
    """Generate mock constructor arguments based on contract type"""
    if contract_type == "ERC20":
        return [
            f"Token{random.randint(1, 1000)}",
            f"TKN{random.randint(1, 1000)}",
            str(random.randint(18, 21))
        ]
    elif contract_type == "ERC721":
        return [
            f"NFT Collection {random.randint(1, 1000)}",
            f"NFTC{random.randint(1, 1000)}"
        ]
    elif contract_type == "ERC1155":
        return [f"Multi Token {random.randint(1, 1000)}"]
    return []

def generate_ens_domain() -> str:
    """Generate a mock ENS domain"""
    tlds = ["eth", "xyz", "app", "dao"]
    name_length = random.randint(3, 15)
    name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=name_length))
    return f"{name}.{random.choice(tlds)}"

def generate_ens_transaction(contract_addresses: List[str], block_number: int) -> Dict:
    """Generate a mock ENS transaction"""
    transaction_types = ["registration", "transfer", "renewal", "resolver_update"]
    tx_type = random.choice(transaction_types)
    
    # Base transaction data
    tx = {
        "type": tx_type,
        "block_number": block_number,
        "tx_hash": generate_tx_hash(),
        "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S"),
        "gas_used": random.randint(50000, 300000),
        "gas_price": random.uniform(10, 100),
        "cost_eth": round(random.uniform(0.01, 0.5), 6)
    }
    
    # Type-specific data
    if tx_type == "registration":
        tx.update({
            "domain": generate_ens_domain(),
            "registrant": generate_ethereum_address(),
            "duration_years": random.randint(1, 10),
            "expiration_date": (datetime.now() + timedelta(days=365*random.randint(1, 10))).strftime("%Y-%m-%d")
        })
    elif tx_type == "transfer":
        tx.update({
            "domain": generate_ens_domain(),
            "from_address": generate_ethereum_address(),
            "to_address": generate_ethereum_address()
        })
    elif tx_type == "renewal":
        tx.update({
            "domain": generate_ens_domain(),
            "owner": generate_ethereum_address(),
            "duration_years": random.randint(1, 5),
            "expiration_date": (datetime.now() + timedelta(days=365*random.randint(1, 5))).strftime("%Y-%m-%d")
        })
    elif tx_type == "resolver_update":
        tx.update({
            "domain": generate_ens_domain(),
            "owner": generate_ethereum_address(),
            "old_resolver": generate_ethereum_address(),
            "new_resolver": generate_ethereum_address()
        })
    
    # 30% chance to link to a contract
    if random.random() < 0.3 and contract_addresses:
        tx["linked_contract"] = random.choice(contract_addresses)
    
    return tx

def generate_mock_contracts(num_contracts: int = 100) -> Tuple[List[Dict], List[str]]:
    """Generate mock contract creation data"""
    contracts = []
    contract_addresses = []
    current_block = 19000000  # Starting block number
    
    for _ in range(num_contracts):
        contract_type = generate_contract_type()
        gas_used = random.randint(100000, 5000000)
        gas_price = random.uniform(10, 100)  # in gwei
        deployment_cost = (gas_used * gas_price) / 1e9  # Convert to ETH
        
        contract_address = generate_ethereum_address()
        contract = {
            "block_number": current_block,
            "tx_hash": generate_tx_hash(),
            "contract_address": contract_address,
            "creator_address": generate_ethereum_address(),
            "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S"),
            "gas_used": gas_used,
            "deployment_cost_eth": round(deployment_cost, 6),
            "constructor_args": generate_constructor_args(contract_type),
            "bytecode": f"0x{''.join(random.choices('0123456789abcdef', k=100))}",  # Simplified mock bytecode
            "is_verified": random.choice([True, False]),
            "contract_type": contract_type
        }
        
        contracts.append(contract)
        contract_addresses.append(contract_address)
        current_block += random.randint(1, 100)  # Increment block number
        
    return contracts, contract_addresses

def generate_mock_ens_transactions(num_transactions: int = 100, contract_addresses: List[str] = None) -> List[Dict]:
    """Generate mock ENS transactions"""
    transactions = []
    current_block = 19000000  # Starting block number
    
    for _ in range(num_transactions):
        tx = generate_ens_transaction(contract_addresses or [], current_block)
        transactions.append(tx)
        current_block += random.randint(1, 50)  # Increment block number
        
    return transactions

def save_to_json(data: Dict, filename: str):
    """Save mock data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    # Create output directory if it doesn't exist
    os.makedirs("mock_data", exist_ok=True)
    
    # Generate mock contract data
    contracts, contract_addresses = generate_mock_contracts(100)
    
    # Generate mock ENS transactions
    ens_transactions = generate_mock_ens_transactions(100, contract_addresses)
    
    # Save both datasets
    save_to_json({
        "contracts": contracts,
        "ens_transactions": ens_transactions
    }, "mock_data/mock_ens_data.json")
    
    print(f"Generated {len(contracts)} mock contracts and {len(ens_transactions)} ENS transactions")
    print("Data saved to mock_data/mock_ens_data.json")

if __name__ == "__main__":
    main() 