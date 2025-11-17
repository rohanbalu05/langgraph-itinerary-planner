from typing import Any, Dict, List, Text
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rapidfuzz import fuzz
import json


class ActionParseIntent(Action):
    def name(self) -> Text:
        return "action_parse_intent"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get("intent", {}).get("name")
        entities = tracker.latest_message.get("entities", [])
        confidence = tracker.latest_message.get("intent", {}).get("confidence", 0.0)

        entity_dict = {}
        for entity in entities:
            entity_type = entity.get("entity")
            entity_value = entity.get("value")
            entity_dict[entity_type] = entity_value

        edit_command = self._build_edit_command(intent, entity_dict)
        human_preview = self._generate_human_preview(intent, entity_dict)

        result = {
            "intent": intent,
            "entities": entity_dict,
            "edit_command": edit_command,
            "confidence": confidence,
            "human_preview": human_preview
        }

        dispatcher.utter_message(json=result)
        return []

    def _build_edit_command(self, intent: str, entities: Dict) -> Dict:
        if intent == "add_activity":
            return {
                "action": "add",
                "target": "activity",
                "poi": entities.get("poi"),
                "day": self._parse_day(entities.get("day")),
                "time_slot": entities.get("time_slot"),
                "duration": entities.get("duration")
            }

        elif intent == "remove_activity":
            return {
                "action": "remove",
                "target": "activity",
                "poi": entities.get("poi"),
                "day": self._parse_day(entities.get("day")),
                "time_slot": entities.get("time_slot"),
                "activity_id": entities.get("activity_id")
            }

        elif intent == "move_activity":
            return {
                "action": "move",
                "target": "activity",
                "poi": entities.get("poi"),
                "activity_id": entities.get("activity_id"),
                "from_day": self._parse_day(entities.get("day")),
                "to_day": self._parse_day(entities.get("day", [])[1] if isinstance(entities.get("day"), list) else None),
                "from_time": entities.get("time_slot"),
                "to_time": entities.get("time_slot", [])[1] if isinstance(entities.get("time_slot"), list) else None
            }

        elif intent == "change_time":
            return {
                "action": "update",
                "target": "time",
                "poi": entities.get("poi"),
                "activity_id": entities.get("activity_id"),
                "day": self._parse_day(entities.get("day")),
                "new_time": entities.get("time_slot")
            }

        elif intent == "change_hotel":
            return {
                "action": "update",
                "target": "hotel",
                "day": self._parse_day(entities.get("day")),
                "hotel_name": entities.get("hotel_name")
            }

        elif intent == "change_transport":
            return {
                "action": "update",
                "target": "transport",
                "day": self._parse_day(entities.get("day")),
                "transport_mode": entities.get("transport_mode")
            }

        elif intent == "update_cost":
            return {
                "action": "update",
                "target": "budget",
                "amount": self._parse_amount(entities.get("amount"))
            }

        elif intent == "combine_days":
            return {
                "action": "combine",
                "target": "days",
                "days": self._parse_day_list(entities.get("day"))
            }

        elif intent == "split_day":
            return {
                "action": "split",
                "target": "day",
                "day": self._parse_day(entities.get("day"))
            }

        elif intent in ["confirm", "cancel", "clarify"]:
            return {
                "action": intent,
                "target": None
            }

        return {"action": "unknown", "target": None}

    def _parse_day(self, day_value) -> int:
        if not day_value:
            return None
        if isinstance(day_value, int):
            return day_value
        if isinstance(day_value, str):
            import re
            match = re.search(r'\d+', day_value)
            if match:
                return int(match.group())
        return None

    def _parse_day_list(self, day_value) -> List[int]:
        if not day_value:
            return []
        if isinstance(day_value, list):
            return [self._parse_day(d) for d in day_value]
        return [self._parse_day(day_value)]

    def _parse_amount(self, amount_value) -> float:
        if not amount_value:
            return None
        if isinstance(amount_value, (int, float)):
            return float(amount_value)
        if isinstance(amount_value, str):
            import re
            amount_value = amount_value.replace('$', '').replace(',', '')
            match = re.search(r'\d+\.?\d*', amount_value)
            if match:
                return float(match.group())
        return None

    def _generate_human_preview(self, intent: str, entities: Dict) -> str:
        if intent == "add_activity":
            poi = entities.get("poi", "activity")
            day = entities.get("day", "itinerary")
            time = entities.get("time_slot", "")
            time_str = f" in the {time}" if time else ""
            return f"Add {poi} to {day}{time_str}"

        elif intent == "remove_activity":
            poi = entities.get("poi", "activity")
            day = entities.get("day", "")
            day_str = f" from {day}" if day else ""
            return f"Remove {poi}{day_str}"

        elif intent == "move_activity":
            poi = entities.get("poi", "activity")
            return f"Move {poi} to a different time/day"

        elif intent == "change_time":
            poi = entities.get("poi", "activity")
            time = entities.get("time_slot", "new time")
            return f"Change {poi} to {time}"

        elif intent == "change_hotel":
            hotel = entities.get("hotel_name", "new hotel")
            return f"Change accommodation to {hotel}"

        elif intent == "change_transport":
            mode = entities.get("transport_mode", "new mode")
            return f"Change transport to {mode}"

        elif intent == "update_cost":
            amount = entities.get("amount", "amount")
            return f"Update budget to {amount}"

        elif intent == "combine_days":
            return "Combine multiple days"

        elif intent == "split_day":
            day = entities.get("day", "day")
            return f"Split {day} into multiple parts"

        return "Process your request"


def fuzzy_match_poi(user_input: str, available_pois: List[str], threshold: int = 70) -> str:
    best_match = None
    best_score = 0

    for poi in available_pois:
        score = fuzz.ratio(user_input.lower(), poi.lower())
        if score > best_score and score >= threshold:
            best_score = score
            best_match = poi

    return best_match
