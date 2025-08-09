"""
Deterministic Kubernetes Investigation Agent.

This agent follows predefined investigation steps to analyze cluster state
and identify issues in a consistent, repeatable manner.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
import time
from datetime import datetime

from .base_investigator import BaseInvestigator
from .tools.kubectl_wrapper import KubectlWrapper
from .tools.k8sgpt_wrapper import K8sgptWrapper
from .tools.report_generator import ReportGenerator, Severity, InvestigationType


class DeterministicInvestigator(BaseInvestigator):
    """
    Deterministic investigation agent that follows predefined steps.
    
    This agent executes a fixed sequence of investigation steps to ensure
    consistent and repeatable analysis of Kubernetes clusters.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.kubectl = KubectlWrapper()
        self.k8sgpt = K8sgptWrapper()
        self.report_generator = ReportGenerator()
        self.report_generator.set_investigation_type(InvestigationType.DETERMINISTIC)
        
        # Investigation step counter
        self.current_step = 0
        
    async def run_investigation(self, 
                              namespace: Optional[str] = None,
                              include_k8sgpt: bool = True,
                              include_events: bool = True,
                              timeout: int = 300) -> Dict[str, Any]:
        """
        Execute the complete deterministic investigation.
        
        Args:
            namespace: Specific namespace to focus on (default: all namespaces)
            include_k8sgpt: Whether to include k8sgpt analysis
            include_events: Whether to analyze cluster events
            timeout: Investigation timeout in seconds
            
        Returns:
            Complete investigation report
        """
        self.logger.info("🚀 Starting Deterministic Kubernetes Investigation")
        print("🚀 Starting Deterministic Kubernetes Investigation")
        print("=" * 60)
        
        try:
            # Set agent metadata
            self.report_generator.set_agent_metadata({
                "agent_type": "deterministic",
                "version": "1.0.0",
                "namespace_filter": namespace,
                "include_k8sgpt": include_k8sgpt,
                "include_events": include_events,
                "timeout_seconds": timeout
            })
            
            # Execute investigation steps in order
            await self._step_1_cluster_overview()
            await self._step_2_node_analysis()
            await self._step_3_pod_analysis(namespace)
            await self._step_4_resource_utilization()
            
            if include_events:
                await self._step_5_event_analysis(namespace)
            
            if include_k8sgpt:
                await self._step_6_k8sgpt_analysis()
            
            await self._step_7_workload_analysis(namespace)
            await self._step_8_network_analysis()
            
            # Generate final report
            final_report = await self._step_9_generate_final_report()
            
            print("✅ Deterministic Investigation Complete!")
            self.logger.info("Deterministic investigation completed successfully")
            
            return final_report
            
        except Exception as e:
            self.logger.error(f"Deterministic investigation failed: {e}")
            print(f"❌ Investigation failed: {e}")
            
            # Generate error report
            self.report_generator.add_finding(
                category="investigation_error",
                severity=Severity.CRITICAL,
                title="Investigation Failed",
                description=f"Deterministic investigation failed with error: {str(e)}",
                affected_resources=["investigation_agent"],
                recommendations=["Review investigation logs", "Check cluster connectivity", "Verify tool availability"],
                evidence=[str(e)],
                source_tool="deterministic_investigator"
            )
            
            return self.report_generator.generate_json_report()
    
    async def _step_1_cluster_overview(self):
        """Step 1: Get basic cluster information."""
        step_start = time.time()
        self.current_step += 1
        
        print(f"🔍 Step {self.current_step}: Collecting cluster overview...")
        self.logger.info(f"Step {self.current_step}: Collecting cluster overview")
        
        try:
            # Get cluster info
            cluster_info = await self.kubectl.get_cluster_info()
            version_info = await self.kubectl.get_version()
            namespaces = await self.kubectl.get_namespaces()
            
            # Process results
            if cluster_info["success"]:
                print(f"   ✅ Cluster info collected")
            else:
                print(f"   ❌ Failed to get cluster info: {cluster_info.get('error', 'Unknown error')}")
                
            if version_info["success"]:
                print(f"   ✅ Version info collected")
            else:
                print(f"   ❌ Failed to get version info: {version_info.get('error', 'Unknown error')}")
                
            if namespaces["success"]:
                ns_count = len(namespaces.get("parsed_output", {}).get("items", []))
                print(f"   ✅ Found {ns_count} namespaces")
            else:
                print(f"   ❌ Failed to get namespaces: {namespaces.get('error', 'Unknown error')}")
            
            # Record step
            duration = time.time() - step_start
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="cluster_overview",
                tool_used="kubectl",
                status="completed",
                duration_seconds=duration,
                output_summary=f"Collected cluster info, version, and {ns_count if namespaces['success'] else 0} namespaces"
            )
            
        except Exception as e:
            duration = time.time() - step_start
            self.logger.error(f"Step {self.current_step} failed: {e}")
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="cluster_overview",
                tool_used="kubectl",
                status="failed",
                duration_seconds=duration,
                output_summary="Failed to collect cluster overview",
                error_message=str(e)
            )
            raise
    
    async def _step_2_node_analysis(self):
        """Step 2: Analyze cluster nodes."""
        step_start = time.time()
        self.current_step += 1
        
        print(f"🔍 Step {self.current_step}: Analyzing cluster nodes...")
        self.logger.info(f"Step {self.current_step}: Analyzing cluster nodes")
        
        try:
            # Get node information
            nodes = await self.kubectl.get_nodes()
            node_conditions = await self.kubectl.describe_nodes()
            
            if nodes["success"]:
                node_items = nodes.get("parsed_output", {}).get("items", [])
                total_nodes = len(node_items)
                ready_nodes = 0
                not_ready_nodes = 0
                
                # Analyze node status
                for node in node_items:
                    conditions = node.get("status", {}).get("conditions", [])
                    is_ready = any(
                        condition.get("type") == "Ready" and condition.get("status") == "True"
                        for condition in conditions
                    )
                    
                    if is_ready:
                        ready_nodes += 1
                    else:
                        not_ready_nodes += 1
                        
                        # Add finding for not ready nodes
                        node_name = node.get("metadata", {}).get("name", "unknown")
                        self.report_generator.add_finding(
                            category="node_health",
                            severity=Severity.HIGH,
                            title=f"Node {node_name} not ready",
                            description=f"Node {node_name} is not in Ready state",
                            affected_resources=[node_name],
                            recommendations=["Check node logs", "Verify node connectivity", "Check kubelet status"],
                            evidence=[f"Node condition: Not Ready"],
                            source_tool="kubectl"
                        )
                
                print(f"   ✅ Analyzed {total_nodes} nodes ({ready_nodes} ready, {not_ready_nodes} not ready)")
                
                # Record summary for cluster summary
                self._node_summary = {
                    "total": total_nodes,
                    "ready": ready_nodes,
                    "not_ready": not_ready_nodes
                }
                
            else:
                print(f"   ❌ Failed to get nodes: {nodes.get('error', 'Unknown error')}")
                self._node_summary = {"total": 0, "ready": 0, "not_ready": 0}
            
            # Record step
            duration = time.time() - step_start
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="node_analysis",
                tool_used="kubectl",
                status="completed" if nodes["success"] else "failed",
                duration_seconds=duration,
                output_summary=f"Analyzed {self._node_summary['total']} nodes"
            )
            
        except Exception as e:
            duration = time.time() - step_start
            self.logger.error(f"Step {self.current_step} failed: {e}")
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="node_analysis",
                tool_used="kubectl",
                status="failed",
                duration_seconds=duration,
                output_summary="Failed to analyze nodes",
                error_message=str(e)
            )
            self._node_summary = {"total": 0, "ready": 0, "not_ready": 0}
    
    async def _step_3_pod_analysis(self, namespace: Optional[str] = None):
        """Step 3: Analyze pods across namespaces."""
        step_start = time.time()
        self.current_step += 1
        
        print(f"🔍 Step {self.current_step}: Analyzing pod states...")
        self.logger.info(f"Step {self.current_step}: Analyzing pod states")
        
        try:
            # Get pod information
            pods = await self.kubectl.get_pods(namespace=namespace)
            
            if pods["success"]:
                pod_items = pods.get("parsed_output", {}).get("items", [])
                total_pods = len(pod_items)
                
                # Categorize pods by status
                pod_stats = {
                    "running": 0,
                    "pending": 0,
                    "failed": 0,
                    "succeeded": 0,
                    "unknown": 0
                }
                
                failed_pods = []
                pending_pods = []
                
                for pod in pod_items:
                    pod_name = pod.get("metadata", {}).get("name", "unknown")
                    pod_namespace = pod.get("metadata", {}).get("namespace", "unknown")
                    phase = pod.get("status", {}).get("phase", "Unknown")
                    
                    # Count by phase
                    phase_lower = phase.lower()
                    if phase_lower in pod_stats:
                        pod_stats[phase_lower] += 1
                    else:
                        pod_stats["unknown"] += 1
                    
                    # Collect problematic pods
                    if phase_lower == "failed":
                        failed_pods.append(f"{pod_namespace}/{pod_name}")
                        
                        self.report_generator.add_finding(
                            category="pod_failures",
                            severity=Severity.HIGH,
                            title=f"Pod {pod_name} failed",
                            description=f"Pod {pod_name} in namespace {pod_namespace} is in Failed state",
                            affected_resources=[f"{pod_namespace}/{pod_name}"],
                            recommendations=["Check pod logs", "Review pod events", "Verify resource limits", "Check image availability"],
                            evidence=[f"Pod phase: {phase}"],
                            source_tool="kubectl"
                        )
                    
                    elif phase_lower == "pending":
                        pending_pods.append(f"{pod_namespace}/{pod_name}")
                        
                        # Pending pods might indicate resource issues
                        self.report_generator.add_finding(
                            category="pod_scheduling",
                            severity=Severity.MEDIUM,
                            title=f"Pod {pod_name} pending",
                            description=f"Pod {pod_name} in namespace {pod_namespace} is stuck in Pending state",
                            affected_resources=[f"{pod_namespace}/{pod_name}"],
                            recommendations=["Check node resources", "Verify pod scheduling constraints", "Review events"],
                            evidence=[f"Pod phase: {phase}"],
                            source_tool="kubectl"
                        )
                
                print(f"   ✅ Analyzed {total_pods} pods:")
                print(f"       Running: {pod_stats['running']}")
                print(f"       Pending: {pod_stats['pending']}")
                print(f"       Failed: {pod_stats['failed']}")
                print(f"       Succeeded: {pod_stats['succeeded']}")
                print(f"       Unknown: {pod_stats['unknown']}")
                
                if failed_pods:
                    print(f"   ⚠️  Failed pods: {', '.join(failed_pods[:5])}")
                if pending_pods:
                    print(f"   ⚠️  Pending pods: {', '.join(pending_pods[:5])}")
                
                # Store for cluster summary
                self._pod_summary = {
                    "total": total_pods,
                    "running": pod_stats["running"],
                    "pending": pod_stats["pending"],
                    "failed": pod_stats["failed"],
                    "succeeded": pod_stats["succeeded"],
                    "healthy": pod_stats["running"] + pod_stats["succeeded"]
                }
                
            else:
                print(f"   ❌ Failed to get pods: {pods.get('error', 'Unknown error')}")
                self._pod_summary = {"total": 0, "running": 0, "pending": 0, "failed": 0, "succeeded": 0, "healthy": 0}
            
            # Record step
            duration = time.time() - step_start
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="pod_analysis",
                tool_used="kubectl",
                status="completed" if pods["success"] else "failed",
                duration_seconds=duration,
                output_summary=f"Analyzed {self._pod_summary['total']} pods"
            )
            
        except Exception as e:
            duration = time.time() - step_start
            self.logger.error(f"Step {self.current_step} failed: {e}")
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="pod_analysis",
                tool_used="kubectl",
                status="failed",
                duration_seconds=duration,
                output_summary="Failed to analyze pods",
                error_message=str(e)
            )
            self._pod_summary = {"total": 0, "running": 0, "pending": 0, "failed": 0, "succeeded": 0, "healthy": 0}
    
    async def _step_4_resource_utilization(self):
        """Step 4: Check resource usage."""
        step_start = time.time()
        self.current_step += 1
        
        print(f"🔍 Step {self.current_step}: Checking resource utilization...")
        self.logger.info(f"Step {self.current_step}: Checking resource utilization")
        
        try:
            # Get resource utilization
            node_metrics = await self.kubectl.get_node_metrics()
            pod_metrics = await self.kubectl.get_pod_metrics()
            
            resource_summary = {"nodes": "Not available", "pods": "Not available"}
            
            if node_metrics["success"]:
                print(f"   ✅ Node resource metrics collected")
                resource_summary["nodes"] = "Available"
            else:
                print(f"   ⚠️  Node metrics not available (metrics-server may not be running)")
                
                # Add finding about missing metrics
                self.report_generator.add_finding(
                    category="monitoring",
                    severity=Severity.MEDIUM,
                    title="Node metrics unavailable",
                    description="Node resource metrics are not available, metrics-server may not be running",
                    affected_resources=["metrics-server"],
                    recommendations=["Install or restart metrics-server", "Verify metrics-server deployment"],
                    evidence=["kubectl top nodes failed"],
                    source_tool="kubectl"
                )
            
            if pod_metrics["success"]:
                print(f"   ✅ Pod resource metrics collected")
                resource_summary["pods"] = "Available"
            else:
                print(f"   ⚠️  Pod metrics not available")
            
            # Store for cluster summary
            self._resource_summary = resource_summary
            
            # Record step
            duration = time.time() - step_start
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="resource_utilization",
                tool_used="kubectl",
                status="completed",
                duration_seconds=duration,
                output_summary=f"Resource metrics: {resource_summary}"
            )
            
        except Exception as e:
            duration = time.time() - step_start
            self.logger.error(f"Step {self.current_step} failed: {e}")
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="resource_utilization",
                tool_used="kubectl",
                status="failed",
                duration_seconds=duration,
                output_summary="Failed to check resource utilization",
                error_message=str(e)
            )
            self._resource_summary = {"nodes": "Error", "pods": "Error"}
    
    async def _step_5_event_analysis(self, namespace: Optional[str] = None):
        """Step 5: Analyze recent cluster events."""
        step_start = time.time()
        self.current_step += 1
        
        print(f"🔍 Step {self.current_step}: Analyzing cluster events...")
        self.logger.info(f"Step {self.current_step}: Analyzing cluster events")
        
        try:
            # Get recent events
            events = await self.kubectl.get_events(namespace=namespace)
            
            if events["success"]:
                event_items = events.get("parsed_output", {}).get("items", [])
                total_events = len(event_items)
                
                warning_events = []
                error_events = []
                
                for event in event_items:
                    event_type = event.get("type", "")
                    reason = event.get("reason", "")
                    message = event.get("message", "")
                    involved_object = event.get("involvedObject", {})
                    object_name = involved_object.get("name", "unknown")
                    object_kind = involved_object.get("kind", "unknown")
                    
                    if event_type == "Warning":
                        warning_events.append({
                            "reason": reason,
                            "message": message,
                            "object": f"{object_kind}/{object_name}"
                        })
                        
                        # Add findings for significant warnings
                        if reason in ["Failed", "Unhealthy", "FailedScheduling", "ErrImagePull", "ImagePullBackOff"]:
                            severity = Severity.HIGH if reason in ["Failed", "ErrImagePull", "ImagePullBackOff"] else Severity.MEDIUM
                            
                            self.report_generator.add_finding(
                                category="cluster_events",
                                severity=severity,
                                title=f"{reason} event for {object_kind} {object_name}",
                                description=message,
                                affected_resources=[f"{object_kind}/{object_name}"],
                                recommendations=self._get_event_recommendations(reason),
                                evidence=[f"Event: {reason} - {message}"],
                                source_tool="kubectl"
                            )
                
                print(f"   ✅ Analyzed {total_events} events ({len(warning_events)} warnings)")
                
                if warning_events:
                    print(f"   ⚠️  Recent warnings found:")
                    for event in warning_events[:3]:  # Show first 3
                        print(f"       {event['reason']}: {event['object']}")
                
            else:
                print(f"   ❌ Failed to get events: {events.get('error', 'Unknown error')}")
            
            # Record step
            duration = time.time() - step_start
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="event_analysis",
                tool_used="kubectl",
                status="completed" if events["success"] else "failed",
                duration_seconds=duration,
                output_summary=f"Analyzed {total_events if events['success'] else 0} events"
            )
            
        except Exception as e:
            duration = time.time() - step_start
            self.logger.error(f"Step {self.current_step} failed: {e}")
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="event_analysis",
                tool_used="kubectl",
                status="failed",
                duration_seconds=duration,
                output_summary="Failed to analyze events",
                error_message=str(e)
            )
    
    async def _step_6_k8sgpt_analysis(self):
        """Step 6: Run k8sgpt AI analysis."""
        step_start = time.time()
        self.current_step += 1
        
        print(f"🔍 Step {self.current_step}: Running AI issue detection (k8sgpt)...")
        self.logger.info(f"Step {self.current_step}: Running k8sgpt analysis")
        
        try:
            # Run k8sgpt analysis
            k8sgpt_result = await self.k8sgpt.analyze_cluster()
            
            if k8sgpt_result["success"]:
                print(f"   ✅ K8sgpt analysis completed")
                
                # Process k8sgpt findings
                issues_count = self.k8sgpt._count_issues(k8sgpt_result)
                print(f"   📊 K8sgpt found {issues_count} issues")
                
                # Add k8sgpt findings to report
                if issues_count > 0:
                    self.report_generator.add_finding(
                        category="ai_analysis",
                        severity=Severity.MEDIUM,
                        title=f"K8sgpt detected {issues_count} issues",
                        description=f"AI-powered analysis found {issues_count} potential issues in the cluster",
                        affected_resources=["cluster"],
                        recommendations=["Review k8sgpt detailed output", "Address identified issues"],
                        evidence=[k8sgpt_result.get("stdout", "")[:500]],
                        source_tool="k8sgpt"
                    )
                
            else:
                print(f"   ❌ K8sgpt analysis failed: {k8sgpt_result.get('error', 'Unknown error')}")
                
                self.report_generator.add_finding(
                    category="tool_availability",
                    severity=Severity.LOW,
                    title="K8sgpt analysis failed",
                    description="AI-powered analysis could not be completed",
                    affected_resources=["k8sgpt"],
                    recommendations=["Check k8sgpt configuration", "Verify API access"],
                    evidence=[k8sgpt_result.get("error", "Unknown error")],
                    source_tool="k8sgpt"
                )
            
            # Record step
            duration = time.time() - step_start
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="k8sgpt_analysis",
                tool_used="k8sgpt",
                status="completed" if k8sgpt_result["success"] else "failed",
                duration_seconds=duration,
                output_summary=f"K8sgpt analysis completed, found {issues_count if k8sgpt_result['success'] else 0} issues"
            )
            
        except Exception as e:
            duration = time.time() - step_start
            self.logger.error(f"Step {self.current_step} failed: {e}")
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="k8sgpt_analysis",
                tool_used="k8sgpt",
                status="failed",
                duration_seconds=duration,
                output_summary="Failed to run k8sgpt analysis",
                error_message=str(e)
            )
    
    async def _step_7_workload_analysis(self, namespace: Optional[str] = None):
        """Step 7: Analyze workloads (deployments, services)."""
        step_start = time.time()
        self.current_step += 1
        
        print(f"🔍 Step {self.current_step}: Analyzing workloads...")
        self.logger.info(f"Step {self.current_step}: Analyzing workloads")
        
        try:
            # Get workload information
            deployments = await self.kubectl.get_deployments(namespace=namespace)
            services = await self.kubectl.get_services(namespace=namespace)
            
            deployment_count = 0
            service_count = 0
            
            # Analyze deployments
            if deployments["success"]:
                deployment_items = deployments.get("parsed_output", {}).get("items", [])
                deployment_count = len(deployment_items)
                
                for deployment in deployment_items:
                    name = deployment.get("metadata", {}).get("name", "unknown")
                    namespace_name = deployment.get("metadata", {}).get("namespace", "unknown")
                    status = deployment.get("status", {})
                    
                    replicas = status.get("replicas", 0)
                    ready_replicas = status.get("readyReplicas", 0)
                    
                    if ready_replicas < replicas:
                        self.report_generator.add_finding(
                            category="workload_health",
                            severity=Severity.MEDIUM,
                            title=f"Deployment {name} not fully ready",
                            description=f"Deployment {name} has {ready_replicas}/{replicas} replicas ready",
                            affected_resources=[f"deployment/{namespace_name}/{name}"],
                            recommendations=["Check pod status", "Review deployment events", "Verify resource availability"],
                            evidence=[f"Ready replicas: {ready_replicas}/{replicas}"],
                            source_tool="kubectl"
                        )
                
                print(f"   ✅ Analyzed {deployment_count} deployments")
            
            # Analyze services
            if services["success"]:
                service_items = services.get("parsed_output", {}).get("items", [])
                service_count = len(service_items)
                print(f"   ✅ Analyzed {service_count} services")
            
            # Store for cluster summary
            self._workload_summary = {
                "deployments": deployment_count,
                "services": service_count
            }
            
            # Record step
            duration = time.time() - step_start
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="workload_analysis",
                tool_used="kubectl",
                status="completed",
                duration_seconds=duration,
                output_summary=f"Analyzed {deployment_count} deployments and {service_count} services"
            )
            
        except Exception as e:
            duration = time.time() - step_start
            self.logger.error(f"Step {self.current_step} failed: {e}")
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="workload_analysis",
                tool_used="kubectl",
                status="failed",
                duration_seconds=duration,
                output_summary="Failed to analyze workloads",
                error_message=str(e)
            )
            self._workload_summary = {"deployments": 0, "services": 0}
    
    async def _step_8_network_analysis(self):
        """Step 8: Basic network analysis."""
        step_start = time.time()
        self.current_step += 1
        
        print(f"🔍 Step {self.current_step}: Analyzing network configuration...")
        self.logger.info(f"Step {self.current_step}: Analyzing network configuration")
        
        try:
            # Get network policies and ingresses
            network_policies = await self.kubectl.get_network_policies()
            ingresses = await self.kubectl.get_ingresses()
            
            policy_count = 0
            ingress_count = 0
            
            if network_policies["success"]:
                policy_items = network_policies.get("parsed_output", {}).get("items", [])
                policy_count = len(policy_items)
                print(f"   ✅ Found {policy_count} network policies")
            
            if ingresses["success"]:
                ingress_items = ingresses.get("parsed_output", {}).get("items", [])
                ingress_count = len(ingress_items)
                print(f"   ✅ Found {ingress_count} ingresses")
            
            # Record step
            duration = time.time() - step_start
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="network_analysis",
                tool_used="kubectl",
                status="completed",
                duration_seconds=duration,
                output_summary=f"Analyzed network: {policy_count} policies, {ingress_count} ingresses"
            )
            
        except Exception as e:
            duration = time.time() - step_start
            self.logger.error(f"Step {self.current_step} failed: {e}")
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="network_analysis",
                tool_used="kubectl",
                status="failed",
                duration_seconds=duration,
                output_summary="Failed to analyze network configuration",
                error_message=str(e)
            )
    
    async def _step_9_generate_final_report(self) -> Dict[str, Any]:
        """Step 9: Generate final investigation report."""
        step_start = time.time()
        self.current_step += 1
        
        print(f"🔍 Step {self.current_step}: Generating investigation report...")
        self.logger.info(f"Step {self.current_step}: Generating final report")
        
        try:
            # Set cluster summary
            self.report_generator.set_cluster_summary(
                total_nodes=getattr(self, '_node_summary', {}).get('total', 0),
                total_pods=getattr(self, '_pod_summary', {}).get('total', 0),
                total_namespaces=0,  # Will be updated if needed
                healthy_pods=getattr(self, '_pod_summary', {}).get('healthy', 0),
                failed_pods=getattr(self, '_pod_summary', {}).get('failed', 0),
                pending_pods=getattr(self, '_pod_summary', {}).get('pending', 0),
                running_pods=getattr(self, '_pod_summary', {}).get('running', 0),
                total_deployments=getattr(self, '_workload_summary', {}).get('deployments', 0),
                total_services=getattr(self, '_workload_summary', {}).get('services', 0),
                resource_utilization=getattr(self, '_resource_summary', {})
            )
            
            # Generate final report
            final_report = self.report_generator.generate_json_report()
            
            # Print summary
            print(f"   ✅ Investigation report generated")
            print(f"   📊 Total findings: {len(self.report_generator.findings)}")
            
            severity_counts = self.report_generator.get_severity_counts()
            if severity_counts.get('critical', 0) > 0:
                print(f"   🚨 Critical issues: {severity_counts['critical']}")
            if severity_counts.get('high', 0) > 0:
                print(f"   ⚠️  High priority issues: {severity_counts['high']}")
            
            # Record step
            duration = time.time() - step_start
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="generate_report",
                tool_used="report_generator",
                status="completed",
                duration_seconds=duration,
                output_summary=f"Generated report with {len(self.report_generator.findings)} findings"
            )
            
            return final_report
            
        except Exception as e:
            duration = time.time() - step_start
            self.logger.error(f"Step {self.current_step} failed: {e}")
            self.report_generator.add_investigation_step(
                step_number=self.current_step,
                action="generate_report",
                tool_used="report_generator",
                status="failed",
                duration_seconds=duration,
                output_summary="Failed to generate final report",
                error_message=str(e)
            )
            raise
    
    def _get_event_recommendations(self, reason: str) -> List[str]:
        """Get recommendations based on event reason."""
        recommendations_map = {
            "Failed": ["Check pod logs", "Verify image availability", "Check resource limits"],
            "FailedScheduling": ["Check node resources", "Verify node selectors", "Review pod constraints"],
            "ErrImagePull": ["Verify image name and tag", "Check registry credentials", "Verify network connectivity"],
            "ImagePullBackOff": ["Check image repository access", "Verify authentication", "Review image pull secrets"],
            "Unhealthy": ["Check readiness/liveness probes", "Verify application health", "Review resource usage"],
            "FailedMount": ["Check volume configuration", "Verify PVC status", "Check storage class"],
        }
        
        return recommendations_map.get(reason, ["Review event details", "Check related resources", "Verify configuration"])


# Convenience function for direct usage
async def run_deterministic_investigation(**kwargs) -> Dict[str, Any]:
    """
    Quick function to run deterministic investigation.
    
    Args:
        **kwargs: Arguments to pass to run_investigation()
        
    Returns:
        Investigation report
    """
    investigator = DeterministicInvestigator()
    return await investigator.run_investigation(**kwargs)
