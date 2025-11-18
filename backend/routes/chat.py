from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx
import uuid
import os
from datetime import datetime
import json
from backend.supabase_client import supabase
from tripcraft_config import build_edit_prompt, extract_json_from_text

router = APIRouter(prefix="/api/chat", tags=["chat"])

NLP_SERVICE_URL = "http://localhost:8001"
USE_OPENAI_FALLBACK = os.getenv("OPENAI_API_KEY") is not None


class ChatMessageRequest(BaseModel):
    itinerary_id: str
    message: str
    user_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    needs_confirmation: bool
    needs_clarification: bool
    session_id: str


class ApplyEditRequest(BaseModel):
    itinerary_id: str
    edit_command: Dict[str, Any]
    user_id: Optional[str] = None


class ApplyEditResponse(BaseModel):
    success: bool
    change_id: str
    diff: Dict[str, Any]
    updated_itinerary: Dict[str, Any]
    message: str


class UndoEditRequest(BaseModel):
    change_id: str
    itinerary_id: str
    user_id: Optional[str] = None


class UndoEditResponse(BaseModel):
    success: bool
    reverted_itinerary: Dict[str, Any]
    message: str


@router.post("/message", response_model=ChatMessageResponse)
async def process_chat_message(
    request: ChatMessageRequest,
    authorization: Optional[str] = Header(None)
):
    try:
        response = await supabase.table("itineraries").select("*").eq("id", request.itinerary_id).maybeSingle().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Itinerary not found")

        itinerary = response.data

        parsed = None
        fallback_used = False

        try:
            async with httpx.AsyncClient() as client:
                nlp_response = await client.post(
                    f"{NLP_SERVICE_URL}/parse",
                    json={
                        "message": request.message,
                        "context": {"itinerary": itinerary}
                    },
                    timeout=4.0
                )

                if nlp_response.status_code == 200:
                    parsed = nlp_response.json()
        except (httpx.RequestError, httpx.TimeoutException):
            if USE_OPENAI_FALLBACK:
                fallback_used = True
                parsed = await parse_with_openai_fallback(
                    request.message,
                    itinerary.get('content', {})
                )
            else:
                raise HTTPException(
                    status_code=503,
                    detail="NLP service unavailable and no fallback configured"
                )

        if not parsed:
            raise HTTPException(
                status_code=500,
                detail="Could not parse message"
            )

        confidence = parsed.get("confidence", 0.0)
        intent = parsed.get("intent")

        needs_confirmation = 0.4 <= confidence < 0.7
        needs_clarification = confidence < 0.4 or intent == "clarify"

        suggestions = [{
            "intent": parsed["intent"],
            "entities": parsed["entities"],
            "edit_command": parsed["edit_command"],
            "confidence": confidence,
            "human_preview": parsed["human_preview"]
        }]

        session_response = await supabase.table("chat_sessions") \
            .select("*") \
            .eq("itinerary_id", request.itinerary_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .maybeSingle() \
            .execute()

        if session_response.data:
            session_id = session_response.data["id"]
            messages = session_response.data.get("messages", [])
            messages.append({
                "role": "user",
                "content": request.message,
                "timestamp": datetime.now().isoformat(),
                "parsed": parsed
            })

            await supabase.table("chat_sessions") \
                .update({
                    "messages": messages,
                    "last_message_at": datetime.now().isoformat()
                }) \
                .eq("id", session_id) \
                .execute()
        else:
            session_data = {
                "itinerary_id": request.itinerary_id,
                "user_id": request.user_id,
                "messages": [{
                    "role": "user",
                    "content": request.message,
                    "timestamp": datetime.now().isoformat(),
                    "parsed": parsed
                }],
                "last_message_at": datetime.now().isoformat()
            }
            session_result = await supabase.table("chat_sessions").insert(session_data).execute()
            session_id = session_result.data[0]["id"]

        return ChatMessageResponse(
            suggestions=suggestions,
            needs_confirmation=needs_confirmation,
            needs_clarification=needs_clarification,
            session_id=session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-edit", response_model=ApplyEditResponse)
async def apply_edit(request: ApplyEditRequest):
    try:
        response = await supabase.table("itineraries").select("*").eq("id", request.itinerary_id).maybeSingle().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Itinerary not found")

        current_itinerary = response.data
        before_snapshot = current_itinerary["content"]

        updated_content = _apply_edit_command(
            before_snapshot,
            request.edit_command
        )

        change_id = f"change_{uuid.uuid4().hex[:8]}"

        await supabase.table("itineraries") \
            .update({
                "content": updated_content,
                "updated_at": datetime.now().isoformat()
            }) \
            .eq("id", request.itinerary_id) \
            .execute()

        edit_record = {
            "change_id": change_id,
            "itinerary_id": request.itinerary_id,
            "user_id": request.user_id,
            "intent": request.edit_command.get("action", "unknown"),
            "entities": {},
            "edit_command": request.edit_command,
            "before_snapshot": before_snapshot,
            "after_snapshot": updated_content,
            "confidence": 1.0,
            "status": "applied"
        }

        await supabase.table("itinerary_edits").insert(edit_record).execute()

        diff = _compute_diff(before_snapshot, updated_content)

        return ApplyEditResponse(
            success=True,
            change_id=change_id,
            diff=diff,
            updated_itinerary=updated_content,
            message="Edit applied successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/undo", response_model=UndoEditResponse)
async def undo_edit(request: UndoEditRequest):
    try:
        edit_response = await supabase.table("itinerary_edits") \
            .select("*") \
            .eq("change_id", request.change_id) \
            .maybeSingle() \
            .execute()

        if not edit_response.data:
            raise HTTPException(status_code=404, detail="Edit not found")

        edit_record = edit_response.data

        if edit_record["status"] == "reverted":
            raise HTTPException(status_code=400, detail="Edit already reverted")

        before_snapshot = edit_record["before_snapshot"]

        await supabase.table("itineraries") \
            .update({
                "content": before_snapshot,
                "updated_at": datetime.now().isoformat()
            }) \
            .eq("id", request.itinerary_id) \
            .execute()

        await supabase.table("itinerary_edits") \
            .update({
                "status": "reverted",
                "reverted_at": datetime.now().isoformat()
            }) \
            .eq("change_id", request.change_id) \
            .execute()

        return UndoEditResponse(
            success=True,
            reverted_itinerary=before_snapshot,
            message="Edit reverted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _apply_edit_command(itinerary: Dict, command: Dict) -> Dict:
    action = command.get("action")
    target = command.get("target")

    updated = json.loads(json.dumps(itinerary))

    if action == "add" and target == "activity":
        day_num = command.get("day", 1)
        day_key = f"day_{day_num}"

        if day_key not in updated:
            updated[day_key] = {"activities": []}

        new_activity = {
            "id": f"act_{uuid.uuid4().hex[:8]}",
            "name": command.get("poi", "New Activity"),
            "time_slot": command.get("time_slot", "morning"),
            "duration": command.get("duration", "2 hours"),
            "cost": 0
        }

        if "activities" not in updated[day_key]:
            updated[day_key]["activities"] = []

        updated[day_key]["activities"].append(new_activity)

    elif action == "remove" and target == "activity":
        day_num = command.get("day")
        poi = command.get("poi")
        activity_id = command.get("activity_id")

        if day_num:
            day_key = f"day_{day_num}"
            if day_key in updated and "activities" in updated[day_key]:
                activities = updated[day_key]["activities"]
                updated[day_key]["activities"] = [
                    act for act in activities
                    if act.get("id") != activity_id and act.get("name") != poi
                ]

    elif action == "update" and target == "budget":
        updated["total_budget"] = command.get("amount", updated.get("total_budget", 0))

    elif action == "update" and target == "hotel":
        day_num = command.get("day")
        hotel_name = command.get("hotel_name")

        if day_num:
            day_key = f"day_{day_num}"
            if day_key not in updated:
                updated[day_key] = {}
            updated[day_key]["hotel"] = hotel_name
        else:
            updated["default_hotel"] = hotel_name

    elif action == "update" and target == "time":
        day_num = command.get("day")
        new_time = command.get("new_time")
        poi = command.get("poi")

        if day_num and new_time:
            day_key = f"day_{day_num}"
            if day_key in updated and "activities" in updated[day_key]:
                for activity in updated[day_key]["activities"]:
                    if activity.get("name") == poi:
                        activity["time_slot"] = new_time
                        break

    return updated


def _compute_diff(before: Dict, after: Dict) -> Dict:
    """Compute delta changes between two itinerary versions"""
    diff = {
        "added": [],
        "removed": [],
        "modified": [],
        "delta": {
            "changes": []
        }
    }

    before_keys = set(before.keys())
    after_keys = set(after.keys())

    for key in after_keys - before_keys:
        diff["added"].append({"key": key, "value": after[key]})
        diff["delta"]["changes"].append({
            "type": "add",
            "target": key,
            "before": None,
            "after": after[key],
            "reason": f"Added new field: {key}"
        })

    for key in before_keys - after_keys:
        diff["removed"].append({"key": key, "value": before[key]})
        diff["delta"]["changes"].append({
            "type": "remove",
            "target": key,
            "before": before[key],
            "after": None,
            "reason": f"Removed field: {key}"
        })

    for key in before_keys & after_keys:
        if before[key] != after[key]:
            diff["modified"].append({
                "key": key,
                "before": before[key],
                "after": after[key]
            })
            diff["delta"]["changes"].append({
                "type": "modify",
                "target": key,
                "before": before[key],
                "after": after[key],
                "reason": f"Modified field: {key}"
            })

    return diff


async def parse_with_openai_fallback(message: str, itinerary: Dict[str, Any]) -> Dict[str, Any]:
    """Use OpenAI as fallback for NLP parsing"""
    try:
        import openai

        openai.api_key = os.getenv("OPENAI_API_KEY")

        prompt = build_edit_prompt(message, itinerary)

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are TripCraft's NLP parser. Parse user edit requests and return structured JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )

        result_text = response.choices[0].message.content.strip()
        parsed_data = extract_json_from_text(result_text)

        return parsed_data

    except ImportError:
        raise Exception("OpenAI package not installed. Run: pip install openai")
    except Exception as e:
        return {
            "intent": "unknown",
            "entities": {},
            "edit_command": {"action": "unknown"},
            "confidence": 0.2,
            "human_preview": f"Could not parse: {message}",
            "error": str(e)
        }
