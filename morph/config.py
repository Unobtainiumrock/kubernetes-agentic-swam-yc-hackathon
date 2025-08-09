"""
MorphLLM Configuration for Kubernetes Agentic System
"""

import os
from pathlib import Path
from typing import Dict, Any, List

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env file from the same directory as this config file
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")
    print("Environment variables will be loaded from system environment only.")

class MorphLLMConfig:
    """Configuration for MorphLLM agent tools integration"""
    
    def __init__(self):
        # MorphLLM API Configuration
        self.api_key = os.getenv("MORPH_API_KEY")
        self.base_url = os.getenv("MORPH_BASE_URL", "https://api.morphllm.com")
        self.model = os.getenv("MORPH_MODEL", "claude-3-5-sonnet-20241022")
        
        # Validate required configuration
        if not self.api_key:
            print("❌ MORPH_API_KEY not found in environment variables!")
            print("Please create a .env file in the morph/ directory with your API key.")
            print("You can copy .env.example to .env and fill in your values.")
        
        # Kubernetes-specific paths (relative to project root)
        self.project_root = Path(__file__).parent.parent
        self.kubernetes_manifests_dir = os.getenv('KUBERNETES_MANIFESTS_DIR', str(self.project_root))
        self.agent_actions_dir = os.getenv('AGENT_ACTIONS_DIR', str(self.project_root / 'agent-actions'))
        self.chaos_scripts_dir = os.getenv(
            "CHAOS_SCRIPTS_DIR",
            "/Users/jade/kubernetes-agentic-swam-yc-hackathon"
        )
        
        # Optional settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        
    def get_morph_tools(self) -> List[Dict[str, Any]]:
        """Get MorphLLM tool definitions for Kubernetes agents"""
        return [
            {
                "name": "read_file",
                "description": "Read the contents of a file to understand its structure before making edits",
                "parameters": {
                    "properties": {
                        "target_file": {
                            "type": "string",
                            "description": "The path of the file to read"
                        },
                        "start_line_one_indexed": {
                            "type": "integer",
                            "description": "Start line number (1-indexed)"
                        },
                        "end_line_one_indexed_inclusive": {
                            "type": "integer",
                            "description": "End line number (1-indexed, inclusive)"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Why you're reading this file"
                        }
                    },
                    "required": ["target_file", "explanation"]
                }
            },
            {
                "name": "codebase_search",
                "description": "Find snippets of code from the codebase most relevant to the search query",
                "parameters": {
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant code"
                        },
                        "target_directories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: limit search scope to specific directories"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Why you're searching for this"
                        }
                    },
                    "required": ["query", "explanation"]
                }
            },
            {
                "name": "grep_search",
                "description": "Fast text-based regex search that finds exact pattern matches within files",
                "parameters": {
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The regex pattern to search for"
                        },
                        "include_pattern": {
                            "type": "string",
                            "description": "File types to include (e.g. '*.yaml', '*.sh')"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Why you're searching for this pattern"
                        }
                    },
                    "required": ["query", "explanation"]
                }
            },
            {
                "name": "list_dir",
                "description": "List the contents of a directory to understand project structure",
                "parameters": {
                    "properties": {
                        "relative_workspace_path": {
                            "type": "string",
                            "description": "Path to list contents of, relative to the workspace root"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Why you're listing this directory"
                        }
                    },
                    "required": ["relative_workspace_path", "explanation"]
                }
            },
            {
                "name": "edit_file",
                "description": "Make precise edits to files without full rewrites",
                "parameters": {
                    "properties": {
                        "target_file": {
                            "type": "string",
                            "description": "The path of the file to edit"
                        },
                        "edit_snippet": {
                            "type": "string",
                            "description": "The new content with // ... existing code ... markers"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Why you're making this edit"
                        }
                    },
                    "required": ["target_file", "edit_snippet", "explanation"]
                }
            }
        ]
    
    def get_kubernetes_search_patterns(self) -> Dict[str, str]:
        """Common Kubernetes search patterns for agents"""
        return {
            "failing_pods": r"(ImagePullBackOff|CrashLoopBackOff|Error|Failed)",
            "resource_limits": r"(resources:|limits:|requests:)",
            "deployments": r"(kind:\s*Deployment)",
            "services": r"(kind:\s*Service)",
            "configmaps": r"(kind:\s*ConfigMap)",
            "secrets": r"(kind:\s*Secret)",
            "ingress": r"(kind:\s*Ingress)",
            "namespaces": r"(namespace:\s*\w+)",
            "image_tags": r"(image:\s*[\w\-\.\/]+:[\w\-\.]+)",
            "pod_errors": r"(Error|Failed|Pending|Unknown)"
        }
    
    def get_common_fixes(self) -> Dict[str, str]:
        """Common Kubernetes fixes that agents can apply"""
        return {
            "fix_image_tag": """
# Fix incorrect image tag
# ... existing code ...
        image: nginx:1.21  # Fixed from nonexistent-tag
# ... existing code ...
            """,
            "increase_memory": """
# Increase memory limits for resource pressure
# ... existing code ...
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"  # Increased from 128Mi
            cpu: "200m"
# ... existing code ...
            """,
            "add_restart_policy": """
# Add restart policy for crash loops
# ... existing code ...
      restartPolicy: Always
      containers:
# ... existing code ...
            """
        }

# Global config instance
morph_config = MorphLLMConfig()
