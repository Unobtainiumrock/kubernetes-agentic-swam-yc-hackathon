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
    echo "1. Pod Failure Simulation (Delete healthy pods)"
    echo "2. Image Pull Failures (Deploy broken images)"
    echo "3. Crash Loop Simulation (Deploy failing apps)"
    echo "4. Resource Pressure (CPU/Memory)"
    echo "5. Service Scaling Chaos (Scale up/down)"
    echo "6. Network Issues (DNS/connectivity)"
    echo "7. Rolling Update Failures"
    echo "8. Recovery Demonstration (Fix issues)"
    echo "9. Show Current Status"
    echo "0. Exit"
    echo ""
}

# Pod failure simulation - delete healthy pods
pod_failure_simulation() {
    echo -e "${RED}💥 Simulating Pod Failures${NC}"
    echo "Deleting healthy pods to trigger recreation..."
    
    # Delete frontend pods
    echo "🎯 Deleting frontend pods..."
    kubectl delete pod -l app=frontend -n frontend --ignore-not-found=true
    
    # Delete some backend pods
    echo "🎯 Deleting backend pods..."
    kubectl delete pod -l app=backend -n backend --ignore-not-found=true | head -2
    
    echo "✅ Pod deletion chaos complete! Pods will be recreated automatically."
    echo "💡 Watch: kubectl get pods --all-namespaces -w"
}

# Image pull failure simulation
image_pull_failure_simulation() {
    echo -e "${RED}🖼️ Simulating Image Pull Failures${NC}"
    echo "Deploying pods with nonexistent images..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken-image-app
  namespace: frontend
  labels:
    app: broken-image-app
    tier: frontend
    chaos: "true"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: broken-image-app
  template:
    metadata:
      labels:
        app: broken-image-app
        tier: frontend
        chaos: "true"
    spec:
      containers:
      - name: broken-app
        image: nginx:nonexistent-tag-12345
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "32Mi"
            cpu: "50m"
          limits:
            memory: "64Mi"
            cpu: "100m"
EOF
    
    echo "✅ ImagePullBackOff chaos deployed!"
    echo "💡 Watch: kubectl get pods -n frontend | grep broken-image"
}

# Crash loop simulation
crash_loop_simulation() {
    echo -e "${RED}💥 Simulating Crash Loop Failures${NC}"
    echo "Deploying applications that immediately crash..."
    
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crash-loop-app
  namespace: frontend
  labels:
    app: crash-loop-app
    tier: frontend
    chaos: "true"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: crash-loop-app
  template:
    metadata:
      labels:
        app: crash-loop-app
        tier: frontend
        chaos: "true"
    spec:
      containers:
      - name: crash-app
        image: busybox:1.35
        command: ["/bin/sh"]
        args: ["-c", "echo 'Starting application...' && sleep 2 && echo 'Critical error occurred!' && exit 1"]
        resources:
          requests:
            memory: "16Mi"
            cpu: "25m"
          limits:
            memory: "32Mi"
            cpu: "50m"
EOF
    
    echo "✅ CrashLoopBackOff chaos deployed!"
    echo "💡 Watch: kubectl get pods -n frontend | grep crash-loop"
}

# Resource pressure simulation
resource_pressure_simulation() {
    echo -e "${RED}⚡ Simulating Resource Pressure${NC}"
    echo "Scaling up CPU-intensive workloads..."
    
    # Scale up CPU stress pods
    kubectl scale deployment cpu-stress --replicas=3 -n monitoring --ignore-not-found=true
    
    # Scale down critical services
    echo "🎯 Reducing backend capacity..."
    kubectl scale deployment backend-app --replicas=1 -n backend
    
    echo "✅ Resource pressure chaos applied!"
    echo "💡 Watch: kubectl top nodes"
}

# Service scaling chaos
service_scaling_chaos() {
    echo -e "${RED}📊 Simulating Service Scaling Issues${NC}"
    echo "Creating availability problems through scaling..."
    
    # Scale different services randomly
    kubectl scale deployment frontend-app --replicas=1 -n frontend
    kubectl scale deployment cache-app --replicas=0 -n backend
    
    echo "✅ Service scaling chaos applied!"
    echo "💡 Watch: kubectl get deployments --all-namespaces"
}

# Network issues simulation (placeholder)
network_issues_simulation() {
    echo -e "${RED}🌐 Simulating Network Issues${NC}"
    echo "Breaking service connectivity..."
    
    # Patch a service to use wrong image (will cause DNS resolution issues)
    kubectl patch deployment database-app -n database -p '{"spec":{"template":{"spec":{"containers":[{"name":"database","image":"nonexistent:broken"}]}}}}'
    
    echo "✅ Network chaos applied!"
    echo "💡 Watch: kubectl get pods -n database"
}

# Rolling update failures (placeholder) 
rolling_update_failure() {
    echo -e "${RED}🔄 Simulating Rolling Update Failures${NC}"
    echo "Triggering failed rolling updates..."
    
    # Update to a broken image
    kubectl set image deployment/backend-app backend=httpd:nonexistent -n backend
    
    echo "✅ Rolling update chaos applied!"
    echo "💡 Watch: kubectl rollout status deployment/backend-app -n backend"
}

# Recovery demonstration
recovery_demonstration() {
    echo -e "${GREEN}🔧 Demonstrating Recovery${NC}"
    echo "Fixing chaos issues..."
    
    # Remove chaos deployments
    echo "🧹 Removing broken deployments..."
    kubectl delete deployment broken-image-app -n frontend --ignore-not-found=true
    kubectl delete deployment crash-loop-app -n frontend --ignore-not-found=true
    
    # Fix broken images
    echo "🔧 Fixing broken images..."
    kubectl patch deployment database-app -n database -p '{"spec":{"template":{"spec":{"containers":[{"name":"database","image":"redis:alpine"}]}}}}' --ignore-not-found=true
    kubectl set image deployment/backend-app backend=httpd:2.4 -n backend --ignore-not-found=true
    
    # Scale services back to normal
    echo "📈 Restoring normal capacity..."
    kubectl scale deployment frontend-app --replicas=3 -n frontend --ignore-not-found=true
    kubectl scale deployment backend-app --replicas=4 -n backend --ignore-not-found=true
    kubectl scale deployment cache-app --replicas=2 -n backend --ignore-not-found=true
    kubectl scale deployment cpu-stress --replicas=1 -n monitoring --ignore-not-found=true
    
    echo "✅ Recovery complete!"
    echo "💡 Watch: kubectl get pods --all-namespaces"
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
        2) image_pull_failure_simulation ;;
        3) crash_loop_simulation ;;
        4) resource_pressure_simulation ;;
        5) service_scaling_chaos ;;
        6) network_issues_simulation ;;
        7) rolling_update_failure ;;
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
    echo "  2 - Image Pull Failures"
    echo "  3 - Crash Loop Simulation"
    echo "  4 - Resource Pressure (CPU/Memory/IO)"
    echo "  5 - Service Scaling Chaos"
    echo "  6 - Network Issues (DNS/connectivity)"
    echo "  7 - Rolling Update Failures"
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
