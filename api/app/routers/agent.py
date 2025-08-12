import uuid
from fastapi import APIRouter, Depends, HTTPException
import os
import sys

from ..schemas import RunRequest, RunResponse

# Add paths for agent imports
if "/root" not in sys.path:
    sys.path.append("/root")
# Add Google ADK to path (use proper relative path that works in both environments)
google_adk_path = os.path.join(os.path.dirname(__file__), "../../../backend/google-adk/src")
google_adk_path = os.path.abspath(google_adk_path)
if google_adk_path not in sys.path:
    sys.path.append(google_adk_path)

try:
    from adk_agent.config.loader import load_runtime_config
    from adk_agent.agents.core_agent import create_core_agent
except ImportError:
    # Fallback for development
    load_runtime_config = None
    create_core_agent = None

router = APIRouter()

@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "adk-agent-api", "version": "0.0.1"}


def get_agent():
    try:
        if load_runtime_config is None or create_core_agent is None:
            raise HTTPException(status_code=500, detail="ADK agent modules not available")
        
        config_path = os.getenv("ADK_CONFIG_PATH")
        if not config_path:
            # Use default config path relative to this file
            default_config = os.path.join(os.path.dirname(__file__), "../../../backend/google-adk/src/adk_agent/config/runtime.yaml")
            config_path = os.path.abspath(default_config)
        
        config = load_runtime_config(config_path)
        agent = create_core_agent(config)
        return agent
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent init failed: {e}")


@router.post("/v1/agent/run", response_model=RunResponse)
async def run_agent(req: RunRequest, agent = Depends(get_agent)) -> RunResponse:
    system_prompt = "You are a helpful AI assistant. Provide clear, concise, and accurate responses to user questions."

    try:
        output = agent.run(system_prompt, req.input)
        return RunResponse(run_id=str(uuid.uuid4()), output=output, metadata={})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Run failed: {e}")
