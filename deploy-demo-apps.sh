#!/bin/bash

# Deploy Demo Applications for Kubernetes Failure Simulation
# This script deploys various applications across different tiers for realistic demo scenarios

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Demo Applications${NC}"
echo "=================================="

# Create namespaces for different tiers
echo -e "${YELLOW}📁 Creating namespaces...${NC}"
kubectl create namespace frontend --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace backend --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace database --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Deploy Frontend Application (NGINX with multiple replicas)
echo -e "${BLUE}🌐 Deploying Frontend Application...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-app
  namespace: frontend
  labels:
    app: frontend
    tier: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
        tier: frontend
    spec:
      nodeSelector:
        tier: frontend
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: frontend
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
EOF

# Deploy Backend Application (Node.js app simulation)
echo -e "${BLUE}⚙️ Deploying Backend Application...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-app
  namespace: backend
  labels:
    app: backend
    tier: backend
spec:
  replicas: 4
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
        tier: backend
    spec:
      nodeSelector:
        tier: backend
      containers:
      - name: backend
        image: httpd:2.4
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "150m"
          limits:
            memory: "256Mi"
            cpu: "300m"
        env:
        - name: NODE_ENV
          value: "production"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: backend
spec:
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
EOF

# Deploy Database Application (Redis simulation)
echo -e "${BLUE}🗄️ Deploying Database Application...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database-app
  namespace: database
  labels:
    app: database
    tier: database
spec:
  replicas: 2
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
        tier: database
    spec:
      nodeSelector:
        tier: database
      containers:
      - name: redis
        image: redis:6.2
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: database-service
  namespace: database
spec:
  selector:
    app: database
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
EOF

# Deploy Cache Application (Memcached)
echo -e "${BLUE}⚡ Deploying Cache Application...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cache-app
  namespace: backend
  labels:
    app: cache
    tier: cache
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cache
  template:
    metadata:
      labels:
        app: cache
        tier: cache
    spec:
      nodeSelector:
        tier: cache
      containers:
      - name: memcached
        image: memcached:1.6
        ports:
        - containerPort: 11211
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: cache-service
  namespace: backend
spec:
  selector:
    app: cache
  ports:
  - port: 11211
    targetPort: 11211
  type: ClusterIP
EOF

# Deploy a CPU-intensive workload for resource pressure simulation
echo -e "${BLUE}🔥 Deploying CPU-intensive workload...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cpu-stress
  namespace: monitoring
  labels:
    app: cpu-stress
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cpu-stress
  template:
    metadata:
      labels:
        app: cpu-stress
    spec:
      containers:
      - name: stress
        image: polinux/stress
        command: ["stress"]
        args: ["--cpu", "1", "--timeout", "3600s", "--verbose"]
        resources:
          requests:
            memory: "100Mi"
            cpu: "100m"
          limits:
            memory: "200Mi"
            cpu: "500m"
EOF

# Note: HPA requires metrics server which may take time to be ready
# For demo purposes, we'll skip HPA initially
echo -e "${YELLOW}📈 Skipping HPA for faster deployment (can be added later)...${NC}"

# Wait for deployments to be ready
echo -e "${YELLOW}⏳ Waiting for applications to be ready...${NC}"
kubectl wait --for=condition=available --timeout=180s deployment/frontend-app -n frontend
kubectl wait --for=condition=available --timeout=180s deployment/backend-app -n backend
kubectl wait --for=condition=available --timeout=180s deployment/cache-app -n backend
kubectl wait --for=condition=available --timeout=180s deployment/database-app -n database

echo -e "${GREEN}✅ All demo applications deployed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Deployed Applications:${NC}"
echo "   Frontend: 3 replicas (NGINX) in frontend namespace"
echo "   Backend: 4 replicas (Apache) in backend namespace"
echo "   Database: 2 replicas (Redis) in database namespace"
echo "   Cache: 2 replicas (Memcached) in backend namespace"
echo "   CPU Stress: 1 replica for load testing"
echo ""
echo -e "${BLUE}🔧 Useful Commands:${NC}"
echo "   kubectl get pods --all-namespaces"
echo "   kubectl get services --all-namespaces"
echo "   kubectl top nodes"
echo "   kubectl top pods --all-namespaces"
