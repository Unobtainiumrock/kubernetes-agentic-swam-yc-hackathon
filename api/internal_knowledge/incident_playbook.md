# AcmeCorp Kubernetes Incident Response Playbook

## Incident Classification

### Severity Levels
- **P0 (Critical)**: Complete service outage, data loss, security breach
- **P1 (High)**: Major functionality impaired, performance degradation >50%
- **P2 (Medium)**: Minor functionality impaired, some users affected
- **P3 (Low)**: Cosmetic issues, no user impact
- **P4 (Planning)**: Technical debt, optimization opportunities

### Response Times
- **P0**: Immediate response, CTO notification within 15 minutes
- **P1**: Response within 30 minutes, Engineering Manager notification
- **P2**: Response within 2 hours, Team Lead notification
- **P3/P4**: Response within 24 hours, standard ticket queue

## Container Image Issues

### ImagePullBackOff Investigation
**Symptoms:**
- Pods stuck in ImagePullBackOff state
- Error messages about image pull failures
- New deployments failing to start

**Immediate Investigation Steps:**
1. **Verify Image Name and Tag**
   ```bash
   kubectl describe pod <pod-name> -n <namespace>
   kubectl get events -n <namespace> --sort-by='.lastTimestamp'
   ```

2. **Check Image Against Approved Registry**
   - Compare against approved_resources.md
   - Verify image exists in harbor.acmecorp.com
   - Check for typos in image name or tag

3. **Test Image Availability**
   ```bash
   docker pull <image-name>
   kubectl run test-pod --image=<image-name> --dry-run=client -o yaml
   ```

**Common Root Causes:**
- **Typo in image name or tag** (90% of cases)
- **Unapproved image source** (not in harbor.acmecorp.com)
- **Image does not exist** (wrong tag, deleted image)
- **Registry authentication issues** (service account problems)
- **Network connectivity** (firewall, DNS issues)

**Resolution Procedures:**
1. **For Typos/Wrong Tags:**
   ```bash
   # Update deployment with correct image
   kubectl set image deployment/<deployment-name> <container-name>=harbor.acmecorp.com/frontend/nginx:1.27.1 -n <namespace>
   ```

2. **For Unapproved Images:**
   - Consult approved_resources.md for company-approved alternative
   - Update deployment manifest with approved image
   - Submit change request if new image approval needed

3. **For Missing Images:**
   - Check if image was deprecated or removed
   - Use latest approved version from approved_resources.md
   - Contact image maintainer if critical image missing

**Prevention:**
- Use image validation webhooks
- Automated scanning in CI/CD pipeline
- Regular review of deployment manifests
- Update approved_resources.md monthly

### ErrImagePull Investigation
**Symptoms:**
- Pods showing ErrImagePull status
- Image pull errors in pod events
- Container creation failures

**Investigation Steps:**
1. **Check Registry Status**
   ```bash
   kubectl get pods -n harbor-system
   curl -k https://harbor.acmecorp.com/health
   ```

2. **Verify Service Account Permissions**
   ```bash
   kubectl get serviceaccount <sa-name> -n <namespace> -o yaml
   kubectl get secret <image-pull-secret> -n <namespace> -o yaml
   ```

3. **Test Registry Connectivity**
   ```bash
   kubectl run debug-pod --image=harbor.acmecorp.com/base/alpine:3.19 --command -- sleep 3600
   kubectl exec -it debug-pod -- nslookup harbor.acmecorp.com
   ```

**Resolution:**
- Fix registry connectivity issues
- Update image pull secrets
- Contact platform team for registry problems

## Pod Lifecycle Issues

### CrashLoopBackOff Investigation
**Symptoms:**
- Pods continuously restarting
- High restart count in pod status
- Application unavailable or degraded

**Immediate Investigation Steps:**
1. **Examine Pod Logs**
   ```bash
   kubectl logs <pod-name> -n <namespace> --previous
   kubectl logs <pod-name> -n <namespace> --tail=100
   ```

2. **Check Pod Resource Usage**
   ```bash
   kubectl top pod <pod-name> -n <namespace>
   kubectl describe pod <pod-name> -n <namespace>
   ```

3. **Analyze Pod Events**
   ```bash
   kubectl get events -n <namespace> --field-selector involvedObject.name=<pod-name>
   ```

**Common Root Causes:**
- **Insufficient Resources** (memory/CPU limits too low)
- **Application Configuration Errors** (missing env vars, config files)
- **Failed Health Checks** (readiness/liveness probe failures)
- **Application Bugs** (segfaults, uncaught exceptions)
- **Missing Dependencies** (database unavailable, external services down)

**Resolution Procedures:**
1. **For Resource Issues:**
   ```bash
   # Check current resource allocation against company standards
   kubectl get deployment <deployment-name> -n <namespace> -o yaml | grep -A 10 resources
   
   # Update resources per AcmeCorp standards (from acmecorp_standards.md)
   kubectl patch deployment <deployment-name> -n <namespace> -p '
   spec:
     template:
       spec:
         containers:
         - name: <container-name>
           resources:
             requests:
               memory: "64Mi"
               cpu: "100m"
             limits:
               memory: "128Mi"
               cpu: "200m"'
   ```

2. **For Configuration Issues:**
   - Review ConfigMaps and Secrets
   - Check environment variables against application requirements
   - Verify mounted volumes and file permissions

3. **For Health Check Issues:**
   ```bash
   # Temporarily disable health checks for debugging
   kubectl patch deployment <deployment-name> -n <namespace> -p '
   spec:
     template:
       spec:
         containers:
         - name: <container-name>
           readinessProbe: null
           livenessProbe: null'
   ```

**Prevention:**
- Follow resource allocation standards from acmecorp_standards.md
- Implement proper health check endpoints
- Use staging environment for configuration testing
- Monitor resource usage trends

### Pending Pod Investigation
**Symptoms:**
- Pods stuck in Pending state
- Scheduling failures
- Insufficient cluster resources

**Investigation Steps:**
1. **Check Node Resources**
   ```bash
   kubectl top nodes
   kubectl describe nodes
   ```

2. **Examine Pod Requirements**
   ```bash
   kubectl describe pod <pod-name> -n <namespace>
   kubectl get pod <pod-name> -n <namespace> -o yaml | grep -A 10 resources
   ```

3. **Check Resource Quotas**
   ```bash
   kubectl get resourcequota -n <namespace>
   kubectl describe resourcequota -n <namespace>
   ```

**Resolution:**
- Scale cluster nodes if insufficient capacity
- Adjust pod resource requests
- Review and update resource quotas
- Balance workload across namespaces

## Resource Management Issues

### Out of Memory (OOMKilled) Investigation
**Symptoms:**
- Pods terminated with reason "OOMKilled"
- High memory usage in monitoring
- Application performance degradation

**Investigation Steps:**
1. **Check Memory Usage Patterns**
   ```bash
   kubectl top pod <pod-name> -n <namespace> --containers
   kubectl logs <pod-name> -n <namespace> --previous | grep -i "memory\|oom"
   ```

2. **Compare Against Company Standards**
   - Review memory allocation in acmecorp_standards.md
   - Check if current limits align with application tier

3. **Analyze Memory Requests vs Limits**
   ```bash
   kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[*].resources}'
   ```

**Resolution:**
```bash
# Update memory allocation per AcmeCorp standards
# Frontend tier: 32Mi request, 64Mi limit
# Backend tier: 64Mi request, 128Mi limit

kubectl patch deployment <deployment-name> -n <namespace> -p '
spec:
  template:
    spec:
      containers:
      - name: <container-name>
        resources:
          requests:
            memory: "64Mi"
          limits:
            memory: "128Mi"'
```

### CPU Throttling Investigation
**Symptoms:**
- High CPU throttling metrics
- Application response time degradation
- Performance below SLA targets

**Investigation Steps:**
1. **Check CPU Usage and Throttling**
   ```bash
   kubectl top pod <pod-name> -n <namespace>
   # Check monitoring dashboard for CPU throttling metrics
   ```

2. **Review CPU Allocation**
   ```bash
   kubectl describe pod <pod-name> -n <namespace> | grep -A 5 "Limits\|Requests"
   ```

**Resolution:**
```bash
# Increase CPU limits per AcmeCorp standards
kubectl patch deployment <deployment-name> -n <namespace> -p '
spec:
  template:
    spec:
      containers:
      - name: <container-name>
        resources:
          requests:
            cpu: "100m"
          limits:
            cpu: "200m"'
```

## Network and Connectivity Issues

### Service Discovery Problems
**Symptoms:**
- Applications cannot connect to dependencies
- DNS resolution failures
- Service-to-service communication errors

**Investigation Steps:**
1. **Test DNS Resolution**
   ```bash
   kubectl run debug-pod --image=harbor.acmecorp.com/base/alpine:3.19 --command -- sleep 3600
   kubectl exec -it debug-pod -- nslookup <service-name>.<namespace>.svc.cluster.local
   ```

2. **Check Service Endpoints**
   ```bash
   kubectl get svc <service-name> -n <namespace>
   kubectl get endpoints <service-name> -n <namespace>
   ```

3. **Verify Network Policies**
   ```bash
   kubectl get networkpolicy -n <namespace>
   kubectl describe networkpolicy <policy-name> -n <namespace>
   ```

**Resolution:**
- Fix service selectors and labels
- Update network policy rules
- Verify pod readiness and health

### Ingress Issues
**Symptoms:**
- External traffic cannot reach applications
- 404 or 502 errors from load balancer
- SSL/TLS certificate problems

**Investigation Steps:**
1. **Check Ingress Configuration**
   ```bash
   kubectl get ingress -n <namespace>
   kubectl describe ingress <ingress-name> -n <namespace>
   ```

2. **Verify Ingress Controller Status**
   ```bash
   kubectl get pods -n ingress-nginx
   kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
   ```

**Resolution:**
- Update ingress rules and annotations
- Fix SSL certificate configuration
- Verify backend service availability

## Post-Incident Procedures

### Immediate Actions
1. **Resolve the immediate issue** using appropriate playbook procedures
2. **Document timeline** of events and actions taken
3. **Communicate status** to stakeholders via status page
4. **Monitor for recurrence** with enhanced alerting

### Post-Incident Review (Required for P0/P1)
1. **Schedule blameless post-mortem** within 48 hours
2. **Document root cause analysis** with timeline
3. **Identify action items** for prevention
4. **Update runbooks** based on lessons learned
5. **Share learnings** with engineering teams

### Follow-up Actions
1. **Implement monitoring improvements** to detect similar issues
2. **Update incident playbooks** with new procedures
3. **Schedule training** if process gaps identified
4. **Review and update** approved_resources.md if needed

## Escalation Procedures

### When to Escalate
- Issue persists after following playbook procedures
- Multiple services affected simultaneously
- Security implications identified
- Customer data potentially impacted

### Escalation Contacts
- **Platform Team**: platform-oncall@acmecorp.com
- **Security Team**: security-incident@acmecorp.com  
- **Engineering Manager**: eng-manager@acmecorp.com
- **CTO (P0 only)**: cto@acmecorp.com

### External Vendor Escalation
- **Cloud Provider**: Use support portal for infrastructure issues
- **Monitoring Vendor**: Contact for observability platform issues
- **Security Vendor**: Engage for security tool failures

This playbook should be the first reference for any Kubernetes-related incident at AcmeCorp. Regular drills and updates ensure readiness for production incidents.
