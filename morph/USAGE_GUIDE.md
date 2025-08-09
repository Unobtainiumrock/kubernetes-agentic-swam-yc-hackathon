# MorphLLM Integration Usage Guide for Google ADK Agents

This guide shows how your existing Google ADK agents can use MorphLLM tools for enhanced Kubernetes diagnosis and repair capabilities **without changing any code in `google-adk/`**.

## 🚀 Quick Start

### 1. Import the MorphLLM Bridge in Your Agent Code

```python
# In your agent code (outside of google-adk/)
import sys
from pathlib import Path

# Add morph to your path
morph_path = Path(__file__).parent / "morph"
sys.path.insert(0, str(morph_path))

from morph import morph_bridge
```

### 2. Use MorphLLM Tools in Your Existing Agents

```python
# Your existing Google ADK agent setup
from google_adk.agents.core_agent import create_core_agent
from google_adk.config.loader import load_runtime_config

# Enhanced with MorphLLM
from morph import morph_bridge

class EnhancedKubernetesAgent:
    def __init__(self, config_path):
        # Your existing agent setup (unchanged)
        self.config = load_runtime_config(config_path)
        self.core_agent = create_core_agent(self.config)
        
        # Add MorphLLM capabilities
        self.morph = morph_bridge
    
    def diagnose_and_fix_cluster(self):
        """High-level method using MorphLLM tools"""
        
        # Diagnose issues
        diagnosis = self.morph.diagnose_kubernetes_issue(
            pod_name="broken-image-app",
            namespace="frontend"
        )
        
        # Fix issues automatically
        if diagnosis["diagnosis"]["issue_type"] != "Unknown":
            fix_result = self.morph.fix_kubernetes_issue(
                issue_type=diagnosis["diagnosis"]["issue_type"],
                pod_name="broken-image-app",
                namespace="frontend"
            )
            
        return {"diagnosis": diagnosis, "fix": fix_result}
```

## 🔧 Available MorphLLM Tools

### File Operations
```python
# Read any file in your project
content = morph_bridge.read_file(
    target_file="./deploy-demo-apps.sh",
    explanation="Reading deployment script to understand pod configuration"
)

# Edit files with precise changes
success = morph_bridge.edit_file(
    target_file="./deploy-demo-apps.sh", 
    edit_snippet="image: nginx:1.21  # Fixed from nginx:nonexistent-tag",
    explanation="Fixing ImagePullBackOff by correcting image tag"
)
```

### Code Analysis
```python
# Search your codebase for patterns
results = morph_bridge.search_codebase(
    query="kind: Deployment",
    explanation="Finding all Kubernetes deployment configurations"
)

# Fast grep search
matches = morph_bridge.grep_search(
    query="ImagePullBackOff|CrashLoopBackOff",
    explanation="Looking for failing pod patterns",
    include_pattern="*.yaml"
)
```

### Kubernetes-Specific Operations
```python
# High-level diagnosis
diagnosis = morph_bridge.diagnose_kubernetes_issue(
    pod_name="my-failing-pod",
    namespace="default"
)

# Automated fixing
fix_result = morph_bridge.fix_kubernetes_issue(
    issue_type="ImagePullBackOff",
    pod_name="broken-image-app", 
    namespace="frontend"
)
```

## 📋 Integration Patterns

### Pattern 1: Enhanced System Prompts

```python
def create_enhanced_system_prompt(base_prompt):
    tools_description = """
You have access to MorphLLM tools for Kubernetes operations:
- diagnose_k8s_issue: Analyze failing pods
- fix_k8s_issue: Automatically repair common issues  
- read_file: Examine configuration files
- edit_file: Make precise configuration changes
- search_codebase: Find relevant code patterns
"""
    return f"{base_prompt}\n\n{tools_description}"

# Use with your existing Google ADK agent
enhanced_prompt = create_enhanced_system_prompt(your_system_prompt)
response = core_agent.run(enhanced_prompt, user_input)
```

### Pattern 2: Tool-Calling Wrapper

```python
class ToolAwareAgent:
    def __init__(self, google_adk_agent):
        self.agent = google_adk_agent
        self.morph = morph_bridge
        
    def run_with_tools(self, system_prompt, user_input):
        # Get response from your Google ADK agent
        response = self.agent.run(system_prompt, user_input)
        
        # Parse for tool calls and execute them
        if "diagnose_k8s_issue" in response:
            diagnosis = self.morph.diagnose_kubernetes_issue("broken-image-app")
            response += f"\n\nDiagnosis Result: {diagnosis['diagnosis']['description']}"
            
        if "fix_k8s_issue" in response:
            fix = self.morph.fix_kubernetes_issue("ImagePullBackOff", "broken-image-app")
            response += f"\n\nFix Result: {'Success' if fix['success'] else 'Failed'}"
            
        return response
```

### Pattern 3: Autonomous Agent Loop

```python
def autonomous_cluster_management():
    """Fully autonomous cluster management using MorphLLM + Google ADK"""
    
    # Step 1: Diagnose all issues
    issues = []
    for pod in ["broken-image-app", "crash-loop-app"]:
        diagnosis = morph_bridge.diagnose_kubernetes_issue(pod, "frontend")
        if diagnosis["diagnosis"]["issue_type"] != "Unknown":
            issues.append(diagnosis)
    
    # Step 2: Use Google ADK agent to plan fixes
    issue_summary = "\n".join([f"- {i['pod_name']}: {i['diagnosis']['description']}" for i in issues])
    
    system_prompt = "You are a Kubernetes expert. Plan the best approach to fix these issues:"
    plan = core_agent.run(system_prompt, issue_summary)
    
    # Step 3: Execute fixes with MorphLLM
    for issue in issues:
        fix_result = morph_bridge.fix_kubernetes_issue(
            issue_type=issue["diagnosis"]["issue_type"],
            pod_name=issue["pod_name"],
            namespace="frontend"
        )
        print(f"Fixed {issue['pod_name']}: {fix_result['success']}")
```

## 🎯 Real-World Usage Examples

### Example 1: Fixing Your Demo Cluster Issues

```python
# This works with your existing broken-image-app and crash-loop-app
def fix_demo_cluster_issues():
    problems = [
        {"pod": "broken-image-app", "issue": "ImagePullBackOff"},
        {"pod": "crash-loop-app", "issue": "CrashLoopBackOff"}
    ]
    
    results = []
    for problem in problems:
        # Use MorphLLM to fix the issue
        result = morph_bridge.fix_kubernetes_issue(
            issue_type=problem["issue"],
            pod_name=problem["pod"],
            namespace="frontend"
        )
        results.append(result)
        
        # Redeploy after fix
        if result["success"]:
            os.system("./deploy-demo-apps.sh")
    
    return results
```

### Example 2: Integration with Your FastAPI Backend

```python
# In your api/app/routers/agent.py
from morph import morph_bridge

@router.post("/agent/diagnose")
async def diagnose_cluster():
    """API endpoint that uses MorphLLM for diagnosis"""
    
    diagnosis = morph_bridge.diagnose_kubernetes_issue(
        pod_name="broken-image-app",
        namespace="frontend"
    )
    
    return {
        "status": "success",
        "diagnosis": diagnosis,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/agent/fix")
async def fix_cluster_issue(issue_type: str, pod_name: str):
    """API endpoint that uses MorphLLM for automated fixes"""
    
    fix_result = morph_bridge.fix_kubernetes_issue(
        issue_type=issue_type,
        pod_name=pod_name,
        namespace="frontend"
    )
    
    return {
        "status": "success" if fix_result["success"] else "failed",
        "fix_result": fix_result,
        "timestamp": datetime.now().isoformat()
    }
```

## 🔒 Security and Configuration

### Environment Variables
```bash
# In your .env file
MORPH_API_KEY=your_morph_api_key_here
MORPH_BASE_URL=https://api.morphllm.com
MORPH_MODEL=claude-3-5-sonnet-20241022

# Optional: Override default paths
KUBERNETES_MANIFESTS_DIR=/path/to/your/manifests
AGENT_ACTIONS_DIR=/path/to/your/agent-actions
```

### Best Practices
1. **Always validate MorphLLM responses** before applying changes
2. **Use dry-run mode** when possible for testing
3. **Log all MorphLLM operations** for debugging
4. **Keep your Google ADK agents unchanged** - only add MorphLLM as enhancement
5. **Test fixes in development** before applying to production clusters

## 🚀 Getting Started Checklist

- [x] Run `./morph/setup.sh` to configure environment
- [x] Add your MorphLLM API key to `.env` file
- [ ] Test basic integration with `python morph/integration_example.py`
- [ ] Import `morph_bridge` in your agent code
- [ ] Start with simple file reading operations
- [ ] Progress to cluster diagnosis and fixing
- [ ] Integrate with your FastAPI backend
- [ ] Connect to your React frontend for real-time updates

## 📚 Next Steps

1. **Test the integration** with your existing failing pods
2. **Add MorphLLM endpoints** to your FastAPI backend
3. **Stream results** to your React frontend dashboard
4. **Implement automated workflows** that combine Google ADK planning with MorphLLM execution
5. **Add monitoring and logging** for production use

The MorphLLM bridge is designed to be **completely non-invasive** to your existing Google ADK setup while providing powerful new capabilities for Kubernetes management!
