"""
Supabase Helper Functions for Itinerary Persistence
"""
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from backend.supabase_client import supabase
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False
    supabase = None


def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured"""
    url = os.getenv("VITE_SUPABASE_URL")
    key = os.getenv("VITE_SUPABASE_SUPABASE_ANON_KEY")
    return SUPABASE_AVAILABLE and url and key


def save_itinerary(itinerary_data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[str]:
    """
    Save itinerary to Supabase

    Args:
        itinerary_data: The itinerary JSON data
        user_id: Optional user ID for tracking

    Returns:
        Itinerary ID if successful, None otherwise
    """
    if not is_supabase_configured():
        print("Warning: Supabase not configured. Itinerary not saved.")
        return None

    try:
        itinerary = itinerary_data.get('itinerary', itinerary_data)

        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "destination": itinerary.get('destination', 'Unknown'),
            "start_date": itinerary.get('start_date'),
            "end_date": itinerary.get('end_date'),
            "content": itinerary,
            "total_cost": itinerary.get('total_estimated_cost', 0),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        response = supabase.table("itineraries").insert(record).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]['id']

        return record["id"]

    except Exception as e:
        print(f"Error saving itinerary to Supabase: {e}")
        return None


def load_itinerary(itinerary_id: str) -> Optional[Dict[str, Any]]:
    """
    Load itinerary from Supabase

    Args:
        itinerary_id: The itinerary ID

    Returns:
        Itinerary data if found, None otherwise
    """
    if not is_supabase_configured():
        return None

    try:
        response = supabase.table("itineraries") \
            .select("*") \
            .eq("id", itinerary_id) \
            .maybeSingle() \
            .execute()

        if response.data:
            return response.data

        return None

    except Exception as e:
        print(f"Error loading itinerary from Supabase: {e}")
        return None


def update_itinerary(itinerary_id: str, updated_content: Dict[str, Any]) -> bool:
    """
    Update existing itinerary in Supabase

    Args:
        itinerary_id: The itinerary ID
        updated_content: The updated itinerary content

    Returns:
        True if successful, False otherwise
    """
    if not is_supabase_configured():
        return False

    try:
        response = supabase.table("itineraries") \
            .update({
                "content": updated_content,
                "updated_at": datetime.now().isoformat()
            }) \
            .eq("id", itinerary_id) \
            .execute()

        return bool(response.data)

    except Exception as e:
        print(f"Error updating itinerary in Supabase: {e}")
        return False


def list_user_itineraries(user_id: str, limit: int = 10) -> list:
    """
    List all itineraries for a user

    Args:
        user_id: The user ID
        limit: Maximum number of itineraries to return

    Returns:
        List of itineraries
    """
    if not is_supabase_configured():
        return []

    try:
        response = supabase.table("itineraries") \
            .select("id, destination, start_date, end_date, total_cost, created_at") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()

        return response.data if response.data else []

    except Exception as e:
        print(f"Error listing itineraries from Supabase: {e}")
        return []


def delete_itinerary(itinerary_id: str) -> bool:
    """
    Delete an itinerary from Supabase

    Args:
        itinerary_id: The itinerary ID

    Returns:
        True if successful, False otherwise
    """
    if not is_supabase_configured():
        return False

    try:
        response = supabase.table("itineraries") \
            .delete() \
            .eq("id", itinerary_id) \
            .execute()

        return True

    except Exception as e:
        print(f"Error deleting itinerary from Supabase: {e}")
        return False
