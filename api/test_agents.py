#!/usr/bin/env python3
"""
Test script for Kubernetes investigation agents.

This script tests both deterministic and agentic investigation agents
to ensure they work correctly in the containerized environment.
"""
import asyncio
import logging
import sys
import os
import json
from datetime import datetime

# Add the api directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.deterministic_investigator import DeterministicInvestigator, run_deterministic_investigation
from agents.agentic_investigator import AgenticInvestigator, run_agentic_investigation


async def test_deterministic_agent():
    """Test the deterministic investigation agent."""
    print("🧪 Testing Deterministic Investigation Agent")
    print("=" * 50)
    
    try:
        # Test using the convenience function
        print("📊 Running deterministic investigation...")
        
        start_time = datetime.now()
        report = await run_deterministic_investigation(
            namespace=None,  # Test all namespaces
            include_k8sgpt=True,
            include_events=True,
            timeout=60
        )
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Deterministic investigation completed in {duration:.2f} seconds")
        print(f"📋 Report ID: {report.get('investigation_id', 'N/A')}")
        print(f"🔍 Findings: {len(report.get('findings', []))}")
        print(f"📊 Investigation steps: {len(report.get('investigation_steps', []))}")
        
        # Show severity breakdown
        findings_summary = report.get('findings_summary', {})
        severity_counts = findings_summary.get('by_severity', {})
        
        if severity_counts:
            print("🎯 Severity breakdown:")
            for severity, count in severity_counts.items():
                if count > 0:
                    print(f"   {severity}: {count}")
        
        # Show executive summary
        exec_summary = report.get('executive_summary', '')
        if exec_summary:
            print("\n📋 Executive Summary:")
            print(exec_summary[:300] + "..." if len(exec_summary) > 300 else exec_summary)
        
        return True, report
        
    except Exception as e:
        print(f"❌ Deterministic investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def test_agentic_agent():
    """Test the agentic investigation agent."""
    print("\n🤖 Testing Agentic Investigation Agent")
    print("=" * 50)
    
    try:
        # Test using the convenience function
        print("🧠 Running AI-driven investigation...")
        
        start_time = datetime.now()
        report = await run_agentic_investigation(
            namespace=None,  # Test all namespaces
            include_k8sgpt=True,
            include_events=True,
            timeout=60
        )
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Agentic investigation completed in {duration:.2f} seconds")
        print(f"📋 Report ID: {report.get('investigation_id', 'N/A')}")
        print(f"🔍 Findings: {len(report.get('findings', []))}")
        
        # Show agentic-specific metadata
        agentic_metadata = report.get('agentic_metadata', {})
        if agentic_metadata:
            print("🤖 AI Agent Statistics:")
            print(f"   Decisions made: {agentic_metadata.get('decisions_made', 0)}")
            print(f"   Tools used: {agentic_metadata.get('tools_used', 0)}")
            print(f"   Investigation depth: {agentic_metadata.get('investigation_depth', 'unknown')}")
        
        # Show severity breakdown
        findings_summary = report.get('findings_summary', {})
        severity_counts = findings_summary.get('by_severity', {})
        
        if severity_counts:
            print("🎯 Severity breakdown:")
            for severity, count in severity_counts.items():
                if count > 0:
                    print(f"   {severity}: {count}")
        
        # Show executive summary
        exec_summary = report.get('executive_summary', '')
        if exec_summary:
            print("\n📋 Executive Summary:")
            print(exec_summary[:300] + "..." if len(exec_summary) > 300 else exec_summary)
        
        return True, report
        
    except Exception as e:
        print(f"❌ Agentic investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


async def compare_agents(det_report, agentic_report):
    """Compare the results from both agents."""
    print("\n🔄 Comparing Agent Results")
    print("=" * 50)
    
    if not det_report or not agentic_report:
        print("❌ Cannot compare - one or both investigations failed")
        return
    
    det_findings = len(det_report.get('findings', []))
    agentic_findings = len(agentic_report.get('findings', []))
    
    det_duration = det_report.get('duration_seconds', 0)
    agentic_duration = agentic_report.get('duration_seconds', 0)
    
    print(f"📊 Findings comparison:")
    print(f"   Deterministic: {det_findings} findings")
    print(f"   Agentic: {agentic_findings} findings")
    
    print(f"⏱️  Duration comparison:")
    print(f"   Deterministic: {det_duration:.2f} seconds")
    print(f"   Agentic: {agentic_duration:.2f} seconds")
    
    # Compare cluster summaries
    det_cluster = det_report.get('cluster_summary', {})
    agentic_cluster = agentic_report.get('cluster_summary', {})
    
    if det_cluster and agentic_cluster:
        print(f"🏗️  Cluster state comparison:")
        print(f"   Nodes: Det={det_cluster.get('total_nodes', 0)}, Agentic={agentic_cluster.get('total_nodes', 0)}")
        print(f"   Pods: Det={det_cluster.get('total_pods', 0)}, Agentic={agentic_cluster.get('total_pods', 0)}")
        print(f"   Failed pods: Det={det_cluster.get('failed_pods', 0)}, Agentic={agentic_cluster.get('failed_pods', 0)}")
    
    # Show unique aspects
    if agentic_report.get('agentic_metadata'):
        agentic_meta = agentic_report['agentic_metadata']
        print(f"🤖 Agentic-specific insights:")
        print(f"   AI decisions made: {agentic_meta.get('decisions_made', 0)}")
        print(f"   Investigation approach: {agentic_meta.get('investigation_depth', 'unknown')}")


async def test_tool_availability():
    """Test that all required tools are available."""
    print("🛠️  Testing Tool Availability")
    print("=" * 30)
    
    # Test kubectl
    try:
        from agents.tools.kubectl_wrapper import KubectlWrapper
        kubectl = KubectlWrapper()
        result = await kubectl.get_version()
        if result["success"]:
            print("✅ kubectl - Available")
        else:
            print(f"❌ kubectl - Error: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"❌ kubectl - Import/execution error: {e}")
    
    # Test k8sgpt
    try:
        from agents.tools.k8sgpt_wrapper import K8sgptWrapper
        k8sgpt = K8sgptWrapper()
        result = await k8sgpt.get_version()
        if result["success"]:
            print("✅ k8sgpt - Available")
        else:
            print(f"⚠️  k8sgpt - Not configured or unavailable")
    except Exception as e:
        print(f"❌ k8sgpt - Import/execution error: {e}")
    
    # Test Google ADK
    try:
        import sys
        sys.path.append('/Users/chalmers/code/kubernetes-agentic-swam-yc-hackathon/google-adk/src')
        from adk_agent.agents.core_agent import create_core_agent
        
        config = {"model": "openai/gpt-4o-mini", "provider": "openrouter"}
        agent = create_core_agent(config)
        print("✅ Google ADK - Available")
    except Exception as e:
        print(f"⚠️  Google ADK - Not available or misconfigured: {e}")


async def save_demo_reports(det_report, agentic_report):
    """Save reports for demo purposes."""
    print("\n💾 Saving Demo Reports")
    print("=" * 30)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save deterministic report
    if det_report:
        det_filename = f"demo_deterministic_report_{timestamp}.json"
        try:
            with open(det_filename, 'w') as f:
                json.dump(det_report, f, indent=2)
            print(f"✅ Deterministic report saved: {det_filename}")
        except Exception as e:
            print(f"❌ Failed to save deterministic report: {e}")
    
    # Save agentic report
    if agentic_report:
        agentic_filename = f"demo_agentic_report_{timestamp}.json"
        try:
            with open(agentic_filename, 'w') as f:
                json.dump(agentic_report, f, indent=2)
            print(f"✅ Agentic report saved: {agentic_filename}")
        except Exception as e:
            print(f"❌ Failed to save agentic report: {e}")


async def main():
    """Main test function."""
    print("🚀 Kubernetes Investigation Agents Test Suite")
    print("=" * 60)
    print(f"📅 Test started at: {datetime.now().isoformat()}")
    print()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test tool availability first
    await test_tool_availability()
    print()
    
    # Test deterministic agent
    det_success, det_report = await test_deterministic_agent()
    
    # Test agentic agent
    agentic_success, agentic_report = await test_agentic_agent()
    
    # Compare results
    if det_success and agentic_success:
        await compare_agents(det_report, agentic_report)
    
    # Save demo reports
    await save_demo_reports(det_report, agentic_report)
    
    # Summary
    print("\n🏁 Test Summary")
    print("=" * 20)
    print(f"✅ Deterministic Agent: {'PASSED' if det_success else 'FAILED'}")
    print(f"🤖 Agentic Agent: {'PASSED' if agentic_success else 'FAILED'}")
    
    if det_success and agentic_success:
        print("\n🎉 All tests passed! Agents are ready for demo.")
        
        # Quick demo commands
        print("\n📋 Demo Commands:")
        print("Deterministic investigation:")
        print("  curl -X POST http://localhost:8000/v1/investigate/deterministic -d '{\"investigation_type\":\"deterministic\"}'")
        print("\nAgentic investigation:")
        print("  curl -X POST http://localhost:8000/v1/investigate/agentic -d '{\"investigation_type\":\"agentic\"}'")
    else:
        print("\n⚠️  Some tests failed. Review errors above before demo.")
    
    print(f"\n📅 Test completed at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
