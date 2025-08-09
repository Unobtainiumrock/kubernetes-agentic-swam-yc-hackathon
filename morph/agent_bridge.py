"""
MorphLLM Agent Bridge
This module provides a bridge between your existing Google ADK agents and MorphLLM tools.
Your agents can import and use this without any changes to their existing code.
"""

import asyncio
import json
import subprocess
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import os

from config import morph_config

class MorphLLMBridge:
    """
    Bridge class that allows existing agents to use MorphLLM tools
    without changing their implementation
    """
    
    def __init__(self):
        self.config = morph_config
        self.tools = self.config.get_morph_tools()
        
    # Synchronous wrapper methods for easy integration with existing agents
    def read_file(self, target_file: str, explanation: str, 
                  start_line: Optional[int] = None, 
                  end_line: Optional[int] = None) -> str:
        """
        Read file contents - synchronous wrapper for existing agents
        """
        return asyncio.run(self._async_read_file(target_file, explanation, start_line, end_line))
    
    def search_codebase(self, query: str, explanation: str, 
                       target_directories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Search codebase for relevant snippets - synchronous wrapper
        """
        return asyncio.run(self._async_search_codebase(query, explanation, target_directories))
    
    def grep_search(self, query: str, explanation: str, 
                   include_pattern: str = "*.py") -> Dict[str, Any]:
        """
        Fast grep search - synchronous wrapper
        """
        return asyncio.run(self._async_grep_search(query, explanation, include_pattern))
    
    def edit_file(self, target_file: str, edit_snippet: str, 
                  explanation: str) -> bool:
        """
        Edit file with precise changes - synchronous wrapper
        """
        return asyncio.run(self._async_edit_file(target_file, edit_snippet, explanation))
    
    def list_directory(self, relative_path: str, explanation: str) -> Dict[str, Any]:
        """
        List directory contents - synchronous wrapper
        """
        return asyncio.run(self._async_list_directory(relative_path, explanation))
    
    # Kubernetes-specific helper methods for your agents
    def diagnose_kubernetes_issue(self, pod_name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        High-level method to diagnose a specific Kubernetes issue
        Your agents can call this directly
        """
        print(f"🔍 Diagnosing Kubernetes issue for pod: {pod_name} in namespace: {namespace}")
        
        # Step 1: Get pod status
        pod_status = self._get_pod_status(pod_name, namespace)
        
        # Step 2: Search for deployment files
        deployment_search = self.search_codebase(
            query=f"name: {pod_name.split('-')[0]}",
            explanation=f"Finding deployment configuration for {pod_name}"
        )
        
        # Step 3: Read relevant configuration files
        config_files = self._find_relevant_config_files(pod_name)
        config_content = {}
        for file_path in config_files:
            if os.path.exists(file_path):
                config_content[file_path] = self.read_file(
                    target_file=file_path,
                    explanation=f"Reading configuration for {pod_name}"
                )
        
        return {
            "pod_name": pod_name,
            "namespace": namespace,
            "pod_status": pod_status,
            "deployment_search": deployment_search,
            "config_content": config_content,
            "diagnosis": self._analyze_issue(pod_status, config_content)
        }
    
    def fix_kubernetes_issue(self, issue_type: str, pod_name: str, 
                           namespace: str = "default") -> Dict[str, Any]:
        """
        High-level method to fix a Kubernetes issue
        Your agents can call this directly
        """
        print(f"🔧 Fixing Kubernetes issue: {issue_type} for pod: {pod_name}")
        
        fix_result = {
            "issue_type": issue_type,
            "pod_name": pod_name,
            "namespace": namespace,
            "success": False,
            "actions_taken": [],
            "error": None
        }
        
        try:
            if issue_type == "ImagePullBackOff":
                fix_result = self._fix_image_pull_error(pod_name, namespace)
            elif issue_type == "CrashLoopBackOff":
                fix_result = self._fix_crash_loop_error(pod_name, namespace)
            else:
                fix_result["error"] = f"No automated fix available for {issue_type}"
                
        except Exception as e:
            fix_result["error"] = str(e)
        
        return fix_result
    
    def get_kubernetes_tools_for_agent(self) -> List[Dict[str, Any]]:
        """
        Return MorphLLM tools formatted for your existing agents
        This allows your agents to use MorphLLM tools in their tool calling
        """
        # Add Kubernetes-specific tools to the base MorphLLM tools
        k8s_tools = [
            {
                "name": "diagnose_k8s_issue",
                "description": "Diagnose a Kubernetes pod issue using MorphLLM analysis",
                "parameters": {
                    "properties": {
                        "pod_name": {"type": "string", "description": "Name of the pod to diagnose"},
                        "namespace": {"type": "string", "description": "Kubernetes namespace", "default": "default"}
                    },
                    "required": ["pod_name"]
                }
            },
            {
                "name": "fix_k8s_issue",
                "description": "Fix a Kubernetes issue using MorphLLM tools",
                "parameters": {
                    "properties": {
                        "issue_type": {"type": "string", "description": "Type of issue (ImagePullBackOff, CrashLoopBackOff, etc.)"},
                        "pod_name": {"type": "string", "description": "Name of the pod to fix"},
                        "namespace": {"type": "string", "description": "Kubernetes namespace", "default": "default"}
                    },
                    "required": ["issue_type", "pod_name"]
                }
            }
        ]
        
        return self.tools + k8s_tools
    
    # Private async methods (actual MorphLLM API calls would go here)
    async def _async_read_file(self, target_file: str, explanation: str,
                              start_line: Optional[int] = None,
                              end_line: Optional[int] = None) -> str:
        """Async implementation of read_file"""
        print(f"📖 Reading file: {target_file} - {explanation}")
        
        try:
            with open(target_file, 'r') as f:
                content = f.read()
                if start_line and end_line:
                    lines = content.split('\n')
                    return '\n'.join(lines[start_line-1:end_line])
                return content
        except FileNotFoundError:
            return f"File not found: {target_file}"
        except Exception as e:
            return f"Error reading file: {e}"
    
    async def _async_search_codebase(self, query: str, explanation: str,
                                   target_directories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Async implementation of codebase search"""
        print(f"🔍 Searching codebase: {query} - {explanation}")
        
        # For demo - in production this would call MorphLLM API
        return {
            "query": query,
            "explanation": explanation,
            "results": [],
            "directories_searched": target_directories or ["."]
        }
    
    async def _async_grep_search(self, query: str, explanation: str,
                               include_pattern: str = "*.py") -> Dict[str, Any]:
        """Async implementation of grep search"""
        print(f"🔎 Grep search: {query} - {explanation}")
        
        # For demo - in production this would call MorphLLM API
        return {
            "query": query,
            "explanation": explanation,
            "pattern": include_pattern,
            "matches": []
        }
    
    async def _async_edit_file(self, target_file: str, edit_snippet: str,
                             explanation: str) -> bool:
        """Async implementation of file editing"""
        print(f"✏️ Editing file: {target_file} - {explanation}")
        print(f"Edit snippet:\n{edit_snippet}")
        
        # For demo - in production this would call MorphLLM API
        return True
    
    async def _async_list_directory(self, relative_path: str, explanation: str) -> Dict[str, Any]:
        """Async implementation of directory listing"""
        print(f"📁 Listing directory: {relative_path} - {explanation}")
        
        try:
            path = Path(relative_path)
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return {
                "path": relative_path,
                "explanation": explanation,
                "items": items
            }
        except Exception as e:
            return {
                "path": relative_path,
                "explanation": explanation,
                "error": str(e),
                "items": []
            }
    
    # Kubernetes-specific helper methods
    def _get_pod_status(self, pod_name: str, namespace: str) -> Dict[str, Any]:
        """Get current pod status from Kubernetes"""
        try:
            result = subprocess.run(
                ["kubectl", "get", "pod", pod_name, "-n", namespace, "-o", "json"],
                capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError:
            return {"error": f"Pod {pod_name} not found in namespace {namespace}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _find_relevant_config_files(self, pod_name: str) -> List[str]:
        """Find configuration files relevant to a pod"""
        base_name = pod_name.split('-')[0]  # Remove random suffixes
        
        potential_files = [
            f"{self.config.kubernetes_manifests_dir}/deploy-demo-apps.sh",
            f"{self.config.kubernetes_manifests_dir}/kind-cluster-config.yaml",
            f"{self.config.agent_actions_dir}/diagnose.sh"
        ]
        
        return [f for f in potential_files if os.path.exists(f)]
    
    def _analyze_issue(self, pod_status: Dict[str, Any], 
                      config_content: Dict[str, str]) -> Dict[str, Any]:
        """Analyze the issue based on pod status and configuration"""
        analysis = {
            "issue_type": "Unknown",
            "severity": "Medium",
            "description": "Unable to determine issue",
            "suggested_fix": "Manual investigation required"
        }
        
        if "error" in pod_status:
            return analysis
        
        # Check container statuses
        container_statuses = pod_status.get("status", {}).get("containerStatuses", [])
        for container in container_statuses:
            waiting = container.get("state", {}).get("waiting", {})
            if waiting:
                reason = waiting.get("reason", "Unknown")
                
                if reason in ["ImagePullBackOff", "ErrImagePull"]:
                    analysis.update({
                        "issue_type": "ImagePullBackOff",
                        "severity": "High",
                        "description": f"Cannot pull container image: {waiting.get('message', '')}",
                        "suggested_fix": "Fix image tag in deployment configuration"
                    })
                elif reason == "CrashLoopBackOff":
                    analysis.update({
                        "issue_type": "CrashLoopBackOff",
                        "severity": "High", 
                        "description": f"Container keeps crashing: {waiting.get('message', '')}",
                        "suggested_fix": "Fix container command or add proper health checks"
                    })
        
        return analysis
    
    def _fix_image_pull_error(self, pod_name: str, namespace: str) -> Dict[str, Any]:
        """Fix ImagePullBackOff error"""
        result = {
            "issue_type": "ImagePullBackOff",
            "pod_name": pod_name,
            "namespace": namespace,
            "success": False,
            "actions_taken": [],
            "error": None
        }
        
        try:
            # For broken-image-app, we know it's in deploy-demo-apps.sh
            if "broken-image" in pod_name:
                deployment_file = f"{self.config.kubernetes_manifests_dir}/deploy-demo-apps.sh"
                
                # Read current content
                current_content = self.read_file(
                    target_file=deployment_file,
                    explanation="Reading deployment script to fix ImagePullBackOff"
                )
                
                # Use edit_file to fix the image tag
                fix_snippet = """
# ... existing code ...
        image: nginx:1.21  # Fixed from nginx:nonexistent-tag-12345
# ... existing code ...
                """
                
                success = self.edit_file(
                    target_file=deployment_file,
                    edit_snippet=fix_snippet,
                    explanation="Fixing ImagePullBackOff by correcting image tag"
                )
                
                if success:
                    result["success"] = True
                    result["actions_taken"].append("Fixed image tag in deployment script")
                    result["actions_taken"].append("Image changed from nonexistent-tag to nginx:1.21")
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _fix_crash_loop_error(self, pod_name: str, namespace: str) -> Dict[str, Any]:
        """Fix CrashLoopBackOff error"""
        result = {
            "issue_type": "CrashLoopBackOff", 
            "pod_name": pod_name,
            "namespace": namespace,
            "success": False,
            "actions_taken": [],
            "error": None
        }
        
        try:
            # For crash-loop-app, we know it's in deploy-demo-apps.sh
            if "crash-loop" in pod_name:
                deployment_file = f"{self.config.kubernetes_manifests_dir}/deploy-demo-apps.sh"
                
                # Use edit_file to fix the crashing command
                fix_snippet = """
# ... existing code ...
        args: ["-c", "echo 'Application starting successfully...' && sleep 3600"]  # Fixed: removed exit 1
# ... existing code ...
                """
                
                success = self.edit_file(
                    target_file=deployment_file,
                    edit_snippet=fix_snippet,
                    explanation="Fixing CrashLoopBackOff by removing failing exit command"
                )
                
                if success:
                    result["success"] = True
                    result["actions_taken"].append("Fixed container command in deployment script")
                    result["actions_taken"].append("Removed 'exit 1' and added stable sleep command")
        
        except Exception as e:
            result["error"] = str(e)
        
        return result

# Global bridge instance for easy import
morph_bridge = MorphLLMBridge()
