"""
MorphLLM Integration Package

This package provides a bridge between your Google ADK agents and MorphLLM tools.
Import this package from your agents to get enhanced Kubernetes capabilities.

Usage in your Google ADK agents:
    from morph import morph_bridge, MorphLLMBridge
    
    # Use the global bridge instance
    diagnosis = morph_bridge.diagnose_kubernetes_issue("my-pod", "default")
    
    # Or create your own instance
    bridge = MorphLLMBridge()
    result = bridge.fix_kubernetes_issue("ImagePullBackOff", "broken-pod")
"""

from .agent_bridge import MorphLLMBridge, morph_bridge
from .config import morph_config

# Export the main interfaces your agents need
__all__ = [
    'MorphLLMBridge',
    'morph_bridge',
    'morph_config'
]

# Version info
__version__ = '1.0.0'
__author__ = 'Kubernetes Agentic System'
__description__ = 'MorphLLM integration for Google ADK agents'
