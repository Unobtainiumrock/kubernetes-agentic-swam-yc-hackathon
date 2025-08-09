# Kubernetes Demo Environment with Kind.

This repository contains infrastructure as code to create a medium complex Kubernetes environment using Kind (Kubernetes in Docker) for demonstrating pod failures, node crashes, and various chaos engineering scenarios.

## 🏗️ Architecture

The demo cluster includes:
- **1 Control Plane Node** with ingress capabilities
- **4 Worker Nodes** with different labels and roles:
  - Frontend tier (zone: us-west-1a)
  - Backend tier (zone: us-west-1b) 
  - Database tier (zone: us-west-1c)
  - Cache tier (zone: us-west-1a)

## 📋 Prerequisites

Before running this demo, ensure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/) - Must be running
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) - `brew install kind`
- [kubectl](https://kubernetes.io/docs/tasks/tools/) - `brew install kubectl`

## 🚀 Quick Start

### 1. Create the Cluster
```bash
chmod +x setup-cluster.sh
./setup-cluster.sh
```

This will:
- Create a 5-node Kind cluster with the specified configuration
- Install NGINX Ingress Controller
- Install Metrics Server for monitoring
- Set up the cluster context

### 2. Deploy Demo Applications
```bash
chmod +x deploy-demo-apps.sh
./deploy-demo-apps.sh
```

This deploys:
- **Frontend**: 3 NGINX replicas in `frontend` namespace
- **Backend**: 4 Apache replicas in `backend` namespace  
- **Database**: 2 Redis StatefulSet replicas in `database` namespace
- **Cache**: 2 Memcached replicas in `backend` namespace
- **CPU Stress**: Load testing application
- **HPA**: Horizontal Pod Autoscaler for backend (2-8 replicas)

### 3. Run Chaos Scenarios
```bash
chmod +x chaos-scenarios.sh
./chaos-scenarios.sh
```

Interactive menu with scenarios:
1. **Pod Failure Simulation** - Randomly kill pods
2. **Node Drain Simulation** - Drain worker nodes
3. **Resource Pressure** - Create CPU/Memory stress
4. **Network Partition** - Block cross-namespace communication
5. **Storage Failure** - Simulate database outages
6. **Rolling Update Failure** - Deploy bad container images
7. **Cascading Failure** - Multi-system failure simulation
8. **Recovery Demonstration** - Restore all services
9. **Show Current Status** - Display cluster health

## 🧹 Cleanup

To remove the entire cluster and clean up resources:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

## 📊 Monitoring Commands

```bash
# View cluster status
kubectl get nodes -o wide
kubectl get pods --all-namespaces

# Monitor resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Check autoscaling
kubectl get hpa --all-namespaces

# View services
kubectl get services --all-namespaces

# Check ingress
kubectl get ingress --all-namespaces
```

## 🎯 Demo Scenarios

### Basic Pod Resilience
1. Kill frontend pods and watch them recover
2. Scale applications up/down
3. Observe HPA behavior under load

### Node Failure Simulation
1. Drain a worker node
2. Watch pods reschedule to healthy nodes
3. Demonstrate node recovery

### Resource Exhaustion
1. Create CPU/Memory pressure
2. Observe pod evictions
3. Watch cluster auto-scaling responses

### Network Issues
1. Apply network policies
2. Simulate network partitions
3. Demonstrate service mesh behavior

### Storage Failures
1. Scale down StatefulSets
2. Simulate persistent volume issues
3. Test backup/recovery procedures

## 🔧 Customization

### Modify Cluster Configuration
Edit `kind-cluster-config.yaml` to:
- Add more nodes
- Change node labels
- Modify networking settings
- Add custom port mappings

### Add More Applications
Extend `deploy-demo-apps.sh` to include:
- Additional microservices
- Different database types
- Monitoring stack (Prometheus, Grafana)
- Service mesh (Istio, Linkerd)

### Create Custom Chaos Scenarios
Modify `chaos-scenarios.sh` to add:
- Custom failure patterns
- Specific application failures
- Time-based scenarios
- Automated recovery procedures

## 📁 File Structure

```
├── kind-cluster-config.yaml    # Kind cluster configuration
├── setup-cluster.sh           # Cluster creation script
├── deploy-demo-apps.sh        # Application deployment script
├── chaos-scenarios.sh         # Chaos engineering scenarios
├── cleanup.sh                 # Cleanup script
└── README.md                  # This file
```

## 🤝 Sharing and Replication

This entire setup is designed to be easily shared and replicated:

1. **Clone this repository**
2. **Run the setup script** - `./setup-cluster.sh`
3. **Deploy applications** - `./deploy-demo-apps.sh`
4. **Start demonstrating** - `./chaos-scenarios.sh`

The infrastructure as code approach ensures consistent environments across different machines and users.

## 🐛 Troubleshooting

### Common Issues

**Docker not running:**
```bash
# Start Docker Desktop or Docker daemon
open -a Docker
```

**Kind cluster creation fails:**
```bash
# Check Docker resources and try again
kind delete cluster --name=demo-cluster
./setup-cluster.sh
```

**Pods stuck in Pending:**
```bash
# Check node resources and events
kubectl describe nodes
kubectl get events --sort-by=.metadata.creationTimestamp
```

**Metrics not available:**
```bash
# Wait for metrics server to be ready
kubectl get pods -n kube-system | grep metrics-server
```

## 📚 Learning Resources

- [Kind Documentation](https://kind.sigs.k8s.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Chaos Engineering Principles](https://principlesofchaos.org/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

## 🎉 Happy Demoing!

This environment provides a realistic Kubernetes setup for demonstrating resilience patterns, failure scenarios, and recovery procedures. Perfect for training, workshops, and proof-of-concepts.
