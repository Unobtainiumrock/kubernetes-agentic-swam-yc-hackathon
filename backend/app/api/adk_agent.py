"""
ADK Agent API Router

Integrates the remote ADK agent functionality into our backend.
Provides fallback implementation when google-adk dependency is not available.
"""

import uuid
import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from ..schemas import RunRequest, RunResponse, HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Try to import ADK agent, fall back to mock if not available
try:
    # Add the google-adk src path to sys.path
    import sys
    google_adk_path = os.path.join(os.path.dirname(__file__), "../../google-adk/src")
    if google_adk_path not in sys.path:
        sys.path.append(google_adk_path)
    
    from adk_agent.config.loader import load_runtime_config
    from adk_agent.agents.core_agent import create_core_agent
    ADK_AVAILABLE = True
    logger.info("ADK agent dependencies loaded successfully")
except ImportError as e:
    ADK_AVAILABLE = False
    logger.warning(f"ADK agent not available, using mock implementation: {e}")

class MockAgent:
    """Mock agent implementation when google-adk is not available"""
    
    def run(self, system_prompt: str, user_input: str) -> str:
        return f"Mock response to: {user_input}\n\nNote: This is a mock response. To use the actual ADK agent, ensure the google-adk dependency is available."

def get_agent():
    """Dependency injection for agent instance"""
    try:
        if ADK_AVAILABLE:
            config_path = os.getenv("ADK_CONFIG_PATH")
            if not config_path:
                # Use default config path relative to this file
                default_config = os.path.join(os.path.dirname(__file__), "../../google-adk/src/adk_agent/config/runtime.yaml")
                config_path = os.path.abspath(default_config)
                logger.info(f"Using default config path: {config_path}")
            
            if not os.path.exists(config_path):
                logger.warning(f"Config file not found at {config_path}, using mock agent")
                return MockAgent()
            
            config = load_runtime_config(config_path)
            agent = create_core_agent(config)
            return agent
        else:
            return MockAgent()
    except Exception as e:
        logger.error(f"Agent initialization failed: {e}")
        # Fall back to mock agent instead of raising exception
        return MockAgent()

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint for ADK agent service"""
    return HealthResponse(
        status="ok",
        service="adk-agent-api", 
        version="0.0.1"
    )

@router.post("/v1/agent/run", response_model=RunResponse)
async def run_agent(req: RunRequest, agent = Depends(get_agent)) -> RunResponse:
    """
    Run the ADK agent with user input
    
    This endpoint accepts user input and returns the agent's response.
    If the google-adk dependency is not available, it returns a mock response.
    """
    system_prompt = "You are a helpful AI assistant. Provide clear, concise, and accurate responses to user questions."

    try:
        output = agent.run(system_prompt, req.input)
        
        # Add metadata about agent type
        metadata = {
            "agent_type": "adk_agent" if ADK_AVAILABLE else "mock_agent",
            "system_prompt": system_prompt,
            "timestamp": str(uuid.uuid4())  # Using uuid as timestamp placeholder
        }
        
        return RunResponse(
            run_id=str(uuid.uuid4()), 
            output=output, 
            metadata=metadata
        )
    except Exception as e:
        logger.error(f"Agent run failed: {e}")
        raise HTTPException(status_code=500, detail=f"Run failed: {e}")

@router.get("/status")
async def get_agent_status():
    """Get current agent status and configuration"""
    return {
        "adk_available": ADK_AVAILABLE,
        "config_path": os.getenv("ADK_CONFIG_PATH"),
        "agent_type": "adk_agent" if ADK_AVAILABLE else "mock_agent",
        "openrouter_configured": bool(os.getenv("OPENROUTER_API_KEY")),
        "deps_path_available": "/deps" in sys.path if 'sys' in globals() else False
    } 