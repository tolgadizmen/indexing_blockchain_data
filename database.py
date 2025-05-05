import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY")
)

def get_existing_block(block_number):
    """
    Check if a block already exists in the database
    """
    try:
        response = supabase.table("blocks").select("block_number").eq("block_number", block_number).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking for existing block: {str(e)}")
        return False

def store_block_data(block_data):
    """
    Store block data in the blocks table
    """
    try:
        data = supabase.table("blocks").insert(block_data).execute()
        return data
    except Exception as e:
        print(f"Error storing block data: {str(e)}")
        return None

def store_transaction_data(transaction_data):
    """
    Store transaction data in the transactions table
    """
    try:
        data = supabase.table("transactions").insert(transaction_data).execute()
        return data
    except Exception as e:
        print(f"Error storing transaction data: {str(e)}")
        return None

def test_connection():
    """
    Test the Supabase connection
    """
    try:
        # Try to fetch a single row from blocks table
        response = supabase.table("blocks").select("*").limit(1).execute()
        print("Successfully connected to Supabase!")
        return True
    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")
        return False 