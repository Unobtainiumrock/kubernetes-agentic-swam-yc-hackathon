"""
Kubectl wrapper for Kubernetes cluster operations.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any


class KubectlWrapper:
    """Wrapper for kubectl commands with async support."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}")
        self.kubectl_cmd = "kubectl"
    
    async def is_available(self) -> bool:
        """Check if kubectl is available."""
        try:
            process = await asyncio.create_subprocess_exec(
                "which", self.kubectl_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except Exception:
            return False
    
    async def can_connect(self) -> bool:
        """Test connectivity to Kubernetes cluster."""
        try:
            result = await self._run_kubectl(["cluster-info"])
            return result["success"]
        except Exception:
            return False
    
    async def _run_kubectl(self, args: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Run kubectl command with given arguments."""
        try:
            cmd = [self.kubectl_cmd] + args
            self.logger.debug(f"Running: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "output": "",
                    "error": f"Command timed out after {timeout}s",
                    "returncode": -1
                }
            
            success = process.returncode == 0
            output = stdout.decode('utf-8') if success else stderr.decode('utf-8')
            
            return {
                "success": success,
                "output": output,
                "error": stderr.decode('utf-8') if not success else "",
                "returncode": process.returncode
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "returncode": -1
            }
    
    async def get_nodes(self) -> Dict[str, Any]:
        """Get all nodes in the cluster."""
        result = await self._run_kubectl(["get", "nodes", "-o", "json"])
        if result["success"]:
            try:
                return json.loads(result["output"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON output"}
        return {"error": result["error"]}
    
    async def get_all_pods(self, namespace: str = None) -> Dict[str, Any]:
        """Get all pods, optionally filtered by namespace."""
        args = ["get", "pods"]
        if namespace:
            args.extend(["-n", namespace])
        else:
            args.append("--all-namespaces")
        args.extend(["-o", "json"])
        
        result = await self._run_kubectl(args)
        if result["success"]:
            try:
                return json.loads(result["output"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON output"}
        return {"error": result["error"]}
    
    async def get_pod_logs(self, pod_name: str, namespace: str, 
                          container: str = None, lines: int = 50) -> Dict[str, Any]:
        """Get logs for a specific pod."""
        args = ["logs", pod_name, "-n", namespace, f"--tail={lines}"]
        if container:
            args.extend(["-c", container])
            
        return await self._run_kubectl(args)
    
    async def describe_pod(self, pod_name: str, namespace: str) -> Dict[str, Any]:
        """Describe a specific pod."""
        args = ["describe", "pod", pod_name, "-n", namespace]
        return await self._run_kubectl(args)
    
    async def get_events(self, namespace: str = None, sort_by_time: bool = True) -> Dict[str, Any]:
        """Get cluster events."""
        args = ["get", "events"]
        if namespace:
            args.extend(["-n", namespace])
        else:
            args.append("--all-namespaces")
        
        if sort_by_time:
            args.append("--sort-by=.metadata.creationTimestamp")
        
        args.extend(["-o", "json"])
        
        result = await self._run_kubectl(args)
        if result["success"]:
            try:
                return json.loads(result["output"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON output"}
        return {"error": result["error"]}
    
    async def get_pod_status_summary(self) -> Dict[str, Any]:
        """Get a summary of pod statuses across all namespaces."""
        try:
            pods_data = await self.get_all_pods()
            if "error" in pods_data:
                return pods_data
                
            status_summary = {}
            namespace_summary = {}
            problematic_pods = []
            
            for pod in pods_data.get("items", []):
                namespace = pod.get("metadata", {}).get("namespace", "unknown")
                pod_name = pod.get("metadata", {}).get("name", "unknown")
                status = pod.get("status", {})
                phase = status.get("phase", "Unknown")
                
                # Count by status
                status_summary[phase] = status_summary.get(phase, 0) + 1
                
                # Count by namespace
                if namespace not in namespace_summary:
                    namespace_summary[namespace] = {}
                namespace_summary[namespace][phase] = namespace_summary[namespace].get(phase, 0) + 1
                
                # Identify problematic pods
                if phase not in ["Running", "Succeeded"]:
                    pod_info = {
                        "name": pod_name,
                        "namespace": namespace,
                        "phase": phase,
                        "message": status.get("message", ""),
                        "reason": status.get("reason", "")
                    }
                    
                    # Get container statuses for more detail
                    container_statuses = status.get("containerStatuses", [])
                    if container_statuses:
                        pod_info["container_issues"] = []
                        for container in container_statuses:
                            if not container.get("ready", False):
                                container_info = {
                                    "name": container.get("name", "unknown"),
                                    "ready": container.get("ready", False),
                                    "restart_count": container.get("restartCount", 0)
                                }
                                
                                # Get waiting/terminated state info
                                state = container.get("state", {})
                                if "waiting" in state:
                                    container_info["waiting_reason"] = state["waiting"].get("reason", "")
                                    container_info["waiting_message"] = state["waiting"].get("message", "")
                                elif "terminated" in state:
                                    container_info["terminated_reason"] = state["terminated"].get("reason", "")
                                    container_info["terminated_message"] = state["terminated"].get("message", "")
                                
                                pod_info["container_issues"].append(container_info)
                    
                    problematic_pods.append(pod_info)
            
            return {
                "success": True,
                "status_summary": status_summary,
                "namespace_summary": namespace_summary,
                "problematic_pods": problematic_pods,
                "total_pods": len(pods_data.get("items", []))
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def get_resource_usage(self) -> Dict[str, Any]:
        """Get resource usage if metrics server is available."""
        try:
            # Try to get node metrics
            node_metrics = await self._run_kubectl(["top", "nodes", "--no-headers"])
            pod_metrics = await self._run_kubectl(["top", "pods", "--all-namespaces", "--no-headers"])
            
            result = {
                "metrics_available": node_metrics["success"] and pod_metrics["success"]
            }
            
            if result["metrics_available"]:
                result["node_metrics"] = node_metrics["output"]
                result["pod_metrics"] = pod_metrics["output"]
            else:
                result["error"] = "Metrics server not available or not responding"
                
            return result
            
        except Exception as e:
            return {"error": str(e), "metrics_available": False}
    
    async def get_namespaces(self) -> Dict[str, Any]:
        """Get all namespaces."""
        result = await self._run_kubectl(["get", "namespaces", "-o", "json"])
        if result["success"]:
            try:
                return {
                    "success": True,
                    "namespaces": json.loads(result["output"])
                }
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON output", "success": False}
        return {"error": result["error"], "success": False}
    
    async def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information."""
        result = await self._run_kubectl(["cluster-info"])
        if result["success"]:
            return {
                "success": True,
                "cluster_info": result["output"]
            }
        return {"error": result["error"], "success": False}
    
    async def get_version(self) -> Dict[str, Any]:
        """Get Kubernetes version information."""
        result = await self._run_kubectl(["version", "-o", "json"])
        if result["success"]:
            try:
                return {
                    "success": True,
                    "version_info": json.loads(result["output"])
                }
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON output", "success": False}
        return {"error": result["error"], "success": False}
    
    async def get_pods(self, namespace: str = None) -> Dict[str, Any]:
        """Get pods in a specific namespace (alias for get_all_pods)."""
        return await self.get_all_pods(namespace)
    
    async def describe_nodes(self) -> Dict[str, Any]:
        """Describe all nodes in the cluster."""
        result = await self._run_kubectl(["describe", "nodes"])
        if result["success"]:
            return {
                "success": True,
                "output": result["output"]
            }
        return {"error": result["error"], "success": False}
    
    async def get_node_metrics(self) -> Dict[str, Any]:
        """Get node metrics (alias for get_resource_usage)."""
        usage = await self.get_resource_usage()
        if usage.get("metrics_available"):
            return {
                "success": True,
                "metrics": usage.get("node_metrics", "")
            }
        return {"error": usage.get("error", "Metrics not available"), "success": False}
    
    async def get_pod_metrics(self) -> Dict[str, Any]:
        """Get pod metrics (alias for get_resource_usage)."""
        usage = await self.get_resource_usage()
        if usage.get("metrics_available"):
            return {
                "success": True,
                "metrics": usage.get("pod_metrics", "")
            }
        return {"error": usage.get("error", "Metrics not available"), "success": False}
    
    async def get_deployments(self, namespace: str = None) -> Dict[str, Any]:
        """Get deployments."""
        args = ["get", "deployments"]
        if namespace:
            args.extend(["-n", namespace])
        else:
            args.append("--all-namespaces")
        args.extend(["-o", "json"])
        
        result = await self._run_kubectl(args)
        if result["success"]:
            try:
                return json.loads(result["output"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON output"}
        return {"error": result["error"]}
    
    async def get_services(self, namespace: str = None) -> Dict[str, Any]:
        """Get services."""
        args = ["get", "services"]
        if namespace:
            args.extend(["-n", namespace])
        else:
            args.append("--all-namespaces")
        args.extend(["-o", "json"])
        
        result = await self._run_kubectl(args)
        if result["success"]:
            try:
                return json.loads(result["output"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON output"}
        return {"error": result["error"]}
    
    async def get_network_policies(self) -> Dict[str, Any]:
        """Get network policies."""
        result = await self._run_kubectl(["get", "networkpolicies", "--all-namespaces", "-o", "json"])
        if result["success"]:
            try:
                return json.loads(result["output"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON output"}
        return {"error": result["error"]}
    
    async def get_ingresses(self) -> Dict[str, Any]:
        """Get ingresses."""
        result = await self._run_kubectl(["get", "ingresses", "--all-namespaces", "-o", "json"])
        if result["success"]:
            try:
                return json.loads(result["output"])
            except json.JSONDecodeError:
                return {"error": "Failed to parse JSON output"}
        return {"error": result["error"]}