"""
Pydantic schemas for the ADK Agent API
"""

from typing import Dict, Any
from pydantic import BaseModel


class RunRequest(BaseModel):
    """Request model for agent run endpoint"""
    input: str


class RunResponse(BaseModel):
    """Response model for agent run endpoint"""
    run_id: str
    output: str
    metadata: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    service: str
    version: str 