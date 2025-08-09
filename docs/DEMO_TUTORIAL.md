Step 1: Clean Cluster Setup
```
cd /path/to/kubernetes-agentic-swam-yc-hackathon
make run
# Inside container:
./cleanup.sh && ./setup-cluster.sh
# Verify: kubectl get nodes, kubectl get pods --all-namespaces
```

Step 2: Terminal 1 - Start Monitoring outside container (Healthy State)
```
cd /root/api
python3 autonomous_monitor.py
# Expected: ✅ Cluster healthy - 5/5 nodes, 19 running
```

Step 3: Terminal 2 - Introduce Bugs outside container
```
docker exec -it k8s-agentic-swarm-command-center-main bash
./deploy-demo-apps.sh
```

Step 4: Terminal 1 - Watch Detection outside container
```
✅ [TIME] Cluster healthy - 5/5 nodes, 19 running
✅ [TIME] Cluster healthy - 5/5 nodes, 19 running

🟠 [TIME] HIGH severity issues detected (1 high) - 5/5 nodes, 32 running, 1 pending
🚨 ISSUES DETECTED! Triggering autonomous investigation...
```