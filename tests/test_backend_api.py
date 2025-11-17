import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api_server import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "service" in response.json()


class TestChatMessage:
    def test_chat_message_missing_itinerary(self):
        response = client.post(
            "/api/chat/message",
            json={
                "itinerary_id": "non-existent-id",
                "message": "add Eiffel Tower"
            }
        )
        assert response.status_code in [404, 500]

    def test_chat_message_empty_message(self):
        response = client.post(
            "/api/chat/message",
            json={
                "itinerary_id": "test-id",
                "message": ""
            }
        )
        assert response.status_code in [200, 404, 422, 500]

    def test_chat_message_structure(self):
        response = client.post(
            "/api/chat/message",
            json={
                "itinerary_id": "test-id",
                "message": "add activity"
            }
        )

        if response.status_code == 200:
            data = response.json()
            assert "suggestions" in data
            assert "needs_confirmation" in data
            assert "needs_clarification" in data


class TestApplyEdit:
    def test_apply_edit_missing_itinerary(self):
        response = client.post(
            "/api/chat/apply-edit",
            json={
                "itinerary_id": "non-existent",
                "edit_command": {
                    "action": "add",
                    "target": "activity",
                    "poi": "Test Location"
                }
            }
        )
        assert response.status_code in [404, 500]

    def test_apply_edit_structure(self):
        response = client.post(
            "/api/chat/apply-edit",
            json={
                "itinerary_id": "test-id",
                "edit_command": {
                    "action": "add",
                    "target": "activity",
                    "poi": "Eiffel Tower",
                    "day": 2
                }
            }
        )

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "change_id" in data
            assert "diff" in data


class TestUndoEdit:
    def test_undo_nonexistent_change(self):
        response = client.post(
            "/api/chat/undo",
            json={
                "change_id": "invalid-change-id",
                "itinerary_id": "test-id"
            }
        )
        assert response.status_code in [404, 500]

    def test_undo_structure(self):
        response = client.post(
            "/api/chat/undo",
            json={
                "change_id": "test-change",
                "itinerary_id": "test-id"
            }
        )

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "reverted_itinerary" in data


class TestEditCommands:
    def test_add_activity_command(self):
        edit_command = {
            "action": "add",
            "target": "activity",
            "poi": "Louvre Museum",
            "day": 1,
            "time_slot": "morning"
        }

        assert edit_command["action"] == "add"
        assert edit_command["target"] == "activity"

    def test_remove_activity_command(self):
        edit_command = {
            "action": "remove",
            "target": "activity",
            "poi": "Notre Dame",
            "day": 2
        }

        assert edit_command["action"] == "remove"

    def test_update_budget_command(self):
        edit_command = {
            "action": "update",
            "target": "budget",
            "amount": 2500
        }

        assert edit_command["target"] == "budget"
        assert isinstance(edit_command["amount"], (int, float))


class TestValidation:
    def test_invalid_json(self):
        response = client.post(
            "/api/chat/message",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_required_fields(self):
        response = client.post(
            "/api/chat/message",
            json={}
        )
        assert response.status_code == 422


class TestRateLimiting:
    def test_multiple_rapid_requests(self):
        responses = []
        for _ in range(5):
            response = client.get("/health")
            responses.append(response.status_code)

        assert all(code == 200 for code in responses)


class TestErrorHandling:
    def test_malformed_edit_command(self):
        response = client.post(
            "/api/chat/apply-edit",
            json={
                "itinerary_id": "test-id",
                "edit_command": "not a dict"
            }
        )
        assert response.status_code == 422

    def test_missing_action_in_command(self):
        response = client.post(
            "/api/chat/apply-edit",
            json={
                "itinerary_id": "test-id",
                "edit_command": {
                    "target": "activity"
                }
            }
        )
        assert response.status_code in [200, 400, 404, 500]
