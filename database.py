import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    logger.error("Supabase credentials not found in environment variables")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def test_connection():
    """
    Test the connection to Supabase
    """
    try:
        # Try to fetch a single row from contract_creations table
        response = supabase.table("contract_creations").select("tx_hash").limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Supabase: {str(e)}")
        return False

def store_transactions_batch(contract_data):
    """
    Store a batch of contract creations in Supabase
    """
    try:
        response = supabase.table("contract_creations").insert(contract_data).execute()
        return True
    except Exception as e:
        logger.error(f"Error storing contract creations: {str(e)}")
        return False 