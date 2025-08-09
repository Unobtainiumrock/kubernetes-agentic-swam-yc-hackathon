"""
Real Kubernetes Client Service

This module provides actual connections to your Kind cluster
to replace the mock data in the API endpoints.
"""

import os
import logging
from typing import List, Dict, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

class KubernetesService:
    """Real Kubernetes client for interacting with Kind cluster"""
    
    def __init__(self):
        self.connected = False
        self._init_client()
    
    def _init_client(self):
        """Initialize Kubernetes client"""
        try:
            # Try to load kube config (works with Kind)
            config.load_kube_config()
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.connected = True
            logger.info("✅ Connected to Kubernetes cluster")
            
            # Test connection
            version = client.VersionApi().get_code()
            logger.info(f"Kubernetes version: {version.git_version}")
            
        except Exception as e:
            logger.warning(f"❌ Failed to connect to Kubernetes: {e}")
            logger.warning("Using mock data fallback")
            self.connected = False
    
    async def get_cluster_info(self) -> Dict:
        """Get real cluster information"""
        if not self.connected:
            return {"error": "Not connected to cluster", "using_mock": True}
        
        try:
            # Get cluster version
            version = client.VersionApi().get_code()
            
            # Get nodes
            nodes = self.v1.list_node()
            node_count = len(nodes.items)
            ready_nodes = sum(1 for node in nodes.items 
                            if any(condition.type == "Ready" and condition.status == "True" 
                                 for condition in node.status.conditions))
            
            return {
                "cluster_name": "kind-demo-cluster",
                "kubernetes_version": version.git_version,
                "node_count": node_count,
                "ready_nodes": ready_nodes,
                "connected": True
            }
            
        except ApiException as e:
            logger.error(f"Kubernetes API error: {e}")
            return {"error": str(e), "connected": False}
    
    async def get_all_pods(self, namespace: Optional[str] = None) -> List[Dict]:
        """Get real pod information"""
        if not self.connected:
            return []
        
        try:
            if namespace:
                pods = self.v1.list_namespaced_pod(namespace=namespace)
            else:
                pods = self.v1.list_pod_for_all_namespaces()
            
            pod_list = []
            for pod in pods.items:
                # Calculate ready containers
                ready_containers = 0
                total_containers = len(pod.spec.containers) if pod.spec.containers else 0
                
                if pod.status.container_statuses:
                    ready_containers = sum(1 for cs in pod.status.container_statuses if cs.ready)
                
                pod_info = {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "ready": f"{ready_containers}/{total_containers}",
                    "restarts": sum(cs.restart_count for cs in pod.status.container_statuses) if pod.status.container_statuses else 0,
                    "age": str(pod.metadata.creation_timestamp),
                    "node": pod.spec.node_name or "unknown"
                }
                pod_list.append(pod_info)
            
            return pod_list
            
        except ApiException as e:
            logger.error(f"Error getting pods: {e}")
            return []
    
    async def get_namespaces(self) -> List[Dict]:
        """Get real namespace information"""
        if not self.connected:
            return []
        
        try:
            namespaces = self.v1.list_namespace()
            ns_list = []
            
            for ns in namespaces.items:
                # Count pods in this namespace
                pods = self.v1.list_namespaced_pod(namespace=ns.metadata.name)
                pod_count = len(pods.items)
                
                # Count services in this namespace  
                services = self.v1.list_namespaced_service(namespace=ns.metadata.name)
                service_count = len(services.items)
                
                ns_info = {
                    "name": ns.metadata.name,
                    "status": ns.status.phase,
                    "pod_count": pod_count,
                    "service_count": service_count,
                    "labels": ns.metadata.labels or {}
                }
                ns_list.append(ns_info)
            
            return ns_list
            
        except ApiException as e:
            logger.error(f"Error getting namespaces: {e}")
            return []

# Global instance
k8s_service = KubernetesService() 