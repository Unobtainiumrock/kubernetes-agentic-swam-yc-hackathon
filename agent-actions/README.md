# Kubernetes Agent Actions

This directory contains Kubernetes command scripts designed to be converted into agent actions. Each script provides safe, validated, and interactive Kubernetes operations with comprehensive error handling and user feedback.

## 🛠️ Available Scripts

### 1. `diagnose.sh` - Cluster Diagnostics
Comprehensive cluster and pod diagnostics tool.

**Usage:**
```bash
./diagnose.sh [OPTIONS]
```

**Options:**
- `-n, --namespace NAMESPACE` - Target specific namespace
- `-p, --pod POD_NAME` - Diagnose specific pod
- `-c, --container CONTAINER` - Target specific container
- `-l, --logs` - Include pod logs in output
- `--log-lines LINES` - Number of log lines (default: 50)

**Examples:**
```bash
./diagnose.sh                          # Full cluster diagnostics
./diagnose.sh -n frontend               # Frontend namespace only
./diagnose.sh -p frontend-app-xyz -l    # Specific pod with logs
./diagnose.sh -n backend -l             # Backend pods with logs
```

**What it does:**
- Shows cluster overview (nodes, namespaces, resource usage)
- Lists pod status across namespaces
- Describes problematic pods automatically
- Shows recent events
- Retrieves logs from failing pods
- Provides helpful follow-up commands

### 2. `delete-pod.sh` - Safe Pod Deletion
Safe pod deletion with validation and confirmation.

**Usage:**
```bash
./delete-pod.sh [OPTIONS] POD_NAME
```

**Options:**
- `-n, --namespace NAMESPACE` - Target namespace
- `-f, --force` - Force deletion (grace period = 0)
- `-g, --grace-period SECONDS` - Custom grace period (default: 30)
- `--dry-run` - Preview deletion without executing

**Examples:**
```bash
./delete-pod.sh frontend-app-xyz -n frontend    # Delete specific pod
./delete-pod.sh backend-app-abc --force         # Force delete
./delete-pod.sh database-app-def --dry-run      # Preview deletion
```

**Safety features:**
- Validates pod exists before deletion
- Shows pod information and dependencies
- Warns about controller-managed pods (will be recreated)
- Requires explicit confirmation
- Monitors deletion progress
- Provides status updates

### 3. `scale-deployment.sh` - Deployment Scaling
Safe deployment scaling with monitoring and validation.

**Usage:**
```bash
./scale-deployment.sh [OPTIONS] DEPLOYMENT_NAME REPLICAS
```

**Options:**
- `-n, --namespace NAMESPACE` - Target namespace
- `--no-wait` - Don't wait for scaling completion
- `--timeout SECONDS` - Wait timeout (default: 300)

**Examples:**
```bash
./scale-deployment.sh frontend-app 5 -n frontend    # Scale to 5 replicas
./scale-deployment.sh backend-app 0                 # Scale down to 0
./scale-deployment.sh database-app 3 --no-wait      # Scale without waiting
```

**Features:**
- Shows current deployment status
- Validates deployment exists
- Confirms scaling operations
- Monitors scaling progress
- Handles scale-to-zero scenarios
- Shows final status and pod distribution

### 4. `apply-manifest.sh` - Manifest Application
Safe Kubernetes manifest application with validation.

**Usage:**
```bash
./apply-manifest.sh [OPTIONS] MANIFEST_FILE
```

**Options:**
- `-n, --namespace NAMESPACE` - Override manifest namespace
- `--dry-run` - Preview changes without applying
- `--validate-only` - Only validate, don't apply
- `-f, --force` - Force apply (may replace resources)
- `--no-wait` - Don't wait for resources to be ready
- `--timeout SECONDS` - Wait timeout (default: 300)

**Examples:**
```bash
./apply-manifest.sh deployment.yaml                 # Apply manifest
./apply-manifest.sh app.yaml -n production         # Apply to namespace
./apply-manifest.sh config.yaml --dry-run          # Preview changes
./apply-manifest.sh service.yaml --validate-only   # Only validate
```

**Safety features:**
- Validates YAML syntax before application
- Shows manifest preview and resource summary
- Checks for existing resources
- Requires confirmation for destructive operations
- Monitors resource readiness
- Shows applied resource status

## 🚀 Making Scripts Executable

```bash
chmod +x agent-actions/*.sh
```

## 🔄 Converting to Agent Actions

These scripts are designed with the following patterns for easy agent conversion:

### Input Validation
- All scripts validate required parameters
- Clear error messages for missing/invalid inputs
- Help text with usage examples

### Safety Features
- Confirmation prompts for destructive operations
- Dry-run capabilities
- Resource existence validation
- Dependency checking

### Structured Output
- Colored output for different message types
- Consistent formatting across scripts
- Progress indicators and status updates
- Helpful follow-up command suggestions

### Error Handling
- Graceful failure handling
- Detailed error messages
- Rollback suggestions where applicable
- Timeout handling for long operations

## 🎯 Agent Action Conversion Guidelines

When converting these scripts to agent actions:

1. **Parameter Extraction**: Use the argument parsing patterns as templates
2. **Validation Logic**: Reuse the validation functions
3. **Safety Checks**: Implement the confirmation and dry-run patterns
4. **Progress Monitoring**: Use the wait and status check patterns
5. **Error Handling**: Adapt the error handling and recovery logic
6. **Output Formatting**: Convert colored output to structured responses

## 🧪 Testing the Scripts

Test with your Kind cluster:

```bash
# Start with diagnostics
./agent-actions/diagnose.sh

# Try scaling
./agent-actions/scale-deployment.sh frontend-app 2 -n frontend

# Test pod deletion
./agent-actions/delete-pod.sh <pod-name> -n <namespace> --dry-run

# Apply a test manifest
./agent-actions/apply-manifest.sh <manifest-file> --validate-only
```

## 📚 Integration with Demo Environment

These scripts work seamlessly with the demo cluster:

- Use with namespaces: `frontend`, `backend`, `database`, `monitoring`
- Test with deployed applications: `frontend-app`, `backend-app`, `database-app`, `cache-app`
- Combine with chaos scenarios for comprehensive testing

## 🔗 Related Files

- `../setup-cluster.sh` - Creates the Kind cluster
- `../deploy-demo-apps.sh` - Deploys test applications
- `../chaos-scenarios.sh` - Failure simulation scenarios
- `../cleanup.sh` - Cluster cleanup
