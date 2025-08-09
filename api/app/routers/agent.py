import uuid
from fastapi import APIRouter, Depends, HTTPException
import os

from app.schemas import RunRequest, RunResponse

# Add /deps to sys.path so API can import agent code when mounted
import sys
if "/deps" not in sys.path:
    sys.path.append("/deps")

from adk_agent.config.loader import load_runtime_config
from adk_agent.agents.core_agent import create_core_agent

router = APIRouter()

@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "adk-agent-api", "version": "0.0.1"}


def get_agent():
    try:
        config_path = os.getenv("ADK_CONFIG_PATH")
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
