#!/bin/bash

# 🚀 Full Stack Agentic Kubernetes Operator Demo Startup Script
# Single behavior: Build container → Start backend in container → Start frontend on host

set -e  # Exit on any error

echo "🚀 Starting Full Stack Agentic Kubernetes Operator Demo"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name failed to start after $((max_attempts * 2)) seconds"
    return 1
}

# Cleanup function
cleanup() {
    echo ""
    print_warning "Shutting down services..."
    
    # Stop container if running
    if docker ps -q -f name=k8s-dev-container > /dev/null 2>&1; then
        print_status "Stopping backend container..."
        docker stop k8s-dev-container > /dev/null 2>&1 || true
    fi
    
    # Kill frontend if we started it
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        print_status "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        wait $FRONTEND_PID 2>/dev/null || true
    fi
    
    print_success "All services stopped"
    exit 0
}

# Setup signal handlers
trap cleanup SIGINT SIGTERM

# Variables for process tracking
FRONTEND_PID=""

print_status "Step 1: Environment Validation"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "run-streaming-stack.sh" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check for required commands
for cmd in docker make node npm; do
    if ! command -v $cmd > /dev/null 2>&1; then
        print_error "$cmd is required but not installed"
        exit 1
    fi
done

print_success "Environment validation completed"

print_status "Step 2: Build Development Container"
echo "=============================================="

print_status "Building development container..."
if ! make build-local; then
    print_error "Failed to build development container"
    exit 1
fi
print_success "Development container built successfully"

print_status "Step 3: Start Backend Services in Container"
echo "=============================================="

print_status "Starting backend container with streaming stack..."

# Get the image name that was just built (same logic as Makefile)
REGISTRY="dfkozlov"
NAME="k8s-agentic-swarm-command-center"
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD | tr '[:upper:]' '[:lower:]')
IMAGE_NAME="${REGISTRY}/${NAME}:${GIT_BRANCH}-latest"

print_status "Using image: $IMAGE_NAME"

# Stop any existing container
docker stop k8s-dev-container > /dev/null 2>&1 || true
docker rm k8s-dev-container > /dev/null 2>&1 || true

# Start container in background with streaming stack
docker run -d --name k8s-dev-container \
    -v ${PWD}:/root \
    -v ${HOME}/.kube:/root/.kube:ro \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -p 8000:8000 \
    --network host \
    ${IMAGE_NAME} bash -c "cd /root && ./run-streaming-stack.sh"

# Wait for backend to be ready
if ! wait_for_service "http://localhost:8000/" "Backend"; then
    print_error "Backend failed to start in container"
    cleanup
    exit 1
fi

print_success "Backend services running in container"

print_status "Step 4: Install Frontend Dependencies"
echo "=============================================="

cd frontend
if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
    print_status "Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        print_error "Failed to install frontend dependencies"
        cleanup
        exit 1
    fi
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi

print_status "Step 5: Start Frontend"
echo "=============================================="

print_status "Starting React frontend..."
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
sleep 5
if ! wait_for_service "http://localhost:3000/" "Frontend"; then
    print_warning "Frontend may still be starting. Check manually at http://localhost:3000"
fi

print_status "Step 6: Full Stack Ready!"
echo "=============================================="
print_success "🎉 Full Stack Agentic Kubernetes Operator Demo is running!"
echo ""
echo "📊 Access Points:"
echo "   🌐 Frontend Dashboard:    http://localhost:3000"
echo "   🔧 Backend API:           http://localhost:8000"
echo "   📚 API Documentation:     http://localhost:8000/docs"
echo "   🔄 WebSocket Endpoint:    ws://localhost:3000/ws/agent-status"
echo ""
echo "📋 Key API Endpoints:"
echo "   GET  /api/agents/          - Agent status"
echo "   GET  /api/cluster/         - Cluster information"
echo "   POST /api/adk/v1/agent/run - AI agent chat"
echo "   GET  /api/adk/status       - ADK integration status"
echo ""
echo "📁 Reports Location: /root/reports/ (in container)"
echo ""
echo "🛡️  Running in SAFE MODE: No OpenRouter API costs"
echo "   To enable AI features: Set AGENT_SAFE_MODE=false in .env"
echo "   Requires: OPENROUTER_API_KEY in backend/google-adk/.env"
echo ""
echo "🚀 The system is now monitoring your Kubernetes cluster!"
echo "   Real-time logs and agent status will appear in the frontend."
echo ""
echo "Press Ctrl+C to stop all services"
echo "=============================================="

# Monitor container and frontend
while true; do
    # Check if container is still running
    if ! docker ps -q -f name=k8s-dev-container > /dev/null 2>&1; then
        print_error "Backend container stopped unexpectedly"
        cleanup
        exit 1
    fi
    
    # Check if frontend is still running
    if [ ! -z "$FRONTEND_PID" ] && ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_warning "Frontend process died unexpectedly"
        # Frontend can be restarted manually, don't exit
    fi
    
    sleep 5
done 