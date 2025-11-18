"""
Mock LLM that generates proper JSON for testing
Can be replaced with actual LLM later
"""
import os
import json
import re
from typing import Optional
from datetime import datetime, timedelta


def extract_date_info(prompt: str):
    """Extract date information from prompt"""
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})', prompt)
    if date_match:
        return date_match.group(1), date_match.group(2)
    return None, None


def extract_destination(prompt: str):
    """Extract destination from prompt"""
    dest_match = re.search(r'Destination[:\*\s]+([^\n]+)', prompt, re.IGNORECASE)
    if dest_match:
        return dest_match.group(1).strip()

    # Try to find in generate itinerary line
    gen_match = re.search(r'Generate.*?for\s+([^\.]+)', prompt, re.IGNORECASE)
    if gen_match:
        return gen_match.group(1).strip()

    return "Unknown Destination"


def extract_budget(prompt: str):
    """Extract budget from prompt"""
    budget_match = re.search(r'Budget[:\*\s]+\$?(\d+)', prompt, re.IGNORECASE)
    if budget_match:
        return int(budget_match.group(1))
    return 1000


def extract_interests(prompt: str):
    """Extract interests from prompt"""
    interests_match = re.search(r'Interests[:\*\s]+([^\n]+)', prompt, re.IGNORECASE)
    if interests_match:
        interests_str = interests_match.group(1)
        return [i.strip() for i in interests_str.split(',')]
    return ["sightseeing", "food"]


def generate_mock_itinerary(prompt: str) -> str:
    """Generate a mock itinerary JSON that matches TripCraft schema"""

    # Extract info from prompt
    start_date, end_date = extract_date_info(prompt)
    destination = extract_destination(prompt)
    budget = extract_budget(prompt)
    interests = extract_interests(prompt)

    if not start_date or not end_date:
        start_date = "2025-11-20"
        end_date = "2025-11-22"

    # Calculate number of days
    from datetime import datetime
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    num_days = (end - start).days + 1

    # Daily budget
    daily_budget = budget // num_days if num_days > 0 else budget

    # Generate daily plans
    daily_plans = []

    activity_templates = {
        "art": {
            "morning": {"title": f"Visit {destination} Art Museum", "cost": 25},
            "afternoon": {"title": "Gallery Walking Tour", "cost": 15},
            "evening": {"title": "Contemporary Art Exhibition", "cost": 20}
        },
        "food": {
            "morning": {"title": "Local Market Tour", "cost": 20},
            "afternoon": {"title": "Cooking Class", "cost": 80},
            "evening": {"title": "Fine Dining Experience", "cost": 100}
        },
        "history": {
            "morning": {"title": "Historical Walking Tour", "cost": 30},
            "afternoon": {"title": "Museum Visit", "cost": 20},
            "evening": {"title": "Cultural Performance", "cost": 40}
        },
        "nature": {
            "morning": {"title": "Park Exploration", "cost": 0},
            "afternoon": {"title": "Botanical Gardens", "cost": 15},
            "evening": {"title": "Sunset Viewpoint", "cost": 0}
        },
        "adventure": {
            "morning": {"title": "Hiking Excursion", "cost": 30},
            "afternoon": {"title": "Adventure Sports", "cost": 100},
            "evening": {"title": "Night Tour", "cost": 50}
        },
        "shopping": {
            "morning": {"title": "Local Markets", "cost": 50},
            "afternoon": {"title": "Shopping District Tour", "cost": 100},
            "evening": {"title": "Boutique Shopping", "cost": 75}
        }
    }

    for day_num in range(1, num_days + 1):
        current_date = start + timedelta(days=day_num - 1)
        date_str = current_date.strftime("%Y-%m-%d")

        # Pick activity theme for the day
        theme = interests[day_num % len(interests)] if interests else "sightseeing"
        if theme not in activity_templates:
            theme = "art"  # fallback

        templates = activity_templates[theme]

        activities = [
            {
                "start_time": "09:00",
                "end_time": "12:00",
                "title": templates["morning"]["title"],
                "type": theme,
                "address": f"{destination}",
                "transportation": {
                    "from": "hotel",
                    "mode": "public transit",
                    "duration_min": 20,
                    "est_cost": 5
                },
                "notes": "Start early to avoid crowds",
                "booking_info": "Advance booking recommended",
                "accessibility": "wheelchair_friendly: true"
            },
            {
                "start_time": "14:00",
                "end_time": "17:00",
                "title": templates["afternoon"]["title"],
                "type": theme,
                "address": f"{destination} City Center",
                "transportation": {
                    "from": "previous location",
                    "mode": "walking",
                    "duration_min": 15,
                    "est_cost": 0
                },
                "notes": "Comfortable walking shoes recommended",
                "booking_info": "Walk-in available",
                "accessibility": "wheelchair_friendly: true"
            }
        ]

        meals = [
            {
                "time": "12:30",
                "suggestion": "Local Restaurant",
                "est_cost": daily_budget // 6,
                "dietary_notes": "vegetarian options available"
            },
            {
                "time": "19:00",
                "suggestion": "Traditional Cuisine",
                "est_cost": daily_budget // 4,
                "dietary_notes": "various dietary accommodations"
            }
        ]

        daily_plans.append({
            "day": day_num,
            "date": date_str,
            "summary": f"Day {day_num} in {destination}",
            "activities": activities,
            "meals": meals,
            "estimated_daily_cost": daily_budget,
            "alternative_options": [
                f"Alternative: Indoor activities if weather is poor",
                f"Backup: Museum visits"
            ]
        })

    # Create full itinerary
    itinerary = {
        "itinerary": {
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "timezone": "Local Time",
            "currency": "USD",
            "daily_plans": daily_plans,
            "total_estimated_cost": budget,
            "assumptions": [
                "Mid-range accommodation included",
                "Public transportation preferred",
                "Weather conditions favorable"
            ],
            "sources": [
                {"type": "static", "citation": "Travel guide database"}
            ],
            "packing_list": [
                "Comfortable walking shoes",
                "Weather-appropriate clothing",
                "Camera",
                "Travel adapter",
                "Reusable water bottle"
            ],
            "safety_notes": [
                "Keep valuables secure",
                "Stay aware of surroundings",
                "Keep emergency contacts handy"
            ]
        },
        "human_readable": f"Generated {num_days}-day itinerary for {destination} with focus on {', '.join(interests[:2])}. Total budget: ${budget}. Includes cultural activities, dining experiences, and practical travel tips."
    }

    return json.dumps(itinerary, indent=2)


def llm(prompt: str, system_prompt: Optional[str] = None, return_json: bool = True) -> str:
    """
    Mock LLM function that generates proper JSON
    In production, this would call actual LLM (TinyLlama or OpenAI)
    """

    # Check if OpenAI is available and configured
    if os.getenv("OPENAI_API_KEY"):
        try:
            return llm_with_openai(prompt, system_prompt, return_json)
        except Exception as e:
            print(f"⚠️  OpenAI failed, using mock: {e}")

    # Use mock generation
    print("📝 Using mock LLM (install transformers/torch or set OPENAI_API_KEY for real LLM)")
    return generate_mock_itinerary(prompt)


def llm_with_openai(prompt: str, system_prompt: Optional[str] = None, return_json: bool = True) -> str:
    """Use OpenAI API if available"""
    try:
        import openai

        openai.api_key = os.getenv("OPENAI_API_KEY")

        if system_prompt is None:
            system_prompt = "You are TripCraft, a professional travel itinerary assistant. Generate detailed, realistic travel plans in valid JSON format."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # Use newer API if available
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            generated_text = response.choices[0].message.content.strip()
        except (ImportError, AttributeError):
            # Fallback to older API
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            generated_text = response.choices[0].message.content.strip()

        if return_json:
            from tripcraft_config import extract_json_from_text
            try:
                json_data = extract_json_from_text(generated_text)
                return json.dumps(json_data, indent=2)
            except Exception:
                return generated_text

        return generated_text

    except ImportError:
        raise Exception("OpenAI package not installed. Run: pip install openai")
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
