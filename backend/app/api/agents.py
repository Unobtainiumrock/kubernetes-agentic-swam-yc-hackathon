"""
Agents API Router

Provides endpoints for:
- Agent status and health monitoring
- Agent history and logs
- Agent configuration management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
import json

router = APIRouter()

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

# Pydantic models
class AgentStatus(BaseModel):
    agent_id: str
    name: str
    status: str  # "running", "idle", "error", "stopped"
    last_action: Optional[str] = None
    last_seen: datetime
    cluster_context: str
    namespace: Optional[str] = None

class AgentAction(BaseModel):
    timestamp: datetime
    agent_id: str
    action_type: str  # "diagnosis", "healing", "monitoring"
    description: str
    status: str  # "success", "failed", "in_progress"
    details: Optional[Dict] = None

class AgentHistoryResponse(BaseModel):
    agent_id: str
    actions: List[AgentAction]
    total_count: int

# Add new models for streaming logs
class AgentLogEntry(BaseModel):
    timestamp: datetime
    agent_id: str
    log_level: str  # "info", "warn", "error", "debug"
    message: str
    source: str  # "autonomous_monitor", "deterministic_investigator", etc.
    details: Optional[Dict] = None

class AgentStreamStatus(BaseModel):
    agent_id: str
    status: str  # "healthy", "issues_detected", "investigating", "error"
    issues_count: int
    nodes_ready: int
    nodes_total: int
    pods_running: int
    pods_total: int
    last_update: datetime

# Mock data for development
MOCK_AGENTS = [
    AgentStatus(
        agent_id="agent-001",
        name="Cluster Monitor",
        status="running",
        last_action="Monitoring pod health in frontend namespace",
        last_seen=datetime.utcnow(),
        cluster_context="demo-cluster",
        namespace="frontend"
    ),
    AgentStatus(
        agent_id="agent-002", 
        name="Healing Agent",
        status="idle",
        last_action="Restarted failed pod: backend-app-xyz",
        last_seen=datetime.utcnow(),
        cluster_context="demo-cluster",
        namespace="backend"
    )
]

MOCK_ACTIONS = [
    AgentAction(
        timestamp=datetime.utcnow(),
        agent_id="agent-001",
        action_type="diagnosis",
        description="Detected pod crash in frontend namespace",
        status="success",
        details={"pod_name": "frontend-app-abc", "error": "CrashLoopBackOff"}
    ),
    AgentAction(
        timestamp=datetime.utcnow(),
        agent_id="agent-002",
        action_type="healing",
        description="Restarted crashed pod",
        status="success", 
        details={"pod_name": "frontend-app-abc", "action": "kubectl delete pod"}
    )
]

# Global storage for recent logs (in production, use Redis or similar)
RECENT_LOGS: List[AgentLogEntry] = []
AGENT_STATUS: Dict[str, AgentStreamStatus] = {}

@router.get("/", response_model=List[AgentStatus])
async def get_all_agents():
    """Get status of all active agents"""
    return MOCK_AGENTS

@router.get("/{agent_id}", response_model=AgentStatus)
async def get_agent_status(agent_id: str):
    """Get detailed status of a specific agent"""
    agent = next((a for a in MOCK_AGENTS if a.agent_id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.get("/{agent_id}/history", response_model=AgentHistoryResponse)
async def get_agent_history(
    agent_id: str, 
    limit: int = 50,
    offset: int = 0
):
    """Get action history for a specific agent"""
    # Filter actions by agent_id
    agent_actions = [a for a in MOCK_ACTIONS if a.agent_id == agent_id]
    
    # Apply pagination
    paginated_actions = agent_actions[offset:offset + limit]
    
    return AgentHistoryResponse(
        agent_id=agent_id,
        actions=paginated_actions,
        total_count=len(agent_actions)
    )

@router.get("/history/all", response_model=List[AgentAction])
async def get_all_agent_history(
    limit: int = 100,
    offset: int = 0,
    action_type: Optional[str] = None
):
    """Get combined action history from all agents"""
    actions = MOCK_ACTIONS
    
    # Filter by action type if specified
    if action_type:
        actions = [a for a in actions if a.action_type == action_type]
    
    # Apply pagination
    return actions[offset:offset + limit]

@router.post("/{agent_id}/restart")
async def restart_agent(agent_id: str):
    """Restart a specific agent"""
    agent = next((a for a in MOCK_AGENTS if a.agent_id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # In a real implementation, this would restart the agent pod
    agent.status = "starting"
    agent.last_seen = datetime.utcnow()
    
    return {"message": f"Agent {agent_id} restart initiated", "status": "starting"}

@router.post("/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop a specific agent"""
    agent = next((a for a in MOCK_AGENTS if a.agent_id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # In a real implementation, this would stop the agent pod
    agent.status = "stopped"
    agent.last_seen = datetime.utcnow()
    
    return {"message": f"Agent {agent_id} stopped", "status": "stopped"} 

@router.get("/logs/stream", response_model=List[AgentLogEntry])
async def get_recent_logs(
    limit: int = 50,
    log_level: Optional[str] = None,
    agent_id: Optional[str] = None
):
    """Get recent agent logs for streaming"""
    logs = RECENT_LOGS
    
    # Filter by log level
    if log_level:
        logs = [log for log in logs if log.log_level == log_level]
    
    # Filter by agent ID
    if agent_id:
        logs = [log for log in logs if log.agent_id == agent_id]
    
    # Return most recent logs first
    return sorted(logs, key=lambda x: x.timestamp, reverse=True)[:limit]

@router.post("/logs/add")
async def add_agent_log(log_entry: AgentLogEntry):
    """Add a new log entry (used by autonomous monitor)"""
    RECENT_LOGS.append(log_entry)
    
    # Keep only last 1000 logs in memory
    if len(RECENT_LOGS) > 1000:
        RECENT_LOGS.pop(0)
    
    # Broadcast to WebSocket clients
    from ..websockets import connection_manager
    log_data = {
        "type": "agent_log",
        "data": log_entry.dict()
    }
    await connection_manager.broadcast_json_to_channel(log_data, "agent-status")
    
    return {"status": "success", "message": "Log entry added"}

@router.post("/status/update")
async def update_agent_status(status: AgentStreamStatus):
    """Update agent streaming status (used by autonomous monitor)"""
    AGENT_STATUS[status.agent_id] = status
    
    # Broadcast to WebSocket clients
    from ..websockets import connection_manager
    status_data = {
        "type": "agent_status_update",
        "data": status.dict()
    }
    await connection_manager.broadcast_json_to_channel(status_data, "agent-status")
    
    return {"status": "success", "message": "Agent status updated"}

@router.get("/status/current")
async def get_current_agent_status():
    """Get current status of all agents"""
    return list(AGENT_STATUS.values())

@router.get("/reports/{filename}")
async def get_investigation_report(filename: str):
    """Get investigation report file"""
    import os
    from fastapi.responses import FileResponse
    
    # Security check - only allow specific file patterns
    if not filename.startswith("autonomous_report_") or not filename.endswith(".txt"):
        raise HTTPException(status_code=404, detail="Report not found")
    
    report_path = f"/root/reports/{filename}"
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=report_path,
        media_type="text/plain",
        filename=filename
    ) 