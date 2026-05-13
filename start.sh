#!/bin/bash
# ── Israel Jobs Finder — Start Script ──
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo ""
echo "🇮🇱  Israel Jobs Finder"
echo "──────────────────────────────"

# 1. Activate venv
cd "$BACKEND_DIR"
source venv/bin/activate

# 2. Start FastAPI backend in background
echo "🚀 Starting backend on http://localhost:8000 ..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 3. Open frontend in browser
sleep 1
echo "🌐 Opening frontend..."
open "$FRONTEND_DIR/index.html"

echo ""
echo "✅ All systems go!"
echo "   • Backend API : http://localhost:8000/docs"
echo "   • Frontend    : $FRONTEND_DIR/index.html"
echo ""
echo "⏳ First scrape is running in the background (~2-5 min)."
echo "   The map will populate automatically."
echo ""
echo "Press Ctrl+C to stop the server."

# Keep running until Ctrl+C
trap "kill $BACKEND_PID 2>/dev/null; echo '👋 Stopped.'; exit 0" INT TERM
wait $BACKEND_PID
