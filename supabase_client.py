# supabase_client.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

load_dotenv()
# Supabase connection credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create and export the Supabase client instance
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_connection():
    """Test the Supabase connection"""
    try:
        # Try to query the database
        response = supabase.table("incomes").select("*").limit(1).execute()
        print("✅ Supabase connection successful!")
        return True
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False

# Connection test when module is run directly
if __name__ == "__main__":
    if test_connection():
        print("Supabase client is ready to use!")
    else:
        print("Failed to connect to Supabase. Please check your credentials.")