#!/bin/bash

# Kubernetes Pod Deletion Script
# This script provides safe pod deletion with confirmation and validation

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
FORCE=false
GRACE_PERIOD=30
DRY_RUN=false

# Function to show usage
show_usage() {
    echo -e "${BLUE}Kubernetes Pod Deletion Tool${NC}"
    echo "Usage: $0 [OPTIONS] POD_NAME"
    echo ""
    echo "Options:"
    echo "  -n, --namespace NAMESPACE    Target namespace (required if not default)"
    echo "  -f, --force                  Force deletion (sets grace period to 0)"
    echo "  -g, --grace-period SECONDS   Grace period for deletion (default: 30)"
    echo "  --dry-run                    Show what would be deleted without doing it"
    echo "  -h, --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 frontend-app-xyz -n frontend     # Delete specific pod"
    echo "  $0 backend-app-abc --force          # Force delete pod"
    echo "  $0 database-app-def --dry-run       # Preview deletion"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            GRACE_PERIOD=0
            shift
            ;;
        -g|--grace-period)
            GRACE_PERIOD="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
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
            if [[ -z "$POD_NAME" ]]; then
                POD_NAME="$1"
            else
                echo -e "${RED}Multiple pod names specified. Please specify only one.${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate required arguments
if [[ -z "$POD_NAME" ]]; then
    echo -e "${RED}Error: Pod name is required${NC}"
    show_usage
    exit 1
fi

# Function to check if pod exists
check_pod_exists() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    if ! kubectl get pod "$POD_NAME" $ns_flag &>/dev/null; then
        echo -e "${RED}Error: Pod '$POD_NAME' not found${NC}"
        if [[ -n "$NAMESPACE" ]]; then
            echo "In namespace: $NAMESPACE"
        fi
        exit 1
    fi
}

# Function to show pod information
show_pod_info() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    echo -e "${BLUE}📋 Pod Information${NC}"
    echo "=================="
    kubectl get pod "$POD_NAME" $ns_flag -o wide
    echo ""
    
    echo -e "${BLUE}📊 Pod Details${NC}"
    echo "=============="
    kubectl describe pod "$POD_NAME" $ns_flag | head -20
    echo ""
}

# Function to check for dependent resources
check_dependencies() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    echo -e "${BLUE}🔍 Checking for controlling resources...${NC}"
    
    # Get pod details to check for owner references
    local owner_info
    owner_info=$(kubectl get pod "$POD_NAME" $ns_flag -o jsonpath='{.metadata.ownerReferences[*].kind}:{.metadata.ownerReferences[*].name}' 2>/dev/null || true)
    
    if [[ -n "$owner_info" ]]; then
        echo -e "${YELLOW}⚠️  This pod is managed by: $owner_info${NC}"
        echo -e "${YELLOW}   The pod will likely be recreated automatically.${NC}"
        echo ""
    else
        echo -e "${GREEN}✅ Pod appears to be standalone (not managed by a controller)${NC}"
        echo ""
    fi
}

# Function to delete pod
delete_pod() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    local delete_cmd="kubectl delete pod $POD_NAME $ns_flag"
    
    if [[ "$FORCE" == true ]]; then
        delete_cmd="$delete_cmd --force --grace-period=0"
    elif [[ "$GRACE_PERIOD" != "30" ]]; then
        delete_cmd="$delete_cmd --grace-period=$GRACE_PERIOD"
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        delete_cmd="$delete_cmd --dry-run=client"
        echo -e "${BLUE}🔍 Dry run - would execute:${NC}"
        echo "$delete_cmd"
        echo ""
        eval "$delete_cmd"
        return
    fi
    
    echo -e "${RED}🗑️  Deleting pod: $POD_NAME${NC}"
    if [[ -n "$NAMESPACE" ]]; then
        echo "   Namespace: $NAMESPACE"
    fi
    echo "   Grace period: $GRACE_PERIOD seconds"
    echo ""
    
    # Execute deletion
    eval "$delete_cmd"
    
    echo -e "${GREEN}✅ Pod deletion initiated${NC}"
    
    # Wait and show status
    echo -e "${YELLOW}⏳ Waiting for pod to terminate...${NC}"
    local timeout=60
    local count=0
    
    while kubectl get pod "$POD_NAME" $ns_flag &>/dev/null && [[ $count -lt $timeout ]]; do
        sleep 1
        ((count++))
        if [[ $((count % 10)) -eq 0 ]]; then
            echo "   Still terminating... (${count}s)"
        fi
    done
    
    if kubectl get pod "$POD_NAME" $ns_flag &>/dev/null; then
        echo -e "${YELLOW}⚠️  Pod is taking longer than expected to terminate${NC}"
        echo "   Current status:"
        kubectl get pod "$POD_NAME" $ns_flag
    else
        echo -e "${GREEN}✅ Pod successfully deleted${NC}"
    fi
}

# Function to confirm deletion
confirm_deletion() {
    if [[ "$DRY_RUN" == true ]]; then
        return 0
    fi
    
    echo -e "${YELLOW}⚠️  Are you sure you want to delete pod '$POD_NAME'?${NC}"
    if [[ -n "$NAMESPACE" ]]; then
        echo "   Namespace: $NAMESPACE"
    fi
    if [[ "$FORCE" == true ]]; then
        echo -e "${RED}   This is a FORCE deletion (immediate)${NC}"
    fi
    echo ""
    
    read -p "Type 'yes' to confirm: " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}❌ Deletion cancelled${NC}"
        exit 0
    fi
}

# Main execution
main() {
    echo -e "${GREEN}🗑️  Kubernetes Pod Deletion Tool${NC}"
    echo "================================="
    
    # Check if pod exists
    check_pod_exists
    
    # Show pod information
    show_pod_info
    
    # Check dependencies
    check_dependencies
    
    # Confirm deletion
    confirm_deletion
    
    # Delete pod
    delete_pod
    
    echo ""
    echo -e "${BLUE}💡 Useful follow-up commands:${NC}"
    echo "   kubectl get pods --all-namespaces"
    echo "   kubectl get events --sort-by=.metadata.creationTimestamp"
    if [[ -n "$NAMESPACE" ]]; then
        echo "   kubectl get pods -n $NAMESPACE"
    fi
}

# Run main function
main
