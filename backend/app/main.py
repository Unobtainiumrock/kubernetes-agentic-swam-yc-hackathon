"""
FastAPI backend for Agentic Kubernetes Operator Demo

This module provides:
- WebSocket endpoints for real-time data streaming
- REST API endpoints for cluster management
- Chaos injection capabilities
- Agent communication interface
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import logging
import os
from typing import Dict, List
from datetime import datetime

from .api import agents, chaos, cluster, adk_agent
from .websockets import connection_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic K8s Operator Demo API",
    description="Backend API for demonstrating AI-based Kubernetes operators",
    version="1.0.0"
)

# Configure CORS - secure for production
def get_cors_origins():
    """Get allowed CORS origins based on environment"""
    if os.getenv("DEBUG", "false").lower() == "true":
        # Development: allow localhost
        return [
            "http://localhost:3000",
            "http://localhost:5173", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ]
    else:
        # Production: specify your Netlify domain
        netlify_url = os.getenv("NETLIFY_URL", "")
        
        if netlify_url:
            origins = [netlify_url]
        else:
            # Fallback - replace with your actual Netlify URL after deployment
            origins = ["https://your-app.netlify.app"]
            
        return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(chaos.router, prefix="/api/chaos", tags=["chaos"])
app.include_router(cluster.router, prefix="/api/cluster", tags=["cluster"])
app.include_router(adk_agent.router, prefix="/api/adk", tags=["adk-agent"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Agentic Kubernetes Operator Demo API", 
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.websocket("/ws/agent-status")
async def websocket_agent_status(websocket: WebSocket):
    """WebSocket endpoint for real-time agent status updates"""
    await connection_manager.connect(websocket, "agent-status")
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            logger.info(f"Received from agent-status client: {data}")
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "agent-status")

@app.websocket("/ws/cluster-events")
async def websocket_cluster_events(websocket: WebSocket):
    """WebSocket endpoint for cluster events and logs"""
    await connection_manager.connect(websocket, "cluster-events")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received from cluster-events client: {data}")
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "cluster-events")

@app.websocket("/ws/global-metrics")
async def websocket_global_metrics(websocket: WebSocket):
    """WebSocket endpoint for global metrics and monitoring data"""
    await connection_manager.connect(websocket, "global-metrics")
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received from global-metrics client: {data}")
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "global-metrics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 