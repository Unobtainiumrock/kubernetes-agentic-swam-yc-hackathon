#!/bin/bash

# Kubernetes Manifest Application Script
# This script provides safe manifest application with validation and monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
MANIFEST_FILE=""
NAMESPACE=""
DRY_RUN=false
VALIDATE_ONLY=false
FORCE=false
WAIT=true
TIMEOUT=300

# Function to show usage
show_usage() {
    echo -e "${BLUE}Kubernetes Manifest Application Tool${NC}"
    echo "Usage: $0 [OPTIONS] MANIFEST_FILE"
    echo ""
    echo "Options:"
    echo "  -n, --namespace NAMESPACE    Target namespace (overrides manifest namespace)"
    echo "  --dry-run                    Show what would be applied without doing it"
    echo "  --validate-only              Only validate the manifest, don't apply"
    echo "  -f, --force                  Force apply (may replace existing resources)"
    echo "  --no-wait                    Don't wait for resources to be ready"
    echo "  --timeout SECONDS            Timeout for waiting (default: 300)"
    echo "  -h, --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deployment.yaml                    # Apply manifest"
    echo "  $0 app.yaml -n production            # Apply to specific namespace"
    echo "  $0 config.yaml --dry-run             # Preview changes"
    echo "  $0 service.yaml --validate-only      # Only validate"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --validate-only)
            VALIDATE_ONLY=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
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
            if [[ -z "$MANIFEST_FILE" ]]; then
                MANIFEST_FILE="$1"
            else
                echo -e "${RED}Multiple manifest files specified. Please specify only one.${NC}"
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate required arguments
if [[ -z "$MANIFEST_FILE" ]]; then
    echo -e "${RED}Error: Manifest file is required${NC}"
    show_usage
    exit 1
fi

# Function to check if manifest file exists
check_manifest_exists() {
    if [[ ! -f "$MANIFEST_FILE" ]]; then
        echo -e "${RED}Error: Manifest file '$MANIFEST_FILE' not found${NC}"
        exit 1
    fi
    
    if [[ ! -r "$MANIFEST_FILE" ]]; then
        echo -e "${RED}Error: Cannot read manifest file '$MANIFEST_FILE'${NC}"
        exit 1
    fi
}

# Function to validate manifest syntax
validate_manifest() {
    echo -e "${BLUE}✅ Validating manifest syntax...${NC}"
    
    # Check YAML syntax
    if ! kubectl apply --dry-run=client -f "$MANIFEST_FILE" &>/dev/null; then
        echo -e "${RED}❌ Manifest validation failed${NC}"
        echo "Detailed error:"
        kubectl apply --dry-run=client -f "$MANIFEST_FILE" 2>&1 || true
        return 1
    fi
    
    echo -e "${GREEN}✅ Manifest syntax is valid${NC}"
    return 0
}

# Function to show manifest preview
show_manifest_preview() {
    echo -e "${BLUE}📋 Manifest Preview${NC}"
    echo "==================="
    
    # Show what resources will be created/updated
    echo -e "${YELLOW}Resources in manifest:${NC}"
    kubectl apply --dry-run=client -f "$MANIFEST_FILE" 2>/dev/null || {
        echo -e "${RED}Could not preview resources${NC}"
        return 1
    }
    echo ""
    
    # Show manifest content summary
    echo -e "${YELLOW}Manifest summary:${NC}"
    echo "   File: $MANIFEST_FILE"
    echo "   Size: $(wc -l < "$MANIFEST_FILE") lines"
    if [[ -n "$NAMESPACE" ]]; then
        echo "   Target namespace: $NAMESPACE"
    fi
    echo ""
}

# Function to check for existing resources
check_existing_resources() {
    echo -e "${BLUE}🔍 Checking for existing resources...${NC}"
    
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    # Get resource names and kinds from the manifest
    local resources
    resources=$(kubectl apply --dry-run=client -f "$MANIFEST_FILE" 2>/dev/null | grep -E "^(deployment|service|configmap|secret|pod|statefulset|daemonset)" || true)
    
    if [[ -n "$resources" ]]; then
        echo "$resources" | while IFS= read -r resource; do
            local resource_type
            local resource_name
            resource_type=$(echo "$resource" | awk '{print $1}' | sed 's/\..*//')
            resource_name=$(echo "$resource" | awk '{print $2}' | sed 's/\..*//')
            
            if kubectl get "$resource_type" "$resource_name" $ns_flag &>/dev/null; then
                echo -e "${YELLOW}⚠️  $resource_type/$resource_name already exists${NC}"
            fi
        done
    fi
    echo ""
}

# Function to apply manifest
apply_manifest() {
    local apply_cmd="kubectl apply -f $MANIFEST_FILE"
    local ns_flag=""
    
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
        apply_cmd="$apply_cmd $ns_flag"
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        apply_cmd="$apply_cmd --dry-run=client"
        echo -e "${BLUE}🔍 Dry run - would execute:${NC}"
        echo "$apply_cmd"
        echo ""
        eval "$apply_cmd"
        return
    fi
    
    if [[ "$FORCE" == true ]]; then
        apply_cmd="$apply_cmd --force"
    fi
    
    echo -e "${BLUE}🚀 Applying manifest...${NC}"
    echo "Command: $apply_cmd"
    echo ""
    
    # Execute application
    if eval "$apply_cmd"; then
        echo -e "${GREEN}✅ Manifest applied successfully${NC}"
    else
        echo -e "${RED}❌ Failed to apply manifest${NC}"
        return 1
    fi
    
    if [[ "$WAIT" == true ]]; then
        wait_for_resources
    fi
}

# Function to wait for resources to be ready
wait_for_resources() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    echo -e "${YELLOW}⏳ Waiting for resources to be ready (timeout: ${TIMEOUT}s)...${NC}"
    
    # Get deployments from the applied manifest
    local deployments
    deployments=$(kubectl get deployments $ns_flag -o name 2>/dev/null | head -5 || true)
    
    if [[ -n "$deployments" ]]; then
        echo "$deployments" | while IFS= read -r deployment; do
            if [[ -n "$deployment" ]]; then
                echo "   Waiting for $deployment..."
                kubectl wait --for=condition=available --timeout="${TIMEOUT}s" "$deployment" $ns_flag 2>/dev/null || {
                    echo -e "${YELLOW}⚠️  $deployment is taking longer than expected${NC}"
                }
            fi
        done
    fi
    
    # Get pods that might have been created
    sleep 5
    local new_pods
    new_pods=$(kubectl get pods $ns_flag --sort-by=.metadata.creationTimestamp -o name 2>/dev/null | tail -3 || true)
    
    if [[ -n "$new_pods" ]]; then
        echo "$new_pods" | while IFS= read -r pod; do
            if [[ -n "$pod" ]]; then
                echo "   Waiting for $pod..."
                kubectl wait --for=condition=ready --timeout=60s "$pod" $ns_flag 2>/dev/null || {
                    echo -e "${YELLOW}⚠️  $pod may not be ready yet${NC}"
                }
            fi
        done
    fi
    
    echo -e "${GREEN}✅ Resource readiness check completed${NC}"
}

# Function to show applied resources
show_applied_resources() {
    local ns_flag=""
    if [[ -n "$NAMESPACE" ]]; then
        ns_flag="-n $NAMESPACE"
    fi
    
    echo ""
    echo -e "${BLUE}📊 Applied Resources Status${NC}"
    echo "=========================="
    
    # Show recent resources (likely the ones we just applied)
    echo -e "${YELLOW}Recent deployments:${NC}"
    kubectl get deployments $ns_flag --sort-by=.metadata.creationTimestamp 2>/dev/null | tail -5 || echo "No deployments found"
    echo ""
    
    echo -e "${YELLOW}Recent services:${NC}"
    kubectl get services $ns_flag --sort-by=.metadata.creationTimestamp 2>/dev/null | tail -5 || echo "No services found"
    echo ""
    
    echo -e "${YELLOW}Recent pods:${NC}"
    kubectl get pods $ns_flag --sort-by=.metadata.creationTimestamp 2>/dev/null | tail -10 || echo "No pods found"
}

# Function to confirm application
confirm_application() {
    if [[ "$DRY_RUN" == true ]] || [[ "$VALIDATE_ONLY" == true ]]; then
        return 0
    fi
    
    echo -e "${YELLOW}⚠️  Confirm manifest application:${NC}"
    echo "   File: $MANIFEST_FILE"
    if [[ -n "$NAMESPACE" ]]; then
        echo "   Namespace: $NAMESPACE"
    fi
    if [[ "$FORCE" == true ]]; then
        echo -e "${RED}   Force mode: This may replace existing resources${NC}"
    fi
    echo ""
    
    read -p "Type 'yes' to confirm: " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}❌ Application cancelled${NC}"
        exit 0
    fi
}

# Main execution
main() {
    echo -e "${GREEN}🚀 Kubernetes Manifest Application Tool${NC}"
    echo "======================================="
    
    # Check if manifest file exists
    check_manifest_exists
    
    # Validate manifest
    if ! validate_manifest; then
        exit 1
    fi
    
    if [[ "$VALIDATE_ONLY" == true ]]; then
        echo -e "${GREEN}✅ Manifest validation completed successfully${NC}"
        exit 0
    fi
    
    # Show manifest preview
    show_manifest_preview
    
    # Check for existing resources
    check_existing_resources
    
    # Confirm application
    confirm_application
    
    # Apply manifest
    apply_manifest
    
    # Show applied resources (if not dry run)
    if [[ "$DRY_RUN" == false ]]; then
        show_applied_resources
    fi
    
    echo ""
    echo -e "${BLUE}💡 Useful follow-up commands:${NC}"
    echo "   kubectl get all --all-namespaces"
    echo "   kubectl describe -f $MANIFEST_FILE"
    if [[ -n "$NAMESPACE" ]]; then
        echo "   kubectl get all -n $NAMESPACE"
    fi
    echo "   kubectl get events --sort-by=.metadata.creationTimestamp"
}

# Run main function
main
