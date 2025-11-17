import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nlp_service.flan_t5_parser import FlanT5Parser


@pytest.fixture
def parser():
    return FlanT5Parser()


class TestAddActivity:
    def test_add_activity_with_day_and_time(self, parser):
        message = "add Eiffel Tower to day 2 in the morning"
        result = parser.parse(message)

        assert result["intent"] == "add_activity"
        assert "Eiffel Tower" in str(result["entities"])
        assert result["edit_command"]["action"] == "add"
        assert result["edit_command"]["target"] == "activity"

    def test_add_activity_simple(self, parser):
        message = "include Louvre Museum in the itinerary"
        result = parser.parse(message)

        assert result["intent"] == "add_activity"
        assert result["edit_command"]["action"] == "add"

    def test_add_activity_with_duration(self, parser):
        message = "add shopping at Champs Elysees for 2 hours"
        result = parser.parse(message)

        assert result["intent"] == "add_activity"
        assert "shopping" in result["human_preview"].lower() or "Champs" in result["human_preview"]


class TestRemoveActivity:
    def test_remove_activity_by_name(self, parser):
        message = "remove Louvre Museum from day 1"
        result = parser.parse(message)

        assert result["intent"] == "remove_activity"
        assert result["edit_command"]["action"] == "remove"
        assert result["edit_command"]["target"] == "activity"

    def test_remove_activity_by_time_slot(self, parser):
        message = "delete the afternoon activity on day 2"
        result = parser.parse(message)

        assert result["intent"] == "remove_activity"

    def test_remove_activity_simple(self, parser):
        message = "cancel Notre Dame"
        result = parser.parse(message)

        assert result["intent"] == "remove_activity"


class TestChangeTime:
    def test_change_time_specific(self, parser):
        message = "change Eiffel Tower time to 3pm"
        result = parser.parse(message)

        assert result["intent"] == "change_time"
        assert result["edit_command"]["action"] == "update"
        assert result["edit_command"]["target"] == "time"

    def test_change_lunch_time(self, parser):
        message = "shift lunch to 1:30pm"
        result = parser.parse(message)

        assert result["intent"] == "change_time"


class TestChangeHotel:
    def test_change_hotel(self, parser):
        message = "change hotel to Hotel Ritz"
        result = parser.parse(message)

        assert result["intent"] == "change_hotel"
        assert result["edit_command"]["action"] == "update"
        assert result["edit_command"]["target"] == "hotel"

    def test_switch_hotel(self, parser):
        message = "switch to Hilton Paris"
        result = parser.parse(message)

        assert result["intent"] == "change_hotel"


class TestUpdateBudget:
    def test_increase_budget(self, parser):
        message = "increase budget by $500"
        result = parser.parse(message)

        assert result["intent"] == "update_cost"
        assert result["edit_command"]["action"] == "update"
        assert result["edit_command"]["target"] == "budget"

    def test_set_budget(self, parser):
        message = "set budget at $3000"
        result = parser.parse(message)

        assert result["intent"] == "update_cost"


class TestConfirmCancel:
    def test_confirm(self, parser):
        message = "yes"
        result = parser.parse(message)

        assert result["intent"] in ["confirm", "add_activity", "clarify"]
        assert result["confidence"] > 0.5

    def test_cancel(self, parser):
        message = "no thanks"
        result = parser.parse(message)

        assert "no" in message.lower()


class TestConfidenceScoring:
    def test_high_confidence_specific_request(self, parser):
        message = "add Eiffel Tower to day 2 in the morning"
        result = parser.parse(message)

        assert result["confidence"] >= 0.4

    def test_lower_confidence_vague_request(self, parser):
        message = "maybe change something"
        result = parser.parse(message)

        assert result["confidence"] < 0.7


class TestFuzzyMatching:
    def test_typo_in_poi_name(self, parser):
        message = "add Effel Tower to day 2"
        result = parser.parse(message)

        assert result["intent"] == "add_activity"

    def test_alternate_spelling(self, parser):
        message = "include the Louvr in day 1"
        result = parser.parse(message)

        assert result["intent"] == "add_activity"


class TestEdgeCase:
    def test_empty_message(self, parser):
        message = ""
        result = parser.parse(message)

        assert "intent" in result
        assert "confidence" in result

    def test_very_long_message(self, parser):
        message = "I would really like to add the Eiffel Tower to my itinerary " * 10
        result = parser.parse(message)

        assert "intent" in result

    def test_special_characters(self, parser):
        message = "add Café de Flore to day 1"
        result = parser.parse(message)

        assert result["intent"] == "add_activity"


class TestMultipleEntities:
    def test_multiple_days_mentioned(self, parser):
        message = "move activity from day 1 to day 3"
        result = parser.parse(message)

        assert result["intent"] in ["move_activity", "add_activity", "remove_activity"]

    def test_multiple_time_slots(self, parser):
        message = "shift morning activity to afternoon"
        result = parser.parse(message)

        assert result["intent"] in ["move_activity", "change_time"]
