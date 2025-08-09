"""
Chaos Engineering API Router

Provides endpoints for:
- Triggering chaos scenarios
- Managing chaos experiments
- Getting chaos history and status
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel
import subprocess
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class ChaosScenario(BaseModel):
    scenario_id: str
    name: str
    description: str
    target_namespace: Optional[str] = None
    difficulty: str  # "easy", "medium", "hard"
    estimated_duration: str  # e.g., "2-5 minutes"

class ChaosExecution(BaseModel):
    execution_id: str
    scenario_id: str
    status: str  # "running", "completed", "failed"
    started_at: datetime
    completed_at: Optional[datetime] = None
    output: Optional[str] = None
    error: Optional[str] = None

class ChaosInjectionRequest(BaseModel):
    scenario_id: str
    target_namespace: Optional[str] = None
    parameters: Optional[Dict] = None

# Available chaos scenarios
CHAOS_SCENARIOS = [
    ChaosScenario(
        scenario_id="pod_failure",
        name="Pod Failure Simulation",
        description="Randomly kill pods to test resilience",
        target_namespace="frontend",
        difficulty="easy",
        estimated_duration="1-2 minutes"
    ),
    ChaosScenario(
        scenario_id="node_drain",
        name="Node Drain Simulation", 
        description="Drain worker nodes to test scheduling",
        difficulty="medium",
        estimated_duration="3-5 minutes"
    ),
    ChaosScenario(
        scenario_id="resource_pressure",
        name="Resource Pressure",
        description="Create CPU/Memory stress",
        target_namespace="backend",
        difficulty="medium",
        estimated_duration="2-4 minutes"
    ),
    ChaosScenario(
        scenario_id="network_partition",
        name="Network Partition",
        description="Block cross-namespace communication",
        difficulty="hard",
        estimated_duration="5-10 minutes"
    ),
    ChaosScenario(
        scenario_id="storage_failure",
        name="Storage Failure",
        description="Simulate database outages",
        target_namespace="database",
        difficulty="hard",
        estimated_duration="3-7 minutes"
    ),
    ChaosScenario(
        scenario_id="cascading_failure",
        name="Cascading Failure",
        description="Multi-system failure simulation",
        difficulty="hard",
        estimated_duration="10-15 minutes"
    )
]

# In-memory storage for execution history (in production, use a database)
execution_history: List[ChaosExecution] = []

async def run_chaos_script(scenario_id: str, execution_id: str, parameters: Optional[Dict] = None):
    """Execute chaos scenario script in background"""
    try:
        # Update status to running
        execution = next((e for e in execution_history if e.execution_id == execution_id), None)
        if execution:
            execution.status = "running"
        
        # In a real implementation, this would call the actual chaos script
        # For now, simulate with a delay
        await asyncio.sleep(2)
        
        # Simulate script output
        if scenario_id == "pod_failure":
            output = "Successfully deleted 2 pods in frontend namespace\nPods are being recreated by ReplicaSet"
        elif scenario_id == "node_drain":
            output = "Drained node demo-cluster-worker2\nPods rescheduled to healthy nodes"
        else:
            output = f"Chaos scenario '{scenario_id}' executed successfully"
        
        # Update execution status
        if execution:
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            execution.output = output
            
        logger.info(f"Chaos scenario {scenario_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Chaos scenario {scenario_id} failed: {e}")
        if execution:
            execution.status = "failed"
            execution.completed_at = datetime.utcnow()
            execution.error = str(e)

@router.get("/scenarios", response_model=List[ChaosScenario])
async def get_chaos_scenarios():
    """Get list of available chaos scenarios"""
    return CHAOS_SCENARIOS

@router.get("/scenarios/{scenario_id}", response_model=ChaosScenario)
async def get_chaos_scenario(scenario_id: str):
    """Get details of a specific chaos scenario"""
    scenario = next((s for s in CHAOS_SCENARIOS if s.scenario_id == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Chaos scenario not found")
    return scenario

@router.post("/inject", response_model=ChaosExecution)
async def inject_chaos(
    request: ChaosInjectionRequest,
    background_tasks: BackgroundTasks
):
    """Trigger a chaos engineering scenario"""
    # Validate scenario exists
    scenario = next((s for s in CHAOS_SCENARIOS if s.scenario_id == request.scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail="Chaos scenario not found")
    
    # Create execution record
    execution_id = f"exec_{len(execution_history) + 1}_{int(datetime.utcnow().timestamp())}"
    execution = ChaosExecution(
        execution_id=execution_id,
        scenario_id=request.scenario_id,
        status="starting",
        started_at=datetime.utcnow()
    )
    
    execution_history.append(execution)
    
    # Run chaos script in background
    background_tasks.add_task(
        run_chaos_script,
        request.scenario_id,
        execution_id,
        request.parameters
    )
    
    return execution

@router.get("/executions", response_model=List[ChaosExecution])
async def get_chaos_executions(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None
):
    """Get chaos execution history"""
    executions = execution_history
    
    # Filter by status if specified
    if status:
        executions = [e for e in executions if e.status == status]
    
    # Sort by most recent first
    executions = sorted(executions, key=lambda x: x.started_at, reverse=True)
    
    # Apply pagination
    return executions[offset:offset + limit]

@router.get("/executions/{execution_id}", response_model=ChaosExecution)
async def get_chaos_execution(execution_id: str):
    """Get details of a specific chaos execution"""
    execution = next((e for e in execution_history if e.execution_id == execution_id), None)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

@router.post("/executions/{execution_id}/stop")
async def stop_chaos_execution(execution_id: str):
    """Stop a running chaos execution"""
    execution = next((e for e in execution_history if e.execution_id == execution_id), None)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.status != "running":
        raise HTTPException(status_code=400, detail="Execution is not running")
    
    # In a real implementation, this would stop the running script
    execution.status = "stopped"
    execution.completed_at = datetime.utcnow()
    execution.output = "Execution stopped by user"
    
    return {"message": f"Execution {execution_id} stopped", "status": "stopped"} 