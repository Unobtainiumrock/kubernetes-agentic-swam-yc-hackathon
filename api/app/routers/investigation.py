"""
FastAPI router for Kubernetes investigation endpoints.
"""
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime

# Import our investigation agents
from api.agents.deterministic_investigator import DeterministicInvestigator
from api.agents.agentic_investigator import AgenticInvestigator

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for investigation results (in production, use Redis/DB)
investigation_results: Dict[str, Dict[str, Any]] = {}
investigation_status: Dict[str, str] = {}


class InvestigationRequest(BaseModel):
    """Request model for starting an investigation."""
    investigation_type: str  # "deterministic" or "agentic"
    namespace: Optional[str] = None
    include_k8sgpt: bool = True
    include_events: bool = True
    timeout_seconds: int = 300


class InvestigationStatusResponse(BaseModel):
    """Response model for investigation status."""
    investigation_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: Optional[str] = None
    started_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class InvestigationResultResponse(BaseModel):
    """Response model for investigation results."""
    investigation_id: str
    status: str
    report: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@router.post("/investigate/deterministic", response_model=Dict[str, str])
async def start_deterministic_investigation(
    request: InvestigationRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Start a deterministic Kubernetes investigation.
    
    This investigation follows predefined steps to analyze cluster state.
    """
    if request.investigation_type != "deterministic":
        raise HTTPException(status_code=400, detail="Invalid investigation type for this endpoint")
    
    investigation_id = str(uuid.uuid4())
    
    # Initialize investigation tracking
    investigation_status[investigation_id] = "pending"
    investigation_results[investigation_id] = {
        "investigation_id": investigation_id,
        "type": "deterministic",
        "started_at": datetime.now().isoformat(),
        "request": request.dict()
    }
    
    # Start investigation in background
    background_tasks.add_task(
        _run_deterministic_investigation,
        investigation_id,
        request
    )
    
    logger.info(f"Started deterministic investigation: {investigation_id}")
    
    return {
        "investigation_id": investigation_id,
        "status": "pending",
        "message": "Deterministic investigation started"
    }


@router.post("/investigate/agentic", response_model=Dict[str, str])
async def start_agentic_investigation(
    request: InvestigationRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Start an AI-driven agentic Kubernetes investigation.
    
    This investigation uses AI to autonomously decide investigation approach.
    """
    if request.investigation_type != "agentic":
        raise HTTPException(status_code=400, detail="Invalid investigation type for this endpoint")
    
    investigation_id = str(uuid.uuid4())
    
    # Initialize investigation tracking
    investigation_status[investigation_id] = "pending"
    investigation_results[investigation_id] = {
        "investigation_id": investigation_id,
        "type": "agentic",
        "started_at": datetime.now().isoformat(),
        "request": request.dict()
    }
    
    # Start investigation in background
    background_tasks.add_task(
        _run_agentic_investigation,
        investigation_id,
        request
    )
    
    logger.info(f"Started agentic investigation: {investigation_id}")
    
    return {
        "investigation_id": investigation_id,
        "status": "pending",
        "message": "Agentic investigation started"
    }


@router.get("/investigate/status/{investigation_id}", response_model=InvestigationStatusResponse)
async def get_investigation_status(investigation_id: str) -> InvestigationStatusResponse:
    """Get the status of an ongoing or completed investigation."""
    if investigation_id not in investigation_status:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    result = investigation_results.get(investigation_id, {})
    
    return InvestigationStatusResponse(
        investigation_id=investigation_id,
        status=investigation_status[investigation_id],
        progress=result.get("progress"),
        started_at=result.get("started_at", ""),
        completed_at=result.get("completed_at"),
        error_message=result.get("error_message")
    )


@router.get("/investigate/report/{investigation_id}", response_model=InvestigationResultResponse)
async def get_investigation_report(investigation_id: str) -> InvestigationResultResponse:
    """Get the complete investigation report."""
    if investigation_id not in investigation_status:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    status = investigation_status[investigation_id]
    result = investigation_results.get(investigation_id, {})
    
    if status not in ["completed", "failed"]:
        raise HTTPException(
            status_code=409, 
            detail=f"Investigation is {status}. Report not available yet."
        )
    
    return InvestigationResultResponse(
        investigation_id=investigation_id,
        status=status,
        report=result.get("report"),
        error_message=result.get("error_message")
    )


@router.get("/investigate/list", response_model=Dict[str, Any])
async def list_investigations() -> Dict[str, Any]:
    """List all investigations with their current status."""
    investigations = []
    
    for inv_id, status in investigation_status.items():
        result = investigation_results.get(inv_id, {})
        investigations.append({
            "investigation_id": inv_id,
            "type": result.get("type", "unknown"),
            "status": status,
            "started_at": result.get("started_at"),
            "completed_at": result.get("completed_at")
        })
    
    return {
        "investigations": investigations,
        "total_count": len(investigations),
        "active_count": len([s for s in investigation_status.values() if s in ["pending", "running"]])
    }


@router.delete("/investigate/{investigation_id}")
async def delete_investigation(investigation_id: str) -> Dict[str, str]:
    """Delete an investigation and its results."""
    if investigation_id not in investigation_status:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    # Can only delete completed or failed investigations
    status = investigation_status[investigation_id]
    if status in ["pending", "running"]:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete active investigation"
        )
    
    del investigation_status[investigation_id]
    del investigation_results[investigation_id]
    
    logger.info(f"Deleted investigation: {investigation_id}")
    
    return {"message": "Investigation deleted successfully"}


@router.post("/investigate/quick-status", response_model=Dict[str, Any])
async def get_quick_cluster_status() -> Dict[str, Any]:
    """
    Get a quick cluster status check without full investigation.
    
    This is a lightweight endpoint for basic cluster health checks.
    """
    try:
        from api.agents.tools.kubectl_wrapper import KubectlWrapper
        from api.agents.tools.k8sgpt_wrapper import K8sgptWrapper
        
        kubectl = KubectlWrapper()
        k8sgpt = K8sgptWrapper()
        
        # Quick parallel checks
        tasks = [
            kubectl.get_nodes(),
            kubectl.get_pods_summary(),
            kubectl.get_cluster_info(),
            k8sgpt.analyze_cluster()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        quick_status = {
            "timestamp": datetime.now().isoformat(),
            "nodes": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "pods_summary": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
            "cluster_info": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
            "k8sgpt_analysis": results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])},
        }
        
        return {
            "status": "success",
            "quick_status": quick_status
        }
        
    except Exception as e:
        logger.error(f"Quick status check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quick status check failed: {str(e)}")


# Background task functions

async def _run_deterministic_investigation(investigation_id: str, request: InvestigationRequest):
    """Run deterministic investigation in background."""
    try:
        investigation_status[investigation_id] = "running"
        investigation_results[investigation_id]["progress"] = "Starting deterministic investigation..."
        
        # Run actual deterministic investigation
        investigator = DeterministicInvestigator()
        report = await investigator.run_investigation(
            namespace=request.namespace,
            include_k8sgpt=request.include_k8sgpt,
            include_events=request.include_events,
            timeout=request.timeout_seconds
        )
        
        investigation_status[investigation_id] = "completed"
        investigation_results[investigation_id].update({
            "completed_at": datetime.now().isoformat(),
            "report": report
        })
        
        logger.info(f"Completed deterministic investigation: {investigation_id}")
        
    except Exception as e:
        logger.error(f"Deterministic investigation failed: {e}")
        investigation_status[investigation_id] = "failed"
        investigation_results[investigation_id].update({
            "completed_at": datetime.now().isoformat(),
            "error_message": str(e)
        })


async def _run_agentic_investigation(investigation_id: str, request: InvestigationRequest):
    """Run agentic investigation in background."""
    try:
        investigation_status[investigation_id] = "running"
        investigation_results[investigation_id]["progress"] = "Starting agentic investigation..."
        
        # Run actual agentic investigation
        investigator = AgenticInvestigator()
        report = await investigator.run_investigation(
            namespace=request.namespace,
            include_k8sgpt=request.include_k8sgpt,
            include_events=request.include_events,
            timeout=request.timeout_seconds
        )
        
        investigation_status[investigation_id] = "completed"
        investigation_results[investigation_id].update({
            "completed_at": datetime.now().isoformat(),
            "report": report
        })
        
        logger.info(f"Completed agentic investigation: {investigation_id}")
        
    except Exception as e:
        logger.error(f"Agentic investigation failed: {e}")
        investigation_status[investigation_id] = "failed"
        investigation_results[investigation_id].update({
            "completed_at": datetime.now().isoformat(),
            "error_message": str(e)
        })


# Health check endpoint
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for the investigation service."""
    return {
        "status": "healthy",
        "service": "kubernetes-investigation",
        "timestamp": datetime.now().isoformat()
    }
