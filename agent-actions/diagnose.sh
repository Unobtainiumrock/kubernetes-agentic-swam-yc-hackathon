#!/bin/bash

# Kubernetes Diagnostics Script
# This script provides comprehensive cluster and pod diagnostics

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NAMESPACE=""
POD_NAME=""
CONTAINER_NAME=""
SHOW_LOGS=false
LOG_LINES=50

# Function to show usage
show_usage() {
    echo -e "${BLUE}Kubernetes Diagnostics Tool${NC}"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -n, --namespace NAMESPACE    Target namespace (default: all namespaces)"
    echo "  -p, --pod POD_NAME          Specific pod to diagnose"
    echo "  -c, --container CONTAINER   Specific container in pod"
    echo "  -l, --logs                  Include pod logs in output"
    echo "  --log-lines LINES           Number of log lines to show (default: 50)"
    echo "  -h, --help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Show all pods across all namespaces"
    echo "  $0 -n frontend              # Show pods in frontend namespace"
    echo "  $0 -p frontend-app-xyz -l   # Diagnose specific pod with logs"
    echo "  $0 -n backend -l            # Show backend pods with logs"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -p|--pod)
            POD_NAME="$2"
            shift 2
            ;;
        -c|--container)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -l|--logs)
            SHOW_LOGS=true
            shift
            ;;
        --log-lines)
            LOG_LINES="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Function to get pods
get_pods() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    else
        ns_flag="--all-namespaces"
    fi
    
    if [[ -n "$POD_NAME" ]]; then
        kubectl get pods $POD_NAME $ns_flag -o wide
    else
        kubectl get pods $ns_flag -o wide
    fi
}

# Function to describe pods
describe_pods() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    else
        ns_flag="--all-namespaces"
    fi
    
    if [[ -n "$POD_NAME" ]]; then
        echo -e "${BLUE}📋 Describing pod: $POD_NAME${NC}"
        kubectl describe pod $POD_NAME $ns_flag
    else
        echo -e "${BLUE}📋 Describing all pods${NC}"
        if [[ -n "$NAMESPACE" ]]; then
            kubectl describe pods -n $NAMESPACE
        else
            # For all namespaces, describe pods that are not Running
            kubectl get pods --all-namespaces --field-selector=status.phase!=Running -o name | while read pod; do
                if [[ -n "$pod" ]]; then
                    echo -e "${YELLOW}Describing problematic pod: $pod${NC}"
                    kubectl describe $pod
                    echo "---"
                fi
            done
        fi
    fi
}

# Function to get pod logs
get_logs() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    if [[ -n "$POD_NAME" ]]; then
        echo -e "${BLUE}📜 Getting logs for pod: $POD_NAME${NC}"
        local container_flag=""
        if [[ -n "$CONTAINER_NAME" ]]; then
            container_flag="-c $CONTAINER_NAME"
        fi
        kubectl logs $POD_NAME $ns_flag $container_flag --tail=$LOG_LINES
    else
        echo -e "${BLUE}📜 Getting logs for pods with issues${NC}"
        # Get logs for pods that are not running properly
        local pods
        if [[ -n "$NAMESPACE" ]]; then
            pods=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running -o name 2>/dev/null || true)
        else
            pods=$(kubectl get pods --all-namespaces --field-selector=status.phase!=Running -o name 2>/dev/null || true)
        fi
        
        if [[ -n "$pods" ]]; then
            echo "$pods" | while read pod; do
                if [[ -n "$pod" ]]; then
                    echo -e "${YELLOW}Logs for $pod:${NC}"
                    kubectl logs $pod --tail=$LOG_LINES 2>/dev/null || echo "No logs available"
                    echo "---"
                fi
            done
        else
            echo -e "${GREEN}No problematic pods found. All pods are running normally.${NC}"
        fi
    fi
}

# Function to show cluster overview
show_cluster_overview() {
    echo -e "${BLUE}🏗️ Cluster Overview${NC}"
    echo "=================="
    
    echo -e "${YELLOW}Nodes:${NC}"
    kubectl get nodes -o wide
    echo ""
    
    echo -e "${YELLOW}Namespaces:${NC}"
    kubectl get namespaces
    echo ""
    
    echo -e "${YELLOW}Resource Usage (if metrics available):${NC}"
    kubectl top nodes 2>/dev/null || echo "Metrics server not available"
    echo ""
}

# Function to show events
show_events() {
    echo -e "${BLUE}📅 Recent Events${NC}"
    echo "================"
    
    if [[ -n "$NAMESPACE" ]]; then
        kubectl get events -n $NAMESPACE --sort-by=.metadata.creationTimestamp
    else
        kubectl get events --all-namespaces --sort-by=.metadata.creationTimestamp | tail -20
    fi
    echo ""
}

# Main execution
main() {
    echo -e "${GREEN}🔍 Starting Kubernetes Diagnostics${NC}"
    echo "=================================="
    
    # Show cluster overview if no specific pod is targeted
    if [[ -z "$POD_NAME" ]]; then
        show_cluster_overview
    fi
    
    # Get pods
    echo -e "${BLUE}🚀 Pod Status${NC}"
    echo "============="
    get_pods
    echo ""
    
    # Show recent events
    show_events
    
    # Describe pods (focus on problematic ones if no specific pod)
    echo -e "${BLUE}📋 Pod Details${NC}"
    echo "=============="
    describe_pods
    echo ""
    
    # Get logs if requested
    if [[ "$SHOW_LOGS" == true ]]; then
        echo -e "${BLUE}📜 Pod Logs${NC}"
        echo "==========="
        get_logs
        echo ""
    fi
    
    echo -e "${GREEN}✅ Diagnostics completed!${NC}"
    
    # Show helpful commands
    echo -e "${BLUE}💡 Helpful Commands:${NC}"
    echo "   kubectl get pods --all-namespaces"
    echo "   kubectl describe pod <pod-name> -n <namespace>"
    echo "   kubectl logs <pod-name> -n <namespace>"
    echo "   kubectl top pods --all-namespaces"
    echo "   kubectl get events --sort-by=.metadata.creationTimestamp"
}

# Run main function
main
