"""
Investigation API endpoints for autonomous Kubernetes agents.
"""

import asyncio
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ..schemas import HealthResponse

# Import the moved agents
try:
    from ..agents.deterministic_investigator import DeterministicInvestigator
    from ..agents.agentic_investigator import AgenticInvestigator
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

router = APIRouter()

class InvestigationRequest(BaseModel):
    investigation_type: str = "deterministic"
    namespace: Optional[str] = None
    include_k8sgpt: bool = True
    include_events: bool = True
    timeout: int = 300

class InvestigationResponse(BaseModel):
    investigation_id: str
    status: str
    message: str

class InvestigationResult(BaseModel):
    investigation_id: str
    status: str
    report: Optional[str] = None
    error: Optional[str] = None

# In-memory storage for investigation results
investigation_results = {}

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check for investigation service"""
    return HealthResponse(
        status="ok" if AGENTS_AVAILABLE else "limited", 
        service="investigation-api", 
        version="0.1.0"
    )

@router.post("/deterministic", response_model=InvestigationResponse)
async def start_deterministic_investigation(
    request: InvestigationRequest,
    background_tasks: BackgroundTasks
) -> InvestigationResponse:
    """Start a deterministic investigation"""
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Investigation agents not available")
    
    investigation_id = str(uuid.uuid4())
    
    # Start investigation in background
    background_tasks.add_task(
        run_deterministic_investigation,
        investigation_id,
        request.namespace,
        request.include_k8sgpt,
        request.include_events,
        request.timeout
    )
    
    return InvestigationResponse(
        investigation_id=investigation_id,
        status="started",
        message="Deterministic investigation started"
    )

@router.post("/agentic", response_model=InvestigationResponse)
async def start_agentic_investigation(
    request: InvestigationRequest,
    background_tasks: BackgroundTasks
) -> InvestigationResponse:
    """Start an AI-driven agentic investigation"""
    if not AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Investigation agents not available")
    
    investigation_id = str(uuid.uuid4())
    
    # Start investigation in background
    background_tasks.add_task(
        run_agentic_investigation,
        investigation_id,
        request.namespace,
        request.include_k8sgpt,
        request.include_events,
        request.timeout
    )
    
    return InvestigationResponse(
        investigation_id=investigation_id,
        status="started",
        message="Agentic investigation started"
    )

@router.get("/status/{investigation_id}", response_model=InvestigationResult)
async def get_investigation_status(investigation_id: str) -> InvestigationResult:
    """Get investigation status and results"""
    if investigation_id not in investigation_results:
        raise HTTPException(status_code=404, detail="Investigation not found")
    
    return investigation_results[investigation_id]

async def run_deterministic_investigation(
    investigation_id: str,
    namespace: Optional[str],
    include_k8sgpt: bool,
    include_events: bool,
    timeout: int
):
    """Background task to run deterministic investigation"""
    try:
        investigation_results[investigation_id] = InvestigationResult(
            investigation_id=investigation_id,
            status="running",
            report=None,
            error=None
        )
        
        investigator = DeterministicInvestigator()
        report = await investigator.investigate(
            namespace=namespace,
            include_k8sgpt=include_k8sgpt,
            include_events=include_events,
            timeout=timeout
        )
        
        investigation_results[investigation_id] = InvestigationResult(
            investigation_id=investigation_id,
            status="completed",
            report=report,
            error=None
        )
        
    except Exception as e:
        investigation_results[investigation_id] = InvestigationResult(
            investigation_id=investigation_id,
            status="failed",
            report=None,
            error=str(e)
        )

async def run_agentic_investigation(
    investigation_id: str,
    namespace: Optional[str],
    include_k8sgpt: bool,
    include_events: bool,
    timeout: int
):
    """Background task to run agentic investigation"""
    try:
        investigation_results[investigation_id] = InvestigationResult(
            investigation_id=investigation_id,
            status="running",
            report=None,
            error=None
        )
        
        investigator = AgenticInvestigator()
        report = await investigator.investigate(
            namespace=namespace,
            include_k8sgpt=include_k8sgpt,
            include_events=include_events,
            timeout=timeout
        )
        
        investigation_results[investigation_id] = InvestigationResult(
            investigation_id=investigation_id,
            status="completed",
            report=report,
            error=None
        )
        
    except Exception as e:
        investigation_results[investigation_id] = InvestigationResult(
            investigation_id=investigation_id,
            status="failed",
            report=None,
            error=str(e)
        ) 