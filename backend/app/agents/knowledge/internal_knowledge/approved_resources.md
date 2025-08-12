# AcmeCorp Approved Resources Registry

## Container Images Registry

### Web Frontend Images
| Image | Version | Registry | Security Status | Last Updated |
|-------|---------|----------|-----------------|--------------|
| nginx | 1.27.1 | harbor.acmecorp.com/frontend/nginx:1.27.1 | ✅ Scanned | 2024-08-01 |
| nginx | 1.26.2 | harbor.acmecorp.com/frontend/nginx:1.26.2 | ✅ Scanned | 2024-07-15 |
| httpd | 2.4.57 | harbor.acmecorp.com/frontend/httpd:2.4.57 | ✅ Scanned | 2024-07-20 |

### Application Runtime Images
| Image | Version | Registry | Security Status | Last Updated |
|-------|---------|----------|-----------------|--------------|
| alpine | 3.19 | harbor.acmecorp.com/base/alpine:3.19 | ✅ Scanned | 2024-08-05 |
| alpine | 3.18 | harbor.acmecorp.com/base/alpine:3.18 | ✅ Scanned | 2024-07-25 |
| busybox | 1.35 | harbor.acmecorp.com/base/busybox:1.35 | ✅ Scanned | 2024-08-01 |
| busybox | 1.34 | harbor.acmecorp.com/base/busybox:1.34 | ✅ Scanned | 2024-07-10 |

### Database Images
| Image | Version | Registry | Security Status | Last Updated |
|-------|---------|----------|-----------------|--------------|
| postgres | 15.4 | harbor.acmecorp.com/data/postgres:15.4 | ✅ Scanned | 2024-08-03 |
| postgres | 14.9 | harbor.acmecorp.com/data/postgres:14.9 | ✅ Scanned | 2024-07-28 |
| redis | 7.2 | harbor.acmecorp.com/data/redis:7.2 | ✅ Scanned | 2024-08-02 |
| redis | 7.0 | harbor.acmecorp.com/data/redis:7.0 | ✅ Scanned | 2024-07-18 |

## Deprecated/Unapproved Images

### ❌ DO NOT USE
| Image | Reason | Replacement |
|-------|---------|-------------|
| nginx:latest | No version pinning | harbor.acmecorp.com/frontend/nginx:1.27.1 |
| nginx:nonexistent-tag | Image does not exist | harbor.acmecorp.com/frontend/nginx:1.27.1 |
| busybox:latest | No version pinning | harbor.acmecorp.com/base/busybox:1.35 |
| alpine:latest | No version pinning | harbor.acmecorp.com/base/alpine:3.19 |
| ubuntu:* | Not approved base image | harbor.acmecorp.com/base/alpine:3.19 |
| centos:* | Not approved base image | harbor.acmecorp.com/base/alpine:3.19 |

## Resource Configuration Templates

### Frontend Application Template
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-app
  namespace: frontend
  labels:
    app: frontend-app
    tier: frontend
    team: platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend-app
  template:
    metadata:
      labels:
        app: frontend-app
        tier: frontend
    spec:
      serviceAccountName: frontend-sa
      containers:
      - name: web-server
        image: harbor.acmecorp.com/frontend/nginx:1.27.1
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "32Mi"
            cpu: "50m"
          limits:
            memory: "64Mi"
            cpu: "100m"
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health/live
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 30
```

### Backend Service Template
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-service
  namespace: backend
  labels:
    app: backend-service
    tier: backend
    team: platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend-service
  template:
    metadata:
      labels:
        app: backend-service
        tier: backend
    spec:
      serviceAccountName: backend-sa
      containers:
      - name: api-server
        image: harbor.acmecorp.com/base/alpine:3.19
        command: ["/bin/sh"]
        args: ["-c", "echo 'Backend service running' && sleep infinity"]
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
```

## Service Account Configurations

### Frontend Service Account
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: frontend-sa
  namespace: frontend
  annotations:
    acmecorp.com/description: "Service account for frontend applications"
automountServiceAccountToken: true
```

### Backend Service Account
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: backend-sa
  namespace: backend
  annotations:
    acmecorp.com/description: "Service account for backend services"
automountServiceAccountToken: true
```

## Network Policy Templates

### Frontend Network Policy
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-network-policy
  namespace: frontend
spec:
  podSelector:
    matchLabels:
      tier: frontend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: backend
    ports:
    - protocol: TCP
      port: 8080
```

## Persistent Volume Configurations

### Database Storage Template
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: database-storage
  namespace: data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 10Gi
```

## ConfigMap Templates

### Application Configuration
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: frontend
data:
  database_host: "postgres.data.svc.cluster.local"
  database_port: "5432"
  cache_host: "redis.data.svc.cluster.local"
  cache_port: "6379"
  log_level: "INFO"
  environment: "production"
```

## Secret Templates

### Database Credentials
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-credentials
  namespace: data
type: Opaque
data:
  username: <base64-encoded-username>
  password: <base64-encoded-password>
```

## Horizontal Pod Autoscaler Templates

### Frontend HPA
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
  namespace: frontend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Resource Quota Templates

### Namespace Resource Quota
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: namespace-quota
  namespace: frontend
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    pods: "50"
    persistentvolumeclaims: "10"
    services: "20"
```

## Image Update Procedures

### Regular Updates
1. Security team publishes approved image list monthly
2. Platform team updates deployment manifests
3. Staging deployment and testing required
4. Production rollout with blue-green deployment
5. Monitoring and rollback procedures ready

### Emergency Updates
1. Security vulnerability identified
2. Immediate image scan and approval
3. Emergency deployment approval from security team
4. Automated rollout with enhanced monitoring
5. Post-incident review required

## Registry Authentication

### Harbor Registry Access
- Service accounts automatically configured with pull secrets
- Push access limited to CI/CD pipelines
- Regular credential rotation (monthly)
- Audit logging of all registry access

### Backup Registry Failover
- Automatic failover to gcr.io/acmecorp-backup
- Emergency procedures for registry outages
- Manual approval required for docker.io usage
- Incident commander notification for registry issues

This registry serves as the single source of truth for all approved resources in the AcmeCorp Kubernetes environment.
