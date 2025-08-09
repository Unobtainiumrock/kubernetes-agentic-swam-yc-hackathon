from fastapi import FastAPI
from .routers.agent import router as agent_router

def create_app() -> FastAPI:
    app = FastAPI(title="ADK Agent API", version="0.0.1")
    app.include_router(agent_router)
    return app
