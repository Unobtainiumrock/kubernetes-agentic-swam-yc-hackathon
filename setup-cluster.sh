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

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ Helm is not installed. Please install it first:${NC}"
    echo "   brew install helm"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Pre-flight checks passed!${NC}"

# Check if cluster already exists
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo -e "${GREEN}✅ Cluster '${CLUSTER_NAME}' already exists, skipping creation${NC}"
    echo -e "${YELLOW}⏳ Verifying cluster is ready...${NC}"
else
    # Create the cluster
    echo -e "${BLUE}🏗️  Creating Kind cluster with config: ${CONFIG_FILE}${NC}"
    kind create cluster --config="${CONFIG_FILE}" --wait=300s
fi

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

# Install k8sgpt-operator via Helm
echo -e "${BLUE}🤖 Installing k8sgpt-operator...${NC}"

# Check if k8sgpt-operator is already installed
if helm list -n k8sgpt-operator-system | grep -q "k8sgpt-operator"; then
    echo -e "${GREEN}✅ k8sgpt-operator already installed, skipping installation${NC}"
else
    helm repo add k8sgpt https://charts.k8sgpt.ai/ || true
    helm repo update
    
    # Install k8sgpt-operator using local chart if available, otherwise from repo
    if [[ -d "k8sgpt-operator" ]]; then
        echo -e "${YELLOW}📁 Using local k8sgpt-operator chart...${NC}"
        helm install k8sgpt-operator ./k8sgpt-operator -n k8sgpt-operator-system --create-namespace
    else
        echo -e "${YELLOW}📦 Using k8sgpt-operator from Helm repository...${NC}"
        helm install k8sgpt-operator k8sgpt/k8sgpt-operator -n k8sgpt-operator-system --create-namespace
    fi
fi

# Wait for k8sgpt-operator to be ready
echo -e "${YELLOW}⏳ Waiting for k8sgpt-operator to be ready...${NC}"
kubectl wait --namespace k8sgpt-operator-system \
  --for=condition=ready pod \
  --selector=control-plane=controller-manager \
  --timeout=300s

echo -e "${GREEN}✅ Cluster setup complete!${NC}"
echo ""
echo -e "${BLUE}📋 Cluster Information:${NC}"
echo "   Cluster Name: ${CLUSTER_NAME}"
echo "   Nodes: $(kubectl get nodes --no-headers | wc -l | tr -d ' ')"
echo "   Context: kind-${CLUSTER_NAME}"
echo "   k8sgpt-operator: Installed in k8sgpt-operator-system namespace"
echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo "   kubectl get nodes -o wide"
echo "   kubectl get pods --all-namespaces"
echo "   kind delete cluster --name=${CLUSTER_NAME}"
echo ""
echo -e "${GREEN}🎉 Your demo environment is ready!${NC}"
echo "   Run './deploy-demo-apps.sh' to deploy sample applications"
echo "   Run './chaos-scenarios.sh' to simulate failures"
echo ""

# k8sgpt Authentication Setup
echo -e "${BLUE}🤖 k8sgpt Authentication Setup${NC}"
echo "========================================"
echo -e "${YELLOW}To enable AI-powered diagnostics, k8sgpt needs API credentials.${NC}"
echo ""

read -p "Would you like to configure k8sgpt authentication now? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}🔧 Running k8sgpt authentication setup...${NC}"
    echo "k8sgpt will guide you through the authentication process."
    echo ""
    
    # Check if k8sgpt CLI is installed
    if ! command -v k8sgpt &> /dev/null; then
        echo -e "${YELLOW}⚠️  k8sgpt CLI not found. Installing via brew...${NC}"
        brew install k8sgpt-ai/k8sgpt/k8sgpt || {
            echo -e "${RED}❌ Failed to install k8sgpt CLI${NC}"
            echo "Please install manually: https://docs.k8sgpt.ai/getting-started/installation/"
            echo "Then run: k8sgpt auth"
            exit 1
        }
    fi

    if ! command -v k8sgpt &> /dev/null; then
    echo -e "${YELLOW}⚠️  k8sgpt CLI not found. Attempting to install...${NC}"

    # --- OS-specific installation ---
    # Check for macOS
    if [[ "$(uname)" == "Darwin" ]]; then
        echo "Detected macOS. Installing via Homebrew..."
        brew install k8sgpt-ai/k8sgpt/k8sgpt || {
            echo -e "${RED}❌ Failed to install k8sgpt via Homebrew.${NC}"
            echo "Please try installing manually: https://docs.k8sgpt.ai/getting-started/installation/"
            echo "After installation, run: k8sgpt auth"
            exit 1
        }
    # Check for Debian-based Linux (e.g., Ubuntu)
    elif [ -x "$(command -v dpkg)" ]; then
        echo "Detected Debian-based Linux. Installing via .deb package..."
        K8SGPT_VERSION="v0.4.22"
        K8SGPT_DEB="k8sgpt_amd64.deb"

        # Download the .deb package
        curl -LO "https://github.com/k8sgpt-ai/k8sgpt/releases/download/${K8SGPT_VERSION}/${K8SGPT_DEB}" || {
            echo -e "${RED}❌ Failed to download k8sgpt .deb package.${NC}"
            exit 1
        }

        # Install the package using dpkg
        sudo dpkg -i "${K8SGPT_DEB}" || {
            echo -e "${RED}❌ Failed to install k8sgpt via dpkg.${NC}"
            echo "Please try installing manually: https://docs.k8sgpt.ai/getting-started/installation/"
            echo "After installation, run: k8sgpt auth"
            # Attempt to clean up the downloaded file
            rm -f "${K8SGPT_DEB}"
            exit 1
        }

        # Clean up the downloaded .deb file on success
        rm -f "${K8SGPT_DEB}"
    else
        echo -e "${RED}❌ Unsupported operating system for automatic installation.${NC}"
        echo "Please install k8sgpt manually from the official documentation:"
        echo "https://docs.k8sgpt.ai/getting-started/installation/"
        echo "Then run: k8sgpt auth"
        exit 1
    fi

    # Verify installation
    if ! command -v k8sgpt &> /dev/null; then
        echo -e "${RED}❌ k8sgpt installation failed.${NC}"
        exit 1
    fi
   fi

    
    # Run k8sgpt auth
    k8sgpt auth
    
    echo ""
    echo -e "${GREEN}✅ k8sgpt authentication completed!${NC}"
    echo ""
    echo -e "${BLUE}🔧 Useful k8sgpt Commands:${NC}"
    echo "   k8sgpt analyze"
    echo "   k8sgpt analyze --explain"
    echo "   k8sgpt analyze --filter=Pod"
    echo "   k8sgpt filters list"
else
    echo -e "${YELLOW}⚠️ Skipping k8sgpt authentication setup.${NC}"
    echo "You can configure it by running: k8sgpt auth"
fi
