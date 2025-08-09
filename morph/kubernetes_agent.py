"""
MorphLLM-powered Kubernetes Diagnostic and Repair Agent
"""

import asyncio
import json
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from config import morph_config

@dataclass
class KubernetesIssue:
    """Represents a detected Kubernetes issue"""
    pod_name: str
    namespace: str
    status: str
    issue_type: str
    description: str
    severity: str
    detected_at: datetime
    suggested_fix: Optional[str] = None

class MorphKubernetesAgent:
    """
    Kubernetes agent powered by MorphLLM tools for intelligent diagnosis and repair
    """
    
    def __init__(self):
        self.config = morph_config
        self.tools = self.config.get_morph_tools()
        self.search_patterns = self.config.get_kubernetes_search_patterns()
        self.common_fixes = self.config.get_common_fixes()
        
    async def diagnose_cluster(self) -> List[KubernetesIssue]:
        """
        Use MorphLLM tools to diagnose cluster issues
        """
        print("🔍 Starting cluster diagnosis with MorphLLM tools...")
        
        issues = []
        
        # Step 1: Use codebase_search to find deployment files
        deployment_search = await self._morph_codebase_search(
            query="kind: Deployment",
            target_directories=[".", "agent-actions"],
            explanation="Finding all Kubernetes deployment files to check for issues"
        )
        
        # Step 2: Use grep_search to find failing pods patterns
        failing_pods = await self._morph_grep_search(
            query=self.search_patterns["failing_pods"],
            include_pattern="*.yaml",
            explanation="Searching for failing pod patterns in YAML files"
        )
        
        # Step 3: Check actual cluster status
        cluster_issues = await self._check_cluster_status()
        
        # Step 4: Analyze findings with MorphLLM
        for issue in cluster_issues:
            # Use read_file to understand the deployment configuration
            if issue.issue_type in ["ImagePullBackOff", "CrashLoopBackOff"]:
                deployment_file = await self._find_deployment_file(issue.pod_name)
                if deployment_file:
                    file_content = await self._morph_read_file(
                        target_file=deployment_file,
                        explanation=f"Reading deployment file to understand {issue.issue_type} issue"
                    )
                    
                    # Generate fix suggestion
                    issue.suggested_fix = await self._generate_fix_suggestion(issue, file_content)
            
            issues.append(issue)
        
        return issues
    
    async def apply_fix(self, issue: KubernetesIssue) -> bool:
        """
        Use MorphLLM edit_file tool to apply fixes
        """
        print(f"🔧 Applying fix for {issue.pod_name} ({issue.issue_type})")
        
        try:
            if issue.issue_type == "ImagePullBackOff":
                return await self._fix_image_pull_error(issue)
            elif issue.issue_type == "CrashLoopBackOff":
                return await self._fix_crash_loop(issue)
            else:
                print(f"⚠️ No automated fix available for {issue.issue_type}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to apply fix: {e}")
            return False
    
    async def _fix_image_pull_error(self, issue: KubernetesIssue) -> bool:
        """Fix ImagePullBackOff by correcting image tag"""
        
        # Find the deployment file
        deployment_file = await self._find_deployment_file(issue.pod_name)
        if not deployment_file:
            return False
        
        # Read current content
        current_content = await self._morph_read_file(
            target_file=deployment_file,
            explanation="Reading deployment to fix ImagePullBackOff issue"
        )
        
        # Use edit_file to fix the image tag
        fix_snippet = """
# ... existing code ...
        image: nginx:1.21  # Fixed from nonexistent image tag
# ... existing code ...
        """
        
        success = await self._morph_edit_file(
            target_file=deployment_file,
            edit_snippet=fix_snippet,
            explanation="Fixing ImagePullBackOff by correcting image tag to valid version"
        )
        
        if success:
            # Apply the changes to cluster
            await self._kubectl_apply(deployment_file)
            print(f"✅ Fixed ImagePullBackOff for {issue.pod_name}")
            return True
        
        return False
    
    async def _fix_crash_loop(self, issue: KubernetesIssue) -> bool:
        """Fix CrashLoopBackOff by adjusting container configuration"""
        
        deployment_file = await self._find_deployment_file(issue.pod_name)
        if not deployment_file:
            return False
        
        # For the crash-loop-app, we need to fix the command that exits with error
        fix_snippet = """
# ... existing code ...
        command: ["/bin/sh"]
        args: ["-c", "echo 'Application starting successfully...' && sleep 3600"]  # Fixed: removed exit 1
# ... existing code ...
        """
        
        success = await self._morph_edit_file(
            target_file=deployment_file,
            edit_snippet=fix_snippet,
            explanation="Fixing CrashLoopBackOff by removing failing exit command"
        )
        
        if success:
            await self._kubectl_apply(deployment_file)
            print(f"✅ Fixed CrashLoopBackOff for {issue.pod_name}")
            return True
        
        return False
    
    async def _check_cluster_status(self) -> List[KubernetesIssue]:
        """Check actual cluster status for issues"""
        issues = []
        
        try:
            # Get all pods with issues
            result = subprocess.run(
                ["kubectl", "get", "pods", "--all-namespaces", "-o", "json"],
                capture_output=True, text=True, check=True
            )
            
            pods_data = json.loads(result.stdout)
            
            for pod in pods_data.get("items", []):
                pod_name = pod["metadata"]["name"]
                namespace = pod["metadata"]["namespace"]
                
                # Check pod status
                status = pod.get("status", {})
                phase = status.get("phase", "Unknown")
                
                # Check container statuses
                container_statuses = status.get("containerStatuses", [])
                for container in container_statuses:
                    waiting = container.get("state", {}).get("waiting", {})
                    if waiting:
                        reason = waiting.get("reason", "Unknown")
                        
                        if reason in ["ImagePullBackOff", "ErrImagePull"]:
                            issues.append(KubernetesIssue(
                                pod_name=pod_name,
                                namespace=namespace,
                                status=reason,
                                issue_type="ImagePullBackOff",
                                description=f"Cannot pull container image: {waiting.get('message', '')}",
                                severity="High",
                                detected_at=datetime.now()
                            ))
                        
                        elif reason in ["CrashLoopBackOff"]:
                            issues.append(KubernetesIssue(
                                pod_name=pod_name,
                                namespace=namespace,
                                status=reason,
                                issue_type="CrashLoopBackOff",
                                description=f"Container keeps crashing: {waiting.get('message', '')}",
                                severity="High",
                                detected_at=datetime.now()
                            ))
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to check cluster status: {e}")
        
        return issues
    
    async def _find_deployment_file(self, pod_name: str) -> Optional[str]:
        """Find the deployment file for a given pod"""
        
        # Use grep_search to find deployment files mentioning this pod
        search_result = await self._morph_grep_search(
            query=pod_name.split("-")[0],  # Get base name without random suffix
            include_pattern="*.yaml",
            explanation=f"Finding deployment file for pod {pod_name}"
        )
        
        # For our demo, we know the problematic pods are in deploy-demo-apps.sh
        return "deploy-demo-apps.sh"
    
    async def _kubectl_apply(self, file_path: str):
        """Apply Kubernetes changes"""
        try:
            if file_path.endswith(".sh"):
                # For shell scripts, we need to re-run them
                subprocess.run([f"./{file_path}"], cwd=self.config.kubernetes_manifests_dir, check=True)
            else:
                subprocess.run(["kubectl", "apply", "-f", file_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to apply changes: {e}")
    
    # MorphLLM tool wrapper methods (these would call actual MorphLLM API)
    async def _morph_read_file(self, target_file: str, explanation: str, 
                              start_line: Optional[int] = None, 
                              end_line: Optional[int] = None) -> str:
        """Wrapper for MorphLLM read_file tool"""
        print(f"📖 Reading file: {target_file} - {explanation}")
        
        # For demo purposes, read file directly
        # In production, this would call MorphLLM API
        try:
            with open(target_file, 'r') as f:
                content = f.read()
                if start_line and end_line:
                    lines = content.split('\n')
                    return '\n'.join(lines[start_line-1:end_line])
                return content
        except FileNotFoundError:
            return f"File not found: {target_file}"
    
    async def _morph_codebase_search(self, query: str, target_directories: List[str], 
                                   explanation: str) -> Dict[str, Any]:
        """Wrapper for MorphLLM codebase_search tool"""
        print(f"🔍 Searching codebase: {query} - {explanation}")
        # This would call MorphLLM API in production
        return {"query": query, "results": []}
    
    async def _morph_grep_search(self, query: str, include_pattern: str, 
                                explanation: str) -> Dict[str, Any]:
        """Wrapper for MorphLLM grep_search tool"""
        print(f"🔎 Grep search: {query} - {explanation}")
        # This would call MorphLLM API in production
        return {"query": query, "matches": []}
    
    async def _morph_edit_file(self, target_file: str, edit_snippet: str, 
                              explanation: str) -> bool:
        """Wrapper for MorphLLM edit_file tool"""
        print(f"✏️ Editing file: {target_file} - {explanation}")
        print(f"Edit snippet:\n{edit_snippet}")
        
        # For demo purposes, return True
        # In production, this would call MorphLLM API to make precise edits
        return True
    
    async def _generate_fix_suggestion(self, issue: KubernetesIssue, 
                                     file_content: str) -> str:
        """Generate fix suggestion using MorphLLM analysis"""
        
        if issue.issue_type == "ImagePullBackOff":
            return "Fix image tag from 'nonexistent-tag-12345' to 'latest' or specific version"
        elif issue.issue_type == "CrashLoopBackOff":
            return "Remove 'exit 1' command and replace with long-running process"
        
        return "No specific fix suggestion available"

# Example usage
async def main():
    """Example of using the MorphLLM Kubernetes agent"""
    
    agent = MorphKubernetesAgent()
    
    print("🚀 Starting MorphLLM Kubernetes Agent...")
    
    # Diagnose cluster issues
    issues = await agent.diagnose_cluster()
    
    print(f"\n📊 Found {len(issues)} issues:")
    for issue in issues:
        print(f"  • {issue.pod_name} ({issue.namespace}): {issue.issue_type}")
        print(f"    Description: {issue.description}")
        if issue.suggested_fix:
            print(f"    Suggested fix: {issue.suggested_fix}")
        print()
    
    # Apply fixes
    for issue in issues:
        print(f"\n🔧 Attempting to fix {issue.pod_name}...")
        success = await agent.apply_fix(issue)
        if success:
            print(f"✅ Successfully fixed {issue.pod_name}")
        else:
            print(f"❌ Failed to fix {issue.pod_name}")

if __name__ == "__main__":
    asyncio.run(main())
