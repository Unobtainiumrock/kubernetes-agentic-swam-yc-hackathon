# AcmeCorp Kubernetes Standards

## Container Image Policy

All container images must be sourced from approved registries and follow naming conventions.

**Approved Image Sources:**
- harbor.acmecorp.com (primary registry)
- gcr.io/acmecorp-prod (backup registry)

**Image Naming Convention:**
- Format: `harbor.acmecorp.com/[team]/[service]:[version]`
- Example: `harbor.acmecorp.com/frontend/nginx:1.27.1`

## Resource Allocation Standards

### Frontend Application Tier
- CPU Request: 100m
- CPU Limit: 200m  
- Memory Request: 64Mi
- Memory Limit: 128Mi

### Backend Service Tier
- CPU Request: 250m
- CPU Limit: 500m
- Memory Request: 128Mi
- Memory Limit: 256Mi

## Network Security Standards

All services must implement proper network policies and service accounts.

## Required Labels

All resources must include:
- `app.kubernetes.io/name`
- `app.kubernetes.io/version` 
- `app.kubernetes.io/component`
- `acmecorp.com/team`
- `acmecorp.com/environment`

## Required Annotations

- `acmecorp.com/owner`: Team responsible for the resource
- `acmecorp.com/contact`: Contact information for escalations 