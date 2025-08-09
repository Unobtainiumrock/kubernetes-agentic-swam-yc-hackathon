from typing import Any, Dict
import os
import httpx


class CoreAgent:
    def __init__(
        self,
        model: str,
        openrouter_base_url: str,
        openrouter_api_key: str,
    ) -> None:
        self.model = model
        self.base_url = openrouter_base_url.rstrip("/")
        self.api_key = openrouter_api_key

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def run(self, system_prompt: str, user_input: str) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        }
        with httpx.Client(base_url=self.base_url, headers=self._headers(), timeout=60) as client:
            resp = client.post("/chat/completions", json=body)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


def create_core_agent(config: Dict[str, Any]) -> CoreAgent:
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY must be set in environment or .env")
    return CoreAgent(
        model=config["model"],
        openrouter_base_url=base_url,
        openrouter_api_key=api_key,
    ) 