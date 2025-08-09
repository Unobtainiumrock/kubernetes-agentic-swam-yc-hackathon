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

router = APIRouter()

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