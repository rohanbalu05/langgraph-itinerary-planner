from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import json
import re
from typing import Dict, Any


class FlanT5Parser:
    def __init__(self, model_name: str = "google/flan-t5-small"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def parse(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        prompt = self._build_prompt(user_message, context)

        inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.3,
                do_sample=True,
                top_p=0.9
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        try:
            parsed_result = self._parse_response(response)
            parsed_result["confidence"] = self._estimate_confidence(user_message, parsed_result)
            return parsed_result
        except Exception as e:
            return {
                "intent": "clarify",
                "entities": {},
                "edit_command": {"action": "clarify", "target": None},
                "confidence": 0.2,
                "human_preview": "I need more information to understand your request",
                "error": str(e)
            }

    def _build_prompt(self, user_message: str, context: Dict = None) -> str:
        few_shot_examples = """
Task: Parse travel itinerary editing requests into structured JSON commands.

Example 1:
Input: "add Eiffel Tower to day 2 in the morning"
Output: {"intent": "add_activity", "entities": {"poi": "Eiffel Tower", "day": "2", "time_slot": "morning"}, "action": "add"}

Example 2:
Input: "remove the Louvre Museum from day 1"
Output: {"intent": "remove_activity", "entities": {"poi": "Louvre Museum", "day": "1"}, "action": "remove"}

Example 3:
Input: "move dinner to 7pm"
Output: {"intent": "change_time", "entities": {"poi": "dinner", "time_slot": "7pm"}, "action": "update"}

Example 4:
Input: "change hotel to Hilton Paris"
Output: {"intent": "change_hotel", "entities": {"hotel_name": "Hilton Paris"}, "action": "update"}

Example 5:
Input: "increase budget by $500"
Output: {"intent": "update_cost", "entities": {"amount": "500"}, "action": "update"}

Now parse this request:
Input: "{user_message}"
Output:"""

        return few_shot_examples.format(user_message=user_message)

    def _parse_response(self, response: str) -> Dict[str, Any]:
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                parsed = json.loads(response)

            intent = parsed.get("intent", "clarify")
            entities = parsed.get("entities", {})
            action = parsed.get("action", "unknown")

            edit_command = self._build_edit_command(intent, entities, action)
            human_preview = self._generate_preview(intent, entities)

            return {
                "intent": intent,
                "entities": entities,
                "edit_command": edit_command,
                "human_preview": human_preview
            }
        except json.JSONDecodeError:
            return self._fallback_parse(response)

    def _build_edit_command(self, intent: str, entities: Dict, action: str) -> Dict:
        command = {"action": action}

        if intent == "add_activity":
            command.update({
                "target": "activity",
                "poi": entities.get("poi"),
                "day": self._extract_number(entities.get("day")),
                "time_slot": entities.get("time_slot"),
                "duration": entities.get("duration")
            })
        elif intent == "remove_activity":
            command.update({
                "target": "activity",
                "poi": entities.get("poi"),
                "day": self._extract_number(entities.get("day")),
                "time_slot": entities.get("time_slot"),
                "activity_id": entities.get("activity_id")
            })
        elif intent == "move_activity":
            command.update({
                "target": "activity",
                "poi": entities.get("poi"),
                "from_day": self._extract_number(entities.get("from_day")),
                "to_day": self._extract_number(entities.get("to_day")),
                "from_time": entities.get("from_time"),
                "to_time": entities.get("to_time")
            })
        elif intent == "change_time":
            command.update({
                "target": "time",
                "poi": entities.get("poi"),
                "day": self._extract_number(entities.get("day")),
                "new_time": entities.get("time_slot")
            })
        elif intent == "change_hotel":
            command.update({
                "target": "hotel",
                "hotel_name": entities.get("hotel_name"),
                "day": self._extract_number(entities.get("day"))
            })
        elif intent == "change_transport":
            command.update({
                "target": "transport",
                "transport_mode": entities.get("transport_mode"),
                "day": self._extract_number(entities.get("day"))
            })
        elif intent == "update_cost":
            command.update({
                "target": "budget",
                "amount": self._extract_number(entities.get("amount"))
            })
        else:
            command["target"] = None

        return command

    def _generate_preview(self, intent: str, entities: Dict) -> str:
        if intent == "add_activity":
            poi = entities.get("poi", "activity")
            day = entities.get("day", "itinerary")
            time = entities.get("time_slot", "")
            time_str = f" in the {time}" if time else ""
            return f"Add {poi} to day {day}{time_str}"

        elif intent == "remove_activity":
            poi = entities.get("poi", "activity")
            day = entities.get("day", "")
            day_str = f" from day {day}" if day else ""
            return f"Remove {poi}{day_str}"

        elif intent == "change_time":
            poi = entities.get("poi", "activity")
            time = entities.get("time_slot", "new time")
            return f"Change {poi} to {time}"

        elif intent == "change_hotel":
            hotel = entities.get("hotel_name", "new hotel")
            return f"Change hotel to {hotel}"

        elif intent == "update_cost":
            amount = entities.get("amount", "amount")
            return f"Update budget to ${amount}"

        return "Process your request"

    def _extract_number(self, value) -> int:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r'\d+', value)
            if match:
                return int(match.group())
        return None

    def _estimate_confidence(self, user_message: str, parsed_result: Dict) -> float:
        confidence = 0.5

        if parsed_result.get("intent") in ["confirm", "cancel"]:
            confidence = 0.95

        if parsed_result.get("entities"):
            entity_count = len([v for v in parsed_result["entities"].values() if v])
            confidence += min(entity_count * 0.1, 0.3)

        intent_keywords = {
            "add_activity": ["add", "include", "insert", "schedule"],
            "remove_activity": ["remove", "delete", "cancel", "skip"],
            "change_time": ["change time", "shift", "reschedule", "move to"],
            "change_hotel": ["change hotel", "switch hotel", "book"],
            "update_cost": ["budget", "cost", "increase", "decrease"]
        }

        user_lower = user_message.lower()
        intent = parsed_result.get("intent", "")
        if intent in intent_keywords:
            if any(kw in user_lower for kw in intent_keywords[intent]):
                confidence += 0.15

        return min(confidence, 0.99)

    def _fallback_parse(self, response: str) -> Dict:
        response_lower = response.lower()

        if any(word in response_lower for word in ["add", "include", "insert"]):
            intent = "add_activity"
        elif any(word in response_lower for word in ["remove", "delete", "cancel"]):
            intent = "remove_activity"
        elif any(word in response_lower for word in ["move", "shift", "reschedule"]):
            intent = "move_activity"
        elif any(word in response_lower for word in ["hotel", "accommodation"]):
            intent = "change_hotel"
        elif any(word in response_lower for word in ["budget", "cost"]):
            intent = "update_cost"
        else:
            intent = "clarify"

        return {
            "intent": intent,
            "entities": {},
            "edit_command": {"action": "clarify", "target": None},
            "confidence": 0.3,
            "human_preview": "Could you rephrase that?"
        }
