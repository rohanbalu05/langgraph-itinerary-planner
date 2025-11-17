#!/bin/bash

set -e

echo "=================================="
echo "Chat Feature Setup Script"
echo "=================================="
echo ""

echo "Step 1: Installing Python dependencies..."
echo ""

if command -v uv &> /dev/null; then
    echo "Using uv package manager..."
    uv sync
else
    echo "Using pip..."
    pip install -r backend/requirements.txt
    pip install -r nlp_service/requirements.txt
fi

echo ""
echo "Step 2: Checking environment variables..."
echo ""

if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env with:"
    echo "  VITE_SUPABASE_URL=your_url"
    echo "  VITE_SUPABASE_SUPABASE_ANON_KEY=your_key"
    exit 1
fi

if grep -q "VITE_SUPABASE_URL" .env && grep -q "VITE_SUPABASE_SUPABASE_ANON_KEY" .env; then
    echo "✓ Environment variables found"
else
    echo "❌ Missing Supabase credentials in .env"
    exit 1
fi

echo ""
echo "Step 3: Checking Docker..."
echo ""

if command -v docker &> /dev/null; then
    echo "✓ Docker is installed"

    if command -v docker-compose &> /dev/null; then
        echo "✓ Docker Compose is installed"
        USE_DOCKER=true
    else
        echo "⚠ Docker Compose not found, will use manual startup"
        USE_DOCKER=false
    fi
else
    echo "⚠ Docker not found, will use manual startup"
    USE_DOCKER=false
fi

echo ""
echo "Step 4: Starting services..."
echo ""

if [ "$USE_DOCKER" = true ]; then
    echo "Using Docker Compose..."
    docker-compose up -d

    echo "Waiting for services to be ready..."
    sleep 5

    if curl -s http://localhost:8001/health > /dev/null; then
        echo "✓ NLP Service is running"
    else
        echo "⚠ NLP Service may not be ready yet"
    fi

    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✓ Backend API is running"
    else
        echo "⚠ Backend API may not be ready yet"
    fi
else
    echo "Manual setup instructions:"
    echo ""
    echo "Terminal 1 - NLP Service:"
    echo "  cd nlp_service"
    echo "  python nlp_api.py"
    echo ""
    echo "Terminal 2 - Backend API:"
    echo "  python -m uvicorn backend.api_server:app --port 8000"
    echo ""
    echo "Terminal 3 - Streamlit App:"
    echo "  streamlit run app_with_chat.py"
fi

echo ""
echo "Step 5: Running tests..."
echo ""

if command -v pytest &> /dev/null; then
    echo "Running test suite..."
    pytest tests/ -v --tb=short || echo "⚠ Some tests failed (this is expected if services aren't fully running)"
else
    echo "⚠ pytest not installed, skipping tests"
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""

if [ "$USE_DOCKER" = true ]; then
    echo "1. Services are running via Docker"
    echo "   - NLP Service: http://localhost:8001"
    echo "   - Backend API: http://localhost:8000"
    echo ""
    echo "2. Start Streamlit app:"
    echo "   streamlit run app_with_chat.py"
    echo ""
    echo "3. View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "4. Stop services:"
    echo "   docker-compose down"
else
    echo "1. Start services in separate terminals (see instructions above)"
    echo ""
    echo "2. Once services are running, start Streamlit:"
    echo "   streamlit run app_with_chat.py"
fi

echo ""
echo "5. Run demo script:"
echo "   python demo_chat_workflow.py"
echo ""
echo "6. Run tests:"
echo "   pytest tests/ -v"
echo ""
echo "7. View API documentation:"
echo "   - Backend: http://localhost:8000/docs"
echo "   - NLP: http://localhost:8001/docs"
echo ""
echo "For full documentation, see:"
echo "  - README_CHAT_FEATURE.md"
echo "  - docs/chat_integration.md"
echo ""
