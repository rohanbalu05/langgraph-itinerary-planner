from langgraph.graph import StateGraph, END
from tavily import TavilyClient
from typing import TypedDict, Dict, Any
from datetime import datetime
import os
import json
from dotenv import load_dotenv

from llm import llm
from tripcraft_config import (
    build_itinerary_prompt,
    validate_itinerary_json,
    extract_json_from_text
)  # our TinyLlama-based LLM function

# Load environment variables
load_dotenv()

# Tavily API client
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class TravelPlanState(TypedDict):
    preferences: dict
    destination_info: str
    itinerary: str
    itinerary_json: dict
    weather: str
    errors: list


# Step 1: Gather preferences
def gather_preferences(state: TravelPlanState):
    return {"preferences": state["preferences"]}


# Step 2: Fetch destination info
def fetch_destination_info(state: TravelPlanState):
    dest = state["preferences"].get("destination", "")
    interests = state["preferences"].get("interests", "")
    if not dest:
        return {"destination_info": "Destination not specified."}

    query = f"Top attractions and activities in {dest} for {interests}"
    info = tavily.search(query=query, max_results=3, search_depth="advanced")

    results = info.get("results", [])
    if not results:
        return {"destination_info": f"No information found for {dest}."}

    # Merge results into a paragraph, respecting sentence boundaries
    snippets = []
    for result in results:
        content = result.get("content", "")
        if content:
            snippets.append(content.strip())

    combined_info = " ".join(snippets)
    # Optional: you could truncate by sentences rather than characters
    if len(combined_info) > 500:
        combined_info = combined_info[:500]
        # Optionally avoid cutting mid-word
        last_space = combined_info.rfind(" ")
        if last_space != -1:
            combined_info = combined_info[:last_space] + "…"

    return {"destination_info": combined_info}



def generate_itinerary(state: TravelPlanState):
    """Generate itinerary using TripCraft JSON format"""
    dates = state['preferences'].get('dates', "")
    try:
        start_date, end_date = dates.split(" to ")
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1
    except (ValueError, AttributeError):
        num_days = 5

    prompt = build_itinerary_prompt(
        preferences=state['preferences'],
        destination_info=state['destination_info'],
        num_days=num_days
    )

    try:
        raw_output = llm(prompt, return_json=True)

        try:
            itinerary_data = json.loads(raw_output)
        except json.JSONDecodeError:
            itinerary_data = extract_json_from_text(raw_output)

        if not validate_itinerary_json(itinerary_data):
            fallback_itinerary = create_fallback_itinerary(
                state['preferences'],
                num_days,
                raw_output
            )
            return {
                "itinerary": format_itinerary_as_markdown(fallback_itinerary),
                "itinerary_json": fallback_itinerary,
                "errors": ["Generated itinerary did not match schema, using fallback"]
            }

        markdown_output = format_itinerary_as_markdown(itinerary_data)

        return {
            "itinerary": markdown_output,
            "itinerary_json": itinerary_data,
            "errors": []
        }

    except Exception as e:
        fallback_itinerary = create_fallback_itinerary(
            state['preferences'],
            num_days,
            str(e)
        )
        return {
            "itinerary": format_itinerary_as_markdown(fallback_itinerary),
            "itinerary_json": fallback_itinerary,
            "errors": [f"Error generating itinerary: {str(e)}"]
        }


def create_fallback_itinerary(preferences: Dict[str, Any], num_days: int, error_info: str) -> Dict[str, Any]:
    """Create a basic fallback itinerary when generation fails"""
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
        day_date = day_date.replace(day=day_date.day + day_num - 1)

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
    """Convert JSON itinerary to markdown format for display"""
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


# Step 4: Fetch weather
def check_weather(state: TravelPlanState):
    query = (
        f"Weather forecast for {state['preferences']['destination']} "
        f"on {state['preferences']['dates']}"
    )
    weather_data = tavily.search(query=query, max_results=1)
    weather_text = weather_data["results"][0]["content"] if weather_data.get("results") else "No weather data found."
    return {"weather": weather_text}


# Build the workflow graph
workflow = StateGraph(TravelPlanState)
workflow.add_node("gather_preferences", gather_preferences)
workflow.add_node("fetch_info", fetch_destination_info)
workflow.add_node("generate_itinerary", generate_itinerary)
workflow.add_node("check_weather", check_weather)

# Define flow
workflow.add_edge("gather_preferences", "fetch_info")
workflow.add_edge("fetch_info", "generate_itinerary")
workflow.add_edge("generate_itinerary", "check_weather")

# Entry and exit
workflow.set_entry_point("gather_preferences")
workflow.add_edge("check_weather", END)

# Compile app
app = workflow.compile()
