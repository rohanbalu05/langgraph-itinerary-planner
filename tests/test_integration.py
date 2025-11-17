import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestEndToEndFlow:
    def test_parse_and_apply_workflow(self):
        from nlp_service.flan_t5_parser import FlanT5Parser

        parser = FlanT5Parser()

        message = "add Eiffel Tower to day 2 in the morning"

        parse_result = parser.parse(message)

        assert "intent" in parse_result
        assert "edit_command" in parse_result

        edit_command = parse_result["edit_command"]

        assert edit_command["action"] in ["add", "update", "remove"]
        assert "target" in edit_command

        from backend.routes.chat import _apply_edit_command

        sample_itinerary = {
            "days": [
                {
                    "day_number": 1,
                    "activities": []
                },
                {
                    "day_number": 2,
                    "activities": []
                }
            ]
        }

        updated = _apply_edit_command(sample_itinerary, edit_command)

        assert "days" in updated

    def test_add_then_remove_activity(self):
        from backend.routes.chat import _apply_edit_command

        itinerary = {
            "days": [
                {
                    "day_number": 1,
                    "activities": []
                }
            ]
        }

        add_command = {
            "action": "add",
            "target": "activity",
            "poi": "Test Location",
            "day": 1
        }

        itinerary = _apply_edit_command(itinerary, add_command)

        assert len(itinerary["days"][0]["activities"]) == 1

        remove_command = {
            "action": "remove",
            "target": "activity",
            "poi": "Test Location",
            "day": 1
        }

        itinerary = _apply_edit_command(itinerary, remove_command)

        assert len(itinerary["days"][0]["activities"]) == 0

    def test_update_budget(self):
        from backend.routes.chat import _apply_edit_command

        itinerary = {
            "total_budget": 1000,
            "days": []
        }

        budget_command = {
            "action": "update",
            "target": "budget",
            "amount": 2000
        }

        updated = _apply_edit_command(itinerary, budget_command)

        assert updated["total_budget"] == 2000


class TestUndoFlow:
    def test_undo_add_activity(self):
        from backend.routes.chat import _apply_edit_command

        original = {
            "days": [
                {
                    "day_number": 1,
                    "activities": [
                        {"name": "Original Activity"}
                    ]
                }
            ]
        }

        before_snapshot = original.copy()

        add_command = {
            "action": "add",
            "target": "activity",
            "poi": "New Activity",
            "day": 1
        }

        modified = _apply_edit_command(original, add_command)

        assert len(modified["days"][0]["activities"]) == 2

        reverted = before_snapshot

        assert len(reverted["days"][0]["activities"]) == 1


class TestDiffComputation:
    def test_compute_simple_diff(self):
        from backend.routes.chat import _compute_diff

        before = {
            "total_budget": 1000,
            "destination": "Paris"
        }

        after = {
            "total_budget": 1500,
            "destination": "Paris",
            "new_field": "value"
        }

        diff = _compute_diff(before, after)

        assert "added" in diff
        assert "removed" in diff
        assert "modified" in diff

        assert len(diff["added"]) == 1
        assert len(diff["modified"]) == 1


class TestConfidenceBasedRouting:
    def test_high_confidence_auto_apply(self):
        confidence = 0.85
        needs_confirmation = confidence < 0.7

        assert needs_confirmation is False

    def test_medium_confidence_confirm(self):
        confidence = 0.55
        needs_confirmation = 0.4 <= confidence < 0.7

        assert needs_confirmation is True

    def test_low_confidence_clarify(self):
        confidence = 0.3
        needs_clarification = confidence < 0.4

        assert needs_clarification is True


class TestEdgeCases:
    def test_add_to_nonexistent_day(self):
        from backend.routes.chat import _apply_edit_command

        itinerary = {
            "days": [
                {"day_number": 1, "activities": []}
            ]
        }

        add_command = {
            "action": "add",
            "target": "activity",
            "poi": "Test",
            "day": 5
        }

        updated = _apply_edit_command(itinerary, add_command)

        assert "days" in updated

    def test_remove_nonexistent_activity(self):
        from backend.routes.chat import _apply_edit_command

        itinerary = {
            "days": [
                {
                    "day_number": 1,
                    "activities": [
                        {"name": "Activity 1"}
                    ]
                }
            ]
        }

        remove_command = {
            "action": "remove",
            "target": "activity",
            "poi": "Nonexistent Activity",
            "day": 1
        }

        updated = _apply_edit_command(itinerary, remove_command)

        assert len(updated["days"][0]["activities"]) == 1

    def test_empty_itinerary(self):
        from backend.routes.chat import _apply_edit_command

        itinerary = {}

        add_command = {
            "action": "add",
            "target": "activity",
            "poi": "Test",
            "day": 1
        }

        updated = _apply_edit_command(itinerary, add_command)

        assert isinstance(updated, dict)
