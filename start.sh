#!/usr/bin/env bash
# Quickstart script to launch Enterprise Multi-Agent AI System locally

set -e

echo "=========================================================="
echo " Starting Enterprise Multi-Agent AI System"
echo " Powered by Google Gemini API, LangGraph, and MCP"
echo "=========================================================="

# Ensure project root is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH:-.}:."

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv venv
  ./venv/bin/pip install -r requirements.txt
fi

# Initialize database
echo "Initializing database..."
./venv/bin/python backend/database/init_db.py

# Launch backend in background
echo "Starting FastAPI Backend on http://localhost:8000..."
./venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cleanup() {
  echo ""
  echo "Shutting down services..."
  kill $BACKEND_PID 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM

echo ""
echo "Backend running (PID $BACKEND_PID). Endpoints:"
echo "• Health Check: http://localhost:8000/health"
echo "• Swagger Docs: http://localhost:8000/docs"
echo "• Interactive CLI Demo: python demo.py"
echo ""

# Check if node/npm is available for frontend
if command -v npm &> /dev/null && [ -d "frontend/node_modules" ]; then
  echo "Starting Next.js Frontend Dashboard on http://localhost:3000..."
  npm --prefix frontend run dev
else
  echo "Tip: Run 'npm --prefix frontend install && npm --prefix frontend run dev' to start the web dashboard."
  echo "Waiting on backend (Press Ctrl+C to stop)..."
  wait $BACKEND_PID
fi
