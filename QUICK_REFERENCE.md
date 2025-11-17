# Quick Reference Card

## 🚀 Getting Started (1 minute)

```bash
# Start services
docker-compose up -d

# Start Streamlit
streamlit run app_with_chat.py

# Run demo
python demo_chat_workflow.py
```

## 💬 Chat Commands Examples

### Add Activities
```
"add Eiffel Tower to day 2 in the morning"
"include Louvre Museum on day 1"
"schedule Seine River cruise for day 3 evening"
```

### Remove Activities
```
"remove Notre Dame from day 2"
"delete the afternoon activity on day 1"
"cancel the Louvre Museum"
```

### Change Timing
```
"change Eiffel Tower time to 3pm"
"shift lunch to 1:30pm"
"move dinner to 7pm"
```

### Update Budget
```
"increase budget to $2500"
"set budget at $3000"
"add $500 to budget"
```

### Change Hotel
```
"change hotel to Hotel Ritz"
"switch to Hilton Paris"
"update accommodation to Marriott"
```

### Other Edits
```
"move activity from day 1 to day 2"
"combine day 1 and day 2"
"split day 3 into two days"
```

## 🔧 Service URLs

| Service | URL | Port |
|---------|-----|------|
| Backend API | http://localhost:8000 | 8000 |
| NLP Service | http://localhost:8001 | 8001 |
| Streamlit | http://localhost:8501 | 8501 |
| Backend Docs | http://localhost:8000/docs | - |
| NLP Docs | http://localhost:8001/docs | - |

## 🧪 Testing Commands

```bash
# All tests
pytest tests/ -v

# Specific tests
pytest tests/test_nlp_parser.py -v
pytest tests/test_backend_api.py -v
pytest tests/test_integration.py -v

# With coverage
pytest tests/ --cov=backend --cov=nlp_service
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build

# View service status
docker-compose ps
```

## 🔍 Health Checks

```bash
# Backend
curl http://localhost:8000/health

# NLP Service
curl http://localhost:8001/health

# Check both
curl http://localhost:8000/health && curl http://localhost:8001/health && echo "✓ All services running"
```

## 📊 API Quick Reference

### Parse Message
```bash
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"message": "add Eiffel Tower to day 2"}'
```

### Send Chat Message
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "itinerary_id": "uuid",
    "message": "add activity"
  }'
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

## 🎨 Confidence Indicators

| Color | Score | Meaning | Action |
|-------|-------|---------|--------|
| 🟢 | >0.7 | High confidence | Auto-suggest |
| 🟡 | 0.4-0.7 | Medium confidence | Confirm required |
| 🔴 | <0.4 | Low confidence | Clarification needed |

## 🗂️ Database Tables

### itineraries
- Stores travel itineraries
- Fields: id, user_id, destination, budget, interests, dates, content

### itinerary_edits
- Audit log with snapshots
- Fields: change_id, before_snapshot, after_snapshot, confidence, status

### chat_sessions
- Conversation history
- Fields: messages (JSONB array), timestamps

## 🔐 Environment Variables

Required in `.env`:
```bash
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_SUPABASE_ANON_KEY=your_anon_key
```

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### NLP service errors
```bash
# Check if model is downloading
docker-compose logs nlp_service

# Manually test
cd nlp_service
python nlp_api.py
```

### Backend connection issues
```bash
# Verify Supabase credentials
cat .env | grep SUPABASE

# Test connection
python -c "from backend.supabase_client import supabase; print(supabase)"
```

### Low confidence scores
- Use more specific language
- Include day numbers and time slots
- Check training examples in `nlp_service/nlu.yml`

## 📚 Documentation Locations

| Document | Location | Purpose |
|----------|----------|---------|
| Quick Start | README_CHAT_FEATURE.md | Getting started |
| Full Guide | docs/chat_integration.md | Complete documentation |
| Architecture | docs/architecture.md | System design |
| Summary | IMPLEMENTATION_SUMMARY.md | Feature overview |
| This File | QUICK_REFERENCE.md | Quick reference |

## 🎯 Common Workflows

### 1. Generate + Edit Itinerary
```
1. Fill travel form → Generate itinerary
2. Chat: "add Eiffel Tower to day 2"
3. Review suggestion → Click "Apply"
4. See updated itinerary
```

### 2. Undo Recent Change
```
1. Make an edit
2. Click "Undo Last Change" button
3. Confirm reversion
```

### 3. Multiple Edits
```
1. Chat: "add activity A"
2. Chat: "remove activity B"
3. Chat: "change time to 3pm"
4. Each edit tracked separately
```

## 💡 Pro Tips

1. **Be Specific**: Include day numbers and time slots
   - ✓ "add Eiffel Tower to day 2 morning"
   - ✗ "add Eiffel Tower"

2. **Use Clear POI Names**: Avoid abbreviations
   - ✓ "Eiffel Tower"
   - ✗ "ET"

3. **Check Confidence**: Review suggestions before auto-apply

4. **Undo is Your Friend**: Experiment freely, changes are reversible

5. **Quick Actions**: Use buttons for common operations

## 🔄 Update Commands

```bash
# Update dependencies
uv sync

# Update NLP service
cd nlp_service
pip install -r requirements.txt --upgrade

# Update backend
cd backend
pip install -r requirements.txt --upgrade
```

## 📞 Support Resources

- **Service Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Test Suite**: `pytest tests/ -v`
- **Demo Script**: `python demo_chat_workflow.py`
- **Logs**: `docker-compose logs -f`

---

**Need more help?** Check `docs/chat_integration.md` for comprehensive documentation.
