"""
TripCraft Configuration Module
Centralizes system prompts and JSON schemas for itinerary generation
"""
import json
from typing import Dict, Any

TRIPCRAFT_SYSTEM_PROMPT = """You are **TripCraft**, a professional travel itinerary assistant.

Your primary function is to create high-quality, realistic, personalized day-by-day travel itineraries and support conversational editing.

## Core Objectives

**Primary Goal**: Generate detailed, actionable day-by-day travel itineraries tailored to user preferences with structured JSON output.

**Quality Standards**:
- Use accurate local opening hours, cultural norms, and seasonal considerations
- Account for rush hours, religious closures, and local customs
- Include realistic travel times with 15-30 minute buffers between nearby activities
- Balance activity intensity with rest periods
- Provide both budget and premium alternatives

## Output Format

You MUST respond with a JSON object following this exact schema:

```json
{
  "itinerary": {
    "destination": "City, Country",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "timezone": "Region/City",
    "currency": "XXX",
    "daily_plans": [
      {
        "day": 1,
        "date": "YYYY-MM-DD",
        "summary": "Brief day overview",
        "activities": [
          {
            "start_time": "HH:MM",
            "end_time": "HH:MM",
            "title": "Activity Name",
            "type": "category",
            "address": "Full address",
            "transportation": {
              "from": "previous location",
              "mode": "transport type",
              "duration_min": 30,
              "est_cost": 100
            },
            "notes": "Important details, tips, or warnings",
            "booking_info": "Reservation requirements or links",
            "accessibility": "wheelchair_friendly: true/false"
          }
        ],
        "meals": [
          {
            "time": "HH:MM",
            "suggestion": "Restaurant name and dish type",
            "est_cost": 50,
            "dietary_notes": "vegetarian/halal/etc options"
          }
        ],
        "estimated_daily_cost": 500,
        "alternative_options": ["Backup plans for weather/closures"]
      }
    ],
    "total_estimated_cost": 2000,
    "assumptions": ["List any assumptions made due to missing data"],
    "sources": [{"type": "web/static", "citation": "Source description"}],
    "packing_list": ["Essential items for this trip"],
    "safety_notes": ["Important safety considerations"]
  },
  "human_readable": "Concise summary with booking recommendations and next steps"
}
```

## Communication Style
- Tone: Friendly, expert, and concise
- Clarity: Use clear, actionable language
- Safety: Always include relevant safety considerations
"""

ITINERARY_JSON_SCHEMA = {
    "type": "object",
    "required": ["itinerary", "human_readable"],
    "properties": {
        "itinerary": {
            "type": "object",
            "required": ["destination", "start_date", "end_date", "daily_plans"],
            "properties": {
                "destination": {"type": "string"},
                "start_date": {"type": "string", "format": "date"},
                "end_date": {"type": "string", "format": "date"},
                "timezone": {"type": "string"},
                "currency": {"type": "string"},
                "daily_plans": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["day", "date", "activities"],
                        "properties": {
                            "day": {"type": "integer"},
                            "date": {"type": "string", "format": "date"},
                            "summary": {"type": "string"},
                            "activities": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["title", "start_time", "end_time"],
                                    "properties": {
                                        "start_time": {"type": "string"},
                                        "end_time": {"type": "string"},
                                        "title": {"type": "string"},
                                        "type": {"type": "string"},
                                        "address": {"type": "string"},
                                        "notes": {"type": "string"},
                                        "booking_info": {"type": "string"}
                                    }
                                }
                            },
                            "meals": {"type": "array"},
                            "estimated_daily_cost": {"type": "number"},
                            "alternative_options": {"type": "array"}
                        }
                    }
                },
                "total_estimated_cost": {"type": "number"},
                "assumptions": {"type": "array"},
                "sources": {"type": "array"},
                "packing_list": {"type": "array"},
                "safety_notes": {"type": "array"}
            }
        },
        "human_readable": {"type": "string"}
    }
}

EDIT_DELTA_SCHEMA = {
    "type": "object",
    "properties": {
        "delta": {
            "type": "object",
            "properties": {
                "changes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["type", "target", "reason"],
                        "properties": {
                            "type": {"type": "string", "enum": ["add", "remove", "modify", "move"]},
                            "target": {"type": "string"},
                            "before": {"type": "object"},
                            "after": {"type": "object"},
                            "reason": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
}


def build_itinerary_prompt(preferences: Dict[str, Any], destination_info: str, num_days: int) -> str:
    """Build a comprehensive prompt for itinerary generation"""

    destination = preferences.get('destination', 'Unknown')
    budget = preferences.get('budget', 'Not specified')
    interests = preferences.get('interests', [])
    dates = preferences.get('dates', 'Not specified')

    interests_str = ', '.join(interests) if isinstance(interests, list) else str(interests)

    prompt = f"""{TRIPCRAFT_SYSTEM_PROMPT}

## User Request

Generate a {num_days}-day itinerary for:
- **Destination**: {destination}
- **Dates**: {dates}
- **Budget**: ${budget}
- **Interests**: {interests_str}

## Available Information
{destination_info}

## Your Task

Create a detailed, realistic itinerary following the JSON schema above. Include:
1. Specific activity times and durations
2. Realistic travel times between locations
3. Cost estimates per activity
4. Meal suggestions with prices
5. Transportation details
6. Booking information where needed
7. Safety notes and packing list
8. Alternative options for flexibility

Return ONLY valid JSON matching the schema. Do not include markdown code fences or explanations.
"""

    return prompt


def build_edit_prompt(message: str, current_itinerary: Dict[str, Any]) -> str:
    """Build prompt for conversational editing"""

    prompt = f"""You are TripCraft, processing an edit request for an existing itinerary.

## Current Itinerary Summary
Destination: {current_itinerary.get('destination', 'Unknown')}
Days: {len(current_itinerary.get('daily_plans', []))}

## User Edit Request
"{message}"

## Your Task

1. Parse the user's intent (add/remove/modify/move)
2. Identify the target (which day, which activity, what attribute)
3. Generate an edit command with high confidence
4. Provide a human-readable preview of the change

Return JSON in this format:
{{
    "intent": "add|remove|modify|move",
    "entities": {{
        "day": 1,
        "time_slot": "morning",
        "poi": "Eiffel Tower",
        "activity_id": "act_123"
    }},
    "edit_command": {{
        "action": "add",
        "target": "activity",
        "day": 1,
        "poi": "Eiffel Tower",
        "time_slot": "morning"
    }},
    "confidence": 0.85,
    "human_preview": "Add Eiffel Tower to Day 1 morning schedule"
}}
"""

    return prompt


def validate_itinerary_json(data: Any) -> bool:
    """Validate itinerary JSON against schema"""
    try:
        if not isinstance(data, dict):
            return False

        if 'itinerary' not in data or 'human_readable' not in data:
            return False

        itinerary = data['itinerary']
        required_fields = ['destination', 'start_date', 'end_date', 'daily_plans']

        for field in required_fields:
            if field not in itinerary:
                return False

        if not isinstance(itinerary['daily_plans'], list):
            return False

        return True
    except Exception:
        return False


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from text that may contain markdown or extra text"""
    import re

    text = text.strip()

    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)

    text = re.sub(r'^```.*?\n', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n```$', '', text)

    text = text.strip()

    if text.startswith('{') or text.startswith('['):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not extract valid JSON from text")
