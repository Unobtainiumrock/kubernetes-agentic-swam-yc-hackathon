#!/usr/bin/env python3
"""
Autonomous Kubernetes Monitor - Chunk 2: Intelligent Issue Detection

Enhanced with comprehensive issue detection including:
- Pod failure detection (CrashLoopBackOff, ImagePullBackOff, etc.)
- Node health monitoring (NotReady, resource pressure)
- Event analysis for warnings and errors
- Automatic investigation triggering
"""
import asyncio
import logging
import sys
import os
from datetime import datetime
import signal

# Add the api directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ..agents.tools.kubectl_wrapper import KubectlWrapper
from ..agents.deterministic_investigator import DeterministicInvestigator
from ..agents.agentic_investigator import AgenticInvestigator
from .log_streamer import AutonomousMonitorStreamer


class AutonomousMonitor:
    """Autonomous monitor with intelligent issue detection - Chunk 2 implementation."""
    
    def __init__(self, safe_mode=None, auto_investigate=None, check_interval=None, backend_url=None):
        self.running = False
        self.kubectl = KubectlWrapper()
        self.investigation_in_progress = False
        self.last_investigation_time = None
        self.streamer = None
        
        # COST-SAFE CONFIGURATION - Use provided params or environment defaults
        if safe_mode is None:
            safe_mode = os.getenv('AGENT_SAFE_MODE', 'true').lower() == 'true'
        self.safe_mode = safe_mode  # Only monitoring + deterministic investigation (no AI calls)
        
        if auto_investigate is None:
            auto_investigate = os.getenv('AGENT_AUTO_INVESTIGATE', 'true').lower() == 'true'
        self.auto_investigate = auto_investigate
        
        if check_interval is None:
            check_interval = int(os.getenv('AGENT_CHECK_INTERVAL', '30'))
        self.check_interval = check_interval
        
        if backend_url is None:
            backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
        self.backend_url = backend_url
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Log safe mode status
        if self.safe_mode:
            print("🛡️  SAFE MODE: Only monitoring + deterministic investigation (no AI API calls)")
        else:
            print("⚠️  FULL MODE: AI investigations enabled (may use OpenRouter API credits)")
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def analyze_pod_issues(self, pod_items):
        """Analyze pods for specific issues like CrashLoopBackOff, ImagePullBackOff, etc."""
        issues = []
        
        for pod in pod_items:
            pod_name = pod.get("metadata", {}).get("name", "unknown")
            namespace = pod.get("metadata", {}).get("namespace", "default")
            phase = pod.get("status", {}).get("phase", "Unknown")
            
            # Check container statuses for specific issues
            container_statuses = pod.get("status", {}).get("containerStatuses", [])
            init_container_statuses = pod.get("status", {}).get("initContainerStatuses", [])
            
            all_statuses = container_statuses + init_container_statuses
            
            for container_status in all_statuses:
                container_name = container_status.get("name", "unknown")
                waiting = container_status.get("state", {}).get("waiting", {})
                terminated = container_status.get("state", {}).get("terminated", {})
                
                # Check for specific failure reasons
                if waiting:
                    reason = waiting.get("reason", "")
                    message = waiting.get("message", "")
                    
                    if reason in ["CrashLoopBackOff", "ImagePullBackOff", "ErrImagePull", 
                                 "InvalidImageName", "CreateContainerConfigError"]:
                        issues.append({
                            "type": "pod_issue",
                            "severity": "high" if reason == "CrashLoopBackOff" else "medium",
                            "resource": f"{namespace}/{pod_name}",
                            "container": container_name,
                            "reason": reason,
                            "message": message,
                            "phase": phase
                        })
                
                if terminated and terminated.get("exitCode", 0) != 0:
                    reason = terminated.get("reason", "")
                    exit_code = terminated.get("exitCode", 0)
                    
                    issues.append({
                        "type": "pod_failure",
                        "severity": "high",
                        "resource": f"{namespace}/{pod_name}",
                        "container": container_name,
                        "reason": reason,
                        "exit_code": exit_code,
                        "phase": phase
                    })
            
            # Check for pods stuck in Pending too long
            if phase == "Pending":
                creation_time = pod.get("metadata", {}).get("creationTimestamp", "")
                if creation_time:
                    # For demo purposes, consider pending > 30 seconds as an issue
                    try:
                        from datetime import datetime, timezone
                        import dateutil.parser
                        
                        created = dateutil.parser.parse(creation_time)
                        now = datetime.now(timezone.utc)
                        age_seconds = (now - created).total_seconds()
                        
                        if age_seconds > 30:  # 30 seconds threshold for demo
                            issues.append({
                                "type": "pod_stuck",
                                "severity": "medium",
                                "resource": f"{namespace}/{pod_name}",
                                "reason": "PodStuckPending",
                                "message": f"Pod pending for {int(age_seconds)} seconds",
                                "phase": phase
                            })
                    except Exception:
                        pass  # Skip timestamp parsing errors
        
        return issues
    
    async def analyze_node_issues(self, node_items):
        """Analyze nodes for health issues."""
        issues = []
        
        for node in node_items:
            node_name = node.get("metadata", {}).get("name", "unknown")
            conditions = node.get("status", {}).get("conditions", [])
            
            # Check node conditions
            for condition in conditions:
                condition_type = condition.get("type", "")
                status = condition.get("status", "")
                reason = condition.get("reason", "")
                message = condition.get("message", "")
                
                # Check for problematic conditions
                if condition_type == "Ready" and status != "True":
                    issues.append({
                        "type": "node_not_ready",
                        "severity": "critical",
                        "resource": node_name,
                        "reason": reason,
                        "message": message
                    })
                elif condition_type in ["MemoryPressure", "DiskPressure", "PIDPressure"] and status == "True":
                    issues.append({
                        "type": "node_pressure",
                        "severity": "high" if condition_type == "MemoryPressure" else "medium",
                        "resource": node_name,
                        "condition": condition_type,
                        "reason": reason,
                        "message": message
                    })
        
        return issues
    
    async def analyze_cluster_events(self):
        """Analyze recent cluster events for warnings and errors."""
        try:
            events_result = await self.kubectl.get_events()
            if not events_result or "items" not in events_result:
                return []
            
            issues = []
            event_items = events_result.get("items", [])
            
            for event in event_items[-20:]:  # Check last 20 events
                event_type = event.get("type", "")
                reason = event.get("reason", "")
                message = event.get("message", "")
                involved_object = event.get("involvedObject", {})
                namespace = involved_object.get("namespace", "default")
                name = involved_object.get("name", "unknown")
                kind = involved_object.get("kind", "unknown")
                
                # Look for warning/error events
                if event_type == "Warning" and reason in [
                    "Failed", "Unhealthy", "BackOff", "FailedMount", 
                    "FailedAttachVolume", "FailedScheduling"
                ]:
                    issues.append({
                        "type": "cluster_event",
                        "severity": "medium",
                        "resource": f"{namespace}/{name}",
                        "kind": kind,
                        "reason": reason,
                        "message": message
                    })
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Failed to analyze events: {e}")
            return []
    
    async def get_enhanced_cluster_health(self):
        """Get comprehensive cluster health information with issue detection."""
        try:
            # Get nodes
            nodes_result = await self.kubectl.get_nodes()
            
            # Check if we got valid nodes data
            if not nodes_result or not isinstance(nodes_result, dict) or "items" not in nodes_result:
                return {
                    "healthy": False,
                    "error": "Failed to get nodes: Invalid response format",
                    "nodes_ready": 0,
                    "nodes_total": 0,
                    "pods_running": 0,
                    "pods_total": 0,
                    "issues": []
                }
            
            # Count ready nodes  
            node_items = nodes_result.get("items", [])
            nodes_total = len(node_items)
            nodes_ready = 0
            
            for node in node_items:
                conditions = node.get("status", {}).get("conditions", [])
                is_ready = any(
                    condition.get("type") == "Ready" and condition.get("status") == "True"
                    for condition in conditions
                )
                if is_ready:
                    nodes_ready += 1
            
            # Get pods
            pods_result = await self.kubectl.get_all_pods()
            if not pods_result or not isinstance(pods_result, dict) or "items" not in pods_result:
                return {
                    "healthy": False,
                    "error": "Failed to get pods: Invalid response format",
                    "nodes_ready": nodes_ready,
                    "nodes_total": nodes_total,
                    "pods_running": 0,
                    "pods_total": 0,
                    "issues": []
                }
            
            # Count pod states
            pod_items = pods_result.get("items", [])
            pods_total = len(pod_items)
            pods_running = 0
            pods_failed = 0
            pods_pending = 0
            
            for pod in pod_items:
                phase = pod.get("status", {}).get("phase", "Unknown")
                if phase == "Running":
                    pods_running += 1
                elif phase == "Failed":
                    pods_failed += 1
                elif phase == "Pending":
                    pods_pending += 1
            
            # Perform comprehensive issue analysis
            all_issues = []
            
            # Analyze pod issues
            pod_issues = await self.analyze_pod_issues(pod_items)
            all_issues.extend(pod_issues)
            
            # Analyze node issues
            node_issues = await self.analyze_node_issues(node_items)
            all_issues.extend(node_issues)
            
            # Analyze cluster events
            event_issues = await self.analyze_cluster_events()
            all_issues.extend(event_issues)
            
            # Determine overall health based on issues
            critical_issues = [i for i in all_issues if i.get("severity") == "critical"]
            high_issues = [i for i in all_issues if i.get("severity") == "high"]
            
            # Basic health: nodes ready and no failed pods
            basic_healthy = (nodes_ready == nodes_total and nodes_ready > 0 and pods_failed == 0)
            
            # Enhanced health: basic health + no critical/high severity issues
            enhanced_healthy = basic_healthy and len(critical_issues) == 0 and len(high_issues) == 0
            
            return {
                "healthy": enhanced_healthy,
                "basic_healthy": basic_healthy,
                "nodes_ready": nodes_ready,
                "nodes_total": nodes_total,
                "pods_running": pods_running,
                "pods_failed": pods_failed,
                "pods_pending": pods_pending,
                "pods_total": pods_total,
                "issues": all_issues,
                "critical_issues": len(critical_issues),
                "high_issues": len(high_issues),
                "total_issues": len(all_issues)
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "nodes_ready": 0,
                "nodes_total": 0,
                "pods_running": 0,
                "pods_total": 0,
                "issues": []
            }
    
    async def trigger_investigation(self, health_data):
        """Trigger autonomous investigation when issues are detected."""
        if self.investigation_in_progress:
            print(f"🔍 Investigation already in progress, skipping...")
            return
        
        issues = health_data.get("issues", [])
        if not issues:
            return
        
        # Prevent investigation spam - wait at least 30 seconds between investigations
        if self.last_investigation_time:
            time_since_last = (datetime.now() - self.last_investigation_time).total_seconds()
            if time_since_last < 30:
                return
        
        print(f"\n🚨 ISSUES DETECTED! Triggering autonomous investigation...")
        print(f"   📊 {len(issues)} total issues found:")
        
        # Show top 3 most severe issues
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_issues = sorted(issues, key=lambda x: severity_order.get(x.get("severity", "low"), 3))
        
        issues_summary = []
        for i, issue in enumerate(sorted_issues[:3]):
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(issue.get("severity", "low"), "⚪")
            issue_text = f"{issue.get('reason', 'Unknown')}: {issue.get('resource', 'Unknown resource')}"
            print(f"   {severity_icon} {issue_text}")
            issues_summary.append(issue_text)
        
        if len(issues) > 3:
            print(f"   ... and {len(issues) - 3} more issues")
        
        # Stream to backend
        if self.streamer:
            await self.streamer.log_issues_detected(len(issues), issues_summary)
        
        # Check if auto-investigation is enabled
        if not self.auto_investigate:
            print(f"🔍 Auto-investigation disabled - only monitoring")
            return
        
        print(f"\n🤖 Starting {'SAFE' if self.safe_mode else 'FULL'} investigation...")
        
        # Mark investigation as in progress
        self.investigation_in_progress = True
        self.last_investigation_time = datetime.now()
        
        try:
            # Run SAFE deterministic investigation (no AI API calls)
            if self.safe_mode:
                print("🛡️  Using deterministic investigator (no API costs)")
                investigator = DeterministicInvestigator()
            else:
                print("⚠️  Full mode: Could use AI investigator (may cost credits)")
                # For now, still use deterministic even in full mode for safety
                investigator = DeterministicInvestigator()
            
            # Create timestamp for report filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"/root/reports/autonomous_report_{timestamp}.txt"
            
            print(f"📝 Investigation results will be saved to: {report_filename}")
            
            # Stream investigation start
            if self.streamer:
                await self.streamer.log_investigation_start(report_filename)
            
            # Run investigation
            await investigator._investigate()
            
            if hasattr(investigator, 'report_data'):
                # Save report to file
                report_content = self.format_investigation_report(investigator.report_data, issues)
                
                with open(report_filename, 'w') as f:
                    f.write(report_content)
                
                print(f"✅ Investigation complete! Report saved to {report_filename}")
                findings_count = len(investigator.report_data.get('findings', []))
                print(f"📋 Summary: {findings_count} findings identified")
                
                # Stream investigation completion
                if self.streamer:
                    await self.streamer.log_investigation_complete(True, findings_count)
            else:
                print(f"❌ Investigation failed or incomplete")
                
                # Stream investigation failure
                if self.streamer:
                    await self.streamer.log_investigation_complete(False)
                
        except Exception as e:
            print(f"❌ Investigation error: {e}")
            self.logger.error(f"Investigation failed: {e}")
        finally:
            # Reset investigation flag
            self.investigation_in_progress = False
            print(f"🔄 Resuming health monitoring...\n")
    
    def format_investigation_report(self, report_data, issues):
        """Format investigation report for file output."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
🤖 AUTONOMOUS KUBERNETES INVESTIGATION REPORT
Generated: {timestamp}
==========================================

TRIGGER ISSUES DETECTED:
{'-' * 25}
"""
        
        for issue in issues:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(issue.get("severity", "low"), "⚪")
            report += f"{severity_icon} {issue.get('severity', 'unknown').upper()}: {issue.get('reason', 'Unknown')}\n"
            report += f"   Resource: {issue.get('resource', 'Unknown')}\n"
            if issue.get('message'):
                report += f"   Details: {issue.get('message')}\n"
            report += "\n"
        
        report += f"""
INVESTIGATION FINDINGS:
{'-' * 23}
"""
        
        findings = report_data.get('findings', [])
        for finding in findings:
            report += f"• {finding.get('title', 'Unknown Finding')}\n"
            if finding.get('description'):
                report += f"  {finding.get('description')}\n"
            report += "\n"
        
        if report_data.get('recommendations'):
            report += f"""
RECOMMENDATIONS:
{'-' * 16}
"""
            for rec in report_data.get('recommendations', []):
                report += f"• {rec}\n"
        
        report += f"""
==========================================
End of Report
"""
        return report
    
    def format_health_status(self, health_data):
        """Format health data for terminal display with enhanced issue information."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if health_data.get("error"):
            return f"❌ [{timestamp}] Health check failed: {health_data['error']}"
        
        nodes_status = f"{health_data['nodes_ready']}/{health_data['nodes_total']}"
        pods_status = f"{health_data['pods_running']} running"
        
        if health_data.get('pods_failed', 0) > 0:
            pods_status += f", {health_data['pods_failed']} failed"
        if health_data.get('pods_pending', 0) > 0:
            pods_status += f", {health_data['pods_pending']} pending"
        
        # Enhanced status with issue detection
        total_issues = health_data.get('total_issues', 0)
        critical_issues = health_data.get('critical_issues', 0)
        high_issues = health_data.get('high_issues', 0)
        
        if health_data.get("healthy", False):
            icon = "✅"
            status = "Cluster healthy"
        elif critical_issues > 0:
            icon = "🔴"
            status = f"CRITICAL issues detected ({critical_issues} critical)"
        elif high_issues > 0:
            icon = "🟠"
            status = f"HIGH severity issues detected ({high_issues} high)"
        elif total_issues > 0:
            icon = "🟡"
            status = f"Issues detected ({total_issues} total)"
        else:
            icon = "⚠️ "
            status = "Cluster issues detected"
        
        base_msg = f"{icon} [{timestamp}] {status} - {nodes_status} nodes, {pods_status}"
        
        # Add investigation status
        if self.investigation_in_progress:
            base_msg += " | 🔍 Investigation in progress..."
        
        return base_msg
    
    async def health_check_loop(self):
        """Enhanced health check loop with issue detection and autonomous investigation."""
        print(f"🔄 Starting enhanced health check loop (every {self.check_interval} second(s))")
        print("   🔍 Automatic investigation triggers on issues detected")
        print("   Press Ctrl+C to stop monitoring")
        print()
        
        while self.running:
            try:
                # Get comprehensive cluster health
                health_data = await self.get_enhanced_cluster_health()
                
                # Display status
                status_message = self.format_health_status(health_data)
                print(status_message)
                
                # Stream status to backend
                if self.streamer:
                    await self.streamer.log_health_status(health_data, status_message)
                
                # Check if investigation should be triggered
                if not health_data.get("healthy", False) and health_data.get("issues"):
                    await self.trigger_investigation(health_data)
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Health check loop error: {e}")
                print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Monitor error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def start_monitoring(self):
        """Start the autonomous monitoring with enhanced issue detection."""
        print("🚀 Autonomous Kubernetes Monitor - Chunk 2")
        print("=" * 50)
        print(f"⏱️  Health check interval: {self.check_interval} second(s)")
        print("🎯 Chunk 2: Enhanced issue detection & autonomous investigation")
        print("🔍 Features: Pod issues, Node health, Events analysis, Auto-investigation")
        print()
        
        # Validate environment first
        print("🔧 Validating environment...")
        try:
            health_data = await self.get_enhanced_cluster_health()
            if health_data.get("error"):
                print(f"❌ Environment validation failed: {health_data['error']}")
                return False
            else:
                print(f"✅ Environment validated - {health_data['nodes_total']} nodes, {health_data['pods_total']} pods found")
                if health_data.get('total_issues', 0) > 0:
                    print(f"⚠️  {health_data['total_issues']} existing issues detected during startup")
                print()
        except Exception as e:
            print(f"❌ Environment validation failed: {e}")
            return False
        
        # Initialize streamer
        try:
            self.streamer = AutonomousMonitorStreamer(backend_url=self.backend_url)
            await self.streamer.__aenter__()
            print(f"✅ Log streaming initialized (backend: {self.backend_url})")
        except Exception as e:
            print(f"⚠️  Log streaming not available: {e}")
            self.streamer = None
        
        # Start monitoring
        self.running = True
        await self.health_check_loop()
        
        # Cleanup streamer
        if self.streamer:
            await self.streamer.__aexit__(None, None, None)
        
        print("\n🛑 Monitoring stopped")
        return True


async def main():
    """Main function."""
    monitor = AutonomousMonitor()
    await monitor.start_monitoring()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)
