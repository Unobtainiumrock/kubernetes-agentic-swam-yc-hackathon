# Autonomous Agent Log Streaming Setup

This setup enables real-time streaming of autonomous agent logs from the Kubernetes monitoring system to the React frontend.

## What This Does

✅ **Real-time Log Streaming**: Autonomous monitor logs stream directly to the frontend
✅ **Investigation Reports**: View autonomous investigation reports with clickable links  
✅ **Live Agent Status**: Real-time cluster health and issue detection
✅ **WebSocket Integration**: Instant updates without page refresh

## Quick Start

### 1. Start the Streaming System

```bash
# Start both backend and autonomous monitor
python3 start_streaming_demo.py
```

This will:
- Start FastAPI backend on http://localhost:8000
- Start autonomous monitor with log streaming
- Display real-time logs and status

### 2. Start the Frontend

```bash
cd frontend
npm start
```

Frontend will be available at http://localhost:3000

### 3. View the Streaming

The frontend will now display:
- **Real-time Agent Logs**: Live stream from autonomous monitor
- **Agent Status Panel**: Current cluster health and issue counts
- **Investigation Reports**: Clickable links to detailed reports
- **Connection Status**: WebSocket connection indicator

## Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐
│  React Frontend │ ◄──────────────► │  FastAPI Backend│
│                 │    (logs &      │                 │
│  - LiveLogStream│     status)     │  - /api/agents/ │
│  - AgentStatus  │                 │  - WebSocket    │
└─────────────────┘                 └─────────────────┘
                                            ▲
                                            │ HTTP POST
                                            │ (logs & status)
                                    ┌─────────────────┐
                                    │ Autonomous      │
                                    │ Monitor         │
                                    │                 │
                                    │ - Health checks │
                                    │ - Issue detection│
                                    │ - Investigations│
                                    └─────────────────┘
```

## Key Features

### 1. Real-time Log Streaming
- Autonomous monitor sends logs to FastAPI backend via HTTP
- Backend broadcasts logs to frontend via WebSocket  
- Frontend displays logs with filtering and real-time updates

### 2. Investigation Reports
- When issues are detected, autonomous monitor generates investigation reports
- Reports are saved to `/root/reports/` directory
- Frontend provides clickable links to view full reports
- Reports include cluster analysis, findings, and recommendations

### 3. Agent Status Updates
- Real-time cluster health metrics (nodes, pods, issues)
- Visual status indicators (healthy, issues detected, critical)
- Issue count and severity tracking

## Log Format

Logs are structured with:
```json
{
  "timestamp": "2025-01-09T12:00:00Z",
  "agent_id": "autonomous_monitor", 
  "log_level": "warn",
  "message": "🚨 ISSUES DETECTED! Triggering investigation...",
  "source": "autonomous_monitor",
  "details": {
    "issues_count": 3,
    "issues_summary": ["CrashLoopBackOff: frontend/pod-xyz", ...]
  }
}
```

## API Endpoints

- `GET /api/agents/logs/stream` - Get recent logs
- `POST /api/agents/logs/add` - Add new log entry  
- `POST /api/agents/status/update` - Update agent status
- `GET /api/agents/status/current` - Get current agent status
- `GET /api/agents/reports/{filename}` - Download investigation reports
- `WS /ws/agent-status` - WebSocket for real-time updates

## Frontend Components

### LiveLogStream.jsx
- Real-time log display with WebSocket connection
- Log filtering by level (info, warn, error) 
- Clickable links for investigation reports
- Connection status indicator

### AgentStatusPanel.jsx  
- Real-time agent status display
- Cluster health metrics (nodes, pods, issues)
- Visual status indicators with color coding
- Last update timestamps

## Troubleshooting

### Backend Not Starting
```bash
# Check if port 8000 is available
lsof -i :8000

# Install missing dependencies
pip install -r backend/requirements.txt
```

### Frontend Not Connecting
- Ensure backend is running on http://localhost:8000
- Check browser console for WebSocket connection errors
- Verify CORS settings in backend

### No Logs Appearing
- Check autonomous monitor is running and detecting issues
- Verify log streamer is connecting to backend
- Check WebSocket connection in browser dev tools

### Reports Not Loading
- Ensure `/root/reports/` directory exists and is writable
- Check file permissions for generated reports
- Verify report endpoint is accessible

## Development Notes

- Log streaming uses aiohttp for async HTTP requests
- WebSocket connections auto-reconnect on failure
- Log buffer handles backend unavailability
- Frontend gracefully handles connection drops

## Example Usage

1. Start the streaming system
2. Open frontend at http://localhost:3000  
3. Watch real-time logs appear in the "Live Logs" panel
4. See agent status updates in the "Agent Status" panel
5. Click "View Report" links to see detailed investigation findings
6. Filter logs by severity level (info, warn, error)

The system will continuously monitor your Kubernetes cluster and stream all autonomous agent activity to the frontend in real-time! 