# AcmeCorp Kubernetes Cluster Standards

## Company Overview
AcmeCorp is a technology company operating a multi-tier Kubernetes platform serving web applications, APIs, and data services. Our cluster follows enterprise security and reliability standards.

## Container Image Policy

### Approved Image Sources
- **Primary Registry**: harbor.acmecorp.com
- **Backup Registry**: gcr.io/acmecorp-backup
- **Emergency Only**: docker.io (requires approval)

### Image Naming Convention
```
harbor.acmecorp.com/[team]/[application]:[semantic-version]
```

### Approved Base Images
- **Web Frontend**: nginx:1.27.1, nginx:1.26.2
- **Application Runtime**: alpine:3.19, alpine:3.18
- **Utilities**: busybox:1.35, busybox:1.34
- **Databases**: postgres:15.4, redis:7.2

### Image Security Requirements
- All images must pass Trivy security scanning
- No critical or high vulnerabilities allowed in production
- Images must be rebuilt monthly for security patches
- Use semantic versioning - NO 'latest' tags in production

## Resource Allocation Standards

### Frontend Application Tier
- **Memory Request**: 32Mi
- **Memory Limit**: 64Mi  
- **CPU Request**: 50m
- **CPU Limit**: 100m
- **Minimum Replicas**: 2 (for high availability)
- **Maximum Replicas**: 10 (auto-scaling limit)

### Backend Service Tier  
- **Memory Request**: 64Mi
- **Memory Limit**: 128Mi
- **CPU Request**: 100m
- **CPU Limit**: 200m
- **Minimum Replicas**: 3 (for high availability)
- **Maximum Replicas**: 15 (auto-scaling limit)

### Database Tier
- **Memory Request**: 256Mi
- **Memory Limit**: 512Mi
- **CPU Request**: 200m
- **CPU Limit**: 500m
- **Minimum Replicas**: 1 (stateful)
- **Storage**: Persistent volumes required

## Namespace Organization

### Production Namespaces
- **frontend**: User-facing web applications
- **backend**: Internal APIs and services
- **data**: Databases and storage systems
- **monitoring**: Observability and alerting stack
- **security**: Security tools and scanning

### Required Labels
All deployments must include:
```yaml
metadata:
  labels:
    app: application-name
    version: semantic-version
    team: responsible-team
    environment: production|staging|dev
    tier: frontend|backend|data
```

### Required Annotations
```yaml
metadata:
  annotations:
    acmecorp.com/owner: team-email@acmecorp.com
    acmecorp.com/oncall: oncall-rotation-name
    acmecorp.com/cost-center: department-code
```

## Health Check Requirements

### Readiness Probes
- **HTTP Applications**: GET /health/ready
- **Timeout**: 5 seconds
- **Initial Delay**: 10 seconds
- **Period**: 10 seconds

### Liveness Probes  
- **HTTP Applications**: GET /health/live
- **Timeout**: 3 seconds
- **Initial Delay**: 30 seconds
- **Period**: 30 seconds

### Startup Probes
- **Complex Applications**: GET /health/startup
- **Timeout**: 10 seconds
- **Initial Delay**: 5 seconds
- **Period**: 5 seconds
- **Failure Threshold**: 30

## Service Account Requirements

### Default Service Accounts
- **frontend-sa**: For frontend applications (read-only cluster access)
- **backend-sa**: For backend services (limited API access)
- **data-sa**: For database operations (storage access)

### RBAC Principles
- Follow principle of least privilege
- No cluster-admin permissions in applications
- Use namespace-scoped roles
- Regular RBAC auditing required

## Network Security Standards

### Network Policies
- Default deny all ingress/egress
- Explicit allow rules for required communications
- No cross-namespace communication without approval
- External traffic only through approved ingress controllers

### Service Mesh Requirements
- All inter-service communication through Istio
- mTLS enabled for all internal traffic
- Traffic encryption in transit required
- Service-to-service authentication mandatory

## Deployment Standards

### Rolling Update Strategy
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 25%
    maxSurge: 25%
```

### Resource Quotas (per namespace)
- **Total CPU**: 2000m
- **Total Memory**: 4Gi
- **Total Pods**: 50
- **Persistent Volumes**: 10

### Horizontal Pod Autoscaler
- **Target CPU**: 70%
- **Target Memory**: 80%
- **Scale up**: 2 pods per minute max
- **Scale down**: 1 pod per minute max

## Monitoring & Observability

### Required Metrics
- Application performance metrics via Prometheus
- Custom business metrics exposed on /metrics
- Resource utilization monitoring
- Error rate and latency tracking

### Logging Standards
- Structured logging in JSON format
- Log level: INFO in production
- No sensitive data in logs
- Centralized logging via Fluentd to Elasticsearch

### Alerting Requirements
- Critical alerts for service unavailability
- Warning alerts for resource exhaustion
- Info alerts for deployment events
- All alerts must have runbook links

## Backup & Disaster Recovery

### Data Protection
- Daily backups of persistent volumes
- Configuration stored in Git repositories
- Secrets managed through HashiCorp Vault
- 30-day retention policy

### Recovery Objectives
- **RTO** (Recovery Time Objective): 15 minutes
- **RPO** (Recovery Point Objective): 1 hour
- **MTTR** (Mean Time To Recovery): 30 minutes
- **Availability SLA**: 99.9%

## Compliance & Security

### Security Scanning
- Container image vulnerability scanning
- Kubernetes cluster security benchmarks (CIS)
- Regular penetration testing
- OWASP security guidelines compliance

### Audit Requirements
- All cluster access logged
- Configuration changes tracked
- Resource usage monitored
- Quarterly security reviews

## Emergency Procedures

### Incident Response
1. **Immediate**: Alert on-call team via PagerDuty
2. **Assessment**: Classify severity (P0-P4)
3. **Communication**: Update status page
4. **Resolution**: Follow incident runbooks
5. **Post-mortem**: Required for P0/P1 incidents

### Escalation Matrix
- **P0 (Critical)**: CTO notification within 15 minutes
- **P1 (High)**: Engineering Manager notification within 30 minutes
- **P2 (Medium)**: Team Lead notification within 1 hour
- **P3/P4 (Low)**: Standard ticket handling

This document serves as the foundation for all Kubernetes operations at AcmeCorp and must be followed for all production deployments.
