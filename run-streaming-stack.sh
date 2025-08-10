#!/bin/bash

echo "🎯 Kubernetes Autonomous Agent Streaming Stack"
echo "=============================================="

# Check if we're inside the container
if [ -f "/.dockerenv" ]; then
    echo "✅ Running inside container"
    INSIDE_CONTAINER=true
else
    echo "⚠️  Running outside container - will use host Python"
    INSIDE_CONTAINER=false
fi

# Function to install dependencies if needed
install_dependencies() {
    echo "🔍 Checking Python dependencies..."
    
    if ! python3 -c "import aiohttp" 2>/dev/null; then
        echo "📦 Installing aiohttp..."
        pip3 install aiohttp>=3.8.0 --break-system-packages 2>/dev/null || \
        pip3 install aiohttp>=3.8.0 --user || \
        pip3 install aiohttp>=3.8.0
    fi
    
    if ! python3 -c "import fastapi" 2>/dev/null; then
        echo "📦 Installing FastAPI requirements..."
        if [ -f "backend/requirements.txt" ]; then
            pip3 install -r backend/requirements.txt --break-system-packages 2>/dev/null || \
            pip3 install -r backend/requirements.txt --user || \
            pip3 install -r backend/requirements.txt
        fi
    fi
    
    if ! python3 -c "import dateutil" 2>/dev/null; then
        echo "📦 Installing python-dateutil..."
        pip3 install python-dateutil --break-system-packages 2>/dev/null || \
        pip3 install python-dateutil --user || \
        pip3 install python-dateutil
    fi
    
    echo "✅ Dependencies ready"
}

# Function to start backend
start_backend() {
    echo "🚀 Starting FastAPI backend..."
    
    cd backend
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    
    # Start backend in background
    python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
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
    export BACKEND_URL="http://localhost:8001"
    
    # Create reports directory
    mkdir -p /root/reports 2>/dev/null || mkdir -p $HOME/reports
    
    # Start autonomous monitor in background
    python3 autonomous_monitor.py &
    MONITOR_PID=$!
    
    cd ..
    
    echo "✅ Autonomous monitor started (PID: $MONITOR_PID)"
    echo "📝 Reports will be saved to: /root/reports/ or $HOME/reports/"
}

# Function to cleanup processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped"
    fi
    
    if [ ! -z "$MONITOR_PID" ]; then
        kill $MONITOR_PID 2>/dev/null
        echo "✅ Autonomous monitor stopped"
    fi
    
    echo "👋 Cleanup complete!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    # Install dependencies
    install_dependencies
    
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
    echo "📋 Available endpoints:"
    echo "  GET  /api/agents/logs/stream - Get recent logs"
    echo "  GET  /api/agents/status/current - Get agent status"
    echo "  GET  /api/agents/reports/{filename} - Get investigation reports"
    echo ""
    echo "🚀 To start the frontend:"
    echo "  cd frontend && npm start"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo "=============================================="
    
    # Keep script running
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