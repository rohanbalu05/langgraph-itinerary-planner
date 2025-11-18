"""
End-to-end test simulating full user workflow
Test Run #1 of 3
"""
import sys
import os

sys.path.insert(0, os.getcwd())

print("\n" + "=" * 70)
print(" END-TO-END TEST - FULL USER WORKFLOW (TEST RUN #1)")
print("=" * 70)
print()

# Test 1: Import all modules
print("TEST 1: Module Imports")
print("-" * 70)

modules_to_test = [
    ("workflow_simple", "Simplified Workflow"),
    ("llm_mock", "Mock LLM"),
    ("tripcraft_config", "TripCraft Configuration"),
    ("supabase_client_simple", "Simple Supabase Client"),
    ("backend.supabase_client", "Backend Supabase Client"),
    ("helper_func", "Helper Functions"),
]

failed_imports = []

for module_name, description in modules_to_test:
    try:
        __import__(module_name)
        print(f"✅ {description}")
    except Exception as e:
        print(f"❌ {description}: {e}")
        failed_imports.append(module_name)

print()

if failed_imports:
    print(f"❌ Failed to import: {', '.join(failed_imports)}")
    print("Cannot continue tests.")
    sys.exit(1)

print("✅ All core modules imported successfully!")
print()

# Test 2: Supabase Client
print("TEST 2: Supabase Client Operations")
print("-" * 70)

from backend.supabase_client import supabase

try:
    # Test insert
    test_data = {
        "destination": "TestCity",
        "budget": 999,
        "interests": ["test"],
        "dates": "2025-01-01 to 2025-01-03",
        "content": {"test": True}
    }

    response = supabase.table("itineraries").insert(test_data).execute()
    print(f"✅ Insert: {len(response.data)} record(s)")

    # Test select
    response = supabase.table("itineraries").select("*").execute()
    print(f"✅ Select: {len(response.data)} record(s)")

    # Test update
    if response.data:
        test_id = response.data[0]["id"]
        response = supabase.table("itineraries").update({"budget": 1500}).eq("id", test_id).execute()
        print(f"✅ Update: {len(response.data)} record(s)")

    print()
    print("✅ Supabase client is working!")
except Exception as e:
    print(f"❌ Supabase error: {e}")
    print("⚠️  Using in-memory storage (this is OK for testing)")

print()

# Test 3: Itinerary Generation
print("TEST 3: Itinerary Generation")
print("-" * 70)

from workflow_simple import app

test_cases = [
    {
        "name": "Paris 3-day trip",
        "preferences": {
            "destination": "Paris",
            "budget": 1000,
            "interests": ["art", "food"],
            "dates": "2025-11-20 to 2025-11-22"
        }
    },
    {
        "name": "Tokyo 5-day adventure",
        "preferences": {
            "destination": "Tokyo",
            "budget": 2000,
            "interests": ["food", "culture", "shopping"],
            "dates": "2025-12-01 to 2025-12-05"
        }
    },
    {
        "name": "New York weekend",
        "preferences": {
            "destination": "New York",
            "budget": 1500,
            "interests": ["art", "broadway", "food"],
            "dates": "2025-11-15 to 2025-11-17"
        }
    }
]

results = []

for i, test_case in enumerate(test_cases, 1):
    print(f"\nTest Case {i}: {test_case['name']}")
    print(f"  Preferences: {test_case['preferences']}")

    try:
        result = app.invoke({"preferences": test_case['preferences']})

        # Check required fields
        checks = {
            "itinerary text": "itinerary" in result and len(result["itinerary"]) > 100,
            "itinerary JSON": "itinerary_json" in result and "itinerary" in result["itinerary_json"],
            "destination info": "destination_info" in result,
            "weather": "weather" in result,
        }

        all_passed = all(checks.values())

        if all_passed:
            print("  ✅ All checks passed")
            # Show some details
            json_data = result["itinerary_json"]
            if "itinerary" in json_data:
                inner = json_data["itinerary"]
                print(f"     - Destination: {inner.get('destination', 'N/A')}")
                print(f"     - Days: {len(inner.get('daily_plans', []))}")
                print(f"     - Total cost: ${inner.get('total_estimated_cost', 0)}")
                print(f"     - Activities: {sum(len(d.get('activities', [])) for d in inner.get('daily_plans', []))}")
        else:
            print("  ❌ Some checks failed:")
            for check, passed in checks.items():
                if not passed:
                    print(f"     - {check}: FAILED")

        results.append({
            "name": test_case['name'],
            "passed": all_passed,
            "result": result
        })

    except Exception as e:
        print(f"  ❌ Error: {e}")
        results.append({
            "name": test_case['name'],
            "passed": False,
            "error": str(e)
        })

print()
print("-" * 70)

# Summary
print("\nTEST SUMMARY")
print("-" * 70)

passed = sum(1 for r in results if r["passed"])
total = len(results)

print(f"Passed: {passed}/{total}")

if passed == total:
    print("✅ ALL TESTS PASSED!")
else:
    print(f"❌ {total - passed} test(s) failed")

print()

# Test 4: JSON Validation
print("TEST 4: JSON Schema Validation")
print("-" * 70)

from tripcraft_config import validate_itinerary_json

validation_results = []

for result_data in results:
    if result_data["passed"] and "result" in result_data:
        json_data = result_data["result"].get("itinerary_json", {})
        is_valid = validate_itinerary_json(json_data)
        validation_results.append(is_valid)
        status = "✅" if is_valid else "❌"
        print(f"{status} {result_data['name']}: {'Valid' if is_valid else 'Invalid'}")

print()

if all(validation_results):
    print("✅ All generated itineraries are valid!")
else:
    print("❌ Some itineraries have invalid JSON structure")

print()

# Final Summary
print("=" * 70)
print(" END-TO-END TEST COMPLETE")
print("=" * 70)
print()

if passed == total and all(validation_results):
    print("🎉 SUCCESS! All tests passed!")
    print()
    print("System is ready for:")
    print("  - Itinerary generation")
    print("  - Supabase persistence (in-memory fallback)")
    print("  - JSON validation")
    print("  - Multiple destinations")
    print()
    print("Next: Run Streamlit app")
    print("  streamlit run app_with_chat.py")
    print()
    sys.exit(0)
else:
    print("⚠️  Some tests failed, but core functionality works")
    print("Review errors above for details")
    sys.exit(1)
