"""
Base investigator class with common functionality for Kubernetes cluster investigation.
"""

import asyncio
import json
import logging
import subprocess
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .tools.kubectl_wrapper import KubectlWrapper
from .tools.k8sgpt_wrapper import K8sgptWrapper
from .tools.report_generator import ReportGenerator


class BaseInvestigator(ABC):
    """
    Base class for Kubernetes cluster investigators.
    Provides common functionality for both deterministic and agentic approaches.
    """
    
    def __init__(self, investigation_id: Optional[str] = None):
        self.investigation_id = investigation_id or f"inv_{int(time.time())}"
        self.start_time = datetime.utcnow()
        self.kubectl = KubectlWrapper()
        self.k8sgpt = K8sgptWrapper()
        self.report_generator = ReportGenerator()
        self.logger = self._setup_logging()
        self.findings: List[Dict[str, Any]] = []
        self.actions_taken: List[Dict[str, Any]] = []
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the investigation."""
        logger = logging.getLogger(f"investigator.{self.investigation_id}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def start_investigation(self) -> Dict[str, Any]:
        """
        Start the investigation process.
        This is the main entry point for any investigator.
        """
        try:
            self.logger.info(f"Starting investigation {self.investigation_id}")
            
            # Pre-flight checks
            if not await self._validate_environment():
                raise RuntimeError("Environment validation failed")
            
            # Run the actual investigation
            await self._investigate()
            
            # Generate final report
            report = await self._generate_final_report()
            
            self.logger.info(f"Investigation {self.investigation_id} completed successfully")
            return report
            
        except Exception as e:
            self.logger.error(f"Investigation failed: {str(e)}")
            return await self._generate_error_report(str(e))
    
    async def _validate_environment(self) -> bool:
        """Validate that all required tools are available."""
        try:
            # Check kubectl
            if not await self.kubectl.is_available():
                self.logger.error("kubectl is not available")
                return False
            
            # Check k8sgpt  
            if not await self.k8sgpt.is_available():
                self.logger.error("k8sgpt is not available")
                return False
            
            # Check cluster connectivity
            if not await self.kubectl.can_connect():
                self.logger.error("Cannot connect to Kubernetes cluster")
                return False
            
            self.logger.info("Environment validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Environment validation failed: {str(e)}")
            return False
    
    @abstractmethod
    async def _investigate(self) -> None:
        """
        Main investigation logic - to be implemented by subclasses.
        This method should populate self.findings and self.actions_taken.
        """
        pass
    
    def _add_finding(self, category: str, severity: str, description: str, 
                    affected_resources: List[str] = None, 
                    recommendations: List[str] = None,
                    evidence: List[str] = None) -> None:
        """Add a finding to the investigation results."""
        finding = {
            "category": category,
            "severity": severity,
            "description": description,
            "affected_resources": affected_resources or [],
            "recommendations": recommendations or [],
            "evidence": evidence or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        self.findings.append(finding)
        self.logger.info(f"Added finding: {category} - {description}")
    
    def _add_action(self, tool: str, command: str, reasoning: str, 
                   output: str = "", success: bool = True) -> None:
        """Record an action taken during investigation."""
        action = {
            "tool": tool,
            "command": command,
            "reasoning": reasoning,
            "output": output[:1000] if output else "",  # Limit output size
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.actions_taken.append(action)
        self.logger.info(f"Action taken: {tool} - {command}")
    
    async def _run_diagnose_script(self, namespace: str = None) -> Dict[str, Any]:
        """Run the existing diagnose.sh script."""
        try:
            cmd = ["/agent-actions/diagnose.sh"]
            if namespace:
                cmd.extend(["-n", namespace])
            
            self.logger.info(f"Running diagnose script: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            success = process.returncode == 0
            output = stdout.decode() if success else stderr.decode()
            
            self._add_action(
                tool="diagnose_script",
                command=" ".join(cmd),
                reasoning="Running comprehensive diagnostics",
                output=output,
                success=success
            )
            
            return {
                "success": success,
                "output": output,
                "returncode": process.returncode
            }
            
        except Exception as e:
            self.logger.error(f"Failed to run diagnose script: {str(e)}")
            return {
                "success": False,
                "output": str(e),
                "returncode": -1
            }
    
    async def _generate_final_report(self) -> Dict[str, Any]:
        """Generate the final investigation report."""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        cluster_summary = await self._get_cluster_summary()
        
        report = {
            "investigation_id": self.investigation_id,
            "timestamp": end_time.isoformat(),
            "agent_type": self.__class__.__name__.lower().replace("investigator", ""),
            "duration_seconds": duration,
            "cluster_summary": cluster_summary,
            "findings": self.findings,
            "actions_taken": self.actions_taken,
            "summary": {
                "total_findings": len(self.findings),
                "critical_findings": len([f for f in self.findings if f["severity"] == "critical"]),
                "high_findings": len([f for f in self.findings if f["severity"] == "high"]),
                "medium_findings": len([f for f in self.findings if f["severity"] == "medium"]),
                "low_findings": len([f for f in self.findings if f["severity"] == "low"]),
                "actions_taken": len(self.actions_taken),
                "tools_used": len(set(a["tool"] for a in self.actions_taken))
            }
        }
        
        return self.report_generator.format_report(report)
    
    async def _generate_error_report(self, error_message: str) -> Dict[str, Any]:
        """Generate an error report when investigation fails."""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        return {
            "investigation_id": self.investigation_id,
            "timestamp": end_time.isoformat(),
            "status": "failed",
            "error": error_message,
            "duration_seconds": duration,
            "findings": self.findings,
            "actions_taken": self.actions_taken
        }
    
    async def _get_cluster_summary(self) -> Dict[str, Any]:
        """Get a high-level summary of cluster state."""
        try:
            nodes = await self.kubectl.get_nodes()
            pods = await self.kubectl.get_all_pods()
            
            pod_statuses = {}
            for pod in pods.get("items", []):
                status = pod.get("status", {}).get("phase", "Unknown")
                pod_statuses[status] = pod_statuses.get(status, 0) + 1
            
            return {
                "nodes": len(nodes.get("items", [])),
                "total_pods": len(pods.get("items", [])),
                "pod_statuses": pod_statuses,
                "healthy_pods": pod_statuses.get("Running", 0),
                "failed_pods": pod_statuses.get("Failed", 0) + pod_statuses.get("Pending", 0)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get cluster summary: {str(e)}")
            return {"error": str(e)}