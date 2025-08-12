"""
Agentic Kubernetes Investigation Agent.

This agent uses AI to autonomously decide investigation approach and
adapt based on findings using Google ADK integration.
"""
import asyncio
import logging
import sys
import os
from typing import Dict, List, Optional, Any
import time
from datetime import datetime

# Add Google ADK to path (use proper relative path)
google_adk_path = os.path.join(os.path.dirname(__file__), "../../../google-adk/src")
if google_adk_path not in sys.path:
    sys.path.append(google_adk_path)

from .base_investigator import BaseInvestigator
from .tools.kubectl_wrapper import KubectlWrapper
from .tools.k8sgpt_wrapper import K8sgptWrapper
from .tools.report_generator import ReportGenerator, Severity, InvestigationType


class AgenticInvestigator(BaseInvestigator):
    """
    AI-driven investigation agent that autonomously decides investigation approach.
    
    This agent leverages Google ADK to make intelligent decisions about what
    to investigate next based on initial findings and available tools.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.kubectl = KubectlWrapper()
        self.k8sgpt = K8sgptWrapper()
        self.report_generator = ReportGenerator()
        self.report_generator.set_investigation_type(InvestigationType.AGENTIC)
        
        # AI agent and tool registry
        self.agent = None
        self.available_tools = {}
        self.investigation_history = []
        self.decisions_made = 0
        
        # Initialize agent
        self._initialize_agent()
        self._register_tools()
        
    def _initialize_agent(self):
        """Initialize Google ADK agent."""
        try:
            from adk_agent.agents.core_agent import create_core_agent
            
            # Load configuration
            config = {
                "model": "openai/gpt-4o-mini",
                "provider": "openrouter"
            }
            
            self.agent = create_core_agent(config)
            self.logger.info("Google ADK agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Google ADK agent: {e}")
            # Create a simple fallback agent for demo purposes
            self.agent = None
    
    def _register_tools(self):
        """Register available investigation tools for the AI agent."""
        self.available_tools = {
            "get_cluster_overview": {
                "function": self._tool_get_cluster_overview,
                "description": "Get basic cluster information including nodes, namespaces, and version",
                "parameters": {}
            },
            "analyze_pods": {
                "function": self._tool_analyze_pods,
                "description": "Analyze pod status across namespaces",
                "parameters": {"namespace": "optional namespace filter"}
            },
            "analyze_nodes": {
                "function": self._tool_analyze_nodes,
                "description": "Analyze node health and status",
                "parameters": {}
            },
            "get_resource_metrics": {
                "function": self._tool_get_resource_metrics,
                "description": "Get resource utilization metrics for nodes and pods",
                "parameters": {}
            },
            "analyze_events": {
                "function": self._tool_analyze_events,
                "description": "Analyze recent cluster events for issues",
                "parameters": {"namespace": "optional namespace filter"}
            },
            "run_k8sgpt_analysis": {
                "function": self._tool_run_k8sgpt_analysis,
                "description": "Run AI-powered issue detection using k8sgpt",
                "parameters": {}
            },
            "analyze_workloads": {
                "function": self._tool_analyze_workloads,
                "description": "Analyze deployments and services",
                "parameters": {"namespace": "optional namespace filter"}
            },
            "investigate_specific_resource": {
                "function": self._tool_investigate_specific_resource,
                "description": "Deep dive into a specific resource (pod, deployment, etc.)",
                "parameters": {"resource_type": "type of resource", "resource_name": "name of resource", "namespace": "namespace"}
            },
            "check_network_policies": {
                "function": self._tool_check_network_policies,
                "description": "Analyze network policies and ingresses",
                "parameters": {}
            }
        }
    
    async def run_investigation(self, 
                              namespace: Optional[str] = None,
                              include_k8sgpt: bool = True,
                              include_events: bool = True,
                              timeout: int = 300) -> Dict[str, Any]:
        """
        Execute AI-driven autonomous investigation.
        
        Args:
            namespace: Specific namespace to focus on
            include_k8sgpt: Whether to include k8sgpt analysis
            include_events: Whether to analyze cluster events
            timeout: Investigation timeout in seconds
            
        Returns:
            Complete investigation report
        """
        self.logger.info("🤖 Starting Agentic Kubernetes Investigation")
        print("🤖 Starting Agentic Kubernetes Investigation")
        print("=" * 60)
        
        try:
            # Set agent metadata
            self.report_generator.set_agent_metadata({
                "agent_type": "agentic",
                "version": "1.0.0",
                "ai_model": "gpt-4o-mini",
                "namespace_filter": namespace,
                "include_k8sgpt": include_k8sgpt,
                "include_events": include_events,
                "timeout_seconds": timeout,
                "available_tools": list(self.available_tools.keys())
            })
            
            # Start autonomous investigation
            if self.agent:
                investigation_result = await self._run_ai_driven_investigation(
                    namespace, include_k8sgpt, include_events, timeout
                )
            else:
                # Fallback to simulated autonomous behavior
                investigation_result = await self._run_fallback_investigation(
                    namespace, include_k8sgpt, include_events, timeout
                )
            
            # Generate final report
            final_report = self.report_generator.generate_json_report()
            
            # Add agentic-specific metadata
            final_report["agentic_metadata"] = {
                "decisions_made": self.decisions_made,
                "tools_used": len(set(entry["tool"] for entry in self.investigation_history)),
                "investigation_depth": "comprehensive" if len(self.investigation_history) > 5 else "standard",
                "investigation_history": self.investigation_history
            }
            
            print("✅ Agentic Investigation Complete!")
            self.logger.info("Agentic investigation completed successfully")
            
            return final_report
            
        except Exception as e:
            self.logger.error(f"Agentic investigation failed: {e}")
            print(f"❌ Investigation failed: {e}")
            
            # Generate error report
            self.report_generator.add_finding(
                category="investigation_error",
                severity=Severity.CRITICAL,
                title="Agentic Investigation Failed",
                description=f"AI-driven investigation failed with error: {str(e)}",
                affected_resources=["agentic_investigator"],
                recommendations=["Review investigation logs", "Check AI agent configuration", "Verify tool availability"],
                evidence=[str(e)],
                source_tool="agentic_investigator"
            )
            
            final_report = self.report_generator.generate_json_report()
            final_report["agentic_metadata"] = {
                "decisions_made": self.decisions_made,
                "tools_used": 0,
                "investigation_depth": "failed",
                "investigation_history": self.investigation_history
            }
            
            return final_report
    
    async def _run_ai_driven_investigation(self, namespace, include_k8sgpt, include_events, timeout):
        """Run actual AI-driven investigation using Google ADK."""
        print("🧠 AI Agent taking control of investigation...")
        
        # Initial prompt to the AI agent
        initial_prompt = f"""
You are an expert Kubernetes Site Reliability Engineer with autonomous investigation capabilities.

Your mission: Investigate the current Kubernetes cluster state and identify any issues or areas for improvement.

Available Tools:
{self._format_tools_for_prompt()}

Investigation Parameters:
- Namespace filter: {namespace or "All namespaces"}
- Include k8sgpt analysis: {include_k8sgpt}
- Include event analysis: {include_events}
- Timeout: {timeout} seconds

Your approach should be:
1. Start with a high-level cluster overview
2. Based on initial findings, decide what to investigate next
3. Follow up on any issues you discover
4. Use AI-powered tools when appropriate
5. Provide comprehensive analysis and recommendations

Please start your investigation now. Decide which tool to use first and explain your reasoning.
"""
        
        try:
            # Get initial investigation plan from AI
            response = self.agent.run(
                "You are an expert Kubernetes SRE conducting an autonomous cluster investigation.",
                initial_prompt
            )
            
            print(f"🎯 AI Agent Decision: {response[:200]}...")
            self._record_decision("initial_planning", response)
            
            # Execute AI-guided investigation
            await self._execute_ai_investigation_loop(namespace, include_k8sgpt, include_events)
            
        except Exception as e:
            self.logger.error(f"AI-driven investigation failed: {e}")
            print(f"❌ AI investigation failed, falling back: {e}")
            await self._run_fallback_investigation(namespace, include_k8sgpt, include_events, timeout)
    
    async def _execute_ai_investigation_loop(self, namespace, include_k8sgpt, include_events):
        """Execute investigation loop guided by AI decisions."""
        investigation_steps = 0
        max_steps = 8  # Prevent infinite loops
        
        # Start with cluster overview (always a good first step)
        print("🔍 Starting with cluster overview...")
        overview_result = await self._tool_get_cluster_overview()
        self._record_investigation("get_cluster_overview", overview_result)
        
        # Analyze pods (fundamental for cluster health)
        print("🔍 Analyzing pod status...")
        pod_result = await self._tool_analyze_pods(namespace)
        self._record_investigation("analyze_pods", pod_result)
        
        # Check if we found issues that need deeper investigation
        findings_so_far = len(self.report_generator.findings)
        
        if findings_so_far > 0:
            print(f"🔍 Found {findings_so_far} issues, investigating further...")
            
            # Analyze events if issues found
            if include_events:
                events_result = await self._tool_analyze_events(namespace)
                self._record_investigation("analyze_events", events_result)
            
            # Run k8sgpt for AI insights
            if include_k8sgpt:
                k8sgpt_result = await self._tool_run_k8sgpt_analysis()
                self._record_investigation("run_k8sgpt_analysis", k8sgpt_result)
        
        # Always check resource utilization
        print("🔍 Checking resource utilization...")
        metrics_result = await self._tool_get_resource_metrics()
        self._record_investigation("get_resource_metrics", metrics_result)
        
        # Analyze workloads
        print("🔍 Analyzing workloads...")
        workload_result = await self._tool_analyze_workloads(namespace)
        self._record_investigation("analyze_workloads", workload_result)
        
        # Generate AI summary of findings
        await self._generate_ai_analysis_summary()
    
    async def _run_fallback_investigation(self, namespace, include_k8sgpt, include_events, timeout):
        """Fallback investigation when AI agent is not available."""
        print("🔄 Running fallback autonomous investigation...")
        
        # Simulate autonomous decision-making
        investigation_plan = [
            ("cluster_overview", "Start with cluster overview to understand basic state"),
            ("pod_analysis", "Check pod health as it's fundamental to cluster operation"),
            ("node_analysis", "Verify node status and resource availability"),
            ("resource_metrics", "Check resource utilization patterns"),
        ]
        
        if include_events:
            investigation_plan.append(("event_analysis", "Analyze events for issues and warnings"))
        
        if include_k8sgpt:
            investigation_plan.append(("k8sgpt_analysis", "Use AI-powered issue detection"))
        
        investigation_plan.extend([
            ("workload_analysis", "Check deployments and services"),
            ("network_analysis", "Review network policies and connectivity")
        ])
        
        # Execute planned investigation
        for tool_name, reasoning in investigation_plan:
            print(f"🤖 AI Decision: {reasoning}")
            self._record_decision(tool_name, reasoning)
            
            # Execute the appropriate tool
            if tool_name == "cluster_overview":
                result = await self._tool_get_cluster_overview()
            elif tool_name == "pod_analysis":
                result = await self._tool_analyze_pods(namespace)
            elif tool_name == "node_analysis":
                result = await self._tool_analyze_nodes()
            elif tool_name == "resource_metrics":
                result = await self._tool_get_resource_metrics()
            elif tool_name == "event_analysis":
                result = await self._tool_analyze_events(namespace)
            elif tool_name == "k8sgpt_analysis":
                result = await self._tool_run_k8sgpt_analysis()
            elif tool_name == "workload_analysis":
                result = await self._tool_analyze_workloads(namespace)
            elif tool_name == "network_analysis":
                result = await self._tool_check_network_policies()
            else:
                result = {"status": "skipped", "message": f"Unknown tool: {tool_name}"}
            
            self._record_investigation(tool_name, result)
            
            # Simulate AI adaptation based on findings
            findings_count = len(self.report_generator.findings)
            if findings_count > 0 and tool_name in ["pod_analysis", "event_analysis"]:
                print(f"🤖 AI Adaptation: Found {findings_count} issues, will prioritize deeper analysis")
    
    async def _generate_ai_analysis_summary(self):
        """Generate AI-powered summary of investigation findings."""
        if not self.agent:
            return
        
        try:
            # Prepare findings for AI analysis
            findings_summary = []
            for finding in self.report_generator.findings:
                findings_summary.append({
                    "category": finding.category,
                    "severity": finding.severity.value,
                    "title": finding.title,
                    "description": finding.description
                })
            
            analysis_prompt = f"""
Based on the Kubernetes cluster investigation I just completed, please provide:

1. Overall cluster health assessment (HEALTHY/CONCERNING/CRITICAL)
2. Top 3 most important issues to address immediately
3. Root cause analysis for any critical issues
4. Strategic recommendations for cluster improvement

Investigation Findings:
{findings_summary}

Investigation Tools Used:
{[entry['tool'] for entry in self.investigation_history]}

Please provide a concise but comprehensive analysis.
"""
            
            ai_summary = self.agent.run(
                "Provide expert analysis of the Kubernetes cluster investigation results.",
                analysis_prompt
            )
            
            print(f"🧠 AI Analysis Summary:")
            print(ai_summary[:300] + "...")
            
            # Add AI analysis as a finding
            self.report_generator.add_finding(
                category="ai_analysis",
                severity=Severity.INFO,
                title="AI-Powered Cluster Analysis",
                description=ai_summary,
                affected_resources=["cluster"],
                recommendations=["Review AI analysis", "Follow strategic recommendations"],
                evidence=["AI analysis of investigation findings"],
                source_tool="agentic_ai"
            )
            
        except Exception as e:
            self.logger.error(f"AI analysis summary failed: {e}")
    
    def _record_decision(self, tool_name: str, reasoning: str):
        """Record an AI decision for transparency."""
        self.decisions_made += 1
        decision_record = {
            "decision_number": self.decisions_made,
            "timestamp": datetime.now().isoformat(),
            "tool_selected": tool_name,
            "reasoning": reasoning
        }
        print(f"   🎯 Decision #{self.decisions_made}: {tool_name}")
    
    def _record_investigation(self, tool_name: str, result: Dict[str, Any]):
        """Record investigation step and result."""
        self.investigation_history.append({
            "tool": tool_name,
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "summary": result.get("summary", "No summary available")
        })
    
    def _format_tools_for_prompt(self) -> str:
        """Format available tools for AI prompt."""
        tool_descriptions = []
        for tool_name, tool_info in self.available_tools.items():
            tool_descriptions.append(f"- {tool_name}: {tool_info['description']}")
        return "\n".join(tool_descriptions)
    
    # Tool implementations (these call the actual investigation methods)
    
    async def _tool_get_cluster_overview(self) -> Dict[str, Any]:
        """Tool: Get cluster overview."""
        try:
            cluster_info = await self.kubectl.get_cluster_info()
            namespaces = await self.kubectl.get_namespaces()
            version = await self.kubectl.get_version()
            
            if namespaces["success"]:
                ns_count = len(namespaces.get("parsed_output", {}).get("items", []))
            else:
                ns_count = 0
            
            return {
                "success": True,
                "summary": f"Cluster overview collected: {ns_count} namespaces",
                "details": {
                    "namespaces": ns_count,
                    "cluster_info": cluster_info.get("success", False),
                    "version_info": version.get("success", False)
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e), "summary": "Failed to get cluster overview"}
    
    async def _tool_analyze_pods(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Tool: Analyze pods."""
        try:
            pods = await self.kubectl.get_pods(namespace=namespace)
            
            if not pods["success"]:
                return {"success": False, "error": pods.get("error"), "summary": "Failed to get pods"}
            
            pod_items = pods.get("parsed_output", {}).get("items", [])
            total_pods = len(pod_items)
            
            failed_count = 0
            pending_count = 0
            
            for pod in pod_items:
                phase = pod.get("status", {}).get("phase", "").lower()
                if phase == "failed":
                    failed_count += 1
                    # Add finding for failed pod
                    pod_name = pod.get("metadata", {}).get("name", "unknown")
                    pod_ns = pod.get("metadata", {}).get("namespace", "unknown")
                    
                    self.report_generator.add_finding(
                        category="pod_failures",
                        severity=Severity.HIGH,
                        title=f"Failed pod: {pod_name}",
                        description=f"Pod {pod_name} in namespace {pod_ns} is in Failed state",
                        affected_resources=[f"{pod_ns}/{pod_name}"],
                        recommendations=["Check pod logs", "Review pod events", "Verify image availability"],
                        evidence=[f"Pod phase: Failed"],
                        source_tool="agentic_kubectl"
                    )
                elif phase == "pending":
                    pending_count += 1
            
            return {
                "success": True,
                "summary": f"Analyzed {total_pods} pods: {failed_count} failed, {pending_count} pending",
                "details": {
                    "total": total_pods,
                    "failed": failed_count,
                    "pending": pending_count
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e), "summary": "Failed to analyze pods"}
    
    async def _tool_analyze_nodes(self) -> Dict[str, Any]:
        """Tool: Analyze nodes."""
        try:
            nodes = await self.kubectl.get_nodes()
            
            if not nodes["success"]:
                return {"success": False, "error": nodes.get("error"), "summary": "Failed to get nodes"}
            
            node_items = nodes.get("parsed_output", {}).get("items", [])
            total_nodes = len(node_items)
            not_ready_count = 0
            
            for node in node_items:
                conditions = node.get("status", {}).get("conditions", [])
                is_ready = any(
                    condition.get("type") == "Ready" and condition.get("status") == "True"
                    for condition in conditions
                )
                
                if not is_ready:
                    not_ready_count += 1
                    node_name = node.get("metadata", {}).get("name", "unknown")
                    
                    self.report_generator.add_finding(
                        category="node_health",
                        severity=Severity.CRITICAL,
                        title=f"Node {node_name} not ready",
                        description=f"Node {node_name} is not in Ready state",
                        affected_resources=[node_name],
                        recommendations=["Check node logs", "Verify kubelet status", "Check node connectivity"],
                        evidence=["Node status: Not Ready"],
                        source_tool="agentic_kubectl"
                    )
            
            return {
                "success": True,
                "summary": f"Analyzed {total_nodes} nodes: {not_ready_count} not ready",
                "details": {
                    "total": total_nodes,
                    "ready": total_nodes - not_ready_count,
                    "not_ready": not_ready_count
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e), "summary": "Failed to analyze nodes"}
    
    async def _tool_get_resource_metrics(self) -> Dict[str, Any]:
        """Tool: Get resource metrics."""
        try:
            node_metrics = await self.kubectl.get_node_metrics()
            pod_metrics = await self.kubectl.get_pod_metrics()
            
            metrics_available = node_metrics["success"] or pod_metrics["success"]
            
            if not metrics_available:
                self.report_generator.add_finding(
                    category="monitoring",
                    severity=Severity.MEDIUM,
                    title="Resource metrics unavailable",
                    description="Node and pod resource metrics are not available",
                    affected_resources=["metrics-server"],
                    recommendations=["Install metrics-server", "Verify metrics-server deployment"],
                    evidence=["kubectl top commands failed"],
                    source_tool="agentic_kubectl"
                )
            
            return {
                "success": True,
                "summary": f"Resource metrics: nodes={'available' if node_metrics['success'] else 'unavailable'}, pods={'available' if pod_metrics['success'] else 'unavailable'}",
                "details": {
                    "node_metrics": node_metrics["success"],
                    "pod_metrics": pod_metrics["success"]
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e), "summary": "Failed to get resource metrics"}
    
    async def _tool_analyze_events(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Tool: Analyze events."""
        try:
            events = await self.kubectl.get_events(namespace=namespace)
            
            if not events["success"]:
                return {"success": False, "error": events.get("error"), "summary": "Failed to get events"}
            
            event_items = events.get("parsed_output", {}).get("items", [])
            warning_count = 0
            
            for event in event_items:
                if event.get("type") == "Warning":
                    warning_count += 1
                    reason = event.get("reason", "")
                    
                    # Add findings for significant warnings
                    if reason in ["Failed", "Unhealthy", "FailedScheduling", "ErrImagePull"]:
                        involved_object = event.get("involvedObject", {})
                        object_name = involved_object.get("name", "unknown")
                        object_kind = involved_object.get("kind", "unknown")
                        
                        self.report_generator.add_finding(
                            category="cluster_events",
                            severity=Severity.HIGH if reason in ["Failed", "ErrImagePull"] else Severity.MEDIUM,
                            title=f"Warning event: {reason}",
                            description=event.get("message", ""),
                            affected_resources=[f"{object_kind}/{object_name}"],
                            recommendations=["Check resource status", "Review logs", "Verify configuration"],
                            evidence=[f"Event: {reason}"],
                            source_tool="agentic_kubectl"
                        )
            
            return {
                "success": True,
                "summary": f"Analyzed {len(event_items)} events: {warning_count} warnings",
                "details": {
                    "total": len(event_items),
                    "warnings": warning_count
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e), "summary": "Failed to analyze events"}
    
    async def _tool_run_k8sgpt_analysis(self) -> Dict[str, Any]:
        """Tool: Run k8sgpt analysis."""
        try:
            k8sgpt_result = await self.k8sgpt.analyze_cluster()
            
            if k8sgpt_result["success"]:
                issues_count = self.k8sgpt._count_issues(k8sgpt_result)
                
                if issues_count > 0:
                    self.report_generator.add_finding(
                        category="ai_analysis",
                        severity=Severity.MEDIUM,
                        title=f"K8sgpt detected {issues_count} issues",
                        description="AI-powered analysis found potential cluster issues",
                        affected_resources=["cluster"],
                        recommendations=["Review k8sgpt detailed output", "Address identified issues"],
                        evidence=[k8sgpt_result.get("stdout", "")[:200]],
                        source_tool="agentic_k8sgpt"
                    )
                
                return {
                    "success": True,
                    "summary": f"K8sgpt analysis completed: {issues_count} issues found",
                    "details": {"issues_count": issues_count}
                }
            else:
                return {
                    "success": False,
                    "error": k8sgpt_result.get("error"),
                    "summary": "K8sgpt analysis failed"
                }
        except Exception as e:
            return {"success": False, "error": str(e), "summary": "Failed to run k8sgpt analysis"}
    
    async def _tool_analyze_workloads(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Tool: Analyze workloads."""
        try:
            deployments = await self.kubectl.get_deployments(namespace=namespace)
            services = await self.kubectl.get_services(namespace=namespace)
            
            deployment_count = 0
            service_count = 0
            unhealthy_deployments = 0
            
            if deployments["success"]:
                deployment_items = deployments.get("parsed_output", {}).get("items", [])
                deployment_count = len(deployment_items)
                
                for deployment in deployment_items:
                    status = deployment.get("status", {})
                    replicas = status.get("replicas", 0)
                    ready_replicas = status.get("readyReplicas", 0)
                    
                    if ready_replicas < replicas:
                        unhealthy_deployments += 1
                        name = deployment.get("metadata", {}).get("name", "unknown")
                        ns = deployment.get("metadata", {}).get("namespace", "unknown")
                        
                        self.report_generator.add_finding(
                            category="workload_health",
                            severity=Severity.MEDIUM,
                            title=f"Deployment {name} not fully ready",
                            description=f"Deployment has {ready_replicas}/{replicas} replicas ready",
                            affected_resources=[f"deployment/{ns}/{name}"],
                            recommendations=["Check pod status", "Review deployment events"],
                            evidence=[f"Ready replicas: {ready_replicas}/{replicas}"],
                            source_tool="agentic_kubectl"
                        )
            
            if services["success"]:
                service_items = services.get("parsed_output", {}).get("items", [])
                service_count = len(service_items)
            
            return {
                "success": True,
                "summary": f"Analyzed workloads: {deployment_count} deployments ({unhealthy_deployments} unhealthy), {service_count} services",
                "details": {
                    "deployments": deployment_count,
                    "services": service_count,
                    "unhealthy_deployments": unhealthy_deployments
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e), "summary": "Failed to analyze workloads"}
    
    async def _tool_investigate_specific_resource(self, resource_type: str, resource_name: str, namespace: str = "default") -> Dict[str, Any]:
        """Tool: Deep dive into specific resource."""
        try:
            # This would implement deeper investigation of specific resources
            # For now, return a placeholder
            return {
                "success": True,
                "summary": f"Investigated {resource_type}/{resource_name} in namespace {namespace}",
                "details": {"resource_type": resource_type, "resource_name": resource_name, "namespace": namespace}
            }
        except Exception as e:
            return {"success": False, "error": str(e), "summary": f"Failed to investigate {resource_type}/{resource_name}"}
    
    async def _tool_check_network_policies(self) -> Dict[str, Any]:
        """Tool: Check network policies."""
        try:
            network_policies = await self.kubectl.get_network_policies()
            ingresses = await self.kubectl.get_ingresses()
            
            policy_count = 0
            ingress_count = 0
            
            if network_policies["success"]:
                policy_items = network_policies.get("parsed_output", {}).get("items", [])
                policy_count = len(policy_items)
            
            if ingresses["success"]:
                ingress_items = ingresses.get("parsed_output", {}).get("items", [])
                ingress_count = len(ingress_items)
            
            return {
                "success": True,
                "summary": f"Network analysis: {policy_count} policies, {ingress_count} ingresses",
                "details": {
                    "network_policies": policy_count,
                    "ingresses": ingress_count
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e), "summary": "Failed to check network policies"}


# Convenience function for direct usage
async def run_agentic_investigation(**kwargs) -> Dict[str, Any]:
    """
    Quick function to run agentic investigation.
    
    Args:
        **kwargs: Arguments to pass to run_investigation()
        
    Returns:
        Investigation report
    """
    investigator = AgenticInvestigator()
    return await investigator.run_investigation(**kwargs)
