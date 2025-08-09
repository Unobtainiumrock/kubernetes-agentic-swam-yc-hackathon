#!/bin/bash

# Kind Cluster Demo Environment Setup Script
# This script creates a medium complex Kubernetes environment for demonstrations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="demo-cluster"
CONFIG_FILE="kind-cluster-config.yaml"

echo -e "${BLUE}🚀 Setting up Kind Kubernetes Demo Cluster${NC}"
echo "=================================================="

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    echo -e "${RED}❌ Kind is not installed. Please install it first:${NC}"
    echo "   brew install kind"
    echo "   Or visit: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl is not installed. Please install it first:${NC}"
    echo "   brew install kubectl"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Pre-flight checks passed!${NC}"

# Delete existing cluster if it exists
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo -e "${YELLOW}🗑️  Deleting existing cluster: ${CLUSTER_NAME}${NC}"
    kind delete cluster --name="${CLUSTER_NAME}"
fi

# Create the cluster
echo -e "${BLUE}🏗️  Creating Kind cluster with config: ${CONFIG_FILE}${NC}"
kind create cluster --config="${CONFIG_FILE}" --wait=300s

# Wait for cluster to be ready
echo -e "${YELLOW}⏳ Waiting for cluster to be fully ready...${NC}"
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Install NGINX Ingress Controller
echo -e "${BLUE}🌐 Installing NGINX Ingress Controller...${NC}"
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress controller to be ready
echo -e "${YELLOW}⏳ Waiting for NGINX Ingress Controller to be ready...${NC}"
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

# Install Metrics Server (for HPA and resource monitoring)
echo -e "${BLUE}📊 Installing Metrics Server...${NC}"
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Patch metrics server to work with Kind
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

echo -e "${GREEN}✅ Cluster setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Cluster Information:${NC}"
echo "   Cluster Name: ${CLUSTER_NAME}"
echo "   Nodes: $(kubectl get nodes --no-headers | wc -l | tr -d ' ')"
echo "   Context: kind-${CLUSTER_NAME}"
echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo "   kubectl get nodes -o wide"
echo "   kubectl get pods --all-namespaces"
echo "   kind delete cluster --name=${CLUSTER_NAME}"
echo ""
echo -e "${GREEN}🎉 Your demo environment is ready!${NC}"
echo "   Run './deploy-demo-apps.sh' to deploy sample applications"
echo "   Run './chaos-scenarios.sh' to simulate failures"
