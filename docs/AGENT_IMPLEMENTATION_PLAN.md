# Autonomous Kubernetes Investigation Agents - Implementation Plan

## Overview

This document outlines the implementation plan for two autonomous Kubernetes investigation agents that will run within our containerized environment. These agents will proactively investigate cluster state and identify issues without requiring user input.

## Architecture Context

Our current setup:
- **FastAPI Application**: Running in Docker container at `/api`
- **Google ADK Agent Core**: Available at `/google-adk` 
- **Container Environment**: `dfkozlov/k8s-agentic-swarm-command-center` with kubectl, k8sgpt, k9s pre-installed
- **Kubernetes Cluster**: Kind cluster with k8sgpt-operator, metrics-server installed
- **Existing Diagnostics**: `/agent-actions/diagnose.sh` script for comprehensive cluster analysis

## Agent Implementation Strategy

### 1. Deterministic Investigation Agent (`deterministic_investigate.py`)

**Purpose**: Follow predefined investigation steps for testing and validation

**Location**: `/api/agents/deterministic_investigate.py`

**Functionality**:
- Execute sequential investigation steps
- Use existing tools (kubectl, k8sgpt, diagnose.sh)
- Generate structured reports
- Log all actions and findings
- Provide consistent, repeatable analysis

**Investigation Steps**:
1. **Cluster Health Check**
   - Node status and resource availability
   - Control plane health
   - Network connectivity

2. **Workload Analysis** 
   - Pod states across all namespaces
   - Resource usage and limits
   - Failed/pending pods

3. **Events and Logs Analysis**
   - Recent cluster events
   - Error logs from problematic pods
   - Warning patterns

4. **k8sgpt Analysis**
   - AI-powered issue detection
   - Explanation of problems found
   - Recommended actions

5. **Report Generation**
   - Structured JSON output
   - Summary of findings
   - Priority classification

### 2. Agentic Investigation Agent (`agentic_investigate.py`)

**Purpose**: AI-driven autonomous investigation using available tools

**Location**: `/api/agents/agentic_investigate.py`

**Functionality**:
- Leverage Google ADK agent core
- Dynamically decide investigation approach
- Adapt based on initial findings
- Use AI reasoning for complex scenarios
- Execute remediation actions when appropriate

**AI Agent Architecture**:
- **Tool Registry**: kubectl, k8sgpt, diagnose.sh, custom scripts
- **Decision Engine**: AI model determines next actions
- **Execution Engine**: Run selected tools and analyze results
- **Learning Loop**: Refine approach based on findings

## Technical Implementation

### Dependencies and Environment

**Python Dependencies** (to add to `/api/requirements.txt`):
```
asyncio
subprocess
json
logging
datetime
pathlib
```

**Environment Access**:
- All tools available in container: `kubectl`, `k8sgpt`, `k9s`
- Existing diagnostic script: `/agent-actions/diagnose.sh`
- Google ADK integration via `/google-adk/src/adk_agent`
- OpenRouter API access configured

### File Structure

```
/api/
├── agents/
│   ├── __init__.py
│   ├── deterministic_investigate.py
│   ├── agentic_investigate.py
│   ├── base_investigator.py
│   └── tools/
│       ├── __init__.py
│       ├── kubectl_wrapper.py
│       ├── k8sgpt_wrapper.py
│       └── report_generator.py
├── app/
│   └── routers/
│       └── investigation.py  # New endpoint for agents
└── requirements.txt  # Updated with new dependencies
```

### Integration Points

1. **FastAPI Endpoints**:
   - `POST /v1/investigate/deterministic` - Run deterministic investigation
   - `POST /v1/investigate/agentic` - Run AI-driven investigation
   - `GET /v1/investigate/status/{task_id}` - Check investigation status
   - `GET /v1/investigate/report/{task_id}` - Retrieve investigation report

2. **Google ADK Integration**:
   - Use existing `CoreAgent` class from `/google-adk/src/adk_agent/agents/core_agent.py`
   - Leverage OpenRouter configuration from `/google-adk/src/adk_agent/config/runtime.yaml`
   - Extend agent with Kubernetes-specific tools

3. **Existing Tools Integration**:
   - Wrap `/agent-actions/diagnose.sh` for deterministic use
   - Create Python wrappers for kubectl and k8sgpt commands
   - Reuse cluster setup from `setup-cluster.sh`

## Implementation Steps

### Phase 1: Base Infrastructure
1. Create base investigator class with common functionality
2. Implement tool wrappers (kubectl, k8sgpt)
3. Create report generation system
4. Add FastAPI endpoints for investigation

### Phase 2: Deterministic Agent
1. Implement step-by-step investigation logic
2. Integrate with existing diagnose.sh script
3. Create structured reporting format
4. Add logging and error handling

### Phase 3: Agentic Agent  
1. Extend Google ADK CoreAgent for Kubernetes
2. Implement tool registry and selection logic
3. Create AI-driven decision making loop
4. Add adaptive investigation capabilities

### Phase 4: Testing and Integration
1. Test both agents in containerized environment
2. Verify cluster access and tool functionality
3. Validate report generation and API responses
4. Prepare for hackathon demonstration

## Expected Outputs

### Deterministic Agent Output
```json
{
  "investigation_id": "det_20240109_143022",
  "timestamp": "2024-01-09T14:30:22Z",
  "agent_type": "deterministic",
  "cluster_summary": {
    "nodes": 5,
    "total_pods": 24,
    "healthy_pods": 20,
    "failed_pods": 4
  },
  "findings": [
    {
      "category": "pod_failures",
      "severity": "high",
      "description": "4 pods in failed state",
      "affected_resources": ["frontend-app-xyz", "backend-db-abc"],
      "recommendations": ["Restart failed pods", "Check resource limits"]
    }
  ],
  "investigation_steps": [
    {"step": 1, "action": "cluster_health_check", "status": "completed", "duration": "2.3s"},
    {"step": 2, "action": "pod_analysis", "status": "completed", "duration": "1.8s"}
  ]
}
```

### Agentic Agent Output
```json
{
  "investigation_id": "agt_20240109_143045", 
  "timestamp": "2024-01-09T14:30:45Z",
  "agent_type": "agentic",
  "reasoning": "Detected pod failures, investigating root cause through logs and events",
  "actions_taken": [
    {"tool": "kubectl", "command": "get pods --all-namespaces", "reasoning": "Initial cluster scan"},
    {"tool": "k8sgpt", "command": "analyze --explain", "reasoning": "AI analysis of detected issues"},
    {"tool": "kubectl", "command": "logs frontend-app-xyz", "reasoning": "Investigating specific failure"}
  ],
  "discoveries": [
    {
      "issue": "Image pull failures due to registry authentication",
      "confidence": 0.9,
      "evidence": ["ErrImagePull events", "Registry authentication errors in logs"],
      "suggested_actions": ["Update image pull secrets", "Verify registry credentials"]
    }
  ],
  "autonomy_metrics": {
    "decisions_made": 7,
    "tools_selected": 4,
    "investigation_depth": "comprehensive"
  }
}
```

## Risk Mitigation

1. **Tool Access**: Verify all required tools are available in container environment
2. **Permissions**: Ensure sufficient RBAC permissions for cluster investigation
3. **Error Handling**: Robust error handling for tool failures and API issues
4. **Resource Usage**: Monitor agent resource consumption during investigation
5. **Security**: Ensure agents don't expose sensitive cluster information

## Success Criteria

1. **Deterministic Agent**: Consistently executes all investigation steps and generates structured reports
2. **Agentic Agent**: Demonstrates autonomous decision-making and adaptive investigation approach
3. **Integration**: Both agents work seamlessly within existing FastAPI container environment
4. **Performance**: Investigations complete within reasonable time frames (< 60 seconds)
5. **Reliability**: Agents handle cluster issues gracefully without crashing
6. **Demo Ready**: Both agents provide compelling demonstration value for hackathon presentation

## Implementation Status ✅

### COMPLETED PHASES

**✅ Phase 1: Base Infrastructure (COMPLETE)**
- ✅ Created `base_investigator.py` with common functionality
- ✅ Implemented tool wrappers (`kubectl_wrapper.py`, `k8sgpt_wrapper.py`)
- ✅ Created `report_generator.py` for structured output
- ✅ Added FastAPI investigation endpoints

**✅ Phase 2: Deterministic Agent (COMPLETE)**
- ✅ Implemented `deterministic_investigator.py` with 9-step investigation process
- ✅ Integrated with existing diagnostic tools
- ✅ Created structured reporting format
- ✅ Added comprehensive logging and error handling

**✅ Phase 3: Agentic Agent (COMPLETE)**
- ✅ Implemented `agentic_investigator.py` with Google ADK integration
- ✅ Created tool registry and AI decision-making loop
- ✅ Added adaptive investigation capabilities
- ✅ Integrated AI-powered analysis and recommendations

**✅ Phase 4: Testing and Demo (COMPLETE)**
- ✅ Created comprehensive test suite (`test_agents.py`)
- ✅ Built interactive demo script (`demo_investigation.py`)
- ✅ Validated both agents in containerized environment
- ✅ Generated demo reports and documentation

### DELIVERABLES

1. **Autonomous Investigation Agents**
   - `api/agents/deterministic_investigator.py` - Step-by-step investigation
   - `api/agents/agentic_investigator.py` - AI-driven autonomous investigation

2. **Supporting Infrastructure**
   - `api/agents/base_investigator.py` - Common base class
   - `api/agents/tools/` - kubectl, k8sgpt, and report generation wrappers
   - `api/app/routers/investigation.py` - REST API endpoints

3. **Testing and Demo**
   - `api/test_agents.py` - Comprehensive test suite
   - `api/demo_investigation.py` - Interactive demo script
   - `api/agents/README.md` - Complete documentation

### READY FOR HACKATHON DEMO 🎯

Both autonomous investigation agents are fully implemented and tested:

**Deterministic Agent:**
- Executes 9 predefined investigation steps
- Provides consistent, repeatable analysis
- Perfect for validation and testing

**Agentic Agent:**
- AI-driven autonomous decision making
- Adapts investigation based on findings
- Demonstrates advanced AI capabilities

**API Endpoints:**
```bash
# Available endpoints
POST /v1/investigate/deterministic
POST /v1/investigate/agentic
GET  /v1/investigate/status/{id}
GET  /v1/investigate/report/{id}
GET  /v1/investigate/list
POST /v1/investigate/quick-status
```

**Demo Commands:**
```bash
# Run test suite
python api/test_agents.py

# Interactive demo
python api/demo_investigation.py

# Start FastAPI server
cd api && uvicorn app.server:app --reload
```

This implementation successfully demonstrates autonomous Kubernetes investigation capabilities with both deterministic and AI-driven approaches, ready for hackathon presentation! 🚀