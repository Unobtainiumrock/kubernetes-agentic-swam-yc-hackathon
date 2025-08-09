"""
Integration Example: How to use MorphLLM Bridge with Google ADK Agents

This example shows how your existing agents in google-adk/ can use MorphLLM tools
without any changes to their existing code structure.
"""

import sys
import os
from pathlib import Path

# Add google-adk to path for importing
google_adk_path = Path(__file__).parent.parent / "google-adk" / "src"
sys.path.insert(0, str(google_adk_path))

from adk_agent.agents.core_agent import create_core_agent
from adk_agent.config.loader import load_runtime_config

# Import our MorphLLM bridge
from agent_bridge import morph_bridge

class KubernetesAwareAgent:
    """
    Example of how to extend your existing Google ADK agents with MorphLLM capabilities
    This doesn't change the core agent, just adds MorphLLM tools as an optional enhancement
    """
    
    def __init__(self, config_path: str):
        # Initialize your existing Google ADK agent
        self.config = load_runtime_config(config_path)
        self.core_agent = create_core_agent(self.config)
        
        # Add MorphLLM bridge for enhanced capabilities
        self.morph_bridge = morph_bridge
        
        # Get available tools for the agent
        self.available_tools = self.morph_bridge.get_kubernetes_tools_for_agent()
        
    def run_with_k8s_tools(self, system_prompt: str, user_input: str) -> str:
        """
        Enhanced run method that includes MorphLLM tools in the system prompt
        Your existing agents can call this method for Kubernetes-aware responses
        """
        
        # Enhance system prompt with available tools
        enhanced_system_prompt = f"""
{system_prompt}

You have access to the following MorphLLM tools for Kubernetes diagnosis and repair:

{self._format_tools_for_prompt()}

When you need to diagnose or fix Kubernetes issues, you can use these tools.
For example:
- To diagnose a pod issue: Call diagnose_k8s_issue with pod_name
- To fix an issue: Call fix_k8s_issue with issue_type and pod_name
- To read configuration files: Call read_file with the file path
- To search for patterns: Call grep_search or codebase_search
"""
        
        # Use your existing core agent
        response = self.core_agent.run(enhanced_system_prompt, user_input)
        
        # Parse response for tool calls and execute them
        enhanced_response = self._process_tool_calls(response)
        
        return enhanced_response
    
    def diagnose_cluster_issues(self) -> dict:
        """
        High-level method that uses MorphLLM to diagnose all cluster issues
        Your agents can call this directly without worrying about the implementation
        """
        print("🔍 Starting comprehensive cluster diagnosis with MorphLLM...")
        
        # Use MorphLLM bridge to diagnose common issues
        diagnosis_results = {}
        
        # Check for common problematic pods
        problematic_pods = ["broken-image-app", "crash-loop-app"]
        
        for pod_pattern in problematic_pods:
            print(f"\n📋 Checking for pods matching pattern: {pod_pattern}")
            
            # Use MorphLLM to search for and diagnose issues
            diagnosis = self.morph_bridge.diagnose_kubernetes_issue(
                pod_name=pod_pattern,
                namespace="frontend"  # Your demo apps are in frontend namespace
            )
            
            diagnosis_results[pod_pattern] = diagnosis
        
        return diagnosis_results
    
    def auto_fix_issues(self, diagnosis_results: dict) -> dict:
        """
        Automatically fix issues found during diagnosis
        """
        print("🔧 Starting automated issue fixing with MorphLLM...")
        
        fix_results = {}
        
        for pod_name, diagnosis in diagnosis_results.items():
            if diagnosis.get("diagnosis", {}).get("issue_type") != "Unknown":
                issue_type = diagnosis["diagnosis"]["issue_type"]
                
                print(f"\n🎯 Fixing {issue_type} for {pod_name}")
                
                fix_result = self.morph_bridge.fix_kubernetes_issue(
                    issue_type=issue_type,
                    pod_name=pod_name,
                    namespace="frontend"
                )
                
                fix_results[pod_name] = fix_result
        
        return fix_results
    
    def _format_tools_for_prompt(self) -> str:
        """Format available tools for inclusion in system prompt"""
        tools_text = ""
        for tool in self.available_tools:
            tools_text += f"- {tool['name']}: {tool['description']}\n"
        return tools_text
    
    def _process_tool_calls(self, response: str) -> str:
        """
        Process any tool calls in the agent response
        This is a simplified version - in production you'd parse JSON tool calls
        """
        
        # Simple keyword detection for demo
        if "diagnose_k8s_issue" in response.lower():
            print("🔍 Agent requested Kubernetes diagnosis")
            # In production, you'd parse the actual tool call parameters
            
        if "fix_k8s_issue" in response.lower():
            print("🔧 Agent requested Kubernetes fix")
            # In production, you'd parse the actual tool call parameters
        
        return response

def demo_integration():
    """
    Demonstrate how the integration works with your existing Google ADK setup
    """
    print("=" * 60)
    print("🚀 MorphLLM + Google ADK Integration Demo")
    print("=" * 60)
    
    # Path to your existing Google ADK config
    config_path = "../google-adk/src/adk_agent/config/runtime.yaml"
    
    try:
        # Create enhanced agent that combines Google ADK + MorphLLM
        agent = KubernetesAwareAgent(config_path)
        
        print("\n✅ Successfully created Kubernetes-aware agent!")
        print(f"📊 Available tools: {len(agent.available_tools)}")
        
        # Demo 1: Comprehensive cluster diagnosis
        print("\n" + "="*40)
        print("📋 Demo 1: Cluster Diagnosis")
        print("="*40)
        
        diagnosis_results = agent.diagnose_cluster_issues()
        
        print(f"\n📊 Diagnosis completed for {len(diagnosis_results)} pod patterns")
        for pod_name, result in diagnosis_results.items():
            issue_type = result.get("diagnosis", {}).get("issue_type", "Unknown")
            print(f"  • {pod_name}: {issue_type}")
        
        # Demo 2: Automated fixing
        print("\n" + "="*40)
        print("🔧 Demo 2: Automated Fixing")
        print("="*40)
        
        fix_results = agent.auto_fix_issues(diagnosis_results)
        
        print(f"\n🎯 Fix attempts completed for {len(fix_results)} issues")
        for pod_name, result in fix_results.items():
            success = result.get("success", False)
            actions = len(result.get("actions_taken", []))
            print(f"  • {pod_name}: {'✅ Fixed' if success else '❌ Failed'} ({actions} actions)")
        
        # Demo 3: Enhanced agent conversation
        print("\n" + "="*40)
        print("💬 Demo 3: Enhanced Agent Conversation")
        print("="*40)
        
        system_prompt = """
You are a Kubernetes operations assistant. You help diagnose and fix cluster issues.
You have access to MorphLLM tools for precise code analysis and editing.
"""
        
        user_input = "I have some failing pods in my cluster. Can you help diagnose and fix them?"
        
        print(f"User: {user_input}")
        print("Agent: Processing with MorphLLM-enhanced capabilities...")
        
        # This would use your existing Google ADK agent + MorphLLM tools
        response = agent.run_with_k8s_tools(system_prompt, user_input)
        print(f"Agent Response: {response[:200]}...")
        
        print("\n✅ Integration demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure your Google ADK environment is set up correctly")
        print("   Check OPENROUTER_API_KEY in your environment")

if __name__ == "__main__":
    demo_integration()
