import streamlit as st
from workflow import app
from helper_func import clean_itinerary, clean_weather
from chat_widget import ChatWidget
import uuid


st.set_page_config(page_title="Travel Planner AI", page_icon="🌍", layout="wide")

st.title("🌍 AI Travel Planner with Chat Editing")
st.write("Plan your trip with an AI-powered itinerary generator, then refine it through conversation.")

with st.form("travel_form"):
    destination = st.text_input("Destination", "Paris")
    budget = st.number_input("Budget (USD)", min_value=100, value=1000, step=50)
    interests = st.multiselect(
        "Interests",
        ["art", "food", "history", "nature", "adventure", "shopping", "beach"],
        default=["art", "food"]
    )
    dates = st.text_input("Travel Dates (YYYY-MM-DD to YYYY-MM-DD)", "2025-10-01 to 2025-10-03")
    submitted = st.form_submit_button("Generate Itinerary")

if submitted:
    with st.spinner("Planning your trip... ✈️"):
        preferences = {
            "destination": destination,
            "budget": budget,
            "interests": interests,
            "dates": dates
        }

        try:
            result = app.invoke({"preferences": preferences})
            itinerary = clean_itinerary(result.get("itinerary", "No itinerary generated."))
            weather = clean_weather(result.get("weather", "No weather data available."))

            if "itinerary_id" not in st.session_state:
                st.session_state.itinerary_id = str(uuid.uuid4())

            st.subheader("📅 Itinerary")
            st.markdown(itinerary)

            st.subheader("🌦️ Weather Forecast")
            st.write(weather)

            st.session_state.itinerary_generated = True
            st.session_state.current_itinerary = itinerary
            st.session_state.preferences = preferences

        except Exception as e:
            st.error(f"An error occurred: {e}")

if st.session_state.get("itinerary_generated"):
    st.divider()

    chat_widget = ChatWidget(
        itinerary_id=st.session_state.itinerary_id,
        backend_url="http://localhost:8000"
    )
    chat_widget.render()

    with st.expander("ℹ️ How to use chat editing"):
        st.write("""
        **Examples of what you can say:**
        - "Add Eiffel Tower to day 2 in the morning"
        - "Remove the Louvre Museum from day 1"
        - "Change lunch time to 1:30pm"
        - "Increase budget to $2500"
        - "Move dinner from day 2 to day 3"

        **Tips:**
        - Be specific about days and times
        - Use location names clearly
        - You can undo changes anytime
        - High confidence suggestions apply automatically
        - Lower confidence suggestions need confirmation
        """)
