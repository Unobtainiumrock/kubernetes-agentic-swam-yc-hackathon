#!/bin/bash

# 🧹 Complete Full Stack Cleanup Script
# Stops the full-stack application and cleans up the Kubernetes cluster

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Full Stack Agentic Kubernetes Demo Cleanup${NC}"
echo "=============================================="

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Stop Full Stack Application
echo
print_status "Step 1: Stopping Full Stack Application"
echo "========================================"

# Stop and remove backend container
if docker ps -q -f name=k8s-dev-container | grep -q .; then
    print_status "Stopping backend container..."
    docker stop k8s-dev-container || true
    docker rm k8s-dev-container || true
    print_success "Backend container stopped"
else
    print_status "Backend container not running"
fi

# Kill any frontend processes (Vite dev server)
if pgrep -f "vite" > /dev/null; then
    print_status "Stopping frontend processes..."
    pkill -f "vite" || true
    print_success "Frontend processes stopped"
else
    print_status "Frontend not running"
fi

# Kill any streaming stack processes
if pgrep -f "run-streaming-stack" > /dev/null; then
    print_status "Stopping streaming stack processes..."
    pkill -f "run-streaming-stack" || true
    print_success "Streaming stack processes stopped"
else
    print_status "Streaming stack not running"
fi

# Step 2: Clean Up Kubernetes Cluster
echo
print_status "Step 2: Cleaning Up Kubernetes Cluster"
echo "======================================"

CLUSTER_NAME="demo-cluster"

# Check if cluster exists
if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    print_status "Found Kind cluster: ${CLUSTER_NAME}"
    
    # Ask for confirmation
    echo
    read -p "Delete the Kubernetes cluster '${CLUSTER_NAME}'? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deleting Kind cluster: ${CLUSTER_NAME}"
        kind delete cluster --name="${CLUSTER_NAME}"
        print_success "Kubernetes cluster deleted"
    else
        print_warning "Kubernetes cluster cleanup skipped"
    fi
else
    print_status "No Kind cluster '${CLUSTER_NAME}' found"
fi

# Step 3: Clean Up Docker Resources
echo
print_status "Step 3: Cleaning Up Docker Resources"
echo "===================================="

# Remove built images (optional)
IMAGE_NAME="dfkozlov/k8s-agentic-swarm-command-center"
if docker images -q "${IMAGE_NAME}" | grep -q .; then
    echo
    read -p "Remove built container images? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing container images..."
        docker rmi $(docker images -q "${IMAGE_NAME}") || true
        print_success "Container images removed"
    else
        print_warning "Container image cleanup skipped"
    fi
else
    print_status "No container images to remove"
fi

# Clean up Docker volumes and networks
print_status "Cleaning up Docker volumes and networks..."
docker volume prune -f || true
docker network prune -f || true
print_success "Docker resources cleaned"

# Step 4: Summary
echo
print_success "🎉 Full Stack Cleanup Complete!"
echo
echo -e "${BLUE}📋 What was cleaned up:${NC}"
echo "   ✓ Backend container (k8s-dev-container)"
echo "   ✓ Frontend processes (Vite dev server)"
echo "   ✓ Streaming stack processes"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "   ✓ Kind cluster: ${CLUSTER_NAME}"
    echo "   ✓ Container images"
fi
echo "   ✓ Docker volumes and networks"
echo
echo -e "${GREEN}🚀 Ready for a fresh start!${NC}"
echo "   Run: ./setup-cluster.sh && ./start-fullstack.sh" 