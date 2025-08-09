#!/usr/bin/env python3
"""
Demo script for Kubernetes Investigation Agents.

This script demonstrates both deterministic and agentic investigation 
approaches for hackathon presentation.
"""
import asyncio
import sys
import os
import json
from datetime import datetime

# Add the api directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.deterministic_investigator import run_deterministic_investigation
from agents.agentic_investigator import run_agentic_investigation


def print_banner():
    """Print demo banner."""
    print("""
🚀 KUBERNETES AGENTIC INVESTIGATION DEMO
========================================

Two AI-Powered Investigation Approaches:
1. 📊 Deterministic Agent - Follows predefined investigation steps
2. 🤖 Agentic Agent - AI autonomously decides investigation approach

Both agents provide comprehensive cluster analysis and recommendations.
""")


def print_separator(title):
    """Print section separator."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_findings_summary(report, agent_type):
    """Print a summary of investigation findings."""
    print(f"\n📋 {agent_type} Investigation Results:")
    print("-" * 40)
    
    # Basic stats
    findings = report.get('findings', [])
    duration = report.get('duration_seconds', 0)
    
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print(f"🔍 Total findings: {len(findings)}")
    
    # Severity breakdown
    severity_counts = report.get('findings_summary', {}).get('by_severity', {})
    if severity_counts:
        print("🎯 Issue severity:")
        for severity, count in severity_counts.items():
            if count > 0:
                emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "ℹ️", "info": "💡"}.get(severity, "📌")
                print(f"   {emoji} {severity.capitalize()}: {count}")
    
    # Cluster summary
    cluster_summary = report.get('cluster_summary', {})
    if cluster_summary:
        print("🏗️  Cluster overview:")
        print(f"   Nodes: {cluster_summary.get('total_nodes', 0)}")
        print(f"   Pods: {cluster_summary.get('total_pods', 0)} (Failed: {cluster_summary.get('failed_pods', 0)})")
        print(f"   Deployments: {cluster_summary.get('total_deployments', 0)}")
        print(f"   Services: {cluster_summary.get('total_services', 0)}")
    
    # Agent-specific info
    if agent_type == "Agentic":
        agentic_meta = report.get('agentic_metadata', {})
        if agentic_meta:
            print("🤖 AI agent stats:")
            print(f"   Decisions made: {agentic_meta.get('decisions_made', 0)}")
            print(f"   Tools used: {agentic_meta.get('tools_used', 0)}")
            print(f"   Investigation depth: {agentic_meta.get('investigation_depth', 'unknown')}")
    
    # Top findings
    if findings:
        print("🔍 Key findings:")
        critical_high = [f for f in findings if f.get('severity') in ['critical', 'high']]
        for finding in critical_high[:3]:  # Show top 3 critical/high issues
            severity_emoji = {"critical": "🚨", "high": "⚠️"}.get(finding.get('severity', ''), "📌")
            print(f"   {severity_emoji} {finding.get('title', 'Unknown issue')}")
    
    # Executive summary
    exec_summary = report.get('executive_summary', '')
    if exec_summary:
        print("📊 Executive summary:")
        # Extract the key health status line
        lines = exec_summary.split('\n')
        for line in lines:
            if any(status in line.upper() for status in ['HEALTHY', 'CRITICAL', 'ISSUES']):
                print(f"   {line.strip()}")
                break


async def demo_deterministic_investigation():
    """Demo the deterministic investigation agent."""
    print_separator("DETERMINISTIC INVESTIGATION AGENT")
    
    print("📊 The Deterministic Agent follows a predefined investigation methodology:")
    print("   1. Cluster overview and basic health checks")
    print("   2. Node analysis and resource availability")
    print("   3. Pod status analysis across all namespaces")
    print("   4. Resource utilization monitoring")
    print("   5. Event analysis for issues and warnings")
    print("   6. AI-powered issue detection (k8sgpt)")
    print("   7. Workload analysis (deployments, services)")
    print("   8. Network configuration review")
    print("   9. Comprehensive report generation")
    
    print("\n🚀 Starting deterministic investigation...")
    
    try:
        start_time = datetime.now()
        report = await run_deterministic_investigation(
            namespace=None,
            include_k8sgpt=True,
            include_events=True,
            timeout=120
        )
        
        print_findings_summary(report, "Deterministic")
        
        return report
        
    except Exception as e:
        print(f"❌ Deterministic investigation failed: {e}")
        return None


async def demo_agentic_investigation():
    """Demo the agentic investigation agent."""
    print_separator("AGENTIC INVESTIGATION AGENT")
    
    print("🤖 The Agentic Agent uses AI to autonomously decide investigation approach:")
    print("   • AI analyzes initial cluster state")
    print("   • Dynamically selects appropriate investigation tools")
    print("   • Adapts investigation based on findings")
    print("   • Makes intelligent decisions about next steps")
    print("   • Provides AI-powered analysis and insights")
    
    print("\n🧠 AI agent available tools:")
    tools = [
        "get_cluster_overview", "analyze_pods", "analyze_nodes",
        "get_resource_metrics", "analyze_events", "run_k8sgpt_analysis",
        "analyze_workloads", "investigate_specific_resource", "check_network_policies"
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool}")
    
    print("\n🚀 Starting AI-driven investigation...")
    
    try:
        start_time = datetime.now()
        report = await run_agentic_investigation(
            namespace=None,
            include_k8sgpt=True,
            include_events=True,
            timeout=120
        )
        
        print_findings_summary(report, "Agentic")
        
        return report
        
    except Exception as e:
        print(f"❌ Agentic investigation failed: {e}")
        return None


def compare_approaches(det_report, agentic_report):
    """Compare the two investigation approaches."""
    print_separator("COMPARISON OF APPROACHES")
    
    if not det_report or not agentic_report:
        print("⚠️  Cannot compare - one or both investigations failed")
        return
    
    print("📊 Investigation Comparison:")
    print("-" * 30)
    
    # Findings comparison
    det_findings = len(det_report.get('findings', []))
    agentic_findings = len(agentic_report.get('findings', []))
    
    print(f"🔍 Findings discovered:")
    print(f"   Deterministic: {det_findings}")
    print(f"   Agentic: {agentic_findings}")
    
    # Duration comparison
    det_duration = det_report.get('duration_seconds', 0)
    agentic_duration = agentic_report.get('duration_seconds', 0)
    
    print(f"⏱️  Investigation time:")
    print(f"   Deterministic: {det_duration:.2f} seconds")
    print(f"   Agentic: {agentic_duration:.2f} seconds")
    
    # Approach differences
    print(f"🎯 Key differences:")
    print(f"   Deterministic: Systematic, step-by-step, predictable")
    print(f"   Agentic: Adaptive, AI-driven, context-aware")
    
    # Agentic-specific insights
    agentic_meta = agentic_report.get('agentic_metadata', {})
    if agentic_meta:
        print(f"🤖 AI agent insights:")
        print(f"   Autonomous decisions: {agentic_meta.get('decisions_made', 0)}")
        print(f"   Tools dynamically selected: {agentic_meta.get('tools_used', 0)}")
        print(f"   Investigation adaptability: {agentic_meta.get('investigation_depth', 'unknown')}")
    
    print("\n💡 Use Cases:")
    print("   📊 Deterministic: Testing, validation, consistent monitoring")
    print("   🤖 Agentic: Complex issues, adaptive analysis, intelligent troubleshooting")


def save_demo_outputs(det_report, agentic_report):
    """Save demo outputs for later review."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print_separator("DEMO OUTPUTS")
    
    if det_report:
        det_file = f"demo_deterministic_{timestamp}.json"
        try:
            with open(det_file, 'w') as f:
                json.dump(det_report, f, indent=2)
            print(f"📄 Deterministic report saved: {det_file}")
        except Exception as e:
            print(f"❌ Failed to save deterministic report: {e}")
    
    if agentic_report:
        agentic_file = f"demo_agentic_{timestamp}.json"
        try:
            with open(agentic_file, 'w') as f:
                json.dump(agentic_report, f, indent=2)
            print(f"📄 Agentic report saved: {agentic_file}")
        except Exception as e:
            print(f"❌ Failed to save agentic report: {e}")


async def main():
    """Main demo function."""
    print_banner()
    
    print("🎬 Demo Overview:")
    print("   1. Demonstrate deterministic investigation approach")
    print("   2. Demonstrate AI-driven agentic investigation approach")
    print("   3. Compare results and methodologies")
    print("   4. Show practical applications")
    
    input("\n Press Enter to start the demo...")
    
    # Demo deterministic approach
    det_report = await demo_deterministic_investigation()
    
    input("\n Press Enter to continue to agentic demo...")
    
    # Demo agentic approach
    agentic_report = await demo_agentic_investigation()
    
    input("\n Press Enter to see comparison...")
    
    # Compare approaches
    compare_approaches(det_report, agentic_report)
    
    # Save outputs
    save_demo_outputs(det_report, agentic_report)
    
    print_separator("DEMO COMPLETE")
    print("🎉 Kubernetes Agentic Investigation Demo Complete!")
    print("\n✨ Key Takeaways:")
    print("   • Both agents provide comprehensive cluster analysis")
    print("   • Deterministic approach ensures consistent, repeatable investigations")
    print("   • Agentic approach provides intelligent, adaptive investigation")
    print("   • AI-powered insights enhance traditional DevOps workflows")
    print("   • Ready for production deployment in containerized environments")
    
    print("\n🚀 Next Steps:")
    print("   • Deploy in production Kubernetes environments")
    print("   • Integrate with monitoring and alerting systems")
    print("   • Extend with custom investigation tools")
    print("   • Scale across multiple clusters")


if __name__ == "__main__":
    asyncio.run(main())
