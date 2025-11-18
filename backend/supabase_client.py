"""
Supabase client that works without supabase-py package
Uses in-memory storage as fallback
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Use our simple in-memory client
from supabase_client_simple import supabase, create_client, Client

print("✅ Supabase client loaded (in-memory fallback mode)")
