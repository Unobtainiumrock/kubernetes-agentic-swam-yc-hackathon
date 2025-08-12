#!/bin/bash

# Cleanup Script for Kind Demo Cluster
# This script removes the demo cluster and all associated resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CLUSTER_NAME="demo-cluster"

echo -e "${BLUE}🧹 Cleaning up Kind Demo Cluster${NC}"
echo "=================================="

# Check if cluster exists
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo -e "${YELLOW}⚠️  Cluster '${CLUSTER_NAME}' does not exist.${NC}"
    exit 0
fi

# Confirm deletion
read -p "Are you sure you want to delete the cluster '${CLUSTER_NAME}'? (y/N): " -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}❌ Cleanup cancelled.${NC}"
    exit 0
fi

# Delete the cluster
echo -e "${YELLOW}🗑️  Deleting Kind cluster: ${CLUSTER_NAME}${NC}"
kind delete cluster --name="${CLUSTER_NAME}"

# Clean up any remaining Docker volumes (optional)
echo -e "${YELLOW}🧽 Cleaning up Docker volumes...${NC}"
docker volume prune -f

echo -e "${GREEN}✅ Cleanup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 What was cleaned up:${NC}"
echo "   ✓ Kind cluster: ${CLUSTER_NAME}"
echo "   ✓ All pods and services"
echo "   ✓ All persistent volumes"
echo "   ✓ Docker volumes (pruned)"
echo ""
echo -e "${GREEN}🎉 Your system is now clean!${NC}"
