# AcmeCorp Resource Policies

## Compute Resource Tiers

### Tier 1: Frontend Applications
**Use Case:** Web servers, static content, user interfaces

**Resource Allocation:**
- CPU Request: 100m (0.1 core)
- CPU Limit: 200m (0.2 core)
- Memory Request: 64Mi
- Memory Limit: 128Mi

**Scaling Policy:**
- Min replicas: 2
- Max replicas: 10
- Target CPU utilization: 70%

### Tier 2: Backend Services
**Use Case:** API services, microservices, business logic

**Resource Allocation:**
- CPU Request: 250m (0.25 core)
- CPU Limit: 500m (0.5 core)  
- Memory Request: 128Mi
- Memory Limit: 256Mi

**Scaling Policy:**
- Min replicas: 3
- Max replicas: 20
- Target CPU utilization: 60%

### Tier 3: Data Services
**Use Case:** Databases, caches, message queues

**Resource Allocation:**
- CPU Request: 500m (0.5 core)
- CPU Limit: 1000m (1 core)
- Memory Request: 512Mi
- Memory Limit: 1Gi

## Resource Allocation Principles

1. **Always set both requests and limits**
2. **Requests should be 50-80% of limits**
3. **Monitor actual usage vs allocated resources**
4. **Review and adjust monthly based on metrics**

## Quality of Service Classes

- **Guaranteed:** requests == limits (critical services)
- **Burstable:** requests < limits (most applications)
- **BestEffort:** no requests/limits (development only)

## Resource Monitoring

- CPU utilization should stay below 80% of limit
- Memory utilization should stay below 85% of limit
- Monitor P95 resource usage for capacity planning 