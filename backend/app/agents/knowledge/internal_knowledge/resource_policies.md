# AcmeCorp Resource Management Policies

## Resource Allocation Philosophy

AcmeCorp follows a tiered resource allocation strategy based on application criticality, performance requirements, and cost optimization. All resource decisions must balance performance, reliability, and infrastructure costs.

## Compute Resource Tiers

### Tier 1: Frontend Applications
**Use Case**: User-facing web applications, static content servers, reverse proxies

**Standard Allocation:**
- **CPU Request**: 50m (0.05 cores)
- **CPU Limit**: 100m (0.1 cores)
- **Memory Request**: 32Mi
- **Memory Limit**: 64Mi
- **Storage**: Ephemeral only (no persistent volumes)

**Scaling Parameters:**
- **Min Replicas**: 2 (high availability requirement)
- **Max Replicas**: 10 (cost control)
- **HPA CPU Target**: 70%
- **HPA Memory Target**: 80%

**Monitoring Thresholds:**
- **CPU Warning**: >60% sustained for 5 minutes
- **CPU Critical**: >85% sustained for 2 minutes
- **Memory Warning**: >70% sustained for 5 minutes
- **Memory Critical**: >90% sustained for 1 minute

### Tier 2: Backend Services
**Use Case**: Internal APIs, microservices, business logic applications

**Standard Allocation:**
- **CPU Request**: 100m (0.1 cores)
- **CPU Limit**: 200m (0.2 cores)
- **Memory Request**: 64Mi
- **Memory Limit**: 128Mi
- **Storage**: ConfigMaps, Secrets, small temp volumes

**Scaling Parameters:**
- **Min Replicas**: 3 (load distribution and availability)
- **Max Replicas**: 15 (performance scaling)
- **HPA CPU Target**: 70%
- **HPA Memory Target**: 80%

**Monitoring Thresholds:**
- **CPU Warning**: >65% sustained for 5 minutes
- **CPU Critical**: >85% sustained for 2 minutes
- **Memory Warning**: >75% sustained for 5 minutes
- **Memory Critical**: >90% sustained for 1 minute

### Tier 3: Data Services
**Use Case**: Databases, caching layers, data processing applications

**Standard Allocation:**
- **CPU Request**: 200m (0.2 cores)
- **CPU Limit**: 500m (0.5 cores)
- **Memory Request**: 256Mi
- **Memory Limit**: 512Mi
- **Storage**: Persistent volumes (10Gi minimum)

**Scaling Parameters:**
- **Min Replicas**: 1 (stateful services)
- **Max Replicas**: 3 (limited by data consistency requirements)
- **Manual scaling**: Automated scaling disabled for stateful services

**Monitoring Thresholds:**
- **CPU Warning**: >70% sustained for 10 minutes
- **CPU Critical**: >90% sustained for 5 minutes
- **Memory Warning**: >80% sustained for 10 minutes
- **Memory Critical**: >95% sustained for 2 minutes

## Resource Request Guidelines

### CPU Allocation Principles
1. **Always set CPU requests** to ensure quality of service
2. **CPU requests = minimum guaranteed resources** during contention
3. **CPU limits prevent noisy neighbor issues** in shared clusters
4. **Use millicores (m)** for precise allocation (1000m = 1 core)

### Memory Allocation Principles
1. **Memory requests = expected baseline usage** under normal load
2. **Memory limits = maximum allowed usage** before OOMKill
3. **Memory is not compressible** - exceeding limits causes termination
4. **Leave 20-30% headroom** between request and limit for traffic spikes

### Quality of Service Classes

#### Guaranteed QoS (Preferred for Production)
```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "100m"
  limits:
    memory: "64Mi"    # Same as request
    cpu: "100m"       # Same as request
```
- **Benefits**: Highest priority, never evicted
- **Use Case**: Critical production services

#### Burstable QoS (Standard for Most Applications)
```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "100m"
  limits:
    memory: "128Mi"   # 2x request
    cpu: "200m"       # 2x request
```
- **Benefits**: Guaranteed baseline, can burst when resources available
- **Use Case**: Most production applications

#### BestEffort QoS (Not Recommended for Production)
```yaml
# No resource requests or limits specified
```
- **Risk**: First to be evicted during resource pressure
- **Use Case**: Development/testing only

## Namespace Resource Quotas

### Frontend Namespace Limits
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: frontend-quota
spec:
  hard:
    requests.cpu: "2000m"      # Total CPU requests
    requests.memory: "4Gi"     # Total memory requests
    limits.cpu: "4000m"        # Total CPU limits
    limits.memory: "8Gi"       # Total memory limits
    pods: "50"                 # Maximum pod count
    services: "20"             # Maximum service count
    persistentvolumeclaims: "5" # Limited persistent storage
```

### Backend Namespace Limits
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: backend-quota
spec:
  hard:
    requests.cpu: "3000m"      # Higher CPU for processing
    requests.memory: "6Gi"     # Higher memory for caching
    limits.cpu: "6000m"        # Allow CPU bursting
    limits.memory: "12Gi"      # Allow memory bursting
    pods: "75"                 # More pods for scaling
    services: "30"             # More internal services
    persistentvolumeclaims: "10" # Moderate persistent storage
```

### Data Namespace Limits
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: data-quota
spec:
  hard:
    requests.cpu: "2000m"      # Steady CPU for databases
    requests.memory: "8Gi"     # High memory for caching
    limits.cpu: "4000m"        # Limited CPU bursting
    limits.memory: "16Gi"      # High memory limits
    pods: "20"                 # Fewer but resource-intensive pods
    services: "15"             # Internal data services
    persistentvolumeclaims: "20" # High storage requirements
```

## Horizontal Pod Autoscaler Policies

### Conservative Scaling (Default)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70    # Scale up at 70% CPU
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80    # Scale up at 80% Memory
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100                # Double pods at most
        periodSeconds: 60
      - type: Pods
        value: 2                  # Add max 2 pods per minute
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50                 # Remove max 50% of pods
        periodSeconds: 60
```

### Aggressive Scaling (High Traffic Applications)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60    # Earlier scale-up
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30  # Faster response
      policies:
      - type: Percent
        value: 200              # Triple pods if needed
        periodSeconds: 30
      - type: Pods
        value: 4                # Add max 4 pods per 30s
        periodSeconds: 30
```

## Vertical Pod Autoscaler Guidelines

### VPA Recommendation Mode (Monitoring Only)
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
spec:
  updatePolicy:
    updateMode: "Off"           # Recommendations only
  resourcePolicy:
    containerPolicies:
    - containerName: app
      maxAllowed:
        cpu: "500m"             # Safety limits
        memory: "1Gi"
      minAllowed:
        cpu: "50m"              # Minimum viable resources
        memory: "32Mi"
```

### VPA Auto Mode (Careful Production Use)
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
spec:
  updatePolicy:
    updateMode: "Auto"          # Automatic updates
  resourcePolicy:
    containerPolicies:
    - containerName: app
      controlledResources: ["memory"] # Only adjust memory
      maxAllowed:
        memory: "512Mi"         # Conservative max
      minAllowed:
        memory: "64Mi"          # Reasonable minimum
```

## Resource Monitoring and Alerting

### Resource Utilization Alerts

#### High Resource Usage Alerts
```yaml
# CPU Usage Alert
alert: HighCPUUsage
expr: rate(container_cpu_usage_seconds_total[5m]) * 100 > 80
for: 5m
labels:
  severity: warning
annotations:
  summary: "High CPU usage detected"
  description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has CPU usage above 80%"

# Memory Usage Alert  
alert: HighMemoryUsage
expr: container_memory_usage_bytes / container_spec_memory_limit_bytes * 100 > 85
for: 5m
labels:
  severity: warning
annotations:
  summary: "High memory usage detected"
  description: "Pod {{ $labels.pod }} has memory usage above 85% of limit"
```

#### Resource Constraint Alerts
```yaml
# Pod Pending Alert
alert: PodPending
expr: kube_pod_status_phase{phase="Pending"} == 1
for: 5m
labels:
  severity: critical
annotations:
  summary: "Pod stuck in pending state"
  description: "Pod {{ $labels.pod }} has been pending for more than 5 minutes"

# OOMKilled Alert
alert: PodOOMKilled
expr: increase(kube_pod_container_status_restarts_total[1h]) > 0 and on (pod) kube_pod_container_status_last_terminated_reason{reason="OOMKilled"} == 1
labels:
  severity: critical
annotations:
  summary: "Pod killed due to out of memory"
  description: "Pod {{ $labels.pod }} was OOMKilled and restarted"
```

## Cost Optimization Strategies

### Right-Sizing Recommendations
1. **Monitor actual usage** vs allocated resources for 30 days
2. **Adjust requests** to 80th percentile of actual usage
3. **Set limits** to 95th percentile plus 20% headroom
4. **Review quarterly** and adjust based on traffic patterns

### Resource Waste Identification
1. **Over-provisioned pods**: Allocated >> Used consistently
2. **Under-utilized nodes**: Multiple nodes with low utilization
3. **Idle resources**: Resources requested but not used

### Optimization Actions
1. **Vertical scaling**: Adjust individual pod resources
2. **Horizontal scaling**: Adjust replica counts
3. **Node optimization**: Consolidate workloads
4. **Workload scheduling**: Use node affinity and anti-affinity

## Emergency Resource Procedures

### Resource Exhaustion Response
1. **Immediate**: Scale up cluster nodes (cloud auto-scaling)
2. **Short-term**: Reduce non-critical workload replicas
3. **Medium-term**: Optimize resource allocations
4. **Long-term**: Capacity planning and forecasting

### Node Pressure Handling
1. **Memory pressure**: Pods evicted in BestEffort → Burstable → Guaranteed order
2. **CPU pressure**: Throttling applied based on CPU limits
3. **Disk pressure**: Ephemeral storage cleanup and pod eviction

### Emergency Scaling Commands
```bash
# Scale down non-critical deployments
kubectl scale deployment <non-critical-app> --replicas=0 -n <namespace>

# Increase node count (cloud provider specific)
kubectl scale deployment cluster-autoscaler --replicas=1 -n kube-system

# Check resource pressure
kubectl describe nodes | grep -E "(Pressure|Allocatable|Allocated)"
```

## Compliance and Governance

### Resource Policy Enforcement
- **Admission controllers** validate resource requests against policies
- **Resource quotas** prevent namespace resource abuse
- **Limit ranges** set default and maximum resource values

### Regular Reviews
- **Monthly**: Resource utilization analysis and optimization
- **Quarterly**: Policy review and adjustment
- **Annually**: Capacity planning and infrastructure scaling

### Documentation Requirements
- All resource changes must be documented with business justification
- Performance impact assessment required for significant changes
- Cost impact analysis for resource tier changes

This policy ensures efficient, cost-effective, and reliable resource management across the AcmeCorp Kubernetes platform.
