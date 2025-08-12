# Kubernetes Investigation Agents

This directory contains autonomous Kubernetes investigation agents that can analyze cluster state and identify issues without requiring user input.

## Architecture

### Agent Types

1. **Deterministic Investigator** (`deterministic_investigator.py`)
   - Follows predefined investigation steps
   - Ensures consistent, repeatable analysis
   - Best for testing, validation, and routine monitoring

2. **Agentic Investigator** (`agentic_investigator.py`)
   - AI-driven autonomous investigation
   - Adapts investigation approach based on findings
   - Uses Google ADK for intelligent decision-making
   - Best for complex issues and adaptive analysis

### Core Components

- **Base Investigator** (`base_investigator.py`) - Common functionality
- **Tool Wrappers** (`tools/`) - Kubernetes tool abstractions
  - `kubectl_wrapper.py` - kubectl command wrapper
  - `k8sgpt_wrapper.py` - k8sgpt AI analysis wrapper
  - `report_generator.py` - Structured report generation

## Usage

### Direct Agent Usage

```python
from agents.deterministic_investigator import run_deterministic_investigation
from agents.agentic_investigator import run_agentic_investigation

# Deterministic investigation
report = await run_deterministic_investigation(
    namespace=None,  # All namespaces
    include_k8sgpt=True,
    include_events=True,
    timeout=300
)

# Agentic investigation
report = await run_agentic_investigation(
    namespace="production",
    include_k8sgpt=True,
    include_events=True,
    timeout=300
)
```

### FastAPI Endpoints

The agents are exposed via REST API endpoints:

```bash
# Start deterministic investigation
curl -X POST http://localhost:8000/v1/investigate/deterministic \
  -H "Content-Type: application/json" \
  -d '{"investigation_type": "deterministic", "include_k8sgpt": true}'

# Start agentic investigation
curl -X POST http://localhost:8000/v1/investigate/agentic \
  -H "Content-Type: application/json" \
  -d '{"investigation_type": "agentic", "include_k8sgpt": true}'

# Check investigation status
curl http://localhost:8000/v1/investigate/status/{investigation_id}

# Get investigation report
curl http://localhost:8000/v1/investigate/report/{investigation_id}
```

## Investigation Process

### Deterministic Agent Steps

1. **Cluster Overview** - Basic cluster information
2. **Node Analysis** - Node health and status
3. **Pod Analysis** - Pod states across namespaces
4. **Resource Utilization** - CPU/memory usage
5. **Event Analysis** - Recent cluster events
6. **K8sgpt Analysis** - AI-powered issue detection
7. **Workload Analysis** - Deployments and services
8. **Network Analysis** - Network policies and ingresses
9. **Report Generation** - Structured findings report

### Agentic Agent Approach

1. **AI Planning** - Agent decides investigation approach
2. **Tool Selection** - Dynamically selects appropriate tools
3. **Adaptive Investigation** - Follows up on discoveries
4. **Intelligent Analysis** - AI-powered insights and recommendations
5. **Comprehensive Reporting** - Includes AI decision history

## Report Structure

Both agents generate structured JSON reports with:

```json
{
  "investigation_id": "det_1704123456",
  "investigation_type": "deterministic",
  "duration_seconds": 45.2,
  "cluster_summary": {
    "total_nodes": 3,
    "total_pods": 25,
    "failed_pods": 2,
    "total_deployments": 8
  },
  "findings": [
    {
      "category": "pod_failures",
      "severity": "high",
      "title": "Failed pods detected",
      "description": "2 pods are in failed state",
      "affected_resources": ["namespace/pod-name"],
      "recommendations": ["Check logs", "Verify image"],
      "evidence": ["Pod status: Failed"],
      "source_tool": "kubectl"
    }
  ],
  "findings_summary": {
    "total_count": 3,
    "by_severity": {"critical": 0, "high": 2, "medium": 1}
  },
  "executive_summary": "CLUSTER STATUS: ISSUES DETECTED...",
  "recommendations": ["Fix failed pods", "Check resource limits"]
}
```

## Testing

### Unit Tests

```bash
# Test both agents
cd api
python test_agents.py
```

### Demo Script

```bash
# Interactive demo
cd api
python demo_investigation.py
```

## Tool Dependencies

The agents require these tools to be available in the container:

- `kubectl` - Kubernetes CLI
- `k8sgpt` - AI-powered Kubernetes analysis
- Python packages in `requirements.txt`
- Google ADK (for agentic agent)

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY` - For Google ADK AI features
- `KUBECONFIG` - Kubernetes cluster access

### Google ADK Configuration

The agentic agent uses Google ADK with this configuration:

```yaml
model: "anthropic/claude-opus-4.1"
provider: "openrouter"
```

## Error Handling

Both agents include comprehensive error handling:

- Tool availability checks
- Timeout management
- Graceful degradation
- Detailed error reporting
- Investigation recovery

## Performance

Typical investigation times:

- **Deterministic**: 30-60 seconds for full cluster scan
- **Agentic**: 45-90 seconds (varies based on AI decisions)

## Extending the Agents

### Adding New Tools

1. Create tool wrapper in `tools/`
2. Register tool in agent `_register_tools()`
3. Implement tool method
4. Update investigation logic

### Custom Investigation Steps

1. Extend base investigator class
2. Implement custom investigation methods
3. Update report generation
4. Register new agent in API endpoints

## Security Considerations

- Agents require read-only cluster access
- No cluster modifications performed
- Sensitive data filtered from reports
- Tool execution sandboxed
- API authentication recommended for production

## Production Deployment

For production use:

1. Configure proper RBAC permissions
2. Set up monitoring and alerting
3. Use persistent storage for reports
4. Implement authentication
5. Configure rate limiting
6. Set up log aggregation

## Troubleshooting

Common issues:

1. **kubectl not available** - Verify container setup
2. **k8sgpt auth errors** - Check API key configuration
3. **Google ADK failures** - Verify OpenRouter access
4. **Permission denied** - Check RBAC settings
5. **Timeout errors** - Increase timeout values
