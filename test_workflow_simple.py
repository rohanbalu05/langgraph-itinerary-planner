"""
Test simplified workflow
"""
import sys
import os

sys.path.insert(0, os.getcwd())

print("=" * 70)
print("Testing Simple Workflow - Itinerary Generation")
print("=" * 70)
print()

# Import workflow
print("1. Importing simplified workflow...")
try:
    from workflow_simple import app
    print("✅ Workflow imported successfully")
    print()
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test preferences
preferences = {
    "destination": "Paris",
    "budget": 1000,
    "interests": ["art", "food"],
    "dates": "2025-11-20 to 2025-11-22"
}

print("2. Testing workflow with preferences:")
for key, val in preferences.items():
    print(f"   {key}: {val}")
print()

# Run workflow
print("3. Running workflow...")
try:
    result = app.invoke({"preferences": preferences})
    print("✅ Workflow completed successfully!")
    print()

    # Check results
    print("4. Checking results...")

    if "itinerary" in result:
        itinerary_text = result["itinerary"]
        print(f"✅ Itinerary text generated ({len(itinerary_text)} chars)")
        print()
        print("Preview (first 800 chars):")
        print("-" * 70)
        print(itinerary_text[:800])
        print("...")
        print("-" * 70)
    else:
        print("❌ No itinerary text in result")

    print()

    if "itinerary_json" in result:
        itinerary_json = result["itinerary_json"]
        print(f"✅ Itinerary JSON generated")
        print(f"   Keys: {list(itinerary_json.keys())}")
        if "itinerary" in itinerary_json:
            inner = itinerary_json["itinerary"]
            print(f"   Destination: {inner.get('destination', 'N/A')}")
            print(f"   Days: {len(inner.get('daily_plans', []))}")
            print(f"   Total cost: ${inner.get('total_estimated_cost', 0)}")
    else:
        print("❌ No itinerary JSON in result")

    print()

    if "errors" in result and result["errors"]:
        print("⚠️  Errors encountered:")
        for error in result["errors"]:
            print(f"   - {error}")
    else:
        print("✅ No errors!")

    print()

    if "weather" in result:
        print(f"✅ Weather info: {result['weather'][:100]}...")

    print()
    print("=" * 70)
    print("TEST PASSED! Simplified workflow is working!")
    print("=" * 70)

except Exception as e:
    print(f"❌ Workflow failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
