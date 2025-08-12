# AcmeCorp Incident Response Playbook

## Incident Classification

### Critical Severity
- Complete service outage
- Data loss or corruption
- Security breaches

### High Severity  
- Partial service degradation
- CrashLoopBackOff in production
- Resource exhaustion

### Medium Severity
- ImagePullBackOff issues
- Scaling problems
- Configuration drift

## ImagePullBackOff Investigation

**Immediate Steps:**
1. Verify image exists in approved registry
2. Check image tag and naming convention
3. Validate registry credentials and access
4. Review network connectivity to registry

**Resolution:**
- Update to approved image from harbor.acmecorp.com
- Fix image tag if using `latest` or invalid tag
- Verify ImagePullSecrets are properly configured

## CrashLoopBackOff Investigation

**Immediate Steps:**
1. Check pod logs: `kubectl logs <pod> --previous`
2. Review resource limits and requests
3. Examine application startup sequence
4. Check for missing dependencies or configurations

**Common Causes:**
- Insufficient memory allocation
- Missing environment variables
- Configuration file errors
- Dependency service unavailability

## Out of Memory (OOMKilled) Investigation

**Immediate Actions:**
1. Review memory limits vs actual usage
2. Check for memory leaks in application
3. Analyze heap dumps if available
4. Adjust resource limits per AcmeCorp standards

## Network and Connectivity Issues

**Troubleshooting Steps:**
1. Verify service discovery (DNS resolution)
2. Check network policies
3. Validate service account permissions
4. Test connectivity between services

## Escalation Procedures

**Level 1:** On-call engineer (15 minutes)
**Level 2:** Senior SRE team (30 minutes)  
**Level 3:** Engineering manager (1 hour)
**Level 4:** CTO escalation (2 hours) 