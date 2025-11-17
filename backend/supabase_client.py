import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("VITE_SUPABASE_URL")
supabase_key = os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Supabase credentials not found in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)
