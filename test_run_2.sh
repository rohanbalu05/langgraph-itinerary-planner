#!/bin/bash
echo "========================================================================"
echo " TEST RUN #2 - Different Scenarios"
echo "========================================================================"
echo ""

python3 << 'PYTHON_EOF'
import sys, os
sys.path.insert(0, os.getcwd())

from workflow_simple import app
from tripcraft_config import validate_itinerary_json

# Test different scenarios
scenarios = [
    {"name": "Budget Trip", "preferences": {"destination": "Bangkok", "budget": 500, "interests": ["food", "temples"], "dates": "2025-12-10 to 2025-12-13"}},
    {"name": "Luxury Week", "preferences": {"destination": "Dubai", "budget": 5000, "interests": ["luxury", "shopping", "beach"], "dates": "2026-01-15 to 2026-01-21"}},
    {"name": "Nature Adventure", "preferences": {"destination": "Iceland", "budget": 3000, "interests": ["nature", "hiking", "photography"], "dates": "2025-07-01 to 2025-07-07"}},
]

print(f"Testing {len(scenarios)} scenarios...\n")

passed = 0
for i, scenario in enumerate(scenarios, 1):
    print(f"Scenario {i}: {scenario['name']}")
    try:
        result = app.invoke({"preferences": scenario['preferences']})
        
        has_itinerary = "itinerary" in result and len(result["itinerary"]) > 100
        has_json = "itinerary_json" in result
        is_valid = validate_itinerary_json(result.get("itinerary_json", {})) if has_json else False
        
        if has_itinerary and has_json and is_valid:
            print(f"  ✅ PASSED")
            json_data = result["itinerary_json"]["itinerary"]
            print(f"     Destination: {json_data['destination']}")
            print(f"     Days: {len(json_data['daily_plans'])}")
            print(f"     Budget: ${json_data['total_estimated_cost']}")
            passed += 1
        else:
            print(f"  ❌ FAILED: itinerary={has_itinerary}, json={has_json}, valid={is_valid}")
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
    print()

print(f"\nResults: {passed}/{len(scenarios)} passed")

if passed == len(scenarios):
    print("✅ TEST RUN #2 PASSED!")
    sys.exit(0)
else:
    print("❌ TEST RUN #2 FAILED")
    sys.exit(1)

PYTHON_EOF
