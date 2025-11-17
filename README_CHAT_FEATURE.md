# Conversational Itinerary Editing Feature

## Quick Start

This feature enables natural language editing of generated travel itineraries through a chat interface.

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (recommended)
- Supabase account (database already configured)

### Installation

1. **Install Python dependencies:**

```bash
# Add to existing project dependencies
uv add fastapi uvicorn pydantic httpx supabase pytest rapidfuzz requests

# Or using pip
pip install fastapi uvicorn pydantic httpx supabase pytest rapidfuzz requests
```

2. **Start services:**

**Option A: Docker (Recommended)**
```bash
docker-compose up -d
```

**Option B: Manual**
```bash
# Terminal 1: NLP Service
cd nlp_service
pip install -r requirements.txt
python nlp_api.py

# Terminal 2: Backend API
pip install -r backend/requirements.txt
python -m uvicorn backend.api_server:app --port 8000

# Terminal 3: Streamlit App
streamlit run app_with_chat.py
```

### Usage

1. Generate an itinerary using the form
2. Use the chat widget below the itinerary to make edits
3. Type natural language commands like:
   - "Add Eiffel Tower to day 2 morning"
   - "Remove Louvre Museum from day 1"
   - "Change budget to $2500"

### Demo Script

Run the automated demo:

```bash
python demo_chat_workflow.py
```

This demonstrates:
- Adding activities
- Removing activities
- Updating budget
- Undoing changes
- Handling low-confidence inputs

### Testing

Run the comprehensive test suite:

```bash
pytest tests/ -v
```

Test categories:
- **Unit tests**: NLU parsing (25+ examples)
- **API tests**: All endpoints with validation
- **Integration tests**: End-to-end workflows

## Architecture

### Components

1. **NLP Service** (`nlp_service/`)
   - Flan-T5 model for intent recognition
   - Rasa configuration for advanced NLU
   - FastAPI server on port 8001

2. **Backend API** (`backend/`)
   - FastAPI REST endpoints
   - Supabase database integration
   - Transaction management
   - Port 8000

3. **Chat Widget** (`chat_widget.py`)
   - Streamlit component
   - Confidence-based UX
   - Real-time suggestions
   - Undo functionality

### Database Schema

Three main tables:
- **itineraries**: Stores travel plans
- **itinerary_edits**: Audit log with snapshots
- **chat_sessions**: Conversation history

All tables have Row Level Security enabled.

### Supported Intents

- `add_activity`: Add POI to itinerary
- `remove_activity`: Delete activity
- `move_activity`: Reschedule activity
- `change_time`: Update timing
- `change_hotel`: Modify accommodation
- `change_transport`: Update travel mode
- `update_cost`: Adjust budget
- `combine_days`: Merge days
- `split_day`: Divide day
- `confirm/cancel/clarify`: Flow control

## API Examples

### Parse Message
```bash
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"message": "add Eiffel Tower to day 2"}'
```

### Apply Edit
```bash
curl -X POST http://localhost:8000/api/chat/apply-edit \
  -H "Content-Type: application/json" \
  -d '{
    "itinerary_id": "uuid",
    "edit_command": {
      "action": "add",
      "target": "activity",
      "poi": "Eiffel Tower",
      "day": 2
    }
  }'
```

### Undo Change
```bash
curl -X POST http://localhost:8000/api/chat/undo \
  -H "Content-Type: application/json" \
  -d '{
    "change_id": "change_abc123",
    "itinerary_id": "uuid"
  }'
```

## Configuration

### Environment Variables

Ensure `.env` contains:
```
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_SUPABASE_ANON_KEY=your_anon_key
```

### Confidence Thresholds

In `chat_widget.py`, adjust:
- Auto-apply: confidence > 0.7
- Confirm: 0.4 ≤ confidence < 0.7
- Clarify: confidence < 0.4

## Troubleshooting

### Services won't start
```bash
# Check Docker logs
docker-compose logs

# Or manual service logs
python nlp_service/nlp_api.py  # Should show "NLP service ready"
```

### Edit not applied
- Verify itinerary_id exists
- Check edit_command structure
- Review backend logs

### Low confidence scores
- Add training examples to `nlp_service/nlu.yml`
- Adjust threshold in code
- Use more specific language

## Documentation

Full documentation: `docs/chat_integration.md`

API docs:
- Backend: http://localhost:8000/docs
- NLP: http://localhost:8001/docs

## Next Steps

1. Run demo script to see features
2. Try Streamlit UI with sample itinerary
3. Experiment with different chat commands
4. Review test cases for examples
5. Customize NLU training data

## Feature Highlights

✅ Natural language processing with Flan-T5
✅ Rasa NLU for advanced intent recognition
✅ Confidence-based UX (auto/confirm/clarify)
✅ Transactional edits with snapshots
✅ Undo functionality with 60s notifications
✅ Comprehensive test suite (25+ examples)
✅ Docker containerization
✅ Supabase integration with RLS
✅ Real-time diff preview
✅ Fuzzy POI matching

## Support

For issues:
1. Check service health endpoints
2. Review logs
3. Run test suite
4. Consult `docs/chat_integration.md`
