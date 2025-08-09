"""
K8sgpt wrapper for AI-powered Kubernetes issue detection.
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
import subprocess


class K8sgptWrapper:
    """Wrapper for k8sgpt AI-powered Kubernetes analysis tool."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def analyze_cluster(self, 
                            namespace: Optional[str] = None,
                            output_format: str = "json",
                            explain: bool = True,
                            filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run k8sgpt analysis on the cluster.
        
        Args:
            namespace: Specific namespace to analyze (default: all namespaces)
            output_format: Output format (json, text, yaml)
            explain: Whether to include explanations
            filter: List of resource types to filter
            
        Returns:
            Analysis results from k8sgpt
        """
        cmd = ["k8sgpt", "analyze"]
        
        if namespace:
            cmd.extend(["--namespace", namespace])
            
        if output_format:
            cmd.extend(["--output", output_format])
            
        if explain:
            cmd.append("--explain")
            
        if filter:
            for f in filter:
                cmd.extend(["--filter", f])
        
        try:
            result = await self._execute_command(cmd)
            
            if result["success"] and output_format == "json":
                try:
                    result["parsed_output"] = json.loads(result["stdout"])
                except json.JSONDecodeError:
                    # k8sgpt might not return valid JSON in all cases
                    result["parsed_output"] = {"raw": result["stdout"]}
                    
            return result
            
        except Exception as e:
            self.logger.error(f"K8sgpt analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "parsed_output": None
            }
    
    async def analyze_with_filters(self, filters: List[str]) -> Dict[str, Any]:
        """
        Run k8sgpt analysis with specific resource filters.
        
        Args:
            filters: List of Kubernetes resource types to analyze
            
        Returns:
            Filtered analysis results
        """
        return await self.analyze_cluster(filter=filters, explain=True)
    
    async def get_integrations(self) -> Dict[str, Any]:
        """Get available k8sgpt integrations."""
        cmd = ["k8sgpt", "integration", "list"]
        
        try:
            result = await self._execute_command(cmd)
            return result
        except Exception as e:
            self.logger.error(f"Failed to get k8sgpt integrations: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    async def check_auth_status(self) -> Dict[str, Any]:
        """Check k8sgpt authentication status."""
        cmd = ["k8sgpt", "auth", "list"]
        
        try:
            result = await self._execute_command(cmd)
            return result
        except Exception as e:
            self.logger.error(f"Failed to check k8sgpt auth: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    async def analyze_pods(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Analyze pod issues specifically."""
        return await self.analyze_cluster(
            namespace=namespace,
            filter=["Pod"],
            explain=True
        )
    
    async def analyze_deployments(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Analyze deployment issues specifically."""
        return await self.analyze_cluster(
            namespace=namespace,
            filter=["Deployment"],
            explain=True
        )
    
    async def analyze_services(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Analyze service issues specifically."""
        return await self.analyze_cluster(
            namespace=namespace,
            filter=["Service"],
            explain=True
        )
    
    async def analyze_events(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Analyze event issues specifically."""
        return await self.analyze_cluster(
            namespace=namespace,
            filter=["Event"],
            explain=True
        )
    
    async def get_version(self) -> Dict[str, Any]:
        """Get k8sgpt version information."""
        cmd = ["k8sgpt", "version"]
        
        try:
            result = await self._execute_command(cmd)
            return result
        except Exception as e:
            self.logger.error(f"Failed to get k8sgpt version: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    async def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report using k8sgpt.
        
        Returns:
            Comprehensive analysis summary
        """
        try:
            # Run comprehensive analysis
            full_analysis = await self.analyze_cluster(explain=True)
            
            # Get specific component analyses
            pod_analysis = await self.analyze_pods()
            deployment_analysis = await self.analyze_deployments()
            service_analysis = await self.analyze_services()
            event_analysis = await self.analyze_events()
            
            # Get system info
            version_info = await self.get_version()
            auth_status = await self.check_auth_status()
            
            summary = {
                "timestamp": asyncio.get_event_loop().time(),
                "k8sgpt_version": version_info.get("stdout", "Unknown"),
                "auth_status": auth_status.get("stdout", "Unknown"),
                "full_analysis": full_analysis,
                "component_analysis": {
                    "pods": pod_analysis,
                    "deployments": deployment_analysis,
                    "services": service_analysis,
                    "events": event_analysis
                },
                "summary_statistics": {
                    "total_issues_found": self._count_issues(full_analysis),
                    "pod_issues": self._count_issues(pod_analysis),
                    "deployment_issues": self._count_issues(deployment_analysis),
                    "service_issues": self._count_issues(service_analysis),
                    "event_issues": self._count_issues(event_analysis)
                }
            }
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate k8sgpt summary: {e}")
            return {
                "success": False,
                "error": str(e),
                "summary": None
            }
    
    def _count_issues(self, analysis_result: Dict[str, Any]) -> int:
        """Count the number of issues found in analysis result."""
        if not analysis_result.get("success"):
            return 0
            
        parsed = analysis_result.get("parsed_output")
        if not parsed:
            return 0
            
        if isinstance(parsed, dict) and "results" in parsed:
            return len(parsed["results"])
        elif isinstance(parsed, list):
            return len(parsed)
        else:
            # Try to count issues from text output
            stdout = analysis_result.get("stdout", "")
            if "No problems detected" in stdout or not stdout.strip():
                return 0
            # Rough estimate based on lines that look like issues
            return len([line for line in stdout.split('\n') if line.strip() and not line.startswith('---')])
    
    async def _execute_command(self, cmd: List[str], timeout: int = 60) -> Dict[str, Any]:
        """Execute k8sgpt command safely."""
        try:
            self.logger.info(f"Executing k8sgpt command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            result = {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8') if stdout else "",
                "stderr": stderr.decode('utf-8') if stderr else "",
                "command": ' '.join(cmd)
            }
            
            if result["success"]:
                self.logger.info(f"K8sgpt command succeeded: {result['command']}")
            else:
                self.logger.warning(f"K8sgpt command failed: {result['command']}, stderr: {result['stderr']}")
                
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"K8sgpt command timed out: {' '.join(cmd)}")
            return {
                "success": False,
                "error": "Command timed out",
                "stdout": "",
                "stderr": "",
                "command": ' '.join(cmd)
            }
        except Exception as e:
            self.logger.error(f"K8sgpt command execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "command": ' '.join(cmd)
            }


# Convenience functions for direct usage
async def analyze_cluster_issues() -> Dict[str, Any]:
    """Quick function to analyze cluster issues."""
    wrapper = K8sgptWrapper()
    return await wrapper.analyze_cluster()


async def get_k8sgpt_summary() -> Dict[str, Any]:
    """Quick function to get comprehensive k8sgpt summary."""
    wrapper = K8sgptWrapper()
    return await wrapper.generate_summary_report()
