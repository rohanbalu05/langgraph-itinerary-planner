# Installation Guide

Complete guide to installing and setting up the LangGraph Travel Itinerary Planner.

---

## 📋 Prerequisites

### Required Software

Before installing, ensure you have:

| Software | Minimum Version | Check Command | Download Link |
|----------|----------------|---------------|---------------|
| Python | 3.12+ | `python --version` | [python.org](https://www.python.org/downloads/) |
| pip | 23.0+ | `pip --version` | Included with Python |
| Git | 2.0+ | `git --version` | [git-scm.com](https://git-scm.com/downloads) |

### Optional (Recommended)

| Software | Purpose | Check Command |
|----------|---------|---------------|
| Docker | Containerization | `docker --version` |
| Docker Compose | Multi-service orchestration | `docker-compose --version` |

---

## 🚀 Installation Methods

Choose the method that works best for you:

### Method 1: Standard Installation (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/rohanbalu05/langgraph-itinerary-planner.git
cd langgraph-itinerary-planner

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install in development mode
pip install -e .

# 5. Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials
```

### Method 2: Using pip directly

```bash
# Install from the project directory
pip install -e .

# Or install with specific extras
pip install -e ".[dev]"  # With development tools
```

### Method 3: Minimal Installation (Without Chat Feature)

If you only want the basic itinerary generation without conversational editing:

```bash
# 1. Install minimal requirements
pip install -r requirements-minimal.txt

# 2. Run the basic app
streamlit run app.py
```

### Method 4: Using uv (Modern Package Manager)

```bash
# Install uv first
pip install uv

# Install all dependencies
uv sync

# Or install in development mode
uv pip install -e .
```

---

## 🐍 Virtual Environment Setup

### Why Use a Virtual Environment?

Virtual environments isolate project dependencies and prevent conflicts with system packages.

### Creating a Virtual Environment

#### Using venv (Standard)

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Verify activation (should show venv path)
which python  # macOS/Linux
where python  # Windows
```

#### Using conda

```bash
# Create environment
conda create -n itinerary-planner python=3.12

# Activate it
conda activate itinerary-planner

# Install dependencies
pip install -e .
```

#### Using virtualenv

```bash
# Install virtualenv
pip install virtualenv

# Create environment
virtualenv venv

# Activate
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

---

## 📦 Dependency Installation

### Understanding Dependencies

The project has several categories of dependencies:

| Category | Files | Purpose |
|----------|-------|---------|
| Full Installation | `requirements.txt` | All features including chat |
| Minimal | `requirements-minimal.txt` | Basic functionality only |
| Development | `setup.py extras_require['dev']` | Testing and development tools |
| Backend | `backend/requirements.txt` | API server dependencies |
| NLP Service | `nlp_service/requirements.txt` | NLP/AI model dependencies |

### Installing All Dependencies

```bash
# Standard installation
pip install -r requirements.txt

# Or using setup.py
pip install -e .
```

### Installing Specific Components

```bash
# Just the backend
pip install -r backend/requirements.txt

# Just the NLP service
pip install -r nlp_service/requirements.txt

# Development tools
pip install -e ".[dev]"
```

---

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Required: Supabase Configuration
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_SUPABASE_ANON_KEY=your-anon-key-here

# Optional: Tavily API Key (for enhanced search)
TAVILY_API_KEY=your-tavily-api-key-here
```

### 2. Getting Supabase Credentials

1. Go to [supabase.com](https://supabase.com)
2. Create a free account
3. Create a new project
4. Go to Project Settings → API
5. Copy:
   - Project URL → `VITE_SUPABASE_URL`
   - `anon` `public` key → `VITE_SUPABASE_SUPABASE_ANON_KEY`

### 3. Database Migration

The database schema is automatically applied when you use the Supabase integration. The migration file is already included.

To verify:
```bash
# Check if tables exist (using Supabase dashboard)
# Tables: itineraries, itinerary_edits, chat_sessions
```

---

## 🐳 Docker Installation

### Prerequisites

- Docker Desktop (includes Docker Compose)
- Download from [docker.com](https://www.docker.com/get-started)

### Quick Start with Docker

```bash
# 1. Clone and navigate
git clone https://github.com/rohanbalu05/langgraph-itinerary-planner.git
cd langgraph-itinerary-planner

# 2. Create .env file
cp .env.example .env
# Edit .env with your Supabase credentials

# 3. Start services
docker-compose up -d

# 4. Verify services
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8001/health

# 5. Run Streamlit (in a separate terminal)
pip install streamlit requests
streamlit run app_with_chat.py
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose up -d --build

# View running containers
docker-compose ps

# Execute command in container
docker-compose exec backend_api bash
```

---

## 🖥️ Platform-Specific Instructions

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Install the project
python3.12 -m venv venv
source venv/bin/activate
pip install -e .
```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3.12-dev

# Install the project
python3.12 -m venv venv
source venv/bin/activate
pip install -e .
```

### Windows

```powershell
# Install Python from python.org
# Download: https://www.python.org/downloads/windows/
# Make sure to check "Add Python to PATH" during installation

# Open Command Prompt or PowerShell
# Navigate to project directory
cd path\to\langgraph-itinerary-planner

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install the project
pip install -e .
```

---

## ✅ Verifying Installation

### Check Python Packages

```bash
# List installed packages
pip list

# Check specific packages
pip show langgraph streamlit fastapi

# Verify version
python -c "import streamlit; print(streamlit.__version__)"
```

### Test Import

```bash
# Test core imports
python -c "from backend.api_server import app; print('Backend OK')"
python -c "from nlp_service.flan_t5_parser import FlanT5Parser; print('NLP OK')"
python -c "from chat_widget import ChatWidget; print('Widget OK')"
```

### Run Health Checks

```bash
# If services are running
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_nlp_parser.py -v

# Run with coverage
pytest tests/ --cov=backend --cov=nlp_service
```

---

## 🔧 Troubleshooting

### Issue 1: `pip install -e .` fails

**Symptom**: Error during installation

**Solutions**:
```bash
# Update pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Try again
pip install -e .

# If still fails, install dependencies first
pip install -r requirements.txt
pip install -e . --no-deps
```

### Issue 2: Python version mismatch

**Symptom**: `requires python >=3.12`

**Solutions**:
```bash
# Check Python version
python --version

# Install Python 3.12
# macOS: brew install python@3.12
# Ubuntu: sudo apt install python3.12
# Windows: Download from python.org

# Use specific version
python3.12 -m venv venv
```

### Issue 3: Virtual environment activation fails

**Symptom**: Virtual environment won't activate

**Solutions**:
```bash
# Windows PowerShell (if execution policy blocks)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again
venv\Scripts\activate

# Alternative on Windows
venv\Scripts\Activate.ps1
```

### Issue 4: ModuleNotFoundError

**Symptom**: `ModuleNotFoundError: No module named 'X'`

**Solutions**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or reinstall in editable mode
pip install -e . --force-reinstall
```

### Issue 5: torch installation fails

**Symptom**: torch/PyTorch installation errors

**Solutions**:
```bash
# Install PyTorch separately (CPU version)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install the rest
pip install -e .

# For GPU support (CUDA)
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Issue 6: Rasa installation fails

**Symptom**: Error installing rasa

**Solutions**:
```bash
# Rasa has many dependencies, install separately
pip install rasa==3.6.0 --no-deps

# Then install rasa dependencies
pip install -r nlp_service/requirements.txt
```

### Issue 7: Permission denied errors

**Symptom**: Permission errors during installation

**Solutions**:
```bash
# Don't use sudo with pip in virtual environment
# Instead, ensure virtual environment is activated

# If on Linux/macOS and still need permissions
pip install --user -e .

# Better: Fix virtual environment permissions
chmod -R u+w venv/
```

---

## 🔄 Updating the Project

### Pull Latest Changes

```bash
# Update code
git pull origin main

# Update dependencies
pip install -e . --upgrade

# Or update specific packages
pip install --upgrade streamlit fastapi
```

### Reinstalling After Updates

```bash
# Clean installation
pip uninstall langgraph-trip-planner
pip install -e .

# Or force reinstall
pip install -e . --force-reinstall --no-cache-dir
```

---

## 🗑️ Uninstallation

### Remove Virtual Environment

```bash
# Deactivate first
deactivate

# Remove virtual environment directory
rm -rf venv/  # macOS/Linux
rmdir /s venv  # Windows
```

### Uninstall Package

```bash
pip uninstall langgraph-trip-planner

# Remove all dependencies (careful!)
pip freeze > installed.txt
pip uninstall -r installed.txt -y
```

---

## 📊 System Requirements

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 5 GB free space
- **Python**: 3.12+

### Recommended Requirements

- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk**: 10 GB free space
- **Python**: 3.12+
- **GPU**: Optional, for faster AI inference

### Dependency Sizes

| Component | Approximate Size |
|-----------|-----------------|
| PyTorch | ~2 GB |
| Transformers | ~500 MB |
| Rasa | ~300 MB |
| Other packages | ~1 GB |
| **Total** | **~4 GB** |

---

## 🎓 Next Steps After Installation

1. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Run the demo**
   ```bash
   python demo_chat_workflow.py
   ```

3. **Start the application**
   ```bash
   streamlit run app_with_chat.py
   ```

4. **Read the documentation**
   - `STEP_BY_STEP_GUIDE.md` - Complete usage guide
   - `QUICK_REFERENCE.md` - Command reference
   - `README_CHAT_FEATURE.md` - Feature documentation

---

## 📞 Getting Help

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Review the logs**
   ```bash
   # For Docker
   docker-compose logs -f

   # For manual services
   # Check terminal output
   ```
3. **Verify installation**
   ```bash
   pip list
   pytest tests/ -v
   ```
4. **Consult documentation**
   - STEP_BY_STEP_GUIDE.md
   - docs/chat_integration.md

---

## ✅ Installation Checklist

- [ ] Python 3.12+ installed
- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -e .`)
- [ ] `.env` file created and configured
- [ ] Services start successfully (if using Docker)
- [ ] Tests pass (`pytest tests/`)
- [ ] Can import main modules
- [ ] Health checks return OK
- [ ] Streamlit app loads

---

**Installation complete!** You're ready to use the LangGraph Travel Itinerary Planner.

For usage instructions, see `STEP_BY_STEP_GUIDE.md` or run:
```bash
python demo_chat_workflow.py
```
