#!/bin/bash

# Chaos Engineering Scenarios for Kubernetes Demo
# This script provides various failure simulation scenarios
# 
# Usage:
#   ./chaos-scenarios.sh                    # Interactive mode
#   ./chaos-scenarios.sh [scenario-number]  # Direct execution
#   ./chaos-scenarios.sh 3                  # Launch resource pressure
#   ./chaos-scenarios.sh status              # Show current status
#   ./chaos-scenarios.sh cleanup             # Clean up all chaos

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_menu() {
    echo -e "${BLUE}🔥 Kubernetes Chaos Engineering Scenarios${NC}"
    echo "=========================================="
    echo "1. Pod Failure Simulation"
    echo "2. Node Drain Simulation"
    echo "3. Resource Pressure (CPU/Memory)"
    echo "4. Network Partition Simulation"
    echo "5. Storage Failure Simulation"
    echo "6. Rolling Update with Failures"
    echo "7. Cascading Failure Scenario"
    echo "8. Recovery Demonstration"
    echo "9. Show Current Status"
    echo "0. Exit"
    echo ""
}

# pod_failure_simulation() {
#     echo -e "${RED}💥 Simulating Pod Failures${NC}"
#     echo "Randomly killing pods across different namespaces..."
    

#     # Kill random frontend pods
#     FRONTEND_PODS=($(kubectl get pods -n frontend --no-headers -o custom-columns=":metadata.name" | grep '^frontend-app' | head -2))
#     for pod in "${FRONTEND_PODS[@]}"; do
#         echo "Deleting $pod"
#         kubectl delete pod "$pod" -n frontend &
#     done
#     wait

    
    # # Kill random backend pods
    # BACKEND_PODS=($(kubectl get pods -n backend -o name | head -2))
    # for pod in "${BACKEND_PODS[@]}"; do
    #     echo "Deleting $pod"
    #     kubectl delete "$pod" -n backend &
    # done
    
#     wait
#     echo -e "${YELLOW}⏳ Waiting for pods to recover...${NC}"
#     sleep 10
#     kubectl get pods --all-namespaces | grep -E "(frontend|backend)"
# }

# node_drain_simulation() {
#     echo -e "${RED}🚫 Simulating Node Drain${NC}"
    
#     # Get a worker node
#     NODE=$(kubectl get nodes -o name | grep -v control-plane | head -1 | cut -d'/' -f2)
    
#     if [ -z "$NODE" ]; then
#         echo -e "${RED}No worker nodes found!${NC}"
#         return 1
#     fi
    
#     echo "Draining node: $NODE"
#     kubectl cordon "$NODE"
#     kubectl drain "$NODE" --ignore-daemonsets --delete-emptydir-data --force --grace-period=30
    
#     echo -e "${YELLOW}Node $NODE is now drained. Pods should reschedule to other nodes.${NC}"
#     echo "Run option 8 (Recovery) to uncordon the node."
    
#     sleep 5
#     kubectl get pods --all-namespaces -o wide | grep -v Running || true
# }

resource_pressure_simulation() {
    echo -e "${RED}🔥 Creating AGGRESSIVE Resource Pressure${NC}"
    echo "This will create significant stress that should impact demo applications..."
    
    # Scale up existing CPU stress to maximum
    echo -e "${YELLOW}📈 Scaling up existing CPU stress deployment...${NC}"
    kubectl scale deployment cpu-stress --replicas=8 -n monitoring 2>/dev/null || echo "CPU stress deployment not found, creating new one..."
    
    # Create multiple aggressive stress deployments
    echo -e "${YELLOW}💾 Creating aggressive memory pressure (will consume ~2GB per node)...${NC}"
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: memory-bomb
  namespace: monitoring
spec:
  replicas: 6
  selector:
    matchLabels:
      app: memory-bomb
  template:
    metadata:
      labels:
        app: memory-bomb
    spec:
      containers:
      - name: stress
        image: polinux/stress
        command: ["stress"]
        args: ["--vm", "2", "--vm-bytes", "400M", "--vm-hang", "0", "--timeout", "600s"]
        resources:
          requests:
            memory: "300Mi"
            cpu: "200m"
          limits:
            memory: "500Mi"
            cpu: "500m"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cpu-bomb
  namespace: monitoring
spec:
  replicas: 8
  selector:
    matchLabels:
      app: cpu-bomb
  template:
    metadata:
      labels:
        app: cpu-bomb
    spec:
      containers:
      - name: stress
        image: polinux/stress
        command: ["stress"]
        args: ["--cpu", "2", "--timeout", "600s", "--verbose"]
        resources:
          requests:
            memory: "50Mi"
            cpu: "400m"
          limits:
            memory: "100Mi"
            cpu: "800m"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: io-bomb
  namespace: monitoring
spec:
  replicas: 4
  selector:
    matchLabels:
      app: io-bomb
  template:
    metadata:
      labels:
        app: io-bomb
    spec:
      containers:
      - name: stress
        image: polinux/stress
        command: ["stress"]
        args: ["--io", "4", "--hdd", "2", "--hdd-bytes", "100M", "--timeout", "600s"]
        resources:
          requests:
            memory: "100Mi"
            cpu: "200m"
          limits:
            memory: "200Mi"
            cpu: "400m"
EOF
    
    echo -e "${RED}⚠️  AGGRESSIVE RESOURCE PRESSURE DEPLOYED!${NC}"
    echo -e "${YELLOW}This will create:${NC}"
    echo "  • 6 memory-bomb pods consuming ~400MB each (2.4GB total)"
    echo "  • 8 cpu-bomb pods consuming 2 CPU cores each"
    echo "  • 4 io-bomb pods creating disk I/O pressure"
    echo "  • Plus scaled CPU stress deployment"
    echo ""
    echo -e "${RED}Expected effects:${NC}"
    echo "  • Node resource exhaustion"
    echo "  • Pod evictions due to memory pressure"
    echo "  • Application slowdowns and potential crashes"
    echo "  • Kubernetes scheduler stress"
    echo ""
    echo -e "${YELLOW}⏳ Monitoring cluster state...${NC}"
    
    # Show immediate impact
    sleep 10
    echo -e "${BLUE}📊 Current resource usage:${NC}"
    kubectl top nodes 2>/dev/null || echo "Metrics loading..."
    echo ""
    echo -e "${BLUE}🔍 Checking for pod evictions:${NC}"
    kubectl get events --sort-by='.lastTimestamp' | grep -E '(Evicted|FailedScheduling|OutOfMemory)' | tail -5 || echo "No evictions yet..."
    echo ""
    echo -e "${YELLOW}💡 Monitor with:${NC}"
    echo "  kubectl top nodes"
    echo "  kubectl get pods --all-namespaces | grep -E '(Evicted|Pending|Error)'"
    echo "  kubectl get events --sort-by='.lastTimestamp' | tail -10"
    echo "  watch 'kubectl get pods --all-namespaces'"
}

network_partition_simulation() {
    echo -e "${RED}🌐 Simulating Network Issues${NC}"
    
    # Create a network policy that blocks traffic between namespaces
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-cross-namespace
  namespace: backend
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: backend
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: backend
EOF
    
    echo -e "${YELLOW}Network policy applied. Cross-namespace communication blocked.${NC}"
    echo "This simulates network partition between services."
}

storage_failure_simulation() {
    echo -e "${RED}💾 Simulating Storage Issues${NC}"
    
    # Scale down database to simulate storage issues
    kubectl scale statefulset database-app --replicas=0 -n database
    
    echo -e "${YELLOW}Database scaled down to simulate storage failure.${NC}"
    echo "Applications depending on database will start failing."
    
    sleep 5
    kubectl get pods -n database
}

# rolling_update_failure() {
#     echo -e "${RED}🔄 Simulating Failed Rolling Update${NC}"
    
#     # Update frontend with a bad image
#     kubectl patch deployment frontend-app -n frontend -p='{"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:bad-tag"}]}}}}'
    
#     echo -e "${YELLOW}Rolling update initiated with bad image. Deployment will fail.${NC}"
#     sleep 10
#     kubectl rollout status deployment/frontend-app -n frontend --timeout=60s || true
#     kubectl get pods -n frontend
# }

# cascading_failure() {
#     echo -e "${RED}💀 Simulating Cascading Failure${NC}"
    
#     echo "Step 1: Database failure"
#     kubectl scale statefulset database-app --replicas=0 -n database
#     sleep 5
    
#     echo "Step 2: Backend overload (scaling up to simulate traffic)"
#     kubectl scale deployment backend-app --replicas=8 -n backend
#     sleep 5
    
#     echo "Step 3: Resource exhaustion"
#     kubectl scale deployment cpu-stress --replicas=4 -n monitoring
#     sleep 5
    
#     echo "Step 4: Frontend instability"
#     kubectl patch deployment frontend-app -n frontend -p='{"spec":{"template":{"spec":{"containers":[{"name":"nginx","resources":{"limits":{"memory":"50Mi"}}}]}}}}'
    
#     echo -e "${YELLOW}Cascading failure initiated. Multiple systems affected.${NC}"
#     sleep 10
#     kubectl get pods --all-namespaces | grep -v Running || true
# }

recovery_demonstration() {
    echo -e "${GREEN}🔧 Initiating Recovery Procedures${NC}"
    
    # Uncordon any cordoned nodes
    for node in $(kubectl get nodes -o name | cut -d'/' -f2); do
        kubectl uncordon "$node" 2>/dev/null || true
    done
    
    # Scale back database
    kubectl scale statefulset database-app --replicas=2 -n database
    
    # Fix frontend deployment
    kubectl patch deployment frontend-app -n frontend -p='{"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:1.21","resources":{"limits":{"memory":"128Mi"}}}]}}}}'
    
    # Scale back backend
    kubectl scale deployment backend-app --replicas=4 -n backend
    
    # Reduce stress
    kubectl scale deployment cpu-stress --replicas=1 -n monitoring
    kubectl delete deployment memory-stress -n monitoring --ignore-not-found=true
    
    # Remove network policy
    kubectl delete networkpolicy deny-cross-namespace -n backend --ignore-not-found=true
    
    echo -e "${YELLOW}⏳ Waiting for recovery...${NC}"
    sleep 30
    
    echo -e "${GREEN}✅ Recovery procedures completed!${NC}"
    show_status
}

show_status() {
    echo -e "${BLUE}📊 Current Cluster Status${NC}"
    echo "=========================="
    
    echo -e "${YELLOW}Nodes:${NC}"
    kubectl get nodes -o wide
    echo ""
    
    echo -e "${YELLOW}Pods by Namespace:${NC}"
    kubectl get pods --all-namespaces -o wide
    echo ""
    
    echo -e "${YELLOW}Resource Usage:${NC}"
    kubectl top nodes 2>/dev/null || echo "Metrics server may still be starting..."
    echo ""
    
    echo -e "${YELLOW}HPA Status:${NC}"
    kubectl get hpa --all-namespaces
    echo ""
    
    echo -e "${YELLOW}Services:${NC}"
    kubectl get services --all-namespaces
}

# Function to execute scenario by number
execute_scenario() {
    case $1 in
        1) pod_failure_simulation ;;
        2) node_drain_simulation ;;
        3) resource_pressure_simulation ;;
        4) network_partition_simulation ;;
        5) storage_failure_simulation ;;
        6) rolling_update_failure ;;
        7) cascading_failure ;;
        8) recovery_demonstration ;;
        9|status) show_status ;;
        cleanup) recovery_demonstration ;;
        *) echo -e "${RED}Invalid scenario: $1${NC}"; show_usage; exit 1 ;;
    esac
}

# Show usage information
show_usage() {
    echo -e "${BLUE}Kubernetes Chaos Engineering Scenarios${NC}"
    echo ""
    echo "Usage:"
    echo "  $0                    # Interactive mode"
    echo "  $0 [scenario]         # Direct execution"
    echo "  $0 status             # Show current status"
    echo "  $0 cleanup            # Clean up all chaos"
    echo ""
    echo "Available scenarios:"
    echo "  1 - Pod Failure Simulation"
    echo "  2 - Node Drain Simulation"
    echo "  3 - Resource Pressure (CPU/Memory/IO)"
    echo "  4 - Network Partition Simulation"
    echo "  5 - Storage Failure Simulation"
    echo "  6 - Rolling Update with Failures"
    echo "  7 - Cascading Failure Scenario"
    echo "  8 - Recovery Demonstration"
    echo ""
    echo "Examples:"
    echo "  $0 3                  # Launch resource pressure scenario"
    echo "  $0 status             # Check current cluster status"
    echo "  $0 cleanup            # Clean up all chaos scenarios"
    echo ""
    echo -e "${YELLOW}💡 After launching a scenario, use these commands to observe:${NC}"
    echo "  k9s                                    # Interactive cluster viewer"
    echo "  kubectl get pods --all-namespaces     # List all pods"
    echo "  kubectl top nodes                     # Node resource usage"
    echo "  kubectl get events --sort-by='.lastTimestamp' | tail -10"
    echo "  watch 'kubectl get pods --all-namespaces | grep -E \"(Evicted|Pending|Error)\"'"
}

# Handle command line arguments
if [ $# -eq 0 ]; then
    # Interactive mode
    while true; do
        show_menu
        read -p "Select a scenario (0-9): " choice
        
        case $choice in
            0) echo -e "${GREEN}👋 Goodbye!${NC}"; exit 0 ;;
            *) execute_scenario $choice ;;
        esac
        
        echo ""
        echo -e "${YELLOW}💡 Scenario launched! You can now use k9s or kubectl to observe the effects.${NC}"
        echo -e "${BLUE}Useful commands:${NC}"
        echo "  k9s"
        echo "  kubectl get pods --all-namespaces"
        echo "  kubectl top nodes"
        echo ""
        read -p "Press Enter to return to menu or Ctrl+C to exit..."
        clear
    done
else
    # Direct execution mode
    case $1 in
        help|--help|-h)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${BLUE}🚀 Launching chaos scenario: $1${NC}"
            execute_scenario $1
            echo ""
            echo -e "${GREEN}✅ Scenario '$1' has been launched!${NC}"
            echo -e "${YELLOW}💡 You can now observe the effects with:${NC}"
            echo "  k9s                                    # Interactive cluster viewer"
            echo "  kubectl get pods --all-namespaces     # List all pods"
            echo "  kubectl top nodes                     # Node resource usage"
            echo "  $0 status                             # Check scenario status"
            echo "  $0 cleanup                            # Clean up when done"
            ;;
    esac
fi
