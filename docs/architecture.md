# Conversational Editing Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Streamlit - app_with_chat.py)              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Travel Form → Itinerary Display → Chat Widget           │  │
│  │                                    ↓                       │  │
│  │                          [Quick Actions] [Undo]           │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 │ HTTP Requests
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                       Backend API Server                         │
│                    (FastAPI - Port 8000)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  POST /api/chat/message                                   │  │
│  │    ├─> Parse user input                                   │  │
│  │    ├─> Call NLP Service ─────────┐                       │  │
│  │    ├─> Route by confidence       │                       │  │
│  │    └─> Return suggestions        │                       │  │
│  │                                   ↓                       │  │
│  │  POST /api/itinerary/apply-edit  │                       │  │
│  │    ├─> Validate command          │                       │  │
│  │    ├─> Create snapshot           │                       │  │
│  │    ├─> Apply transformation      │                       │  │
│  │    ├─> Save to Supabase ─────────┼──────┐               │  │
│  │    └─> Return diff + change_id   │      │               │  │
│  │                                   │      │               │  │
│  │  POST /api/itinerary/undo        │      │               │  │
│  │    ├─> Find edit record ─────────┼──────┤               │  │
│  │    ├─> Restore snapshot          │      │               │  │
│  │    └─> Update status             │      │               │  │
│  └───────────────────────────────────┘      │               │  │
└──────────────────────────┬──────────────────┼───────────────────┘
                           │                  │
                           │                  │
        ┌──────────────────┼──────────────────┼──────────┐
        │                  │                  │          │
        ↓                  ↓                  ↓          │
┌───────────────────┐  ┌────────────────────────────┐   │
│   NLP Service     │  │    Supabase Database       │   │
│  (Port 8001)      │  │   (PostgreSQL + RLS)       │   │
│  ┌─────────────┐  │  │  ┌──────────────────────┐  │   │
│  │ Flan-T5     │  │  │  │  itineraries         │  │   │
│  │ Parser      │  │  │  │    - id (PK)         │  │   │
│  │  ↓          │  │  │  │    - content (JSON)  │  │   │
│  │ Intent      │  │  │  │    - user_id (FK)    │  │   │
│  │ Recognition │  │  │  └──────────────────────┘  │   │
│  │  ↓          │  │  │  ┌──────────────────────┐  │   │
│  │ Entity      │  │  │  │  itinerary_edits     │  │   │
│  │ Extraction  │  │  │  │    - change_id (UK)  │  │   │
│  │  ↓          │  │  │  │    - before_snapshot │  │   │
│  │ Edit Cmd    │  │  │  │    - after_snapshot  │  │   │
│  │ Builder     │  │  │  │    - confidence      │  │   │
│  │  ↓          │  │  │  │    - status          │  │   │
│  │ Confidence  │  │  │  └──────────────────────┘  │   │
│  │ Score       │  │  │  ┌──────────────────────┐  │   │
│  └─────────────┘  │  │  │  chat_sessions       │  │   │
│  ┌─────────────┐  │  │  │    - messages (JSON) │  │   │
│  │ Rasa NLU    │  │  │  │    - itinerary_id    │  │   │
│  │ (Optional)  │  │  │  └──────────────────────┘  │   │
│  └─────────────┘  │  └────────────────────────────┘   │
└───────────────────┘                                     │
                                                          │
┌─────────────────────────────────────────────────────────┘
│  LangGraph Workflow (workflow.py)
│  ┌─────────────────────────────────────────┐
│  │  gather_preferences                     │
│  │         ↓                                │
│  │  fetch_destination_info                 │
│  │         ↓                                │
│  │  generate_itinerary                     │
│  │         ↓                                │
│  │  structure_itinerary  ← (new)          │
│  │         ↓                                │
│  │  save_to_db          ← (new)           │
│  │         ↓                                │
│  │  apply_pending_edit  ← (new)           │
│  │         ↓                                │
│  │  check_weather                          │
│  └─────────────────────────────────────────┘
└────────────────────────────────────────────┘
```

## Request Flow

### 1. Chat Message Flow

```
User: "add Eiffel Tower to day 2 morning"
  │
  ↓
[ChatWidget] sends to /api/chat/message
  │
  ↓
[Backend] forwards to NLP Service /parse
  │
  ↓
[NLP] Flan-T5 processes:
  - Tokenize input
  - Few-shot prompting
  - Generate JSON output
  │
  ↓
[NLP] Returns:
  {
    "intent": "add_activity",
    "entities": {
      "poi": "Eiffel Tower",
      "day": "2",
      "time_slot": "morning"
    },
    "edit_command": {...},
    "confidence": 0.85,
    "human_preview": "Add Eiffel Tower to day 2 in the morning"
  }
  │
  ↓
[Backend] Evaluates confidence:
  - >0.7: Auto-suggest
  - 0.4-0.7: Needs confirmation
  - <0.4: Needs clarification
  │
  ↓
[Backend] Saves to chat_sessions table
  │
  ↓
[Backend] Returns suggestions to UI
  │
  ↓
[ChatWidget] Displays:
  - High confidence: "Apply This Change" button
  - Medium confidence: "Confirm" / "Cancel" buttons
  - Low confidence: "Please clarify" message
```

### 2. Apply Edit Flow

```
User clicks "Apply" / "Confirm"
  │
  ↓
[ChatWidget] sends edit_command to /api/itinerary/apply-edit
  │
  ↓
[Backend] Validates:
  - Itinerary exists
  - Command structure valid
  - User authorized (RLS)
  │
  ↓
[Backend] Creates snapshot:
  before_snapshot = current_content.copy()
  │
  ↓
[Backend] Applies transformation:
  updated_content = _apply_edit_command(before, command)
  │
  ↓
[Backend] Saves to Supabase:
  - UPDATE itineraries SET content = updated_content
  - INSERT INTO itinerary_edits (snapshots, change_id, ...)
  │
  ↓
[Backend] Computes diff:
  diff = {added: [...], removed: [...], modified: [...]}
  │
  ↓
[Backend] Returns:
  {
    "success": true,
    "change_id": "change_abc123",
    "diff": {...},
    "updated_itinerary": {...}
  }
  │
  ↓
[ChatWidget] Updates UI:
  - Show success message
  - Store change_id for undo
  - Suggest page refresh
```

### 3. Undo Flow

```
User clicks "Undo"
  │
  ↓
[ChatWidget] sends change_id to /api/itinerary/undo
  │
  ↓
[Backend] Queries itinerary_edits:
  - Find edit by change_id
  - Check status != "reverted"
  │
  ↓
[Backend] Restores snapshot:
  UPDATE itineraries SET content = before_snapshot
  │
  ↓
[Backend] Marks edit reverted:
  UPDATE itinerary_edits SET status = 'reverted', reverted_at = NOW()
  │
  ↓
[Backend] Returns reverted itinerary
  │
  ↓
[ChatWidget] Shows undo confirmation
```

## Confidence-Based Routing

```
┌─────────────────────────────────────────────────┐
│  Confidence Score from NLP                      │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
    >0.7         0.4-0.7    <0.4
        │          │          │
        ↓          ↓          ↓
  ┌─────────┐ ┌─────────┐ ┌─────────┐
  │Auto-    │ │ Confirm │ │ Clarify │
  │Suggest  │ │ Required│ │ Request │
  └─────────┘ └─────────┘ └─────────┘
       │          │            │
       ↓          ↓            ↓
  [Single    [Confirm/    [Ask for
   click     Cancel       more
   apply]    buttons]     details]
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────┐
│  User Input                                          │
│  "add Eiffel Tower to day 2 morning"               │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────┐
│  NLP Processing                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │ Input: Raw text                                 │ │
│  │ Process: Tokenize → Flan-T5 → Parse JSON       │ │
│  │ Output: {intent, entities, command, confidence}│ │
│  └────────────────────────────────────────────────┘ │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────┐
│  Structured Edit Command                             │
│  {                                                   │
│    "action": "add",                                 │
│    "target": "activity",                            │
│    "poi": "Eiffel Tower",                          │
│    "day": 2,                                        │
│    "time_slot": "morning"                           │
│  }                                                   │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────┐
│  Itinerary Transformation                            │
│  Before:                     After:                  │
│  {                           {                       │
│    "days": [                   "days": [             │
│      {                           {                   │
│        "day_number": 2,            "day_number": 2, │
│        "activities": [...]         "activities": [  │
│      }                               ...,            │
│    ]                                 {               │
│  }                                     "name": "...",│
│                                        "poi": "..."  │
│                                      }                │
│                                   ]                  │
│                                 }                    │
│                               ]                      │
│                             }                        │
└────────────────┬─────────────────────────────────────┘
                 │
                 ↓
┌──────────────────────────────────────────────────────┐
│  Database Persistence                                │
│  ┌────────────────────────────────────────────────┐ │
│  │ itineraries: Updated content                   │ │
│  │ itinerary_edits: Audit record with snapshots   │ │
│  │ chat_sessions: Message history                 │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────┐
│  Client Request                                     │
│  (Contains user_id from auth session)              │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  Backend Validation                                 │
│  - Check authentication token                       │
│  - Validate request structure                       │
│  - Sanitize inputs                                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  Supabase RLS (Row Level Security)                 │
│  ┌───────────────────────────────────────────────┐ │
│  │ Policy: "Users can only access own data"      │ │
│  │ WHERE auth.uid() = user_id                    │ │
│  └───────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────┐ │
│  │ ALL queries filtered by user_id automatically │ │
│  │ Unauthorized access = 403 Forbidden           │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend Layer
- **Streamlit**: UI framework
- **Python Requests**: HTTP client

### Backend Layer
- **FastAPI**: REST API framework
- **Pydantic**: Data validation
- **httpx**: Async HTTP client

### NLP Layer
- **Flan-T5**: Language model
- **Transformers**: Model inference
- **Rasa**: Advanced NLU (optional)

### Data Layer
- **Supabase**: PostgreSQL database
- **RLS**: Row-level security
- **JSONB**: Flexible schema storage

### Orchestration Layer
- **LangGraph**: Workflow management
- **StateGraph**: State machine

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **pytest**: Testing framework
