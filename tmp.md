# 🚀 **AI-Powered Kubernetes Demo - Simple Workflow**

## 📋 **Prerequisites**
```bash
# Set up environment variables in .env file:
OPENROUTER_API_KEY=<your-key-here>
AGENT_SAFE_MODE=false
AGENT_AUTO_INVESTIGATE=true
AGENT_CHECK_INTERVAL=30
```

## 🎯 **Complete Demo in 4 Commands**

### **1. Setup & Deploy (Clean Start)**
```bash
make setup-cluster && make deploy-demo-apps && make start-fullstack
```
**What this does:**
- Creates 5-node Kubernetes cluster
- Deploys healthy applications only
- Starts AI monitoring system
- Opens frontend at http://localhost:3000

### **2. Create Chaos (On-Demand)**
```bash
# Interactive menu with 8 scenarios
make chaos

# Or direct commands:
make chaos-images    # Deploy ImagePullBackOff pods
make chaos-crashes   # Deploy CrashLoopBackOff pods  
make chaos-pods      # Delete healthy pods (auto-recreate)
```

### **3. Watch AI Response**
- **Frontend**: Real-time AI investigations at http://localhost:3000
- **Reports**: Detailed analysis in `reports/` directory
- **Enhanced Reasoning**: Company knowledge integration

### **4. Cleanup**
```bash
make clean
```
**Complete shutdown:** Removes containers, cluster, and reclaims disk space.

---

## 🔥 **Available Chaos Scenarios**

| Command | Effect | AI Detects |
|---------|--------|------------|
| `make chaos-images` | Deploy broken images | ImagePullBackOff |
| `make chaos-crashes` | Deploy failing apps | CrashLoopBackOff |
| `make chaos-pods` | Delete healthy pods | Pod recreation events |
| `make chaos-recovery` | Fix all issues | Recovery validation |

## 🎪 **Perfect Demo Flow**

```bash
# 1. Clean, healthy start
make setup-cluster && make deploy-demo-apps && make start-fullstack

# 2. Create chaos on-demand (while AI is watching!)
make chaos-images    # Watch AI detect ImagePullBackOff
make chaos-crashes   # Watch AI detect CrashLoopBackOff  

# 3. Demonstrate recovery
make chaos-recovery  # Show AI recommendations being applied

# 4. Clean shutdown
make clean
```

## ✅ **Success Metrics**
- **Real-time AI analysis** with company knowledge
- **Dynamic issue detection** as you create problems
- **Intelligent recommendations** for resolution
- **100% containerized workflow** - no host dependencies

---

**That's it!** Pure container-first AI-powered Kubernetes investigation demo. 🧠⚡