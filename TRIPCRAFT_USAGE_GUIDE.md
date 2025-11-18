# TripCraft Usage Guide

## Overview

TripCraft is now fully integrated into your LangGraph Travel Itinerary Planner! The system generates high-quality, realistic travel itineraries with structured JSON output and supports conversational editing via chat.

---

## 🎯 What's New

### ✅ Implemented Features

1. **TripCraft System Prompt** - Professional itinerary assistant with quality standards
2. **Structured JSON Output** - Complete itinerary schema with all details
3. **Markdown Formatting** - Beautiful, readable itinerary display
4. **Supabase Persistence** - Automatic saving to database
5. **OpenAI Fallback** - Use OpenAI API when local models need help
6. **Delta Change Tracking** - See exactly what changed in edits
7. **Enhanced Chat Widget** - Visual change indicators and undo support
8. **Error Handling** - Graceful fallbacks when things go wrong

---

## 🚀 Quick Start

### 1. **Install Dependencies**

```bash
# Install all dependencies
pip install -e .

# Optional: Install OpenAI for better results
pip install openai
```

### 2. **Configure Environment**

Edit your `.env` file:

```bash
# Supabase (already configured)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key

# Optional: OpenAI for fallback
OPENAI_API_KEY=sk-your-api-key-here

# Optional: Tavily for web search
TAVILY_API_KEY=your-tavily-key
```

### 3. **Start the Application**

```bash
# Start Streamlit app
streamlit run app_with_chat.py

# Optional: Start backend service (for chat editing)
python -m uvicorn backend.api_server:app --reload --port 8000
```

---

## 📋 How It Works

### **Itinerary Generation Flow**

```
User Input → Preferences → Tavily Search → LLM Generation → JSON Validation
     ↓
Markdown Format → Supabase Storage → Display to User
```

### **Chat Editing Flow**

```
User Message → Backend API → NLP Parsing → Intent Recognition
     ↓
Edit Command → Apply to Itinerary → Compute Delta → Update Supabase
     ↓
Show Changes → Confirm/Undo Options
```

---

## 💬 Using the Chat Feature

### **Example Commands**

```
✅ "Add Eiffel Tower to day 2 morning"
✅ "Remove Louvre from day 1"
✅ "Change lunch time to 1:30pm"
✅ "Increase budget to $3000"
✅ "Move dinner from day 2 to day 3"
✅ "Make day 2 more relaxed"
✅ "Add a cooking class"
```

### **Chat Features**

1. **Confidence Scoring**
   - 🟢 High confidence (≥70%) - Applies automatically
   - 🟡 Medium confidence (40-70%) - Asks for confirmation
   - 🔴 Low confidence (<40%) - Requests clarification

2. **Delta Visualization**
   - See before/after changes
   - Understand what was modified
   - Review additions and removals

3. **Undo Functionality**
   - One-click undo of last change
   - Reverts to previous state
   - Tracks all modifications

---

## 🎨 Itinerary JSON Schema

The system generates structured JSON following this schema:

```json
{
  "itinerary": {
    "destination": "Paris, France",
    "start_date": "2025-10-01",
    "end_date": "2025-10-03",
    "timezone": "Europe/Paris",
    "currency": "EUR",
    "daily_plans": [
      {
        "day": 1,
        "date": "2025-10-01",
        "summary": "Arrival and Eiffel Tower",
        "activities": [
          {
            "start_time": "09:00",
            "end_time": "12:00",
            "title": "Eiffel Tower Visit",
            "type": "sightseeing",
            "address": "Champ de Mars, 5 Avenue Anatole France",
            "transportation": {
              "from": "hotel",
              "mode": "metro",
              "duration_min": 25,
              "est_cost": 2
            },
            "notes": "Book tickets online in advance",
            "booking_info": "eiffel-tower.com",
            "accessibility": "wheelchair_friendly: true"
          }
        ],
        "meals": [
          {
            "time": "12:30",
            "suggestion": "Le Jules Verne (Eiffel Tower restaurant)",
            "est_cost": 80,
            "dietary_notes": "vegetarian options available"
          }
        ],
        "estimated_daily_cost": 350,
        "alternative_options": ["Backup: Visit Trocadéro Gardens if weather is bad"]
      }
    ],
    "total_estimated_cost": 1050,
    "assumptions": ["3-star hotel accommodation", "Public transport preferred"],
    "sources": [{"type": "web", "citation": "Paris Tourist Board"}],
    "packing_list": ["Comfortable walking shoes", "Weather-appropriate clothing"],
    "safety_notes": ["Watch for pickpockets in tourist areas"]
  },
  "human_readable": "Created a 3-day Paris itinerary featuring the Eiffel Tower, Louvre, and local cuisine. Book Eiffel Tower tickets in advance. Total cost: €1050."
}
```

---

## 🔧 Advanced Configuration

### **Using OpenAI Fallback**

When `OPENAI_API_KEY` is set, the system automatically uses OpenAI API for:

1. **LLM Generation** - When TinyLlama needs help
2. **NLP Parsing** - When backend NLP service is unavailable
3. **Better Quality** - More accurate itineraries and edits

To enable:

```bash
# Install OpenAI
pip install openai

# Add to .env
OPENAI_API_KEY=sk-your-key-here
```

### **Backend Fallback Strategy**

The chat system implements intelligent fallbacks:

```
Primary: NLP Service (localhost:8001)
    ↓ (4-second timeout)
Fallback: OpenAI API for parsing
    ↓ (if OpenAI available)
Error: User-friendly message
```

### **Supabase Integration**

Itineraries are automatically saved to Supabase with:

- Unique ID for each itinerary
- Full JSON content
- Creation and update timestamps
- User tracking (if authenticated)
- Edit history

---

## 📊 Quality Features

### **Realistic Itineraries**

- ✅ Accurate travel times between locations
- ✅ 15-30 minute buffers between activities
- ✅ Realistic activity durations
- ✅ Cost estimates per activity and meal
- ✅ Transportation details
- ✅ Booking information
- ✅ Safety notes and packing lists

### **Smart Editing**

- ✅ Intent recognition (add/remove/modify/move)
- ✅ Entity extraction (days, times, POIs)
- ✅ Confidence scoring
- ✅ Change tracking with delta
- ✅ Automatic cost recalculation
- ✅ Time slot adjustments

---

## 🐛 Troubleshooting

### **Error: "Itinerary not saved to database"**

```bash
# Check Supabase credentials
cat .env | grep SUPABASE

# Test connection
python -c "from backend.supabase_client import supabase; print(supabase.table('itineraries').select('*').limit(1).execute())"
```

### **Error: "NLP service unavailable"**

```bash
# Option 1: Add OpenAI API key to .env
OPENAI_API_KEY=sk-your-key-here

# Option 2: Start NLP service
cd nlp_service
python nlp_api.py
```

### **Error: "Could not generate JSON"**

The system automatically creates a fallback itinerary. You can then use chat to refine it:

```
"Add Eiffel Tower to day 1"
"Make this more detailed"
```

### **Chat not working**

```bash
# Start backend server
python -m uvicorn backend.api_server:app --reload --port 8000

# Test backend
curl http://localhost:8000/health

# Check in browser
http://localhost:8000/docs
```

---

## 📈 Performance Tips

### **Faster Generation**

1. **Use OpenAI** - Much faster than local TinyLlama
2. **Shorter trips** - 2-3 days generate faster than 7+ days
3. **Fewer interests** - Reduces search and generation time

### **Better Quality**

1. **Be specific** - "Visit Louvre" vs "art museums"
2. **Include dates** - Real dates enable weather forecasts
3. **Set budget** - Helps filter appropriate options
4. **Use OpenAI** - Generally better itineraries

---

## 📚 API Documentation

### **Generate Itinerary Programmatically**

```python
from workflow import app

result = app.invoke({
    "preferences": {
        "destination": "Tokyo",
        "budget": 2000,
        "interests": ["food", "temples", "shopping"],
        "dates": "2025-11-01 to 2025-11-05"
    }
})

itinerary = result["itinerary"]
itinerary_json = result["itinerary_json"]
```

### **Save to Supabase**

```python
from supabase_helpers import save_itinerary

itinerary_id = save_itinerary(
    itinerary_data=result["itinerary_json"],
    user_id="user123"
)
```

### **Apply Edit**

```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat/message",
    json={
        "itinerary_id": itinerary_id,
        "message": "Add Senso-ji Temple to day 2"
    }
)

suggestions = response.json()["suggestions"]
```

---

## 🎓 Best Practices

### **For Users**

1. **Be Specific** - "Add sushi lunch at 12:30pm on day 2" is better than "add food"
2. **Review Changes** - Check the delta before confirming
3. **Use Undo** - Don't hesitate to try things out
4. **Iterate** - Make small changes and build up

### **For Developers**

1. **Validate JSON** - Use `validate_itinerary_json()` from tripcraft_config
2. **Handle Errors** - System has fallbacks, but check for edge cases
3. **Test Prompts** - TripCraft prompt can be customized in `tripcraft_config.py`
4. **Monitor Costs** - OpenAI API calls add up, use caching

---

## 🔮 Future Enhancements

Potential improvements:

- [ ] Multi-language support
- [ ] Real-time collaboration
- [ ] Export to Google Calendar
- [ ] Map visualization
- [ ] Price comparison integration
- [ ] Booking links generation
- [ ] Weather-based recommendations
- [ ] User authentication
- [ ] Saved itinerary history
- [ ] Social sharing

---

## ✅ Summary

TripCraft is fully integrated with:

✅ **High-quality itinerary generation** with structured JSON
✅ **Conversational editing** via chat interface
✅ **Automatic Supabase persistence**
✅ **OpenAI fallback** for better reliability
✅ **Delta tracking** to see all changes
✅ **Undo functionality** for easy corrections
✅ **Error handling** with graceful fallbacks

**Everything is working and ready to use!** 🎉

---

## 🆘 Need Help?

1. Check this guide first
2. Review error messages carefully
3. Test with simple examples first
4. Use OpenAI API key for best results
5. Check logs for detailed error information

**Enjoy planning amazing trips with TripCraft!** ✈️🌍
