# Complete Setup Guide: Autonomous Agent Streaming Stack

This guide shows you how to spin up the entire streaming stack for Kubernetes autonomous agents with real-time log streaming and investigation reports.

## 🎯 What This Sets Up

✅ **FastAPI Backend** - API endpoints and WebSocket streaming  
✅ **Autonomous Monitor Agent** - Real-time Kubernetes monitoring with issue detection  
✅ **React Frontend** - Real-time dashboard with live logs and agent status  
✅ **Investigation Reports** - Clickable links to detailed cluster analysis  
✅ **WebSocket Streaming** - Instant updates without page refresh  

## 🚀 Quick Start Options

### Option 1: Docker Compose Stack (Recommended)

This runs everything in containers with proper networking:

```bash
# Build and start the entire stack
make dev-up

# View logs from all services
make dev-logs

# Stop everything
make dev-down
```

**Endpoints:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000  
- API Docs: http://localhost:8000/docs

### Option 2: Inside Container Environment (Your Original Setup)

This runs inside your existing container with kubectl/k8s tools:

```bash
# Build and enter container
make build-local
make run-local

# Inside container, run the streaming stack
./run-streaming-stack.sh
```

Then in another terminal:
```bash
# Start the frontend (outside container)
cd frontend
npm start
```

**Endpoints:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000 (direct connection)
- API Docs: http://localhost:8000/docs
- WebSocket: ws://localhost:3000/ws/agent-status (via Vite proxy)

**Environment Configuration:**
```bash
# Cost-safe defaults (no AI API calls)
export AGENT_SAFE_MODE=true          # Only monitoring + deterministic investigation
export AGENT_AUTO_INVESTIGATE=true   # Auto-investigate with kubectl/k8sgpt

# Optional: Enable AI investigations (requires OpenRouter API key)
export AGENT_SAFE_MODE=false
export OPENROUTER_API_KEY=your_key_here
```

### Option 3: Host System with Script

Run directly on your host system:

```bash
# Run the streaming backend and agent
./run-streaming-stack.sh

# In another terminal, start frontend
cd frontend && npm start
```

## 📋 Detailed Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend)
- Kubernetes cluster (Kind, minikube, or real cluster)
- kubectl configured

### 1. Container-Based Setup (Recommended)

```bash
# Clone and enter directory
cd yc2

# Build the entire stack
make stack-build

# Start services one by one to see progress
make backend-up
make agent-up  
make frontend-up

# Or start everything at once
make dev-up
```

**View individual service logs:**
```bash
make backend-logs    # FastAPI backend logs
make agent-logs      # Autonomous monitor logs  
make frontend-logs   # React frontend logs
```

### 2. Manual Container Setup

If you prefer to see each step:

```bash
# Build images
docker-compose build

# Start backend first
docker-compose up -d backend

# Wait for backend health check
docker-compose exec backend curl -f http://localhost:8000/

# Start autonomous monitor
docker-compose up -d autonomous-monitor

# Start frontend
docker-compose up -d frontend

# View logs
docker-compose logs -f
```

### 3. Inside Existing Container (Your Original Method)

```bash
# Enter your development container
make run-local

# Inside container - start streaming stack
./run-streaming-stack.sh
```

This will:
- Install missing Python dependencies
- Start FastAPI backend on port 8000
- Start autonomous monitor with log streaming
- Show real-time logs and status

Then open another terminal for frontend:
```bash
cd frontend
npm install  # if first time
npm start    # starts on port 3000
```

## 🔧 Development Workflow

### Quick Restarts

```bash
# Restart just the agent (most common during development)
make dev-restart-agent

# Restart backend
make dev-restart-backend

# View live logs
make dev-logs
```

### Debugging

```bash
# Check individual service status
docker-compose ps

# Enter running containers
docker-compose exec backend bash
docker-compose exec autonomous-monitor bash

# View specific service logs
docker-compose logs backend
docker-compose logs autonomous-monitor
```

### Frontend Development

The frontend supports hot reload when running in development mode:

```bash
cd frontend
npm start
```

Changes to React components will automatically reload the browser.

## 📊 Monitoring the System

### Backend Health

**Development Setup (Container Environment):**
- Health endpoint: http://localhost:8000/
- API documentation: http://localhost:8000/docs
- Agent logs endpoint: http://localhost:8000/api/agents/logs/stream

**Docker Compose Setup:**
- Health endpoint: http://localhost:8002/
- API documentation: http://localhost:8002/docs
- Agent logs endpoint: http://localhost:8002/api/agents/logs/stream

### Real-time Logs

The frontend displays:
- Live stream of autonomous monitor logs
- Real-time cluster health status  
- Issue detection alerts
- Clickable investigation report links
- Connection status indicators

### WebSocket Testing

You can test WebSocket connections directly:

```bash
# Install wscat if needed
npm install -g wscat

# Connect to agent status WebSocket
# Development setup (via Vite proxy)
wscat -c ws://localhost:3000/ws/agent-status

# Or direct to backend (if no frontend running)
wscat -c ws://localhost:8000/ws/agent-status
```

## 🎯 What You'll See

### 1. Autonomous Monitor Logs
Real-time streaming of logs like:
```
🚨 ISSUES DETECTED! Triggering autonomous investigation...
📊 7 total issues found:
🟠 CrashLoopBackOff: frontend/crash-loop-app-6c8974df7f-phzdh
🤖 Starting deterministic investigation...
📝 Investigation results will be saved to: /root/reports/autonomous_report_20250810_002600.txt
✅ Investigation complete! Report saved
```

### 2. Agent Status Panel
- Real-time cluster metrics (nodes, pods, issues)
- Visual status indicators (healthy, issues detected, critical)
- Issue count and severity tracking
- Last update timestamps

### 3. Investigation Reports  
- Generated automatically when issues are detected
- Clickable "View Report" buttons in the logs
- Detailed cluster analysis with findings and recommendations
- Saved to `/root/reports/` directory

### 4. Live Log Stream
- Real-time log display with WebSocket connection
- Log filtering by level (info, warn, error)
- Auto-scroll and connection status
- Color-coded sources and log levels

## 🔄 Architecture Overview

```
┌─────────────────┐    WebSocket    ┌─────────────────┐    HTTP POST   ┌─────────────────┐
│  React Frontend │ ◄──────────────► │  FastAPI Backend│ ◄──────────────│ Autonomous      │
│  (Port 3000)    │                 │  (Port 8000)    │                │ Monitor Agent   │
│                 │                 │                 │                │                 │
│ - LiveLogStream │                 │ - /api/agents/  │                │ - kubectl       │
│ - AgentStatus   │                 │ - WebSocket     │                │ - Issue detect  │
│ - Reports       │                 │ - CORS enabled  │                │ - Investigations│
└─────────────────┘                 └─────────────────┘                └─────────────────┘
                                                                                │
                                                                                ▼
                                                                        ┌─────────────────┐
                                                                        │ Kubernetes      │
                                                                        │ Cluster         │
                                                                        │                 │
                                                                        │ - Pods          │
                                                                        │ - Nodes         │
                                                                        │ - Events        │
                                                                        └─────────────────┘
```

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check port availability
lsof -i :8000

# View backend logs
make backend-logs

# Restart backend
make dev-restart-backend
```

### Agent Not Connecting
```bash
# Check agent logs
make agent-logs

# Verify backend is accessible
curl http://localhost:8000/

# Restart agent
make dev-restart-agent
```

### Frontend Not Loading
```bash
# Check if backend is running
curl http://localhost:8000/

# Check WebSocket connection in browser console
# Should see: "WebSocket connected to agent status"

# Restart frontend
cd frontend && npm start
```

### No Logs Appearing
1. Ensure Kubernetes cluster is running
2. Check autonomous monitor is detecting issues
3. Verify WebSocket connection in browser dev tools
4. Check backend `/api/agents/logs/stream` endpoint

### Reports Not Loading
```bash
# Check reports directory exists
ls -la /root/reports/

# Check report endpoint
curl http://localhost:8000/api/agents/reports/autonomous_report_YYYYMMDD_HHMMSS.txt
```

## 🧹 Cleanup

```bash
# Stop all services
make dev-down

# Remove all containers and volumes
make clean

# Or manually
docker-compose down -v --remove-orphans
```

## 🚀 Production Notes

For production deployment:
1. Use proper secrets management
2. Configure HTTPS/TLS
3. Set up proper logging aggregation
4. Use production-grade WebSocket scaling
5. Implement authentication/authorization
6. Use external database for log persistence

## 📝 Next Steps

1. Start the stack using your preferred method above
2. Open http://localhost:3000 to see the frontend
3. Watch real-time logs stream in from the autonomous monitor
4. Click "View Report" links to see detailed investigation findings
5. Monitor cluster health in real-time

The system will continuously monitor your Kubernetes cluster and stream all autonomous agent activity to the frontend in real-time! 