# AcmeCorp Approved Resources

## Container Images Registry

### Web Frontend Images
- `harbor.acmecorp.com/frontend/nginx:1.27.1` - Production web server
- `harbor.acmecorp.com/frontend/react:18.2.0` - React applications
- `harbor.acmecorp.com/frontend/vue:3.3.4` - Vue.js applications

### Application Runtime Images
- `harbor.acmecorp.com/backend/node:18-alpine` - Node.js applications
- `harbor.acmecorp.com/backend/python:3.11-slim` - Python applications
- `harbor.acmecorp.com/backend/golang:1.21-alpine` - Go applications

### Database Images
- `harbor.acmecorp.com/data/postgres:15.4` - PostgreSQL database
- `harbor.acmecorp.com/data/redis:7.2-alpine` - Redis cache

## Deprecated/Unapproved Images

**DO NOT USE:**
- Any images from Docker Hub public registry
- Images with `latest` tag
- Images from unknown or untrusted registries
- Self-built images without security scanning

## Resource Configuration Templates

### ConfigMap Templates
Standard configuration patterns for AcmeCorp applications.

### Secret Templates  
Approved secret management patterns and encryption requirements.

## Security Scan Requirements

All approved images must pass:
- Vulnerability scanning (Snyk/Trivy)
- Policy compliance (OPA Gatekeeper)
- License compliance checks 