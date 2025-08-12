#!/bin/bash

# 🚀 Full Stack Container-First Startup Script
# Runs everything inside the container - pure container-first approach

set -e

echo "🚀 Full Stack Container-First Startup"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment variables from .env files if they exist
if [ -f ".env" ]; then
    echo "📁 Loading environment from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

if [ -f "backend/google-adk/.env" ]; then
    echo "📁 Loading ADK environment from backend/google-adk/.env"
    export $(cat backend/google-adk/.env | grep -v '^#' | xargs)
fi

# Function for graceful shutdown
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        echo "  Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        wait $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "  Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        wait $FRONTEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$MONITOR_PID" ] && kill -0 $MONITOR_PID 2>/dev/null; then
        echo "  Stopping autonomous monitor (PID: $MONITOR_PID)..."
        kill $MONITOR_PID
        wait $MONITOR_PID 2>/dev/null
    fi
    
    echo "✅ All services stopped"
    exit 0
}

# Trap signals for graceful shutdown
trap cleanup SIGINT SIGTERM

# Verify environment
print_status "Validating container environment..."

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js not found in container!"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    print_error "npm not found in container!"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python3 not found in container!"
    exit 1
fi

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found in container!"
    exit 1
fi

print_success "Container environment validated"

print_status "Node.js version: $(node --version)"
print_status "npm version: $(npm --version)"
print_status "Python version: $(python3 --version)"
print_status "kubectl version: $(kubectl version --client --short 2>/dev/null || echo 'kubectl available')"

# Start backend services
print_status "Starting backend services in container..."

cd backend
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Start FastAPI backend
print_status "Starting FastAPI backend..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
print_status "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/ >/dev/null 2>&1; then
        print_success "Backend is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start"
        exit 1
    fi
done

# Start autonomous monitor
print_status "Starting autonomous monitor..."
export BACKEND_URL="http://localhost:8000"

python3 -c "
import asyncio
import os
import sys

# Add the backend app directory to Python path
sys.path.insert(0, '/root/backend')

from app.services.autonomous_monitor import AutonomousMonitor

async def main():
    monitor = AutonomousMonitor(
        safe_mode=os.getenv('AGENT_SAFE_MODE', 'true').lower() == 'true',
        auto_investigate=os.getenv('AGENT_AUTO_INVESTIGATE', 'true').lower() == 'true',
        check_interval=int(os.getenv('AGENT_CHECK_INTERVAL', '30')),
        backend_url='http://localhost:8000'
    )
    await monitor.start_monitoring()

if __name__ == '__main__':
    asyncio.run(main())
" &
MONITOR_PID=$!

cd ..

print_success "Autonomous monitor started (PID: $MONITOR_PID)"

# Start frontend
print_status "Starting frontend in container..."

cd frontend

# Ensure dependencies are installed
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
fi

# Start Vite dev server with container-friendly settings
print_status "Starting Vite dev server..."
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

# Wait for frontend to be ready
print_status "Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:3000/ >/dev/null 2>&1; then
        print_success "Frontend is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        print_error "Frontend failed to start"
        exit 1
    fi
done

cd ..

echo ""
print_success "🎉 Full Stack Application Running in Container!"
echo "=============================================="
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🐍 Backend:  http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo ""
echo "🤖 Autonomous Monitor: Active (checking every ${AGENT_CHECK_INTERVAL:-30} seconds)"
echo "📝 Investigation Reports: /root/reports/"
echo ""
echo "💡 Container Environment Features:"
echo "   ✅ Node.js $(node --version) + npm $(npm --version)"
echo "   ✅ Python $(python3 --version | cut -d' ' -f2)"
echo "   ✅ All Kubernetes tools (kubectl, k8sgpt, k9s)"
echo "   ✅ Complete development environment"
echo ""
echo "Available endpoints:"
echo "   🏠 GET  /                           - API health check"
echo "   📊 GET  /docs                       - API documentation"
echo "   🤖 GET  /api/agents                 - Agent status"
echo "   📝 GET  /api/agents/logs/stream     - Live log stream"
echo "   🔥 POST /api/chaos/inject           - Trigger chaos scenarios"
echo "   📸 GET  /api/cluster/snapshot       - Cluster state snapshot"
echo "   🔍 POST /api/investigations/deterministic - Start deterministic investigation"
echo "   🧠 POST /api/investigations/agentic - Start AI investigation"
echo "   📈 GET  /api/monitoring/status      - Monitor status"
echo ""

if [ "${AGENT_SAFE_MODE:-true}" = "true" ]; then
    echo "⚠️  AI Features: SAFE MODE (deterministic only)"
    echo "   To enable AI features: Set AGENT_SAFE_MODE=false in .env"
    echo "   Requires: OPENROUTER_API_KEY in backend/google-adk/.env"
else
    echo "🧠 AI Features: ENABLED with AcmeCorp knowledge base"
    echo "   Enhanced investigations with company-specific guidance"
fi

echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Keep the script running and wait for services
wait 