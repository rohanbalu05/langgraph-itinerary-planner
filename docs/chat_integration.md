# Conversational Itinerary Editing - Integration Guide

## Overview

This document describes the conversational editing feature that enables users to modify generated travel itineraries through natural language chat interactions.

## Architecture

The system consists of three main components:

### 1. NLP Service (`nlp_service/`)
- **Primary Engine**: Rasa Open Source v3+ with custom NLU pipeline
- **Fallback Engine**: Flan-T5 language model for prompt-to-JSON conversion
- **API**: FastAPI wrapper exposing `/parse` endpoint
- **Port**: 8001

The NLP service processes natural language inputs and converts them to structured edit commands.

### 2. Backend API (`backend/`)
- **Framework**: FastAPI
- **Port**: 8000
- **Database**: Supabase (PostgreSQL with Row Level Security)

#### Endpoints:

**POST /api/chat/message**
- Processes user chat messages
- Returns up to 3 suggestions sorted by confidence
- Handles confidence-based routing logic

Request:
```json
{
  "itinerary_id": "uuid",
  "message": "add Eiffel Tower to day 2 morning",
  "user_id": "uuid (optional)"
}
```

Response:
```json
{
  "suggestions": [
    {
      "intent": "add_activity",
      "entities": {"poi": "Eiffel Tower", "day": "2", "time_slot": "morning"},
      "edit_command": {...},
      "confidence": 0.85,
      "human_preview": "Add Eiffel Tower to day 2 in the morning"
    }
  ],
  "needs_confirmation": false,
  "needs_clarification": false,
  "session_id": "uuid"
}
```

**POST /api/itinerary/apply-edit**
- Validates and applies edits transactionally
- Creates before/after snapshots
- Returns diff and change_id for undo operations

Request:
```json
{
  "itinerary_id": "uuid",
  "edit_command": {
    "action": "add",
    "target": "activity",
    "poi": "Eiffel Tower",
    "day": 2,
    "time_slot": "morning"
  },
  "user_id": "uuid (optional)"
}
```

Response:
```json
{
  "success": true,
  "change_id": "change_abc123",
  "diff": {
    "added": [...],
    "removed": [...],
    "modified": [...]
  },
  "updated_itinerary": {...},
  "message": "Edit applied successfully"
}
```

**POST /api/itinerary/undo**
- Reverts specific changes using change_id
- Restores previous state from snapshot

Request:
```json
{
  "change_id": "change_abc123",
  "itinerary_id": "uuid",
  "user_id": "uuid (optional)"
}
```

### 3. Frontend Chat Widget (`chat_widget.py`)
- **Framework**: Streamlit
- **Features**:
  - Real-time chat interface
  - Confidence-based UX (auto-apply, confirm, clarify)
  - Preview diffs before applying
  - Undo functionality with 60s notifications
  - Quick action buttons

#### Confidence-Based Flow:
- **>0.7 confidence**: Auto-suggest with single-click apply
- **0.4-0.7 confidence**: Show confirm/cancel options
- **<0.4 confidence**: Request clarification

## Database Schema

### Tables

**itineraries**
- Stores generated travel itineraries
- Fields: id, user_id, destination, budget, interests, dates, content, timestamps

**itinerary_edits**
- Audit log of all edits
- Fields: id, change_id, itinerary_id, user_id, intent, entities, edit_command, before_snapshot, after_snapshot, confidence, status, timestamps

**chat_sessions**
- Manages conversation history
- Fields: id, itinerary_id, user_id, messages (JSONB), timestamps

All tables have Row Level Security (RLS) enabled with user-based policies.

## NLU Intent Schema

### Supported Intents:

1. **add_activity**: Add new activity to itinerary
   - Entities: poi, day, time_slot, duration

2. **remove_activity**: Remove existing activity
   - Entities: poi, day, time_slot, activity_id

3. **move_activity**: Reschedule activity
   - Entities: poi, from_day, to_day, from_time, to_time

4. **change_time**: Update activity timing
   - Entities: poi, day, new_time

5. **change_hotel**: Update accommodation
   - Entities: hotel_name, day

6. **change_transport**: Modify transportation
   - Entities: transport_mode, day

7. **update_cost**: Adjust budget
   - Entities: amount

8. **combine_days**: Merge multiple days
   - Entities: days (array)

9. **split_day**: Divide day into parts
   - Entities: day

10. **confirm/cancel/clarify**: Flow control intents

### Edit Command Format:

```json
{
  "action": "add|remove|update|move|combine|split",
  "target": "activity|time|hotel|transport|budget|days|day",
  "poi": "Location name (optional)",
  "day": 1,
  "time_slot": "morning|afternoon|evening|HH:MM",
  "duration": "X hours (optional)",
  "amount": 1500 (for budget updates)
}
```

## Integration with LangGraph

The existing workflow has been extended with edit capability:

1. **structure_itinerary**: Converts raw LLM output to structured JSON
2. **save_to_db**: Persists itinerary to Supabase
3. **apply_edit**: Processes pending edits as graph events

Edit operations integrate seamlessly with the existing agent pipeline.

## Setup Instructions

### 1. Install Dependencies

```bash
# Update pyproject.toml
uv add fastapi uvicorn pydantic httpx supabase pytest rapidfuzz

# For NLP service
cd nlp_service
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure `.env` contains:
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_SUPABASE_ANON_KEY=your_anon_key
```

### 3. Run Services

**Option A: Docker (Recommended)**
```bash
docker-compose up -d
```

**Option B: Manual**
```bash
# Terminal 1: NLP Service
cd nlp_service
python nlp_api.py

# Terminal 2: Backend API
python -m uvicorn backend.api_server:app --port 8000

# Terminal 3: Streamlit App
streamlit run app.py
```

### 4. Database Migration

Migrations are automatically applied via Supabase. Verify tables exist:
```bash
# Check Supabase dashboard or use SQL client
SELECT * FROM itineraries LIMIT 1;
```

## Usage Example

### Python/Direct API:

```python
import requests

# 1. Send chat message
response = requests.post("http://localhost:8000/api/chat/message", json={
    "itinerary_id": "your-itinerary-id",
    "message": "add Eiffel Tower to day 2 morning"
})
suggestions = response.json()["suggestions"]

# 2. Apply edit
response = requests.post("http://localhost:8000/api/chat/apply-edit", json={
    "itinerary_id": "your-itinerary-id",
    "edit_command": suggestions[0]["edit_command"]
})
change_id = response.json()["change_id"]

# 3. Undo if needed
requests.post("http://localhost:8000/api/chat/undo", json={
    "change_id": change_id,
    "itinerary_id": "your-itinerary-id"
})
```

### Streamlit Integration:

```python
from chat_widget import ChatWidget

# After itinerary generation
if result.get("itinerary_id"):
    widget = ChatWidget(itinerary_id=result["itinerary_id"])
    widget.render()
```

## Testing

Run the comprehensive test suite:

```bash
# All tests
pytest tests/

# Specific test modules
pytest tests/test_nlp_parser.py -v
pytest tests/test_backend_api.py -v
pytest tests/test_integration.py -v
```

### Test Coverage:

- **Unit Tests**: 25+ NLU intent mapping examples
- **API Tests**: All endpoints with error cases
- **Integration Tests**: End-to-end chat→apply→undo flows
- **Edge Cases**: Empty inputs, nonexistent entities, malformed commands

## Security Considerations

1. **Rate Limiting**: Implement on `/api/chat/*` endpoints (not included, add via middleware)
2. **Input Sanitization**: All user inputs validated before model processing
3. **Private Network**: NLP service should be internal-only (use Docker network)
4. **RLS Policies**: All database operations respect user ownership
5. **Encrypted Logs**: Sensitive edit data encrypted at rest (Supabase default)

## Performance Optimization

- **Caching**: Implement Redis cache for frequent NLP queries
- **Batch Processing**: Group multiple edits in single transaction
- **Model Loading**: Keep Flan-T5 model in memory (FastAPI startup event)
- **Connection Pooling**: Use Supabase connection pooling

## Troubleshooting

### NLP Service Not Responding
```bash
# Check service health
curl http://localhost:8001/health

# View logs
docker logs nlp_service
```

### Edit Not Applied
- Verify itinerary_id exists in database
- Check edit_command structure matches schema
- Review backend logs for validation errors

### Low Confidence Scores
- Add more training examples to `nlu.yml`
- Retrain Rasa model: `rasa train`
- Adjust confidence thresholds in code

## Future Enhancements

1. **Multi-turn Conversations**: Context-aware follow-up questions
2. **Batch Edits**: Apply multiple changes atomically
3. **Conflict Resolution**: Handle concurrent edits
4. **Voice Input**: Speech-to-text integration
5. **Suggestions Engine**: Proactive recommendations
6. **Analytics Dashboard**: Track popular edits and patterns

## API Reference

Full OpenAPI documentation available at:
- Backend: `http://localhost:8000/docs`
- NLP Service: `http://localhost:8001/docs`

## Support

For issues or questions:
1. Check logs in `docker-compose logs`
2. Review test cases for examples
3. Consult Supabase dashboard for data verification
4. File issues with detailed error messages
