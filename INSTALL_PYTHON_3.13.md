# Quick Installation Guide for Python 3.13+

## ✅ Fixed: Python 3.13 Compatibility

All dependency issues have been resolved! You can now install on Python 3.12, 3.13, and likely 3.14.

---

## 🚀 Quick Install (3 Commands)

```bash
# 1. Update pip
python3 -m pip install --upgrade pip setuptools wheel

# 2. Install the project
pip install -e .

# 3. Run the app
streamlit run app_with_chat.py
```

That's it! 🎉

---

## 📋 Step-by-Step Installation

### Step 1: Verify Python Version

```bash
python3 --version
```

**Expected output:** `Python 3.13.x` or `Python 3.12.x`

---

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

---

### Step 3: Update pip

```bash
python3 -m pip install --upgrade pip setuptools wheel
```

---

### Step 4: Install Project

```bash
# Install in development mode
pip install -e .
```

This will install all dependencies automatically!

---

### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Supabase credentials
nano .env  # or use any text editor
```

Add your credentials:
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_SUPABASE_ANON_KEY=your-anon-key-here
```

---

### Step 6: Run the Application

```bash
streamlit run app_with_chat.py
```

Your browser will open automatically! 🎉

---

## 🐳 Alternative: Docker Installation

```bash
# Start services
docker-compose up -d

# Run Streamlit
streamlit run app_with_chat.py
```

---

## 🧪 Verify Installation

### Check Packages

```bash
pip list | grep -E "(fastapi|streamlit|torch|transformers)"
```

### Test Imports

```bash
python3 -c "import fastapi, streamlit, torch, transformers; print('✅ Success!')"
```

### Run Tests

```bash
pytest tests/ -v
```

---

## ⚡ Minimal Installation (Faster, ~2 GB)

If you want just the basic features without conversational editing:

```bash
pip install -r requirements-minimal.txt
streamlit run app.py
```

---

## 🔧 Troubleshooting

### Error: "No module named pip"

```bash
# Install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

### Error: Permission denied

```bash
# Use virtual environment instead of --user
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Error: Package conflicts

```bash
# Clear cache and reinstall
pip cache purge
pip install -e . --force-reinstall --no-cache-dir
```

### PyTorch installation is slow

```bash
# Install PyTorch separately first
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install the rest
pip install -e .
```

---

## 📊 What Changed?

### ✅ Fixed Version Conflicts
- Updated 25+ packages to Python 3.13-compatible versions
- Changed from exact pins (`==`) to minimum versions (`>=`)
- Removed incompatible packages (Rasa)

### ✅ All Features Still Work
- ✅ AI itinerary generation
- ✅ Conversational editing via chat
- ✅ Streamlit UI
- ✅ Database persistence
- ✅ Search functionality

---

## 🎯 Next Steps After Installation

1. **Generate an itinerary:**
   - Fill out the form (destination, budget, dates)
   - Click "Generate Itinerary"

2. **Try the chat feature:**
   ```
   "add Eiffel Tower to day 2 morning"
   "change budget to $3000"
   ```

3. **Run the demo:**
   ```bash
   python demo_chat_workflow.py
   ```

---

## 📚 More Documentation

- **INSTALL.md** - Complete installation guide
- **PYTHON_3.13_COMPATIBILITY_FIX.md** - Detailed fix documentation
- **STEP_BY_STEP_GUIDE.md** - Usage instructions
- **QUICK_REFERENCE.md** - Command cheat sheet

---

## ✅ Installation Checklist

- [ ] Python 3.12+ installed
- [ ] Virtual environment created & activated
- [ ] pip updated to latest version
- [ ] Project installed (`pip install -e .`)
- [ ] `.env` file configured with Supabase credentials
- [ ] Can import core packages (fastapi, streamlit, torch)
- [ ] Streamlit app runs successfully
- [ ] Tests pass (optional)

---

**Installation is now working for Python 3.13!** 🚀

If you encounter any issues, see **PYTHON_3.13_COMPATIBILITY_FIX.md** for detailed troubleshooting.
