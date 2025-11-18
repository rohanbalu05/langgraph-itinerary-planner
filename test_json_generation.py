"""
Test JSON generation to diagnose the issue
"""
import sys
import os

sys.path.insert(0, os.getcwd())

from tripcraft_config import build_itinerary_prompt, extract_json_from_text, validate_itinerary_json

# Test preferences
preferences = {
    "destination": "Paris",
    "budget": 1000,
    "interests": ["art", "food"],
    "dates": "2025-11-20 to 2025-11-22"
}

destination_info = "Paris is the capital of France, famous for the Eiffel Tower, Louvre Museum, and excellent French cuisine."

print("=" * 70)
print("Testing JSON Generation")
print("=" * 70)
print()

# Test 1: Build prompt
print("1. Building prompt...")
prompt = build_itinerary_prompt(preferences, destination_info, 3)
print("✅ Prompt built successfully")
print(f"   Length: {len(prompt)} characters")
print()

# Test 2: Check if we can generate without LLM
print("2. Creating mock JSON response...")

mock_response = """{
  "itinerary": {
    "destination": "Paris, France",
    "start_date": "2025-11-20",
    "end_date": "2025-11-22",
    "timezone": "Europe/Paris",
    "currency": "EUR",
    "daily_plans": [
      {
        "day": 1,
        "date": "2025-11-20",
        "summary": "Arrival and Eiffel Tower",
        "activities": [
          {
            "start_time": "09:00",
            "end_time": "12:00",
            "title": "Visit Eiffel Tower",
            "type": "sightseeing",
            "address": "Champ de Mars, 5 Avenue Anatole France",
            "notes": "Book tickets online"
          }
        ],
        "meals": [
          {
            "time": "12:30",
            "suggestion": "Le Petit Cler",
            "est_cost": 25
          }
        ],
        "estimated_daily_cost": 150
      }
    ],
    "total_estimated_cost": 450,
    "assumptions": ["3-star hotel"],
    "sources": [{"type": "static", "citation": "Paris tourism guide"}]
  },
  "human_readable": "3-day Paris itinerary with art and food focus. Total cost: 450 EUR"
}"""

print("✅ Mock JSON created")
print()

# Test 3: Extract JSON
print("3. Testing JSON extraction...")
try:
    extracted = extract_json_from_text(mock_response)
    print("✅ JSON extracted successfully")
    print(f"   Keys: {list(extracted.keys())}")
except Exception as e:
    print(f"❌ Extraction failed: {e}")
    sys.exit(1)

print()

# Test 4: Validate JSON
print("4. Testing JSON validation...")
if validate_itinerary_json(extracted):
    print("✅ JSON validation passed")
else:
    print("❌ JSON validation failed")
    sys.exit(1)

print()

# Test 5: Test with markdown code blocks
print("5. Testing extraction from markdown...")
markdown_json = f"""Here's your itinerary:

```json
{mock_response}
```

Let me know if you need changes!"""

try:
    extracted2 = extract_json_from_text(markdown_json)
    print("✅ Markdown extraction works")
except Exception as e:
    print(f"❌ Markdown extraction failed: {e}")

print()

# Test 6: Test with invalid JSON
print("6. Testing error handling...")
try:
    extract_json_from_text("This is not JSON at all!")
    print("❌ Should have raised error")
except ValueError:
    print("✅ Error handling works correctly")

print()
print("=" * 70)
print("All tests passed! JSON extraction is working correctly.")
print("=" * 70)
print()
print("Next step: Check LLM generation...")
