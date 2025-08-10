#!/bin/bash

echo "🎯 Kubernetes Autonomous Agent Streaming Stack"
echo "=============================================="

# Load environment variables from .env files if they exist
if [ -f ".env" ]; then
    echo "📁 Loading environment from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

if [ -f "backend/google-adk/.env" ]; then
    echo "📁 Loading ADK environment from backend/google-adk/.env"
    export $(cat backend/google-adk/.env | grep -v '^#' | xargs)
fi

# Set cost-safe defaults
export AGENT_SAFE_MODE="${AGENT_SAFE_MODE:-true}"
export AGENT_AUTO_INVESTIGATE="${AGENT_AUTO_INVESTIGATE:-true}"

echo "🛡️  Agent Configuration:"
echo "   SAFE_MODE: $AGENT_SAFE_MODE (true = no AI API calls, false = may use OpenRouter)"
echo "   AUTO_INVESTIGATE: $AGENT_AUTO_INVESTIGATE (true = auto investigate issues, false = monitor only)"

# Setup signal handlers for graceful shutdown
BACKEND_PID=""
MONITOR_PID=""

cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        echo "  Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        wait $BACKEND_PID 2>/dev/null
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

# Function to start backend
start_backend() {
    echo "🚀 Starting FastAPI backend..."
    
    cd backend
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    
    # Start backend in background (without reload to avoid file watcher issues)
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    
    echo "✅ Backend started (PID: $BACKEND_PID)"
    echo "🔗 Backend available at: http://localhost:8000"
    
    # Wait for backend to be ready
    echo "⏳ Waiting for backend to start..."
    for i in {1..30}; do
        if curl -f http://localhost:8000/ >/dev/null 2>&1; then
            echo "✅ Backend is ready!"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo "❌ Backend failed to start"
            return 1
        fi
    done
}

# Function to start autonomous monitor
start_autonomous_monitor() {
    echo "🤖 Starting autonomous monitor..."
    
    cd api
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    export BACKEND_URL="http://localhost:8000"
    
    # Create reports directory
    mkdir -p /root/reports 2>/dev/null || mkdir -p $HOME/reports
    
    # Start autonomous monitor in background
    python3 autonomous_monitor.py &
    MONITOR_PID=$!
    
    cd ..
    
    echo "✅ Autonomous monitor started (PID: $MONITOR_PID)"
    echo "📝 Reports will be saved to: /root/reports/ or $HOME/reports/"
}

main() {
    # Start backend
    if ! start_backend; then
        echo "❌ Failed to start backend"
        exit 1
    fi
    
    # Start autonomous monitor
    if ! start_autonomous_monitor; then
        echo "❌ Failed to start autonomous monitor"
        exit 1
    fi
    
    echo ""
    echo "🎉 Streaming stack is running!"
    echo "=============================================="
    echo "📊 Backend API: http://localhost:8000"
    echo "📝 API Documentation: http://localhost:8000/docs"
    echo "🔄 WebSocket endpoint: ws://localhost:8000/ws/agent-status"
    echo ""
    echo "📋 Key endpoints:"
    echo "  GET  /api/agents/ - Agent status"
    echo "  GET  /api/cluster/ - Cluster status"
    echo "  POST /api/adk/v1/agent/run - AI agent chat"
    echo "  GET  /api/adk/status - ADK integration status"
    echo ""
    echo "🚀 To start the frontend:"
    echo "  cd frontend && npm start"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo "=============================================="
    
    # Keep script running and monitor processes
    while true; do
        # Check if processes are still running
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo "❌ Backend process died"
            break
        fi
        
        if ! kill -0 $MONITOR_PID 2>/dev/null; then
            echo "❌ Monitor process died"
            break
        fi
        
        sleep 5
    done
    
    cleanup
}

# Run main function
main 