import requests
import json
import time
from typing import Dict, Any


class ChatDemo:
    def __init__(
        self,
        backend_url: str = "http://localhost:8000",
        nlp_url: str = "http://localhost:8001"
    ):
        self.backend_url = backend_url
        self.nlp_url = nlp_url
        self.itinerary_id = None
        self.change_history = []

    def check_services(self):
        print("Checking service health...")

        try:
            backend = requests.get(f"{self.backend_url}/health", timeout=5)
            print(f"✓ Backend API: {backend.json()['status']}")
        except Exception as e:
            print(f"✗ Backend API: {e}")
            return False

        try:
            nlp = requests.get(f"{self.nlp_url}/health", timeout=5)
            print(f"✓ NLP Service: {nlp.json()['status']}")
        except Exception as e:
            print(f"✗ NLP Service: {e}")
            return False

        print()
        return True

    def create_sample_itinerary(self) -> str:
        sample_itinerary = {
            "id": "demo-itinerary-001",
            "user_id": "demo-user",
            "destination": "Paris",
            "budget": 2000,
            "interests": ["art", "food", "history"],
            "dates": "2025-06-01 to 2025-06-03",
            "content": {
                "days": [
                    {
                        "day_number": 1,
                        "activities": [
                            {
                                "id": "act_001",
                                "name": "Visit Louvre Museum",
                                "time_slot": "morning",
                                "duration": "3 hours",
                                "cost": 20
                            },
                            {
                                "id": "act_002",
                                "name": "Lunch at Café de Flore",
                                "time_slot": "afternoon",
                                "duration": "1 hour",
                                "cost": 30
                            }
                        ]
                    },
                    {
                        "day_number": 2,
                        "activities": [
                            {
                                "id": "act_003",
                                "name": "Notre Dame Cathedral",
                                "time_slot": "morning",
                                "duration": "2 hours",
                                "cost": 0
                            }
                        ]
                    },
                    {
                        "day_number": 3,
                        "activities": []
                    }
                ]
            }
        }

        print("Created sample itinerary:")
        print(f"  Destination: {sample_itinerary['destination']}")
        print(f"  Budget: ${sample_itinerary['budget']}")
        print(f"  Days: {len(sample_itinerary['content']['days'])}")
        print()

        self.itinerary_id = sample_itinerary["id"]
        return sample_itinerary["id"]

    def send_message(self, message: str) -> Dict[str, Any]:
        print(f"User: {message}")

        response = requests.post(
            f"{self.backend_url}/api/chat/message",
            json={
                "itinerary_id": self.itinerary_id,
                "message": message
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"  Error: {response.status_code} - {response.text}")
            return None

        data = response.json()

        print(f"  Confidence: {data['suggestions'][0]['confidence']:.2%}")
        print(f"  Preview: {data['suggestions'][0]['human_preview']}")
        print(f"  Needs Confirmation: {data['needs_confirmation']}")
        print(f"  Needs Clarification: {data['needs_clarification']}")
        print()

        return data

    def apply_edit(self, edit_command: Dict[str, Any]) -> Dict[str, Any]:
        print("Applying edit...")

        response = requests.post(
            f"{self.backend_url}/api/chat/apply-edit",
            json={
                "itinerary_id": self.itinerary_id,
                "edit_command": edit_command
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"  Error: {response.status_code} - {response.text}")
            return None

        data = response.json()
        change_id = data.get("change_id")

        self.change_history.append(change_id)

        print(f"  ✓ {data['message']}")
        print(f"  Change ID: {change_id}")
        print(f"  Diff: {len(data['diff']['modified'])} modified, "
              f"{len(data['diff']['added'])} added, {len(data['diff']['removed'])} removed")
        print()

        return data

    def undo_last_change(self):
        if not self.change_history:
            print("No changes to undo")
            return

        change_id = self.change_history[-1]
        print(f"Undoing change: {change_id}")

        response = requests.post(
            f"{self.backend_url}/api/chat/undo",
            json={
                "change_id": change_id,
                "itinerary_id": self.itinerary_id
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"  Error: {response.status_code} - {response.text}")
            return

        data = response.json()
        print(f"  ✓ {data['message']}")
        self.change_history.pop()
        print()

    def run_demo(self):
        print("=" * 60)
        print("CONVERSATIONAL ITINERARY EDITING - DEMO")
        print("=" * 60)
        print()

        if not self.check_services():
            print("Services not ready. Please start them first:")
            print("  docker-compose up -d")
            print("  OR")
            print("  python nlp_service/nlp_api.py")
            print("  python -m uvicorn backend.api_server:app --port 8000")
            return

        self.create_sample_itinerary()

        print("SCENARIO 1: Add activity with high confidence")
        print("-" * 60)
        result = self.send_message("add Eiffel Tower to day 2 in the morning")

        if result and not result["needs_clarification"]:
            self.apply_edit(result["suggestions"][0]["edit_command"])

        time.sleep(1)

        print("SCENARIO 2: Remove activity")
        print("-" * 60)
        result = self.send_message("remove Notre Dame from day 2")

        if result and not result["needs_clarification"]:
            self.apply_edit(result["suggestions"][0]["edit_command"])

        time.sleep(1)

        print("SCENARIO 3: Change budget")
        print("-" * 60)
        result = self.send_message("increase budget to $2500")

        if result and not result["needs_clarification"]:
            self.apply_edit(result["suggestions"][0]["edit_command"])

        time.sleep(1)

        print("SCENARIO 4: Undo last change")
        print("-" * 60)
        self.undo_last_change()

        time.sleep(1)

        print("SCENARIO 5: Low confidence - needs clarification")
        print("-" * 60)
        result = self.send_message("maybe change something")

        if result and result["needs_clarification"]:
            print("  System would prompt for clarification in UI")

        print()
        print("=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print()
        print(f"Total changes made: {len(self.change_history)}")
        print("Change history:", self.change_history)
        print()
        print("Next steps:")
        print("  - Try the Streamlit UI: streamlit run app.py")
        print("  - Run tests: pytest tests/ -v")
        print("  - View API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    demo = ChatDemo()
    demo.run_demo()
