#!/usr/bin/env python3
"""
Example usage of MorphLLM Kubernetes Agent

This demonstrates how the MorphLLM-powered agent can:
1. Detect failing pods in your Kind cluster
2. Use MorphLLM tools to analyze and fix issues
3. Apply precise edits to deployment configurations
4. Integrate with your existing Kubernetes setup
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kubernetes_agent import MorphKubernetesAgent, KubernetesIssue

async def demo_morph_kubernetes_integration():
    """
    Demonstrate MorphLLM integration with your Kubernetes agentic system
    """
    
    print("=" * 60)
    print("🚀 MorphLLM Kubernetes Agent Demo")
    print("=" * 60)
    print()
    
    # Initialize the agent
    agent = MorphKubernetesAgent()
    
    print("🔧 Agent initialized with MorphLLM tools:")
    for tool in agent.tools:
        print(f"  • {tool['name']}: {tool['description'][:50]}...")
    print()
    
    # Step 1: Diagnose cluster issues
    print("🔍 Step 1: Diagnosing cluster issues...")
    print("-" * 40)
    
    issues = await agent.diagnose_cluster()
    
    if not issues:
        print("✅ No issues detected in cluster!")
        return
    
    print(f"📊 Detected {len(issues)} issues:")
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. Pod: {issue.pod_name}")
        print(f"   Namespace: {issue.namespace}")
        print(f"   Issue: {issue.issue_type}")
        print(f"   Status: {issue.status}")
        print(f"   Description: {issue.description}")
        print(f"   Severity: {issue.severity}")
        if issue.suggested_fix:
            print(f"   💡 Suggested Fix: {issue.suggested_fix}")
    
    print()
    
    # Step 2: Apply fixes using MorphLLM tools
    print("🔧 Step 2: Applying fixes with MorphLLM...")
    print("-" * 40)
    
    fixed_count = 0
    for issue in issues:
        print(f"\n🛠️ Processing {issue.pod_name} ({issue.issue_type})...")
        
        # Show what MorphLLM tools would be used
        print("   MorphLLM workflow:")
        print("   1. 🔍 codebase_search - Find deployment files")
        print("   2. 📖 read_file - Analyze current configuration")
        print("   3. ✏️ edit_file - Apply precise fixes")
        print("   4. 🔄 Validate changes")
        
        success = await agent.apply_fix(issue)
        if success:
            fixed_count += 1
            print(f"   ✅ Successfully fixed {issue.pod_name}")
        else:
            print(f"   ❌ Could not fix {issue.pod_name}")
    
    print()
    print("=" * 60)
    print(f"🎯 Summary: Fixed {fixed_count}/{len(issues)} issues")
    print("=" * 60)
    
    # Step 3: Show integration benefits
    print("\n🌟 MorphLLM Integration Benefits:")
    print("  • Precise YAML edits without full file rewrites")
    print("  • Context-aware analysis of Kubernetes configurations")
    print("  • Pattern matching for similar issues across codebase")
    print("  • Automated fix generation and application")
    print("  • Integration with existing FastAPI backend")
    print("  • Real-time updates to frontend dashboard")
    
    print("\n🔗 Integration Points:")
    print("  • FastAPI backend: /api/morph/diagnose endpoint")
    print("  • WebSocket updates: Real-time fix progress")
    print("  • Frontend dashboard: Visual MorphLLM agent activity")
    print("  • k8sgpt integration: Enhanced AI diagnostics")

async def demo_specific_scenarios():
    """Demo specific scenarios that MorphLLM can handle"""
    
    print("\n" + "=" * 60)
    print("📋 MorphLLM Scenario Demonstrations")
    print("=" * 60)
    
    scenarios = [
        {
            "name": "ImagePullBackOff Fix",
            "description": "Agent detects broken-image-app with nonexistent tag",
            "morph_workflow": [
                "grep_search: Find 'ImagePullBackOff' patterns",
                "codebase_search: Locate deployment with broken image",
                "read_file: Analyze deploy-demo-apps.sh",
                "edit_file: Fix image tag to valid version",
                "Validate: Confirm pod starts successfully"
            ]
        },
        {
            "name": "CrashLoopBackOff Fix", 
            "description": "Agent fixes crash-loop-app that exits immediately",
            "morph_workflow": [
                "grep_search: Find 'exit 1' patterns in deployments",
                "read_file: Understand container command structure",
                "edit_file: Replace failing command with stable process",
                "Validate: Monitor pod restart count"
            ]
        },
        {
            "name": "Resource Optimization",
            "description": "Agent adjusts resource limits during pressure",
            "morph_workflow": [
                "codebase_search: Find resource limit configurations",
                "read_file: Analyze current resource allocations", 
                "edit_file: Increase memory/CPU limits surgically",
                "Validate: Monitor resource usage improvements"
            ]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   📝 {scenario['description']}")
        print("   🔄 MorphLLM Workflow:")
        for step in scenario['morph_workflow']:
            print(f"      • {step}")

def show_integration_architecture():
    """Show how MorphLLM integrates with existing system"""
    
    print("\n" + "=" * 60)
    print("🏗️ MorphLLM Integration Architecture")
    print("=" * 60)
    
    architecture = """
    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
    │   Kind Cluster  │    │  FastAPI Backend │    │   Frontend      │
    │                 │    │                  │    │   Dashboard     │
    │ • Demo Apps     │◄──►│ • Agent API      │◄──►│                 │
    │ • Failing Pods  │    │ • Google ADK     │    │ • Agent Status  │
    │ • k8sgpt-op     │    │ • MorphLLM Agent │    │ • Fix Progress  │
    └─────────────────┘    └──────────────────┘    └─────────────────┘
            ▲                        ▲                        ▲
            │                        │                        │
            ▼                        ▼                        ▼
    ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
    │ MorphLLM Tools  │    │   Integration    │    │   Real-time     │
    │                 │    │                  │    │   Updates       │
    │ • edit_file     │◄──►│ • Kubernetes API │◄──►│                 │
    │ • codebase_search│    │ • YAML Editing   │    │ • WebSockets    │
    │ • grep_search   │    │ • Pattern Match  │    │ • Live Logs     │
    │ • read_file     │    │ • Auto Fixes     │    │ • Fix Results   │
    └─────────────────┘    └──────────────────┘    └─────────────────┘
    """
    
    print(architecture)
    
    print("\n🔗 Data Flow:")
    print("1. Cluster issues detected → MorphLLM analysis")
    print("2. MorphLLM tools → Precise configuration fixes")
    print("3. Applied fixes → Kubernetes cluster updates")
    print("4. Results → Frontend dashboard display")
    print("5. User feedback → Agent learning and improvement")

async def main():
    """Main demo function"""
    
    # Check if we're in the right directory
    if not os.path.exists("../deploy-demo-apps.sh"):
        print("❌ Please run this from the morph/ directory in your Kubernetes project")
        return
    
    try:
        await demo_morph_kubernetes_integration()
        await demo_specific_scenarios()
        show_integration_architecture()
        
        print("\n🎯 Next Steps:")
        print("1. Set up MorphLLM API credentials")
        print("2. Integrate with existing FastAPI backend")
        print("3. Add WebSocket endpoints for real-time updates")
        print("4. Connect to frontend dashboard")
        print("5. Test with your failing pods (broken-image-app, crash-loop-app)")
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
