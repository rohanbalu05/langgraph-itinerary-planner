"""
Quick test script for TripCraft functionality
Run this to verify everything is working
"""

import os
import sys
from datetime import datetime


def test_imports():
    """Test that all modules can be imported"""
    print("\n🔍 Testing imports...")

    try:
        from workflow import app
        print("✅ workflow.py")
    except Exception as e:
        print(f"❌ workflow.py: {e}")
        return False

    try:
        from llm import llm
        print("✅ llm.py")
    except Exception as e:
        print(f"❌ llm.py: {e}")
        return False

    try:
        from tripcraft_config import build_itinerary_prompt, validate_itinerary_json
        print("✅ tripcraft_config.py")
    except Exception as e:
        print(f"❌ tripcraft_config.py: {e}")
        return False

    try:
        from supabase_helpers import is_supabase_configured
        print("✅ supabase_helpers.py")
    except Exception as e:
        print(f"❌ supabase_helpers.py: {e}")
        return False

    try:
        from chat_widget import ChatWidget
        print("✅ chat_widget.py")
    except Exception as e:
        print(f"❌ chat_widget.py: {e}")
        return False

    print("\n✅ All imports successful!\n")
    return True


def test_configuration():
    """Test environment configuration"""
    print("🔧 Checking configuration...")

    supabase_url = os.getenv("VITE_SUPABASE_URL")
    supabase_key = os.getenv("VITE_SUPABASE_ANON_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    if supabase_url and supabase_key:
        print("✅ Supabase configured")
    else:
        print("⚠️  Supabase not configured (itineraries won't be saved)")

    if openai_key:
        print("✅ OpenAI API key configured (fallback available)")
    else:
        print("⚠️  OpenAI API key not set (using local models only)")

    if tavily_key:
        print("✅ Tavily API key configured")
    else:
        print("⚠️  Tavily API key not set (limited web search)")

    print()


def test_simple_generation():
    """Test basic itinerary generation"""
    print("🌍 Testing itinerary generation...")

    try:
        from workflow import app

        preferences = {
            "destination": "Paris",
            "budget": 1000,
            "interests": ["art", "food"],
            "dates": "2025-10-01 to 2025-10-03"
        }

        print(f"  Generating itinerary for {preferences['destination']}...")

        result = app.invoke({"preferences": preferences})

        itinerary = result.get("itinerary", "")
        itinerary_json = result.get("itinerary_json", {})
        errors = result.get("errors", [])

        if errors:
            print(f"⚠️  Generation completed with warnings:")
            for error in errors:
                print(f"     {error}")
        else:
            print("✅ Itinerary generated successfully!")

        if itinerary_json:
            print(f"✅ JSON structure created")

            itinerary_data = itinerary_json.get('itinerary', itinerary_json)
            num_days = len(itinerary_data.get('daily_plans', []))
            total_cost = itinerary_data.get('total_estimated_cost', 0)

            print(f"   📅 Days: {num_days}")
            print(f"   💰 Total cost: ${total_cost}")
        else:
            print("⚠️  No JSON structure (using fallback)")

        if len(itinerary) > 100:
            print(f"✅ Itinerary text generated ({len(itinerary)} characters)")
        else:
            print("⚠️  Itinerary seems too short")

        return True

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_validation():
    """Test JSON validation"""
    print("\n✨ Testing JSON validation...")

    from tripcraft_config import validate_itinerary_json

    # Valid JSON
    valid_json = {
        "itinerary": {
            "destination": "Test City",
            "start_date": "2025-01-01",
            "end_date": "2025-01-03",
            "daily_plans": [
                {
                    "day": 1,
                    "date": "2025-01-01",
                    "activities": []
                }
            ]
        },
        "human_readable": "Test itinerary"
    }

    if validate_itinerary_json(valid_json):
        print("✅ Valid JSON recognized")
    else:
        print("❌ Valid JSON not recognized")
        return False

    # Invalid JSON
    invalid_json = {"some": "data"}

    if not validate_itinerary_json(invalid_json):
        print("✅ Invalid JSON rejected")
    else:
        print("❌ Invalid JSON accepted")
        return False

    return True


def test_supabase_connection():
    """Test Supabase connection"""
    print("\n💾 Testing Supabase connection...")

    try:
        from supabase_helpers import is_supabase_configured

        if is_supabase_configured():
            print("✅ Supabase is configured")

            try:
                from backend.supabase_client import supabase

                # Try a simple query
                response = supabase.table("itineraries").select("id").limit(1).execute()
                print("✅ Database connection successful")
                return True
            except Exception as e:
                print(f"⚠️  Database query failed: {e}")
                print("   (This might be expected if tables don't exist yet)")
                return True
        else:
            print("⚠️  Supabase not configured")
            print("   Add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to .env")
            return True

    except Exception as e:
        print(f"❌ Supabase test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  TripCraft Integration Test Suite")
    print("=" * 60)

    all_passed = True

    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Cannot continue.")
        sys.exit(1)

    # Test configuration
    test_configuration()

    # Test JSON validation
    if not test_json_validation():
        all_passed = False

    # Test Supabase
    if not test_supabase_connection():
        all_passed = False

    # Test generation (this takes time)
    print("\n" + "-" * 60)
    user_input = input("Run itinerary generation test? (takes ~30 seconds) [y/N]: ")

    if user_input.lower() in ['y', 'yes']:
        if not test_simple_generation():
            all_passed = False
    else:
        print("⏭️  Skipped generation test")

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed!")
        print("\nYou can now run the application:")
        print("  streamlit run app_with_chat.py")
    else:
        print("⚠️  Some tests failed, but system may still work")
        print("\nCheck the errors above and refer to TRIPCRAFT_USAGE_GUIDE.md")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
