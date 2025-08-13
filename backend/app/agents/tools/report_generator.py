"""
Report generator for Kubernetes investigation findings.
"""
import json
import time
from datetime import datetime
from ...utils import now_local, format_timestamp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class InvestigationType(Enum):
    """Types of investigation approaches."""
    DETERMINISTIC = "deterministic"
    AGENTIC = "agentic"


@dataclass
class Finding:
    """Individual investigation finding."""
    category: str
    severity: Severity
    title: str
    description: str
    affected_resources: List[str]
    recommendations: List[str]
    evidence: List[str]
    timestamp: str
    source_tool: str  # kubectl, k8sgpt, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "category": self.category,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "affected_resources": self.affected_resources,
            "recommendations": self.recommendations,
            "evidence": self.evidence,
            "timestamp": self.timestamp,
            "source_tool": self.source_tool
        }


@dataclass
class InvestigationStep:
    """Individual investigation step record."""
    step_number: int
    action: str
    tool_used: str
    status: str  # completed, failed, skipped
    duration_seconds: float
    output_summary: str
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary."""
        return asdict(self)


@dataclass
class ClusterSummary:
    """Summary of cluster state."""
    total_nodes: int
    total_pods: int
    total_namespaces: int
    healthy_pods: int
    failed_pods: int
    pending_pods: int
    running_pods: int
    total_deployments: int
    total_services: int
    resource_utilization: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to dictionary."""
        return asdict(self)


class ReportGenerator:
    """Generate structured investigation reports."""
    
    def __init__(self):
        self.findings: List[Finding] = []
        self.investigation_steps: List[InvestigationStep] = []
        self.cluster_summary: Optional[ClusterSummary] = None
        self.investigation_type: Optional[InvestigationType] = None
        self.start_time: float = time.time()
        self.end_time: Optional[float] = None
        self.agent_metadata: Dict[str, Any] = {}
        
    def add_finding(self, 
                   category: str,
                   severity: Severity,
                   title: str,
                   description: str,
                   affected_resources: List[str],
                   recommendations: List[str],
                   evidence: List[str],
                   source_tool: str) -> None:
        """Add a new finding to the report."""
        finding = Finding(
            category=category,
            severity=severity,
            title=title,
            description=description,
            affected_resources=affected_resources,
            recommendations=recommendations,
            evidence=evidence,
            timestamp=format_timestamp(now_local()),
            source_tool=source_tool
        )
        self.findings.append(finding)
    
    def add_investigation_step(self,
                             step_number: int,
                             action: str,
                             tool_used: str,
                             status: str,
                             duration_seconds: float,
                             output_summary: str,
                             error_message: Optional[str] = None) -> None:
        """Add an investigation step to the report."""
        step = InvestigationStep(
            step_number=step_number,
            action=action,
            tool_used=tool_used,
            status=status,
            duration_seconds=duration_seconds,
            output_summary=output_summary,
            error_message=error_message
        )
        self.investigation_steps.append(step)
    
    def set_cluster_summary(self,
                          total_nodes: int,
                          total_pods: int,
                          total_namespaces: int,
                          healthy_pods: int,
                          failed_pods: int,
                          pending_pods: int,
                          running_pods: int,
                          total_deployments: int,
                          total_services: int,
                          resource_utilization: Dict[str, Any]) -> None:
        """Set cluster summary information."""
        self.cluster_summary = ClusterSummary(
            total_nodes=total_nodes,
            total_pods=total_pods,
            total_namespaces=total_namespaces,
            healthy_pods=healthy_pods,
            failed_pods=failed_pods,
            pending_pods=pending_pods,
            running_pods=running_pods,
            total_deployments=total_deployments,
            total_services=total_services,
            resource_utilization=resource_utilization
        )
    
    def set_investigation_type(self, investigation_type: InvestigationType) -> None:
        """Set the type of investigation."""
        self.investigation_type = investigation_type
    
    def set_agent_metadata(self, metadata: Dict[str, Any]) -> None:
        """Set metadata about the investigating agent."""
        self.agent_metadata = metadata
    
    def finalize_investigation(self) -> None:
        """Mark investigation as complete."""
        self.end_time = time.time()
    
    def get_investigation_duration(self) -> float:
        """Get total investigation duration in seconds."""
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def get_severity_counts(self) -> Dict[str, int]:
        """Get count of findings by severity."""
        counts = {severity.value: 0 for severity in Severity}
        for finding in self.findings:
            counts[finding.severity.value] += 1
        return counts
    
    def get_findings_by_category(self) -> Dict[str, List[Finding]]:
        """Group findings by category."""
        categories = {}
        for finding in self.findings:
            if finding.category not in categories:
                categories[finding.category] = []
            categories[finding.category].append(finding)
        return categories
    
    def get_critical_issues(self) -> List[Finding]:
        """Get only critical severity findings."""
        return [f for f in self.findings if f.severity == Severity.CRITICAL]
    
    def get_high_priority_issues(self) -> List[Finding]:
        """Get critical and high severity findings."""
        return [f for f in self.findings if f.severity in [Severity.CRITICAL, Severity.HIGH]]
    
    def generate_executive_summary(self) -> str:
        """Generate executive summary of investigation."""
        if not self.cluster_summary:
            return "Investigation completed but cluster summary unavailable."
        
        severity_counts = self.get_severity_counts()
        critical_count = severity_counts[Severity.CRITICAL.value]
        high_count = severity_counts[Severity.HIGH.value]
        
        total_issues = len(self.findings)
        
        if critical_count > 0:
            status = "CRITICAL ISSUES DETECTED"
        elif high_count > 0:
            status = "HIGH PRIORITY ISSUES DETECTED"
        elif total_issues > 0:
            status = "MINOR ISSUES DETECTED"
        else:
            status = "CLUSTER HEALTHY"
        
        summary = f"""
CLUSTER INVESTIGATION SUMMARY
{status}

Cluster Overview:
- Nodes: {self.cluster_summary.total_nodes}
- Pods: {self.cluster_summary.total_pods} (Running: {self.cluster_summary.running_pods}, Failed: {self.cluster_summary.failed_pods}, Pending: {self.cluster_summary.pending_pods})
- Namespaces: {self.cluster_summary.total_namespaces}
- Deployments: {self.cluster_summary.total_deployments}
- Services: {self.cluster_summary.total_services}

Issues Found:
- Critical: {critical_count}
- High: {high_count}
- Medium: {severity_counts[Severity.MEDIUM.value]}
- Low: {severity_counts[Severity.LOW.value]}
- Info: {severity_counts[Severity.INFO.value]}

Investigation Duration: {self.get_investigation_duration():.2f} seconds
Investigation Type: {self.investigation_type.value if self.investigation_type else 'Unknown'}
        """.strip()
        
        return summary
    
    def generate_json_report(self) -> Dict[str, Any]:
        """Generate complete investigation report in JSON format."""
        self.finalize_investigation()
        
        report = {
            "investigation_id": f"{self.investigation_type.value if self.investigation_type else 'unknown'}_{int(self.start_time)}",
            "timestamp": datetime.fromtimestamp(self.start_time).isoformat(),
            "investigation_type": self.investigation_type.value if self.investigation_type else "unknown",
            "duration_seconds": self.get_investigation_duration(),
            "agent_metadata": self.agent_metadata,
            "cluster_summary": self.cluster_summary.to_dict() if self.cluster_summary else {},
            "executive_summary": self.generate_executive_summary(),
            "findings": [finding.to_dict() for finding in self.findings],
            "findings_summary": {
                "total_count": len(self.findings),
                "by_severity": self.get_severity_counts(),
                "by_category": {cat: len(findings) for cat, findings in self.get_findings_by_category().items()}
            },
            "investigation_steps": [step.to_dict() for step in self.investigation_steps],
            "recommendations": self._generate_recommendations(),
            "next_actions": self._generate_next_actions()
        }
        
        return report
    
    def generate_text_report(self) -> str:
        """Generate human-readable text report."""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("KUBERNETES CLUSTER INVESTIGATION REPORT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Executive Summary
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 40)
        report_lines.append(self.generate_executive_summary())
        report_lines.append("")
        
        # Critical Issues
        critical_issues = self.get_critical_issues()
        if critical_issues:
            report_lines.append("🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION")
            report_lines.append("-" * 60)
            for issue in critical_issues:
                report_lines.append(f"• {issue.title}")
                report_lines.append(f"  Description: {issue.description}")
                report_lines.append(f"  Affected: {', '.join(issue.affected_resources)}")
                report_lines.append("")
        
        # High Priority Issues
        high_issues = [f for f in self.findings if f.severity == Severity.HIGH]
        if high_issues:
            report_lines.append("⚠️  HIGH PRIORITY ISSUES")
            report_lines.append("-" * 30)
            for issue in high_issues:
                report_lines.append(f"• {issue.title}")
                report_lines.append(f"  Description: {issue.description}")
                report_lines.append("")
        
        # All Findings by Category
        if self.findings:
            report_lines.append("ALL FINDINGS BY CATEGORY")
            report_lines.append("-" * 35)
            by_category = self.get_findings_by_category()
            for category, findings in by_category.items():
                report_lines.append(f"\n{category.upper()} ({len(findings)} issues):")
                for finding in findings:
                    report_lines.append(f"  [{finding.severity.value.upper()}] {finding.title}")
        
        # Investigation Steps
        if self.investigation_steps:
            report_lines.append("\nINVESTIGATION STEPS EXECUTED")
            report_lines.append("-" * 35)
            for step in self.investigation_steps:
                status_icon = "✅" if step.status == "completed" else "❌" if step.status == "failed" else "⏭️"
                report_lines.append(f"{status_icon} Step {step.step_number}: {step.action} ({step.duration_seconds:.2f}s)")
        
        # Recommendations
        recommendations = self._generate_recommendations()
        if recommendations:
            report_lines.append("\nRECOMMENDATIONS")
            report_lines.append("-" * 20)
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations based on findings."""
        recommendations = []
        
        # Critical issues first
        critical_issues = self.get_critical_issues()
        for issue in critical_issues:
            recommendations.extend(issue.recommendations)
        
        # High priority issues
        high_issues = [f for f in self.findings if f.severity == Severity.HIGH]
        for issue in high_issues:
            recommendations.extend(issue.recommendations)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]  # Top 10 recommendations
    
    def _generate_next_actions(self) -> List[str]:
        """Generate suggested next actions based on investigation."""
        actions = []
        
        critical_count = len(self.get_critical_issues())
        high_count = len([f for f in self.findings if f.severity == Severity.HIGH])
        
        if critical_count > 0:
            actions.append(f"Address {critical_count} critical issues immediately")
            actions.append("Set up continuous monitoring for critical components")
            actions.append("Prepare incident response plan")
        elif high_count > 0:
            actions.append(f"Schedule resolution of {high_count} high priority issues")
            actions.append("Review resource allocation and scaling policies")
        else:
            actions.append("Continue regular monitoring and maintenance")
            actions.append("Review and optimize resource utilization")
            actions.append("Update cluster documentation and runbooks")
        
        # Add tool-specific actions
        if any(step.tool_used == "k8sgpt" for step in self.investigation_steps):
            actions.append("Review k8sgpt analysis recommendations")
        
        return actions


def create_sample_report() -> ReportGenerator:
    """Create a sample report for testing."""
    generator = ReportGenerator()
    generator.set_investigation_type(InvestigationType.DETERMINISTIC)
    
    # Sample cluster summary
    generator.set_cluster_summary(
        total_nodes=3,
        total_pods=25,
        total_namespaces=6,
        healthy_pods=23,
        failed_pods=2,
        pending_pods=0,
        running_pods=23,
        total_deployments=8,
        total_services=12,
        resource_utilization={"cpu": 65, "memory": 70}
    )
    
    # Sample findings
    generator.add_finding(
        category="pod_failures",
        severity=Severity.HIGH,
        title="Failed pods detected",
        description="2 pods are in failed state due to image pull errors",
        affected_resources=["frontend-app-xyz", "backend-db-abc"],
        recommendations=["Update image pull secrets", "Verify registry connectivity"],
        evidence=["Pod status: Failed", "Event: ErrImagePull"],
        source_tool="kubectl"
    )
    
    return generator
