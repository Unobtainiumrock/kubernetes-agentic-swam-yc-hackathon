#!/bin/bash

# Chaos Engineering Scenarios for Kubernetes Demo
# This script provides various failure simulation scenarios

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
    echo -e "${RED}🔥 Creating Resource Pressure${NC}"
    
    # Scale up CPU stress
    kubectl scale deployment cpu-stress --replicas=3 -n monitoring
    
    # Create memory pressure
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: memory-stress
  namespace: monitoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: memory-stress
  template:
    metadata:
      labels:
        app: memory-stress
    spec:
      containers:
      - name: stress
        image: polinux/stress
        command: ["stress"]
        args: ["--vm", "1", "--vm-bytes", "150M", "--timeout", "300s"]
        resources:
          requests:
            memory: "100Mi"
            cpu: "100m"
          limits:
            memory: "200Mi"
            cpu: "200m"
EOF
    
    echo -e "${YELLOW}⏳ Resource pressure created. Monitor with 'kubectl top nodes'${NC}"
    sleep 5
    kubectl top nodes 2>/dev/null || echo "Metrics may take a moment to appear"
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

# Main menu loop
while true; do
    show_menu
    read -p "Select a scenario (0-9): " choice
    
    case $choice in
        1) pod_failure_simulation ;;
        2) node_drain_simulation ;;
        3) resource_pressure_simulation ;;
        4) network_partition_simulation ;;
        5) storage_failure_simulation ;;
        6) rolling_update_failure ;;
        7) cascading_failure ;;
        8) recovery_demonstration ;;
        9) show_status ;;
        0) echo -e "${GREEN}👋 Goodbye!${NC}"; exit 0 ;;
        *) echo -e "${RED}Invalid option. Please try again.${NC}" ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    clear
done
