"""
Enhanced Agentic Kubernetes Investigation Agent (Version 2)

This agent uses AI to autonomously decide investigation approach and
adapt based on findings using Google ADK integration and company-specific
internal knowledge base for intelligent solution generation.
"""
import asyncio
import logging
import sys
import os
import json
from typing import Dict, List, Optional, Any
import time
from datetime import datetime

# Add paths for Google ADK imports (container and local paths)
if "/root" not in sys.path:
    sys.path.append("/root")
if "/root/google-adk/src" not in sys.path:
    sys.path.append("/root/google-adk/src")
# Also add local development path for testing outside container
local_adk_path = '/Users/chalmers/code/kubernetes-agentic-swam-yc-hackathon/google-adk/src'
if local_adk_path not in sys.path and os.path.exists(local_adk_path):
    sys.path.append(local_adk_path)

from .base_investigator import BaseInvestigator
from .tools.kubectl_wrapper import KubectlWrapper
from .tools.k8sgpt_wrapper import K8sgptWrapper
from .tools.report_generator import ReportGenerator, Severity, InvestigationType
from .knowledge.knowledge_engine import AcmeCorpKnowledgeEngine


class AgenticInvestigatorV2(BaseInvestigator):
    """
    Enhanced AI-driven investigation agent with company knowledge integration.
    
    This agent leverages Google ADK to make intelligent decisions about what
    to investigate next based on initial findings and uses AcmeCorp internal
    knowledge to generate company-compliant solutions.
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
        
        # Knowledge engine for company-specific guidance
        self.knowledge_engine = AcmeCorpKnowledgeEngine()
        
        # Investigation state
        self.current_issues = []
        self.classified_issues = []
        self.generated_solutions = []
        
        # Initialize agent and tools
        self._initialize_agent()
        self._register_tools()
        
    def _initialize_agent(self):
        """Initialize Google ADK agent."""
        try:
            # Import Google ADK components
            from adk_agent.config.loader import load_runtime_config
            from adk_agent.agents.core_agent import create_core_agent
            
            # Load configuration
            config_path = os.getenv("ADK_CONFIG_PATH", "/root/google-adk/src/adk_agent/config/runtime.yaml")
            config = load_runtime_config(config_path)
            
            # Create core agent
            self.agent = create_core_agent(config)
            self.logger.info("Google ADK agent initialized successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize Google ADK agent: {e}")
            self.agent = None  # Will use fallback investigation
    
    def _register_tools(self):
        """Register investigation tools for AI agent."""
        self.available_tools = {
            "detect_cluster_issues": self._detect_cluster_issues,
            "classify_issue_with_ai": self._classify_issue_with_ai,
            "get_company_knowledge": self._get_company_knowledge,
            "generate_ai_solutions": self._generate_knowledge_based_solutions,
            "analyze_pod_problems": self._analyze_pod_problems,
            "analyze_node_health": self._analyze_node_health,
            "analyze_cluster_events": self._analyze_cluster_events
        }
        
        self.logger.info(f"Registered {len(self.available_tools)} investigation tools")
    
    async def _investigate(self) -> None:
        """
        Main AI-driven investigation with knowledge integration.
        Implementation of the abstract method from BaseInvestigator.
        """
        try:
            self.logger.info("Starting enhanced AI-driven investigation...")
            print("🧠 Starting Enhanced AI Investigation with AcmeCorp Knowledge...")
            
            # Run comprehensive AI investigation
            report_data = await self.run_investigation()
            
            # Store results for autonomous monitor
            self.report_data = report_data
            
            self.logger.info("Enhanced AI investigation completed successfully")
            print("✅ Enhanced AI Investigation Complete!")
            
        except Exception as e:
            self.logger.error(f"Enhanced AI investigation failed: {e}")
            print(f"❌ AI investigation failed, running fallback: {e}")
            # Fallback to basic investigation
            await self._run_fallback_investigation()
    
    async def run_investigation(self, 
                              namespace: Optional[str] = None,
                              include_k8sgpt: bool = True,
                              include_events: bool = True,
                              timeout: int = 300) -> Dict[str, Any]:
        """
        Run enhanced AI-driven investigation with company knowledge.
        """
        start_time = time.time()
        
        try:
            print("🚀 Enhanced Agentic Investigation Starting...")
            print("==================================================")
            print("🧠 AI Agent: Analyzing cluster with company knowledge")
            print("📚 Knowledge Base: AcmeCorp internal documentation")
            print("⚡ Investigation Mode: Adaptive AI-driven analysis")
            print()
            
            # Step 1: Detect and classify issues using AI
            print("🔍 Step 1: AI-Powered Issue Detection and Classification...")
            detected_issues = await self._detect_cluster_issues(namespace)
            
            if not detected_issues:
                print("✅ No issues detected - cluster appears healthy")
                return await self._generate_healthy_cluster_report(start_time)
            
            print(f"📊 Detected {len(detected_issues)} potential issues")
            
            # Step 2: AI classification and prioritization
            print("🧠 Step 2: AI Issue Classification and Prioritization...")
            classified_issues = []
            
            for issue in detected_issues:
                classification = await self._classify_issue_with_ai(issue)
                classified_issues.append({
                    "issue": issue,
                    "classification": classification
                })
                
                print(f"   🏷️  {issue.get('resource', 'Unknown')}: {classification.get('type', 'Unknown')} "
                      f"(Severity: {classification.get('severity', 'Unknown')})")
            
            # Step 3: Generate company-aware solutions
            print("📚 Step 3: Generating Company-Aware Solutions...")
            investigation_results = []
            
            for classified_issue in classified_issues:
                issue = classified_issue["issue"]
                classification = classified_issue["classification"]
                
                print(f"   💡 Analyzing: {issue.get('resource', 'Unknown')}")
                
                # Get relevant company knowledge
                knowledge = await self._get_company_knowledge(classification)
                
                # Generate AI solutions using company knowledge
                solutions = await self._generate_knowledge_based_solutions(
                    classification, issue, knowledge
                )
                
                # Record findings
                await self._record_ai_finding(issue, classification, solutions, knowledge)
                
                investigation_results.append({
                    "issue": issue,
                    "classification": classification,
                    "knowledge_used": len(knowledge),
                    "solutions": solutions
                })
                
                print(f"   ✅ Generated {len(solutions)} company-compliant solutions")
            
            # Step 4: Generate comprehensive report
            print("📋 Step 4: Generating AI Investigation Report...")
            final_report = await self._generate_ai_investigation_report(
                investigation_results, start_time
            )
            
            print(f"🎯 Investigation Complete: {len(classified_issues)} issues analyzed")
            print(f"📝 Total solutions generated: {sum(len(r['solutions']) for r in investigation_results)}")
            print(f"⏱️  Investigation duration: {time.time() - start_time:.1f} seconds")
            
            return final_report
            
        except Exception as e:
            self.logger.error(f"Enhanced AI investigation failed: {e}")
            print(f"❌ Investigation failed: {e}")
            
            # Fallback to basic investigation
            return await self._run_fallback_investigation(namespace, include_k8sgpt, include_events, timeout)
    
    async def _detect_cluster_issues(self, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Detect cluster issues using kubectl analysis."""
        issues = []
        
        try:
            # Get pod issues
            pods_result = await self.kubectl.get_all_pods(namespace)
            if pods_result and "items" in pods_result:
                pod_issues = await self._analyze_pod_problems(pods_result["items"])
                issues.extend(pod_issues)
            
            # Get node issues
            nodes_result = await self.kubectl.get_nodes()
            if nodes_result and "items" in nodes_result:
                node_issues = await self._analyze_node_health(nodes_result["items"])
                issues.extend(node_issues)
            
            # Get event issues
            if namespace:
                events_result = await self.kubectl.get_events(namespace)
            else:
                events_result = await self.kubectl.get_events()
            
            if events_result and "items" in events_result:
                event_issues = await self._analyze_cluster_events(events_result["items"])
                issues.extend(event_issues)
            
        except Exception as e:
            self.logger.error(f"Failed to detect cluster issues: {e}")
        
        return issues
    
    async def _classify_issue_with_ai(self, issue_details: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to classify and understand the issue type."""
        
        # If Google ADK is available, use it for classification
        if self.agent:
            try:
                return await self._ai_classify_with_adk(issue_details)
            except Exception as e:
                self.logger.warning(f"ADK classification failed: {e}")
        
        # Fallback: rule-based classification
        return self._rule_based_classification(issue_details)
    
    async def _ai_classify_with_adk(self, issue_details: Dict[str, Any]) -> Dict[str, Any]:
        """Use Google ADK for intelligent issue classification with visible reasoning."""
        
        classification_prompt = f"""
        You are AcmeCorp's Senior SRE analyzing a Kubernetes issue. Think step by step and show your reasoning process.

        ISSUE DETAILS:
        - Resource: {issue_details.get('resource', 'unknown')}
        - Status: {issue_details.get('status', 'unknown')}
        - Message: {issue_details.get('message', 'No message')}
        - Type: {issue_details.get('type', 'unknown')}
        - Namespace: {issue_details.get('namespace', 'unknown')}
        
        THINK THROUGH THIS SYSTEMATICALLY:
        
        OBSERVATION: What technical symptoms do you observe?
        ANALYSIS: What is the likely root cause based on these symptoms?
        COMPANY_IMPACT: How does this affect AcmeCorp operations?
        URGENCY: How quickly does this need resolution?
        CLASSIFICATION: What category and severity is this?
        
        After your analysis, provide final classification as JSON:
        {{
            "type": "descriptive_issue_type",
            "severity": "low|medium|high|critical", 
            "components": ["affected", "components"],
            "root_cause_category": "image|resource|network|config|security",
            "investigation_priority": 1-10,
            "immediate_action_needed": true/false,
            "company_impact": "minimal|moderate|significant|severe"
        }}
        """
        
        try:
            print("   🧠 AI Agent analyzing issue...")
            
            response = self.agent.run(
                "You are AcmeCorp's Senior SRE with deep Kubernetes expertise.",
                classification_prompt
            )
            
            # Display AI reasoning process
            print("   💭 AI Reasoning Process:")
            self._display_ai_thinking(response)
            
            # Extract JSON from response
            classification = self._extract_json_from_reasoning(response)
            self._record_ai_decision("issue_classification", response)
            
            return classification
            
        except Exception as e:
            self.logger.error(f"ADK classification parsing failed: {e}")
            print(f"   ⚠️  AI classification failed, using rule-based fallback: {e}")
            return self._rule_based_classification(issue_details)
    
    def _rule_based_classification(self, issue_details: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based issue classification."""
        
        issue_type = issue_details.get("type", "").lower()
        status = issue_details.get("status", "").lower()
        message = issue_details.get("message", "").lower()
        
        # Classification rules
        if "imagepullbackoff" in issue_type or "errimagepull" in issue_type:
            return {
                "type": "ImagePullBackOff",
                "severity": "high",
                "components": ["image", "registry", "deployment"],
                "root_cause_category": "image", 
                "investigation_priority": 8,
                "immediate_action_needed": True,
                "company_impact": "significant"
            }
        
        elif "crashloopbackoff" in issue_type:
            return {
                "type": "CrashLoopBackOff",
                "severity": "critical",
                "components": ["application", "resource", "config"],
                "root_cause_category": "resource",
                "investigation_priority": 9,
                "immediate_action_needed": True,
                "company_impact": "severe"
            }
        
        elif "pending" in status:
            return {
                "type": "PodPending",
                "severity": "medium",
                "components": ["scheduling", "resource", "node"],
                "root_cause_category": "resource",
                "investigation_priority": 6,
                "immediate_action_needed": False,
                "company_impact": "moderate"
            }
        
        else:
            return {
                "type": "UnknownIssue",
                "severity": "medium",
                "components": ["general"],
                "root_cause_category": "config",
                "investigation_priority": 5,
                "immediate_action_needed": False,
                "company_impact": "minimal"
            }
    
    async def _get_company_knowledge(self, classification: Dict[str, Any]) -> str:
        """Retrieve relevant AcmeCorp knowledge for the classified issue."""
        try:
            knowledge = await self.knowledge_engine.get_relevant_knowledge(classification)
            self.logger.debug(f"Retrieved {len(knowledge)} characters of company knowledge")
            return knowledge
        except Exception as e:
            self.logger.error(f"Failed to retrieve company knowledge: {e}")
            return "AcmeCorp knowledge base unavailable."
    
    async def _generate_knowledge_based_solutions(self, classification: Dict, issue_details: Dict, knowledge: str) -> List[str]:
        """Generate solutions by reasoning through company knowledge."""
        
        if self.agent and knowledge:
            try:
                return await self._ai_generate_solutions(classification, issue_details, knowledge)
            except Exception as e:
                self.logger.warning(f"AI solution generation failed: {e}")
        
        # Fallback: rule-based solutions
        return self._rule_based_solutions(classification, issue_details)
    
    async def _ai_generate_solutions(self, classification: Dict, issue_details: Dict, knowledge: str) -> List[str]:
        """Use AI to generate detailed, actionable solutions with visible reasoning."""
        
        # Extract specific context for better solutions
        resource_name = issue_details.get('resource', 'unknown').split('/')[-1]
        namespace = issue_details.get('namespace', 'default')
        error_message = issue_details.get('message', '')
        issue_type = classification.get('type', '')
        
        solution_prompt = f"""
        You are AcmeCorp's Senior SRE providing detailed resolution instructions. Think through this systematically and show your reasoning.

        ACMECORP INTERNAL KNOWLEDGE BASE:
        {knowledge}
        
        SPECIFIC PRODUCTION ISSUE:
        - Deployment: {resource_name}
        - Namespace: {namespace}  
        - Issue Type: {issue_type}
        - Error Message: {error_message}
        - Severity: {classification.get('severity', 'unknown')}
        
        THINK THROUGH THE RESOLUTION SYSTEMATICALLY:
        
        ROOT_CAUSE_ANALYSIS: What is the exact technical cause of this issue?
        COMPANY_POLICY_CHECK: Which AcmeCorp standards/policies are violated?
        IMMEDIATE_IMPACT: What is the business impact right now?
        SOLUTION_BRAINSTORM: What are the possible technical fixes?
        BEST_APPROACH: What is the recommended resolution strategy?
        SPECIFIC_STEPS: What are the exact commands and code changes needed?
        VERIFICATION: How do we confirm the fix worked?
        PREVENTION: How do we prevent this from happening again?
        
        After your analysis, provide detailed resolution steps in this format:

        RESOLUTION PLAN:
        ===============
        
        ROOT CAUSE: [Specific technical reason]
        COMPANY VIOLATION: [Which policy/standard violated]
        BUSINESS IMPACT: [Service/user impact]
        
        RESOLUTION STEPS:
        ================
        1️⃣ IMMEDIATE FIX:
           [Exact kubectl/bash commands with real values]
           
        2️⃣ VERIFICATION:
           [Commands to verify fix worked]
           
        3️⃣ PERMANENT SOLUTION:
           [YAML/config changes needed with specific code]
           
        4️⃣ PREVENTION:
           [Process/automation changes to prevent recurrence]
        
        TIMELINE: [Expected time to resolution]
        RISK: [Deployment risk level and mitigation]
        REFERENCE: [Specific AcmeCorp policy section]
        
        Use ONLY AcmeCorp-approved resources from the knowledge base.
        Be specific with namespaces, image tags, resource limits, exact commands.
        """
        
        try:
            print("   🧠 AI Agent generating resolution plan...")
            
            response = self.agent.run(
                "You are AcmeCorp's Senior SRE providing actionable resolution guidance.",
                solution_prompt
            )
            
            # Display AI reasoning process
            print("   💭 AI Resolution Reasoning:")
            self._display_ai_thinking(response)
            
            # Format the detailed resolution
            formatted_solution = self._format_detailed_resolution(response, resource_name, namespace)
            self._record_ai_decision("solution_generation", response)
            
            return [formatted_solution]
            
        except Exception as e:
            self.logger.error(f"AI solution generation failed: {e}")
            print(f"   ⚠️  AI solution generation failed, using rule-based fallback: {e}")
            return self._rule_based_solutions(classification, issue_details)
    
    def _rule_based_solutions(self, classification: Dict, issue_details: Dict) -> List[str]:
        """Fallback rule-based solutions."""
        
        issue_type = classification.get("type", "").lower()
        resource = issue_details.get("resource", "unknown")
        
        if "imagepullbackoff" in issue_type:
            return [
                f"**Issue**: Image pull failure for {resource}\n"
                f"**Solution**: Update to AcmeCorp approved image\n"
                f"**Command**: `kubectl set image deployment/{resource.split('/')[-1]} container=harbor.acmecorp.com/frontend/nginx:1.27.1`\n"
                f"**Reference**: AcmeCorp Standards - Container Image Policy\n"
                f"**Priority**: high",
                
                f"**Issue**: Unapproved image source\n"
                f"**Solution**: Use company registry images only\n"
                f"**Command**: Check approved images in harbor.acmecorp.com\n"
                f"**Reference**: Approved Resources Registry\n"
                f"**Priority**: high"
            ]
        
        elif "crashloopbackoff" in issue_type:
            return [
                f"**Issue**: Pod crashing due to resource constraints\n"
                f"**Solution**: Adjust resources per AcmeCorp standards\n"
                f"**Command**: `kubectl patch deployment {resource.split('/')[-1]} -p '{{\"spec\":{{\"template\":{{\"spec\":{{\"containers\":[{{\"name\":\"app\",\"resources\":{{\"requests\":{{\"memory\":\"64Mi\",\"cpu\":\"100m\"}},\"limits\":{{\"memory\":\"128Mi\",\"cpu\":\"200m\"}}}}}}]}}}}}}}}'`\n"
                f"**Reference**: AcmeCorp Resource Allocation Standards\n"
                f"**Priority**: critical"
            ]
        
        else:
            return [
                f"**Issue**: General Kubernetes issue with {resource}\n"
                f"**Solution**: Follow AcmeCorp troubleshooting procedures\n"
                f"**Command**: `kubectl describe pod {resource.split('/')[-1]}`\n"
                f"**Reference**: AcmeCorp Incident Playbook\n"
                f"**Priority**: medium"
            ]
    
    async def _analyze_pod_problems(self, pods: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze pod issues from kubectl output."""
        issues = []
        
        for pod in pods:
            pod_name = pod.get("metadata", {}).get("name", "unknown")
            namespace = pod.get("metadata", {}).get("namespace", "unknown")
            status = pod.get("status", {})
            phase = status.get("phase", "Unknown")
            
            # Check container statuses for issues
            container_statuses = status.get("containerStatuses", [])
            for container in container_statuses:
                state = container.get("state", {})
                
                if "waiting" in state:
                    waiting_reason = state["waiting"].get("reason", "")
                    waiting_message = state["waiting"].get("message", "")
                    
                    if waiting_reason in ["ImagePullBackOff", "ErrImagePull", "CrashLoopBackOff"]:
                        issues.append({
                            "resource": f"{namespace}/{pod_name}",
                            "type": waiting_reason,
                            "status": phase,
                            "message": waiting_message,
                            "namespace": namespace,
                            "container": container.get("name", "unknown")
                        })
        
        return issues
    
    async def _analyze_node_health(self, nodes: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze node health issues."""
        issues = []
        
        for node in nodes:
            node_name = node.get("metadata", {}).get("name", "unknown")
            conditions = node.get("status", {}).get("conditions", [])
            
            for condition in conditions:
                condition_type = condition.get("type", "")
                status = condition.get("status", "")
                reason = condition.get("reason", "")
                message = condition.get("message", "")
                
                # Check for problematic conditions
                if condition_type == "Ready" and status != "True":
                    issues.append({
                        "resource": f"node/{node_name}",
                        "type": "NodeNotReady",
                        "status": "NotReady",
                        "message": message,
                        "namespace": "kube-system",
                        "reason": reason
                    })
        
        return issues
    
    async def _analyze_cluster_events(self, events: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze cluster events for issues."""
        issues = []
        
        for event in events[-20:]:  # Last 20 events
            event_type = event.get("type", "")
            reason = event.get("reason", "")
            message = event.get("message", "")
            involved_object = event.get("involvedObject", {})
            
            if event_type == "Warning" and reason in ["Failed", "FailedScheduling", "Unhealthy"]:
                resource_name = involved_object.get("name", "unknown")
                namespace = involved_object.get("namespace", "unknown")
                
                issues.append({
                    "resource": f"{namespace}/{resource_name}",
                    "type": f"Event{reason}",
                    "status": "Warning",
                    "message": message,
                    "namespace": namespace,
                    "event_reason": reason
                })
        
        return issues
    
    async def _record_ai_finding(self, issue: Dict, classification: Dict, solutions: List[str], knowledge: str):
        """Record AI investigation finding with solutions."""
        
        # Determine severity enum
        severity_map = {
            "low": Severity.LOW,
            "medium": Severity.MEDIUM,
            "high": Severity.HIGH,
            "critical": Severity.CRITICAL
        }
        
        severity = severity_map.get(classification.get("severity", "medium"), Severity.MEDIUM)
        
        # Create finding
        self.report_generator.add_finding(
            category=classification.get("root_cause_category", "unknown"),
            severity=severity,
            title=f"{classification.get('type', 'Unknown Issue')} in {issue.get('resource', 'unknown')}",
            description=issue.get("message", "No description available"),
            affected_resources=[issue.get("resource", "unknown")],
            recommendations=[sol.split("**Solution**:")[-1].split("**Command**:")[0].strip() for sol in solutions[:3]],
            evidence=[f"Classification: {classification}", f"Knowledge used: {len(knowledge)} chars"],
            source_tool="ai_agent_with_acmecorp_knowledge"
        )
    
    def _display_ai_thinking(self, ai_response: str):
        """Display AI thinking process in a readable format."""
        # Split response into sections for better readability
        lines = ai_response.split('\n')
        
        thinking_sections = []
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.upper() for keyword in ['OBSERVATION:', 'ANALYSIS:', 'COMPANY_', 'ROOT_CAUSE', 'SOLUTION_', 'IMMEDIATE_', 'VERIFICATION:', 'PREVENTION:']):
                if current_section:
                    thinking_sections.append(current_section)
                current_section = line
            elif line and not line.startswith('{') and not line.startswith('['):
                current_section += f" {line}"
        
        if current_section:
            thinking_sections.append(current_section)
        
        # Display formatted thinking
        for section in thinking_sections[:6]:  # Limit to first 6 sections
            if len(section) > 10:  # Skip very short sections
                print(f"      {section[:150]}{'...' if len(section) > 150 else ''}")
    
    def _extract_json_from_reasoning(self, response: str) -> Dict[str, Any]:
        """Extract JSON classification from AI reasoning response."""
        try:
            # Look for JSON in the response
            lines = response.split('\n')
            json_started = False
            json_lines = []
            
            for line in lines:
                if '{' in line and not json_started:
                    json_started = True
                    json_lines.append(line[line.index('{'):])
                elif json_started:
                    json_lines.append(line)
                    if '}' in line:
                        break
            
            json_str = '\n'.join(json_lines)
            return json.loads(json_str)
            
        except Exception as e:
            # Fallback: extract key information manually
            return {
                "type": "ParsedFromReasoning",
                "severity": "medium",
                "components": ["kubernetes"],
                "root_cause_category": "unknown",
                "investigation_priority": 5,
                "immediate_action_needed": True,
                "company_impact": "moderate"
            }
    
    def _format_detailed_resolution(self, ai_response: str, resource_name: str, namespace: str) -> str:
        """Format AI resolution into structured, actionable steps."""
        
        # Extract resolution sections from AI response
        resolution_sections = self._parse_resolution_sections(ai_response)
        
        formatted_resolution = f"""
{'='*80}
🚨 DETAILED RESOLUTION PLAN: {resource_name}
{'='*80}

{resolution_sections.get('root_cause', 'Root cause analysis from AI reasoning')}

BUSINESS IMPACT: {resolution_sections.get('impact', 'Service disruption analysis')}
COMPANY VIOLATION: {resolution_sections.get('violation', 'Policy compliance check')}

RESOLUTION STEPS:
================
{resolution_sections.get('steps', self._generate_fallback_steps(resource_name, namespace))}

⏱️  TIMELINE: {resolution_sections.get('timeline', '15-30 minutes')}
⚠️  RISK LEVEL: {resolution_sections.get('risk', 'Medium - Standard deployment change')}
📖 REFERENCE: {resolution_sections.get('reference', 'AcmeCorp Standards Documentation')}

{'='*80}
        """
        
        return formatted_resolution.strip()
    
    def _parse_resolution_sections(self, response: str) -> Dict[str, str]:
        """Parse AI response into structured resolution sections."""
        sections = {}
        current_section = None
        current_content = []
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if 'ROOT CAUSE:' in line.upper():
                current_section = 'root_cause'
                current_content = [line]
            elif 'BUSINESS IMPACT:' in line.upper() or 'IMPACT:' in line.upper():
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'impact'
                current_content = [line]
            elif 'COMPANY VIOLATION:' in line.upper() or 'VIOLATION:' in line.upper():
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'violation'
                current_content = [line]
            elif 'RESOLUTION STEPS:' in line.upper() or '1️⃣' in line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'steps'
                current_content = [line]
            elif 'TIMELINE:' in line.upper():
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'timeline'
                current_content = [line]
            elif 'RISK:' in line.upper():
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'risk'
                current_content = [line]
            elif 'REFERENCE:' in line.upper():
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'reference'
                current_content = [line]
            elif current_section and line:
                current_content.append(line)
        
        # Save final section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _generate_fallback_steps(self, resource_name: str, namespace: str) -> str:
        """Generate fallback resolution steps when AI parsing fails."""
        return f"""
1️⃣ IMMEDIATE FIX:
   kubectl describe pod -l app={resource_name} -n {namespace}
   kubectl get events -n {namespace} --sort-by='.lastTimestamp'
   
2️⃣ VERIFICATION:
   kubectl get pods -n {namespace} -l app={resource_name} -o wide
   kubectl logs -n {namespace} -l app={resource_name} --tail=50
   
3️⃣ APPLY COMPANY STANDARDS:
   # Update deployment to use AcmeCorp approved resources
   kubectl patch deployment {resource_name} -n {namespace} -p '...'
   
4️⃣ MONITOR RECOVERY:
   watch kubectl get pods -n {namespace} -l app={resource_name}
        """
    
    def _record_ai_decision(self, decision_type: str, details: str):
        """Record AI decision for investigation history."""
        self.investigation_history.append({
            "timestamp": datetime.now().isoformat(),
            "decision_type": decision_type,
            "details": details[:500],  # Limit size
            "decision_number": self.decisions_made
        })
        self.decisions_made += 1
    
    async def _generate_ai_investigation_report(self, investigation_results: List[Dict], start_time: float) -> Dict[str, Any]:
        """Generate comprehensive AI investigation report."""
        
        total_issues = len(investigation_results)
        total_solutions = sum(len(result["solutions"]) for result in investigation_results)
        duration = time.time() - start_time
        
        # Generate final report
        report = self.report_generator.generate_json_report()
        
        # Add AI-specific metadata
        report["ai_investigation"] = {
            "agent_type": "Enhanced Agentic with AcmeCorp Knowledge",
            "total_issues_analyzed": total_issues,
            "total_solutions_generated": total_solutions,
            "ai_decisions_made": self.decisions_made,
            "knowledge_base_used": "AcmeCorp Internal Documentation",
            "investigation_mode": "adaptive_ai_driven",
            "duration_seconds": duration
        }
        
        return report
    
    async def _generate_healthy_cluster_report(self, start_time: float) -> Dict[str, Any]:
        """Generate report for healthy cluster."""
        
        duration = time.time() - start_time
        
        return {
            "investigation_id": f"agentic_v2_{int(start_time)}",
            "timestamp": datetime.now().isoformat(),
            "investigation_type": "agentic_v2",
            "duration_seconds": duration,
            "cluster_status": "healthy",
            "findings": [],
            "ai_investigation": {
                "agent_type": "Enhanced Agentic with AcmeCorp Knowledge",
                "total_issues_analyzed": 0,
                "total_solutions_generated": 0,
                "ai_decisions_made": 1,
                "knowledge_base_used": "AcmeCorp Internal Documentation",
                "investigation_mode": "adaptive_ai_driven",
                "cluster_assessment": "No issues detected - cluster operating within AcmeCorp standards"
            }
        }
    
    async def _run_fallback_investigation(self, namespace=None, include_k8sgpt=True, include_events=True, timeout=300):
        """Fallback investigation when AI fails."""
        
        print("🔄 Running fallback investigation...")
        
        # Basic issue detection
        issues = await self._detect_cluster_issues(namespace)
        
        # Simple classification and solutions
        investigation_results = []
        for issue in issues:
            classification = self._rule_based_classification(issue)
            solutions = self._rule_based_solutions(classification, issue)
            
            investigation_results.append({
                "issue": issue,
                "classification": classification,
                "solutions": solutions
            })
        
        # Generate basic report
        return {
            "investigation_id": f"fallback_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "investigation_type": "fallback",
            "findings": investigation_results,
            "ai_investigation": {
                "agent_type": "Fallback (AI unavailable)",
                "total_issues_analyzed": len(issues),
                "note": "AI agent unavailable, used rule-based analysis"
            }
        }
