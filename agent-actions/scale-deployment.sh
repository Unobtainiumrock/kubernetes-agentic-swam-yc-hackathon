#!/bin/bash

# Kubernetes Deployment Scaling Script
# This script provides safe deployment scaling with validation and monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NAMESPACE=""
DEPLOYMENT_NAME=""
REPLICAS=""
WAIT=true
TIMEOUT=300

# Function to show usage
show_usage() {
    echo -e "${BLUE}Kubernetes Deployment Scaling Tool${NC}"
    echo "Usage: $0 [OPTIONS] DEPLOYMENT_NAME REPLICAS"
    echo ""
    echo "Options:"
    echo "  -n, --namespace NAMESPACE    Target namespace (required if not default)"
    echo "  --no-wait                    Don't wait for scaling to complete"
    echo "  --timeout SECONDS            Timeout for waiting (default: 300)"
    echo "  -h, --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 frontend-app 5 -n frontend        # Scale frontend to 5 replicas"
    echo "  $0 backend-app 0                     # Scale down to 0 (stop all pods)"
    echo "  $0 database-app 3 --no-wait         # Scale without waiting"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --no-wait)
            WAIT=false
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
        *)
            if [[ -z "$DEPLOYMENT_NAME" ]]; then
                DEPLOYMENT_NAME="$1"
            elif [[ -z "$REPLICAS" ]]; then
                REPLICAS="$1"
            else
                echo -e "${RED}Too many arguments${NC}"
                show_usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate required arguments
if [[ -z "$DEPLOYMENT_NAME" ]]; then
    echo -e "${RED}Error: Deployment name is required${NC}"
    show_usage
    exit 1
fi

if [[ -z "$REPLICAS" ]]; then
    echo -e "${RED}Error: Number of replicas is required${NC}"
    show_usage
    exit 1
fi

# Validate replicas is a number
if ! [[ "$REPLICAS" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}Error: Replicas must be a non-negative integer${NC}"
    exit 1
fi

# Function to check if deployment exists
check_deployment_exists() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    if ! kubectl get deployment "$DEPLOYMENT_NAME" $ns_flag &>/dev/null; then
        echo -e "${RED}Error: Deployment '$DEPLOYMENT_NAME' not found${NC}"
        if [[ -n "$NAMESPACE" ]]; then
            echo "In namespace: $NAMESPACE"
        fi
        echo ""
        echo -e "${BLUE}Available deployments:${NC}"
        kubectl get deployments $ns_flag 2>/dev/null || echo "No deployments found"
        exit 1
    fi
}

# Function to show current deployment status
show_deployment_status() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    echo -e "${BLUE}📊 Current Deployment Status${NC}"
    echo "============================"
    kubectl get deployment "$DEPLOYMENT_NAME" $ns_flag -o wide
    echo ""
    
    echo -e "${BLUE}🚀 Current Pods${NC}"
    echo "==============="
    kubectl get pods $ns_flag -l app="$(kubectl get deployment "$DEPLOYMENT_NAME" $ns_flag -o jsonpath='{.spec.selector.matchLabels.app}' 2>/dev/null || echo "$DEPLOYMENT_NAME")" -o wide 2>/dev/null || {
        # Fallback: show pods with deployment name in the name
        kubectl get pods $ns_flag | grep "$DEPLOYMENT_NAME" || echo "No pods found for this deployment"
    }
    echo ""
}

# Function to get current replica count
get_current_replicas() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    kubectl get deployment "$DEPLOYMENT_NAME" $ns_flag -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0"
}

# Function to scale deployment
scale_deployment() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    local current_replicas
    current_replicas=$(get_current_replicas)
    
    echo -e "${BLUE}⚖️  Scaling Deployment${NC}"
    echo "====================="
    echo "   Deployment: $DEPLOYMENT_NAME"
    if [[ -n "$NAMESPACE" ]]; then
        echo "   Namespace: $NAMESPACE"
    fi
    echo "   Current replicas: $current_replicas"
    echo "   Target replicas: $REPLICAS"
    echo ""
    
    if [[ "$current_replicas" == "$REPLICAS" ]]; then
        echo -e "${YELLOW}⚠️  Deployment is already at $REPLICAS replicas${NC}"
        return 0
    fi
    
    # Perform scaling
    echo -e "${YELLOW}🔄 Scaling deployment...${NC}"
    kubectl scale deployment "$DEPLOYMENT_NAME" $ns_flag --replicas="$REPLICAS"
    
    echo -e "${GREEN}✅ Scaling command issued${NC}"
    
    if [[ "$WAIT" == true ]]; then
        wait_for_scaling
    else
        echo -e "${YELLOW}⏩ Not waiting for scaling to complete (--no-wait specified)${NC}"
    fi
}

# Function to wait for scaling to complete
wait_for_scaling() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    echo -e "${YELLOW}⏳ Waiting for scaling to complete (timeout: ${TIMEOUT}s)...${NC}"
    
    if [[ "$REPLICAS" == "0" ]]; then
        # Special case for scaling to 0
        echo "   Waiting for all pods to terminate..."
        kubectl wait --for=delete pods $ns_flag -l app="$(kubectl get deployment "$DEPLOYMENT_NAME" $ns_flag -o jsonpath='{.spec.selector.matchLabels.app}' 2>/dev/null || echo "$DEPLOYMENT_NAME")" --timeout="${TIMEOUT}s" 2>/dev/null || {
            echo -e "${YELLOW}⚠️  Some pods may still be terminating${NC}"
        }
    else
        # Wait for deployment to be ready
        kubectl wait --for=condition=available --timeout="${TIMEOUT}s" deployment/"$DEPLOYMENT_NAME" $ns_flag || {
            echo -e "${YELLOW}⚠️  Scaling is taking longer than expected${NC}"
            echo "   Current status:"
            kubectl get deployment "$DEPLOYMENT_NAME" $ns_flag
            return 1
        }
    fi
    
    echo -e "${GREEN}✅ Scaling completed successfully${NC}"
}

# Function to show final status
show_final_status() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    echo ""
    echo -e "${BLUE}📊 Final Status${NC}"
    echo "==============="
    kubectl get deployment "$DEPLOYMENT_NAME" $ns_flag -o wide
    echo ""
    
    if [[ "$REPLICAS" != "0" ]]; then
        echo -e "${BLUE}🚀 Running Pods${NC}"
        echo "==============="
        kubectl get pods $ns_flag -l app="$(kubectl get deployment "$DEPLOYMENT_NAME" $ns_flag -o jsonpath='{.spec.selector.matchLabels.app}' 2>/dev/null || echo "$DEPLOYMENT_NAME")" -o wide 2>/dev/null || {
            kubectl get pods $ns_flag | grep "$DEPLOYMENT_NAME" || echo "No pods found"
        }
    else
        echo -e "${YELLOW}No pods running (scaled to 0)${NC}"
    fi
}

# Function to confirm scaling
confirm_scaling() {
    local current_replicas
    current_replicas=$(get_current_replicas)
    
    echo -e "${YELLOW}⚠️  Confirm scaling operation:${NC}"
    echo "   Deployment: $DEPLOYMENT_NAME"
    if [[ -n "$NAMESPACE" ]]; then
        echo "   Namespace: $NAMESPACE"
    fi
    echo "   Current replicas: $current_replicas"
    echo "   Target replicas: $REPLICAS"
    
    if [[ "$REPLICAS" == "0" ]]; then
        echo -e "${RED}   This will STOP all pods for this deployment!${NC}"
    elif [[ "$current_replicas" -gt "$REPLICAS" ]]; then
        echo -e "${YELLOW}   This will REDUCE the number of running pods${NC}"
    else
        echo -e "${GREEN}   This will INCREASE the number of running pods${NC}"
    fi
    
    echo ""
    read -p "Type 'yes' to confirm: " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}❌ Scaling cancelled${NC}"
        exit 0
    fi
}

# Main execution
main() {
    echo -e "${GREEN}⚖️  Kubernetes Deployment Scaling Tool${NC}"
    echo "======================================"
    
    # Check if deployment exists
    check_deployment_exists
    
    # Show current status
    show_deployment_status
    
    # Confirm scaling
    confirm_scaling
    
    # Scale deployment
    scale_deployment
    
    # Show final status
    show_final_status
    
    echo ""
    echo -e "${BLUE}💡 Useful follow-up commands:${NC}"
    echo "   kubectl get deployments --all-namespaces"
    echo "   kubectl get pods --all-namespaces"
    if [[ -n "$NAMESPACE" ]]; then
        echo "   kubectl get pods -n $NAMESPACE"
    fi
    echo "   kubectl describe deployment $DEPLOYMENT_NAME"
}

# Run main function
main
