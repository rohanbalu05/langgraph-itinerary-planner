from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
import json
import uuid
from datetime import datetime
from backend.supabase_client import supabase


class EditableItineraryState(TypedDict):
    preferences: dict
    destination_info: str
    itinerary: str
    weather: str
    itinerary_id: str
    structured_content: dict
    edit_history: list
    pending_edit: dict


async def save_itinerary_to_db(state: EditableItineraryState):
    try:
        itinerary_data = {
            "id": state.get("itinerary_id") or str(uuid.uuid4()),
            "user_id": state.get("preferences", {}).get("user_id"),
            "destination": state["preferences"]["destination"],
            "budget": state["preferences"]["budget"],
            "interests": state["preferences"]["interests"],
            "dates": state["preferences"]["dates"],
            "content": state.get("structured_content", {}),
            "updated_at": datetime.now().isoformat()
        }

        existing = await supabase.table("itineraries") \
            .select("id") \
            .eq("id", itinerary_data["id"]) \
            .maybeSingle() \
            .execute()

        if existing.data:
            await supabase.table("itineraries") \
                .update(itinerary_data) \
                .eq("id", itinerary_data["id"]) \
                .execute()
        else:
            await supabase.table("itineraries").insert(itinerary_data).execute()

        return {"itinerary_id": itinerary_data["id"]}

    except Exception as e:
        print(f"Error saving itinerary: {e}")
        return {"itinerary_id": state.get("itinerary_id")}


def structure_itinerary(state: EditableItineraryState):
    raw_itinerary = state.get("itinerary", "")

    structured = {
        "days": [],
        "total_budget": state["preferences"]["budget"],
        "destination": state["preferences"]["destination"]
    }

    import re
    day_sections = re.split(r'### Day (\d+)', raw_itinerary)

    for i in range(1, len(day_sections), 2):
        if i + 1 < len(day_sections):
            day_num = int(day_sections[i])
            day_content = day_sections[i + 1]

            activities = []

            morning_match = re.search(r'Morning[:\s]*(.+?)(?=Afternoon|Evening|💰|$)', day_content, re.DOTALL)
            afternoon_match = re.search(r'Afternoon[:\s]*(.+?)(?=Evening|💰|$)', day_content, re.DOTALL)
            evening_match = re.search(r'Evening[:\s]*(.+?)(?=💰|$)', day_content, re.DOTALL)

            if morning_match:
                activities.append({
                    "id": f"act_{uuid.uuid4().hex[:8]}",
                    "name": morning_match.group(1).strip(),
                    "time_slot": "morning",
                    "duration": "3 hours",
                    "cost": 0
                })

            if afternoon_match:
                activities.append({
                    "id": f"act_{uuid.uuid4().hex[:8]}",
                    "name": afternoon_match.group(1).strip(),
                    "time_slot": "afternoon",
                    "duration": "3 hours",
                    "cost": 0
                })

            if evening_match:
                activities.append({
                    "id": f"act_{uuid.uuid4().hex[:8]}",
                    "name": evening_match.group(1).strip(),
                    "time_slot": "evening",
                    "duration": "2 hours",
                    "cost": 0
                })

            structured["days"].append({
                "day_number": day_num,
                "activities": activities
            })

    return {"structured_content": structured}


async def apply_pending_edit(state: EditableItineraryState):
    pending_edit = state.get("pending_edit", {})

    if not pending_edit:
        return {}

    current_content = state.get("structured_content", {})
    action = pending_edit.get("action")
    target = pending_edit.get("target")

    updated_content = json.loads(json.dumps(current_content))

    if action == "add" and target == "activity":
        day_num = pending_edit.get("day", 1)
        day_index = day_num - 1

        if day_index < len(updated_content.get("days", [])):
            new_activity = {
                "id": f"act_{uuid.uuid4().hex[:8]}",
                "name": pending_edit.get("poi", "New Activity"),
                "time_slot": pending_edit.get("time_slot", "morning"),
                "duration": pending_edit.get("duration", "2 hours"),
                "cost": 0
            }
            updated_content["days"][day_index]["activities"].append(new_activity)

    elif action == "remove" and target == "activity":
        day_num = pending_edit.get("day")
        poi = pending_edit.get("poi")

        if day_num:
            day_index = day_num - 1
            if day_index < len(updated_content.get("days", [])):
                activities = updated_content["days"][day_index]["activities"]
                updated_content["days"][day_index]["activities"] = [
                    act for act in activities if act.get("name") != poi
                ]

    edit_history = state.get("edit_history", [])
    edit_history.append({
        "timestamp": datetime.now().isoformat(),
        "edit": pending_edit,
        "before": current_content
    })

    return {
        "structured_content": updated_content,
        "edit_history": edit_history,
        "pending_edit": {}
    }


def create_extended_workflow():
    workflow = StateGraph(EditableItineraryState)

    workflow.add_node("structure_itinerary", structure_itinerary)
    workflow.add_node("save_to_db", save_itinerary_to_db)
    workflow.add_node("apply_edit", apply_pending_edit)

    return workflow
