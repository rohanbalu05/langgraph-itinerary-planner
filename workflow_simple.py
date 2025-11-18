"""
Simplified workflow without LangGraph dependency
Maintains the same functionality using simple function calls
"""
from typing import Dict, Any
from datetime import datetime
import os
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Import mock LLM
from llm_mock import llm
from tripcraft_config import (
    build_itinerary_prompt,
    validate_itinerary_json,
    extract_json_from_text
)

# Tavily is optional
try:
    from tavily import TavilyClient
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        tavily = TavilyClient(api_key=tavily_key)
        print("✅ Tavily search enabled")
    else:
        tavily = None
        print("⚠️  Tavily API key not set (search disabled)")
except:
    tavily = None
    print("⚠️  Tavily not available")

print("✅ Using mock LLM (transformers not available)")


class TravelPlanState:
    """State container for travel planning"""

    def __init__(self, preferences: Dict[str, Any]):
        self.preferences = preferences
        self.destination_info = ""
        self.itinerary = ""
        self.itinerary_json = {}
        self.weather = ""
        self.errors = []


def gather_preferences(state: TravelPlanState) -> TravelPlanState:
    """Step 1: Gather preferences (no-op, already in state)"""
    return state


def fetch_destination_info(state: TravelPlanState) -> TravelPlanState:
    """Step 2: Fetch destination information"""
    dest = state.preferences.get("destination", "")
    interests = state.preferences.get("interests", "")

    if not dest:
        state.destination_info = "Destination not specified."
        return state

    # Try Tavily if available
    if tavily:
        try:
            query = f"Top attractions and activities in {dest} for {interests}"
            info = tavily.search(query=query, max_results=3, search_depth="advanced")

            results = info.get("results", [])
            if results:
                snippets = []
                for result in results:
                    content = result.get("content", "")
                    if content:
                        snippets.append(content.strip())

                combined_info = " ".join(snippets)
                if len(combined_info) > 500:
                    combined_info = combined_info[:500]
                    last_space = combined_info.rfind(" ")
                    if last_space != -1:
                        combined_info = combined_info[:last_space] + "…"

                state.destination_info = combined_info
                return state
        except Exception as e:
            print(f"⚠️  Tavily search failed: {e}")

    # Fallback
    interests_str = ', '.join(interests) if isinstance(interests, list) else str(interests)
    state.destination_info = f"{dest} is a popular travel destination known for its attractions. Recommended activities based on your interests ({interests_str}): exploring local culture, visiting landmarks, enjoying local cuisine, and experiencing the unique atmosphere of the city."

    return state


def generate_itinerary(state: TravelPlanState) -> TravelPlanState:
    """Step 3: Generate itinerary using LLM"""
    dates = state.preferences.get('dates', "")

    try:
        start_date, end_date = dates.split(" to ")
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
    except (ValueError, AttributeError):
        num_days = 5

    try:
        # Build prompt
        prompt = build_itinerary_prompt(
            preferences=state.preferences,
            destination_info=state.destination_info,
            num_days=num_days
        )

        # Generate with LLM
        raw_output = llm(prompt, return_json=True)

        try:
            itinerary_data = json.loads(raw_output)
        except json.JSONDecodeError:
            itinerary_data = extract_json_from_text(raw_output)

        if not validate_itinerary_json(itinerary_data):
            fallback_itinerary = create_fallback_itinerary(
                state.preferences,
                num_days,
                "Generated itinerary did not match schema"
            )
            state.itinerary = format_itinerary_as_markdown(fallback_itinerary)
            state.itinerary_json = fallback_itinerary
            state.errors.append("Generated itinerary did not match schema, using fallback")
        else:
            state.itinerary = format_itinerary_as_markdown(itinerary_data)
            state.itinerary_json = itinerary_data

    except Exception as e:
        fallback_itinerary = create_fallback_itinerary(
            state.preferences,
            num_days,
            str(e)
        )
        state.itinerary = format_itinerary_as_markdown(fallback_itinerary)
        state.itinerary_json = fallback_itinerary
        state.errors.append(f"Error generating itinerary: {str(e)}")

    return state


def check_weather(state: TravelPlanState) -> TravelPlanState:
    """Step 4: Check weather forecast"""
    if tavily:
        try:
            query = (
                f"Weather forecast for {state.preferences['destination']} "
                f"on {state.preferences['dates']}"
            )
            weather_data = tavily.search(query=query, max_results=1)
            state.weather = weather_data["results"][0]["content"] if weather_data.get("results") else "No weather data found."
            return state
        except Exception as e:
            print(f"⚠️  Weather check failed: {e}")

    state.weather = "Weather information unavailable. Please check local weather services for your travel dates."
    return state


def create_fallback_itinerary(preferences: Dict[str, Any], num_days: int, error_info: str) -> Dict[str, Any]:
    """Create a basic fallback itinerary"""
    from datetime import timedelta

    destination = preferences.get('destination', 'Unknown Destination')
    dates = preferences.get('dates', '')
    budget = preferences.get('budget', 0)

    try:
        start_date = dates.split(' to ')[0]
    except Exception:
        start_date = datetime.now().strftime('%Y-%m-%d')

    daily_plans = []
    for day_num in range(1, num_days + 1):
        day_date = datetime.strptime(start_date, '%Y-%m-%d')
        day_date = day_date + timedelta(days=day_num - 1)

        daily_plans.append({
            "day": day_num,
            "date": day_date.strftime('%Y-%m-%d'),
            "summary": f"Day {day_num} in {destination}",
            "activities": [
                {
                    "start_time": "09:00",
                    "end_time": "12:00",
                    "title": f"Morning exploration of {destination}",
                    "type": "sightseeing",
                    "address": destination,
                    "notes": "Explore the main attractions"
                },
                {
                    "start_time": "14:00",
                    "end_time": "17:00",
                    "title": "Afternoon activities",
                    "type": "leisure",
                    "address": destination,
                    "notes": "Enjoy local culture"
                }
            ],
            "meals": [
                {"time": "12:30", "suggestion": "Local restaurant", "est_cost": 25},
                {"time": "19:00", "suggestion": "Dinner venue", "est_cost": 40}
            ],
            "estimated_daily_cost": int(budget / num_days) if budget else 150
        })

    return {
        "itinerary": {
            "destination": destination,
            "start_date": start_date,
            "end_date": daily_plans[-1]['date'] if daily_plans else start_date,
            "currency": "USD",
            "daily_plans": daily_plans,
            "total_estimated_cost": budget if budget else num_days * 150,
            "assumptions": ["Basic itinerary generated due to: " + error_info],
            "sources": [{"type": "fallback", "citation": "System generated"}]
        },
        "human_readable": f"Generated a basic {num_days}-day itinerary for {destination}. Please refine using the chat feature."
    }


def format_itinerary_as_markdown(itinerary_data: Dict[str, Any]) -> str:
    """Convert JSON itinerary to markdown"""
    try:
        itinerary = itinerary_data.get('itinerary', itinerary_data)
        lines = []

        lines.append(f"# {itinerary['destination']}")
        lines.append(f"**{itinerary['start_date']} to {itinerary['end_date']}**")
        lines.append(f"**Total Budget: {itinerary.get('currency', 'USD')} {itinerary['total_estimated_cost']}**\n")

        for day_plan in itinerary['daily_plans']:
            lines.append(f"## Day {day_plan['day']} - {day_plan['date']}")
            if day_plan.get('summary'):
                lines.append(f"*{day_plan['summary']}*\n")

            for activity in day_plan.get('activities', []):
                lines.append(f"### {activity['start_time']} - {activity['end_time']}: {activity['title']}")
                if activity.get('address'):
                    lines.append(f"📍 {activity['address']}")
                if activity.get('notes'):
                    lines.append(f"ℹ️ {activity['notes']}")
                lines.append("")

            if day_plan.get('meals'):
                lines.append("**Meals:**")
                for meal in day_plan['meals']:
                    lines.append(f"- {meal['time']}: {meal['suggestion']} (${meal.get('est_cost', 0)})")
                lines.append("")

            lines.append(f"💰 **Daily Cost: ${day_plan.get('estimated_daily_cost', 0)}**\n")

        if itinerary.get('safety_notes'):
            lines.append("## Safety Notes")
            for note in itinerary['safety_notes']:
                lines.append(f"- {note}")
            lines.append("")

        if itinerary.get('packing_list'):
            lines.append("## Packing List")
            for item in itinerary['packing_list']:
                lines.append(f"- {item}")

        return "\n".join(lines)

    except Exception as e:
        return f"Error formatting itinerary: {str(e)}\n\nRaw data: {json.dumps(itinerary_data, indent=2)}"


class SimpleWorkflowApp:
    """Simple workflow executor"""

    def invoke(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow"""
        # Create state
        state = TravelPlanState(initial_state.get("preferences", {}))

        # Run steps in sequence
        state = gather_preferences(state)
        state = fetch_destination_info(state)
        state = generate_itinerary(state)
        state = check_weather(state)

        # Return as dict
        return {
            "preferences": state.preferences,
            "destination_info": state.destination_info,
            "itinerary": state.itinerary,
            "itinerary_json": state.itinerary_json,
            "weather": state.weather,
            "errors": state.errors
        }


# Create app instance
app = SimpleWorkflowApp()

print("✅ Simple workflow initialized (no LangGraph)")
