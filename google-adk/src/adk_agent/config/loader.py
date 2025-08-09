import os
from typing import Any, Dict, Optional

import yaml


def load_runtime_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    if not config_path:
        raise RuntimeError("Config path must be provided")
    
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    
    # Allow environment override for model
    model = os.getenv("MODEL_SLUG", data.get("model"))
    data["model"] = model
    
    return data

