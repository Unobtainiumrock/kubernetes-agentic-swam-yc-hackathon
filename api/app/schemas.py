from typing import Dict, Any
from pydantic import BaseModel


class RunRequest(BaseModel):
    input: str


class RunResponse(BaseModel):
    run_id: str
    output: str
    metadata: Dict[str, Any] = {}

