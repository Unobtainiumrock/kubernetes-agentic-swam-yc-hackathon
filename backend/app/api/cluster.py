"""
Cluster API Router

Provides endpoints for:
- Cluster status and health information
- Node and pod metrics
- Namespace and resource information
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel

# Import the real Kubernetes service
from ..services.k8s_client import k8s_service

router = APIRouter()

# Pydantic models
class NodeStatus(BaseModel):
    name: str
    status: str  # "Ready", "NotReady", "Unknown"
    role: str  # "control-plane", "worker"
    cpu_usage: float  # percentage
    memory_usage: float  # percentage
    disk_usage: float  # percentage
    pod_count: int
    labels: Dict[str, str]

class PodStatus(BaseModel):
    name: str
    namespace: str
    status: str  # "Running", "Pending", "Failed", "Succeeded"
    ready: str  # "1/1", "0/1", etc.
    restarts: int
    age: str
    node: str

class NamespaceInfo(BaseModel):
    name: str
    status: str  # "Active", "Terminating"
    pod_count: int
    service_count: int
    labels: Dict[str, str]

class ClusterSnapshot(BaseModel):
    cluster_name: str
    kubernetes_version: str
    nodes: List[NodeStatus]
    namespaces: List[NamespaceInfo]
    total_pods: int
    running_pods: int
    failed_pods: int
    timestamp: datetime

class ClusterMetrics(BaseModel):
    cluster_cpu_usage: float  # percentage
    cluster_memory_usage: float  # percentage
    cluster_disk_usage: float  # percentage
    total_pods: int
    running_pods: int
    failed_pods: int
    total_nodes: int
    ready_nodes: int
    timestamp: datetime

# Mock data for development
MOCK_NODES = [
    NodeStatus(
        name="demo-cluster-control-plane",
        status="Ready",
        role="control-plane",
        cpu_usage=35.2,
        memory_usage=45.8,
        disk_usage=22.1,
        pod_count=8,
        labels={"node-role.kubernetes.io/control-plane": "", "kubernetes.io/hostname": "demo-cluster-control-plane"}
    ),
    NodeStatus(
        name="demo-cluster-worker",
        status="Ready",
        role="worker",
        cpu_usage=12.4,
        memory_usage=28.7,
        disk_usage=15.3,
        pod_count=12,
        labels={"tier": "frontend", "zone": "us-west-1a", "kubernetes.io/hostname": "demo-cluster-worker"}
    ),
    NodeStatus(
        name="demo-cluster-worker2",
        status="Ready", 
        role="worker",
        cpu_usage=18.9,
        memory_usage=33.2,
        disk_usage=19.8,
        pod_count=10,
        labels={"tier": "backend", "zone": "us-west-1b", "kubernetes.io/hostname": "demo-cluster-worker2"}
    ),
    NodeStatus(
        name="demo-cluster-worker3",
        status="Ready",
        role="worker",
        cpu_usage=22.1,
        memory_usage=41.6,
        disk_usage=25.4,
        pod_count=8,
        labels={"tier": "database", "zone": "us-west-1c", "kubernetes.io/hostname": "demo-cluster-worker3"}
    ),
    NodeStatus(
        name="demo-cluster-worker4",
        status="Ready",
        role="worker",
        cpu_usage=8.7,
        memory_usage=19.3,
        disk_usage=11.2,
        pod_count=6,
        labels={"tier": "cache", "zone": "us-west-1a", "kubernetes.io/hostname": "demo-cluster-worker4"}
    )
]

MOCK_NAMESPACES = [
    NamespaceInfo(
        name="frontend",
        status="Active",
        pod_count=3,
        service_count=2,
        labels={"tier": "frontend"}
    ),
    NamespaceInfo(
        name="backend",
        status="Active",
        pod_count=6,
        service_count=3,
        labels={"tier": "backend"}
    ),
    NamespaceInfo(
        name="database",
        status="Active",
        pod_count=2,
        service_count=1,
        labels={"tier": "database"}
    ),
    NamespaceInfo(
        name="monitoring",
        status="Active",
        pod_count=4,
        service_count=2,
        labels={"tier": "monitoring"}
    )
]

MOCK_PODS = [
    PodStatus(
        name="frontend-app-abc123",
        namespace="frontend",
        status="Running",
        ready="1/1",
        restarts=0,
        age="2h",
        node="demo-cluster-worker"
    ),
    PodStatus(
        name="frontend-app-def456",
        namespace="frontend", 
        status="Running",
        ready="1/1",
        restarts=1,
        age="2h",
        node="demo-cluster-worker"
    ),
    PodStatus(
        name="backend-app-ghi789",
        namespace="backend",
        status="Running",
        ready="1/1",
        restarts=0,
        age="1h",
        node="demo-cluster-worker2"
    ),
    PodStatus(
        name="backend-app-jkl012",
        namespace="backend",
        status="Failed",
        ready="0/1",
        restarts=3,
        age="45m",
        node="demo-cluster-worker2"
    ),
    PodStatus(
        name="database-redis-0",
        namespace="database",
        status="Running",
        ready="1/1",
        restarts=0,
        age="3h",
        node="demo-cluster-worker3"
    )
]

@router.get("/snapshot", response_model=ClusterSnapshot)
async def get_cluster_snapshot():
    """Get complete cluster status snapshot"""
    total_pods = sum(ns.pod_count for ns in MOCK_NAMESPACES)
    running_pods = len([p for p in MOCK_PODS if p.status == "Running"])
    failed_pods = len([p for p in MOCK_PODS if p.status == "Failed"])
    
    return ClusterSnapshot(
        cluster_name="demo-cluster",
        kubernetes_version="v1.28.0",
        nodes=MOCK_NODES,
        namespaces=MOCK_NAMESPACES,
        total_pods=total_pods,
        running_pods=running_pods,
        failed_pods=failed_pods,
        timestamp=datetime.utcnow()
    )

@router.get("/metrics", response_model=ClusterMetrics)
async def get_cluster_metrics():
    """Get cluster resource usage metrics"""
    # Calculate cluster-wide averages
    cluster_cpu = sum(node.cpu_usage for node in MOCK_NODES) / len(MOCK_NODES)
    cluster_memory = sum(node.memory_usage for node in MOCK_NODES) / len(MOCK_NODES)
    cluster_disk = sum(node.disk_usage for node in MOCK_NODES) / len(MOCK_NODES)
    
    total_pods = len(MOCK_PODS)
    running_pods = len([p for p in MOCK_PODS if p.status == "Running"])
    failed_pods = len([p for p in MOCK_PODS if p.status == "Failed"])
    
    ready_nodes = len([n for n in MOCK_NODES if n.status == "Ready"])
    
    return ClusterMetrics(
        cluster_cpu_usage=round(cluster_cpu, 1),
        cluster_memory_usage=round(cluster_memory, 1),
        cluster_disk_usage=round(cluster_disk, 1),
        total_pods=total_pods,
        running_pods=running_pods,
        failed_pods=failed_pods,
        total_nodes=len(MOCK_NODES),
        ready_nodes=ready_nodes,
        timestamp=datetime.utcnow()
    )

@router.get("/nodes", response_model=List[NodeStatus])
async def get_nodes():
    """Get status of all cluster nodes"""
    return MOCK_NODES

@router.get("/nodes/{node_name}", response_model=NodeStatus)
async def get_node_status(node_name: str):
    """Get detailed status of a specific node"""
    node = next((n for n in MOCK_NODES if n.name == node_name), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.get("/namespaces", response_model=List[NamespaceInfo])
async def get_namespaces():
    """Get list of all namespaces"""
    # Try to get real namespaces first, fallback to mock
    try:
        real_namespaces = await k8s_service.get_namespaces()
        if real_namespaces:
            return [NamespaceInfo(**ns) for ns in real_namespaces]
    except Exception as e:
        import logging
        logging.warning(f"Failed to get real namespaces, using mock data: {e}")
    
    return MOCK_NAMESPACES

@router.get("/namespaces/{namespace}/pods", response_model=List[PodStatus])
async def get_namespace_pods(namespace: str):
    """Get pods in a specific namespace"""
    # Check if namespace exists
    if not any(ns.name == namespace for ns in MOCK_NAMESPACES):
        raise HTTPException(status_code=404, detail="Namespace not found")
    
    # Filter pods by namespace
    namespace_pods = [p for p in MOCK_PODS if p.namespace == namespace]
    return namespace_pods

@router.get("/pods", response_model=List[PodStatus])
async def get_all_pods(
    namespace: Optional[str] = None,
    status: Optional[str] = None,
    node: Optional[str] = None
):
    """Get pods with optional filtering"""
    # Try to get real pods first, fallback to mock
    try:
        real_pods = await k8s_service.get_all_pods(namespace=namespace)
        if real_pods:
            # Convert to PodStatus objects and apply filters
            pods = []
            for pod_dict in real_pods:
                pod = PodStatus(**pod_dict)
                # Apply additional filters
                if status and pod.status != status:
                    continue
                if node and pod.node != node:
                    continue
                pods.append(pod)
            return pods
    except Exception as e:
        # Log the error but continue with mock data
        import logging
        logging.warning(f"Failed to get real pods, using mock data: {e}")
    
    # Fallback to mock data
    pods = MOCK_PODS
    
    # Apply filters
    if namespace:
        pods = [p for p in pods if p.namespace == namespace]
    if status:
        pods = [p for p in pods if p.status == status]
    if node:
        pods = [p for p in pods if p.node == node]
    
    return pods

@router.get("/health")
async def get_cluster_health():
    """Get cluster health summary"""
    # Try to get real cluster info first
    try:
        cluster_info = await k8s_service.get_cluster_info()
        if cluster_info.get("connected"):
            # Get real pods for health calculation
            all_pods = await k8s_service.get_all_pods()
            
            total_nodes = cluster_info.get("node_count", 0)
            ready_nodes = cluster_info.get("ready_nodes", 0)
            
            total_pods = len(all_pods)
            running_pods = len([p for p in all_pods if p.get("status") == "Running"])
            failed_pods = len([p for p in all_pods if p.get("status") in ["Failed", "Error"]])
            
            # Determine overall health
            node_health = "healthy" if ready_nodes == total_nodes else "degraded"
            pod_health = "healthy" if failed_pods == 0 else "degraded" if failed_pods < 3 else "critical"
            
            overall_health = "healthy"
            if node_health == "degraded" or pod_health == "degraded":
                overall_health = "degraded"
            elif node_health == "critical" or pod_health == "critical":
                overall_health = "critical"
            
            return {
                "overall_status": overall_health,
                "nodes": {
                    "total": total_nodes,
                    "ready": ready_nodes,
                    "status": node_health
                },
                "pods": {
                    "total": total_pods,
                    "running": running_pods,
                    "failed": failed_pods,
                    "status": pod_health
                },
                "cluster_info": cluster_info,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        import logging
        logging.warning(f"Failed to get real cluster health, using mock data: {e}")
    
    # Fallback to mock data
    total_nodes = len(MOCK_NODES)
    ready_nodes = len([n for n in MOCK_NODES if n.status == "Ready"])
    
    total_pods = len(MOCK_PODS)
    running_pods = len([p for p in MOCK_PODS if p.status == "Running"])
    failed_pods = len([p for p in MOCK_PODS if p.status == "Failed"])
    
    # Determine overall health
    node_health = "healthy" if ready_nodes == total_nodes else "degraded"
    pod_health = "healthy" if failed_pods == 0 else "degraded" if failed_pods < 3 else "critical"
    
    overall_health = "healthy"
    if node_health == "degraded" or pod_health == "degraded":
        overall_health = "degraded"
    elif node_health == "critical" or pod_health == "critical":
        overall_health = "critical"
    
    return {
        "overall_status": overall_health,
        "nodes": {
            "total": total_nodes,
            "ready": ready_nodes,
            "status": node_health
        },
        "pods": {
            "total": total_pods,
            "running": running_pods,
            "failed": failed_pods,
            "status": pod_health
        },
        "using_mock_data": True,
        "timestamp": datetime.utcnow().isoformat()
    } 