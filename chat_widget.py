import streamlit as st
import requests
import json
from typing import Dict, Any, List


class ChatWidget:
    def __init__(self, itinerary_id: str, backend_url: str = "http://localhost:8000"):
        self.itinerary_id = itinerary_id
        self.backend_url = backend_url
        self.session_key = f"chat_history_{itinerary_id}"

        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = []

        if "pending_confirmation" not in st.session_state:
            st.session_state.pending_confirmation = None

        if "last_change_id" not in st.session_state:
            st.session_state.last_change_id = None

    def render(self):
        st.subheader("💬 Edit Your Itinerary")
        st.write("Tell me what changes you'd like to make!")

        chat_container = st.container()

        with chat_container:
            self._render_chat_history()

        col1, col2 = st.columns([4, 1])

        with col1:
            user_input = st.text_input(
                "Your message",
                key="chat_input",
                placeholder="e.g., 'Add Eiffel Tower to day 2 morning'"
            )

        with col2:
            send_button = st.button("Send", type="primary")

        if send_button and user_input:
            self._handle_user_message(user_input)
            st.rerun()

        if st.session_state.last_change_id:
            if st.button("↶ Undo Last Change"):
                self._handle_undo()
                st.rerun()

        self._render_quick_actions()

    def _render_chat_history(self):
        chat_history = st.session_state[self.session_key]

        for message in chat_history:
            role = message.get("role")
            content = message.get("content")

            if role == "user":
                st.chat_message("user").write(content)
            elif role == "assistant":
                with st.chat_message("assistant"):
                    st.write(content)

                    if message.get("suggestions"):
                        self._render_suggestions(message["suggestions"], message.get("needs_confirmation"))

    def _render_suggestions(self, suggestions: List[Dict], needs_confirmation: bool):
        for i, suggestion in enumerate(suggestions[:3]):
            confidence = suggestion.get("confidence", 0)
            preview = suggestion.get("human_preview", "")

            confidence_color = self._get_confidence_color(confidence)

            st.markdown(f"**Suggestion {i+1}** (Confidence: {confidence_color} {confidence:.0%})")
            st.write(f"📝 {preview}")

            if needs_confirmation or confidence < 0.7:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✓ Confirm", key=f"confirm_{i}_{suggestion}"):
                        self._apply_edit(suggestion["edit_command"])
                        st.rerun()
                with col2:
                    if st.button(f"✗ Cancel", key=f"cancel_{i}_{suggestion}"):
                        self._add_message("assistant", "Okay, I won't make that change.")
                        st.rerun()
            else:
                if st.button(f"Apply This Change", key=f"apply_{i}_{suggestion}"):
                    self._apply_edit(suggestion["edit_command"])
                    st.rerun()

            st.divider()

    def _render_quick_actions(self):
        with st.expander("⚡ Quick Actions"):
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("➕ Add Activity"):
                    st.session_state.chat_input = "Add an activity to "
                    st.rerun()

            with col2:
                if st.button("➖ Remove Activity"):
                    st.session_state.chat_input = "Remove "
                    st.rerun()

            with col3:
                if st.button("⏰ Change Time"):
                    st.session_state.chat_input = "Change the time for "
                    st.rerun()

    def _handle_user_message(self, message: str):
        self._add_message("user", message)

        try:
            response = requests.post(
                f"{self.backend_url}/api/chat/message",
                json={
                    "itinerary_id": self.itinerary_id,
                    "message": message
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                needs_clarification = data.get("needs_clarification", False)
                needs_confirmation = data.get("needs_confirmation", False)
                suggestions = data.get("suggestions", [])

                if needs_clarification:
                    self._add_message(
                        "assistant",
                        "I'm not sure I understood that. Could you rephrase or provide more details?",
                        suggestions=suggestions,
                        needs_confirmation=False
                    )
                elif needs_confirmation:
                    self._add_message(
                        "assistant",
                        "Here's what I understood. Please confirm:",
                        suggestions=suggestions,
                        needs_confirmation=True
                    )
                else:
                    top_suggestion = suggestions[0] if suggestions else None
                    if top_suggestion and top_suggestion.get("confidence", 0) >= 0.7:
                        self._apply_edit(top_suggestion["edit_command"])
                    else:
                        self._add_message(
                            "assistant",
                            "Here are some suggestions:",
                            suggestions=suggestions,
                            needs_confirmation=True
                        )
            else:
                self._add_message("assistant", "Sorry, I encountered an error processing your request.")

        except requests.RequestException as e:
            self._add_message("assistant", f"Error connecting to backend: {str(e)}")

    def _apply_edit(self, edit_command: Dict):
        try:
            response = requests.post(
                f"{self.backend_url}/api/chat/apply-edit",
                json={
                    "itinerary_id": self.itinerary_id,
                    "edit_command": edit_command
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                change_id = data.get("change_id")

                st.session_state.last_change_id = change_id

                self._add_message(
                    "assistant",
                    f"✅ {data.get('message', 'Edit applied successfully!')}"
                )

                st.success("Itinerary updated! Refresh to see changes.")
            else:
                self._add_message("assistant", "Failed to apply edit. Please try again.")

        except requests.RequestException as e:
            self._add_message("assistant", f"Error applying edit: {str(e)}")

    def _handle_undo(self):
        if not st.session_state.last_change_id:
            return

        try:
            response = requests.post(
                f"{self.backend_url}/api/chat/undo",
                json={
                    "change_id": st.session_state.last_change_id,
                    "itinerary_id": self.itinerary_id
                },
                timeout=30
            )

            if response.status_code == 200:
                st.session_state.last_change_id = None
                self._add_message("assistant", "↶ Last change has been reverted.")
                st.success("Change undone!")
            else:
                self._add_message("assistant", "Failed to undo change.")

        except requests.RequestException as e:
            self._add_message("assistant", f"Error undoing change: {str(e)}")

    def _add_message(self, role: str, content: str, suggestions: List = None, needs_confirmation: bool = False):
        message = {
            "role": role,
            "content": content,
            "suggestions": suggestions,
            "needs_confirmation": needs_confirmation
        }
        st.session_state[self.session_key].append(message)

    def _get_confidence_color(self, confidence: float) -> str:
        if confidence >= 0.7:
            return "🟢"
        elif confidence >= 0.4:
            return "🟡"
        else:
            return "🔴"
