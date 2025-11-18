# ✈️ AI Travel Itinerary Planner

*A search-augmented, locally powered travel itinerary generator with conversational editing.*

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 📌 Overview

The **AI Travel Itinerary Planner** creates personalized travel itineraries using a multi-step agent pipeline powered by LangGraph. It combines real-time web search, local LLM inference, and natural language processing to generate and edit travel plans through conversation.

**Key Features:**
- 🤖 AI-powered itinerary generation using LangGraph
- 💬 Conversational editing with natural language (NEW!)
- 🔍 Search-augmented generation (no hallucinations)
- 🏠 Local LLM for privacy and cost-efficiency
- 📊 Supabase database with audit trails
- 🔄 Undo/redo functionality
- 🎨 Clean Streamlit UI

---

## 🚀 Quick Start

### One-Command Installation

```bash
# Clone the repository
git clone https://github.com/rohanbalu05/langgraph-itinerary-planner.git
cd langgraph-itinerary-planner

# Install in development mode
pip install -e .

# Set up environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the app
streamlit run app_with_chat.py
```

### Using Docker (Recommended)

```bash
# Start services
docker-compose up -d

# Run Streamlit
streamlit run app_with_chat.py
```

**See detailed instructions:** [INSTALL.md](INSTALL.md)

---

## 📋 Requirements

- **Python**: 3.12, 3.13, or higher ✅
- **Disk Space**: ~5 GB (for ML models)
- **RAM**: 4 GB minimum, 8 GB recommended
- **OS**: Windows, macOS, or Linux

> **✅ Python 3.13 Fully Supported!** All dependency conflicts resolved. See [INSTALL_PYTHON_3.13.md](INSTALL_PYTHON_3.13.md) for quick setup.

**Optional:**
- Docker & Docker Compose (for containerized deployment)
- GPU (for faster model inference)

---

## 🧠 How It Works

### Architecture

```
User Input → Search Agent → Web Results → LLM Generation → Itinerary
                                                              ↓
                                                         Chat Widget
                                                              ↓
                                                    NLP Parser → Edit
                                                              ↓
                                                         Supabase DB
```

### **1. User Preferences → Search Queries**

LangGraph agents transform user travel goals (budget, cuisine, culture, places, duration) into targeted search queries.

### **2. Automated Web Search**

The Tavily search agent gathers real-time information:
- Popular attractions and hidden gems
- Food recommendations
- Cultural highlights
- Practical tips and timings

### **3. LLM Generation**

A locally hosted TinyLlama model generates:
- Day-wise itinerary with activities
- Time slots and durations
- Cost estimates
- Travel logistics

### **4. Conversational Editing (NEW!)**

Edit your itinerary through natural language:
```
"add Eiffel Tower to day 2 morning"
"remove the Louvre Museum"
"change budget to $2500"
```

The system uses Flan-T5 for intent recognition and provides confidence-based suggestions.

---

## ✨ Features

### Core Features
- ✅ Real-time information using automated search
- ✅ Search-augmented generation (no hallucinations)
- ✅ Local LLM (TinyLlama) for privacy
- ✅ LangGraph workflow orchestration
- ✅ Clean Streamlit UI

### Conversational Editing (v0.2.0)
- ✅ Natural language processing (Flan-T5 + Rasa)
- ✅ 12 supported intents (add, remove, change, etc.)
- ✅ Confidence-based UX (auto-apply, confirm, clarify)
- ✅ Undo/redo functionality
- ✅ Audit trails and versioning
- ✅ Real-time diff preview
- ✅ Fuzzy matching for location names

---

## 📦 Installation

### Method 1: Standard Installation (pip)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

### Method 2: Minimal Installation (No Chat)

```bash
# Install only basic features
pip install -r requirements-minimal.txt

# Run basic app (without conversational editing)
streamlit run app.py
```

### Method 3: Using uv (Modern Package Manager)

```bash
# Install uv
pip install uv

# Install all dependencies
uv sync
```

**For detailed installation instructions, see:** [INSTALL.md](INSTALL.md)

---

## 🎯 Usage

### Basic Usage

1. **Start the application:**
   ```bash
   streamlit run app_with_chat.py
   ```

2. **Fill out the form:**
   - Destination: e.g., "Paris"
   - Budget: e.g., $2000
   - Interests: art, food, history
   - Dates: 2025-06-01 to 2025-06-03

3. **Generate itinerary** (10-20 seconds)

4. **Edit via chat:**
   ```
   "add Eiffel Tower to day 2 morning"
   "change budget to $2500"
   ```

### With Docker

```bash
# Start backend services
docker-compose up -d

# Check health
curl http://localhost:8000/health
curl http://localhost:8001/health

# Run Streamlit
streamlit run app_with_chat.py
```

### Run Demo

```bash
# Automated demonstration
python demo_chat_workflow.py
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific tests
pytest tests/test_nlp_parser.py -v
pytest tests/test_backend_api.py -v
pytest tests/test_integration.py -v

# With coverage
pytest tests/ --cov=backend --cov=nlp_service
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [INSTALL.md](INSTALL.md) | Complete installation guide |
| [STEP_BY_STEP_GUIDE.md](STEP_BY_STEP_GUIDE.md) | Detailed usage instructions |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Command cheat sheet |
| [README_CHAT_FEATURE.md](README_CHAT_FEATURE.md) | Chat feature documentation |
| [docs/chat_integration.md](docs/chat_integration.md) | Technical architecture |
| [docs/architecture.md](docs/architecture.md) | System diagrams |
| [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | All documentation links |

---

## 🏗️ Project Structure

```
langgraph-itinerary-planner/
├── app.py                      # Basic Streamlit app
├── app_with_chat.py            # Enhanced app with chat
├── chat_widget.py              # Chat UI component
├── workflow.py                 # LangGraph workflow
├── workflow_extensions.py      # Edit operations
├── llm.py                      # LLM integration
├── backend/                    # FastAPI backend
│   ├── api_server.py          # Main API server
│   ├── routes/chat.py         # Chat endpoints
│   └── supabase_client.py     # Database client
├── nlp_service/               # NLP microservice
│   ├── nlp_api.py            # FastAPI NLP server
│   ├── flan_t5_parser.py     # Flan-T5 parser
│   ├── actions.py            # Rasa actions
│   └── nlu.yml               # Training data (60+ examples)
├── tests/                     # Test suite
│   ├── test_nlp_parser.py
│   ├── test_backend_api.py
│   └── test_integration.py
├── docs/                      # Documentation
├── requirements.txt           # All dependencies
├── requirements-minimal.txt   # Minimal setup
├── setup.py                   # Package setup
└── docker-compose.yml         # Docker orchestration
```

---

## 🛠️ Development

### Setting Up Development Environment

```bash
# Clone and install with dev tools
git clone https://github.com/rohanbalu05/langgraph-itinerary-planner.git
cd langgraph-itinerary-planner
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Format code
black .

# Lint code
flake8 .
```

### Making a Package Installable

The project uses `setup.py` for package management:

```bash
# Install in development mode (editable)
pip install -e .

# Install with extras
pip install -e ".[dev]"

# Build distribution
python setup.py sdist bdist_wheel
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Required
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_SUPABASE_ANON_KEY=your-anon-key

# Optional
TAVILY_API_KEY=your-tavily-key
OPENAI_API_KEY=your-openai-key
```

### Supabase Setup

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings → API
4. Copy URL and anon key to `.env`

Database schema is automatically applied.

---

## 🐛 Troubleshooting

### Common Issues

**`pip install -e .` fails:**
```bash
pip install --upgrade pip setuptools wheel
pip install -e .
```

**Module not found:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Docker services won't start:**
```bash
docker-compose down
docker-compose up -d --build
```

**PyTorch installation issues:**
```bash
# Install CPU version separately
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e .
```

For more troubleshooting, see [INSTALL.md](INSTALL.md#troubleshooting)

---

## 📊 Performance

- **Itinerary Generation**: 10-20 seconds
- **Chat Response**: ~500ms (NLP parsing)
- **Edit Application**: ~100ms (database transaction)
- **Model Loading**: One-time ~2-5 minutes (first run)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangGraph** - Workflow orchestration
- **Hugging Face** - Transformers and models
- **Streamlit** - UI framework
- **Supabase** - Backend as a Service
- **Rasa** - NLU framework
- **FastAPI** - API framework

---

## 📞 Support

- **Documentation**: See `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/rohanbalu05/langgraph-itinerary-planner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rohanbalu05/langgraph-itinerary-planner/discussions)

---

## 🗺️ Roadmap

- [ ] Multi-user support with authentication
- [ ] Mobile-responsive chat interface
- [ ] Voice input for chat commands
- [ ] Export itineraries to PDF/Calendar
- [ ] Multi-language support
- [ ] Collaborative editing
- [ ] Integration with booking APIs

---

**Made with ❤️ using LangGraph and AI**

**Star ⭐ this repo if you find it helpful!**
