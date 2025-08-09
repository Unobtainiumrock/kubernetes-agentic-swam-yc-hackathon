#!/usr/bin/env python3
"""
Autonomous Kubernetes Monitor - Chunk 1: Basic Health Check Loop

This is the first chunk - just a simple health check loop that runs every 1 second.
"""
import asyncio
import logging
import sys
import os
from datetime import datetime
import signal

# Add the api directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.tools.kubectl_wrapper import KubectlWrapper


class AutonomousMonitor:
    """Simple autonomous monitor - Chunk 1 implementation."""
    
    def __init__(self):
        self.running = False
        self.kubectl = KubectlWrapper()
        self.check_interval = 1  # 1 second for live demo
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def get_basic_cluster_health(self):
        """Get basic cluster health information."""
        try:
            # Get nodes
            nodes_result = await self.kubectl.get_nodes()
            
            # Check if we got valid nodes data
            if not nodes_result or not isinstance(nodes_result, dict) or "items" not in nodes_result:
                return {
                    "healthy": False,
                    "error": "Failed to get nodes: Invalid response format",
                    "nodes_ready": 0,
                    "nodes_total": 0,
                    "pods_running": 0,
                    "pods_total": 0
                }
            
            # Count ready nodes  
            node_items = nodes_result.get("items", [])
            nodes_total = len(node_items)
            nodes_ready = 0
            
            for node in node_items:
                conditions = node.get("status", {}).get("conditions", [])
                is_ready = any(
                    condition.get("type") == "Ready" and condition.get("status") == "True"
                    for condition in conditions
                )
                if is_ready:
                    nodes_ready += 1
            
            # Get pods
            pods_result = await self.kubectl.get_all_pods()
            if not pods_result or not isinstance(pods_result, dict) or "items" not in pods_result:
                return {
                    "healthy": False,
                    "error": "Failed to get pods: Invalid response format",
                    "nodes_ready": nodes_ready,
                    "nodes_total": nodes_total,
                    "pods_running": 0,
                    "pods_total": 0
                }
            
            # Count pod states
            pod_items = pods_result.get("items", [])
            pods_total = len(pod_items)
            pods_running = 0
            pods_failed = 0
            pods_pending = 0
            
            for pod in pod_items:
                phase = pod.get("status", {}).get("phase", "Unknown")
                if phase == "Running":
                    pods_running += 1
                elif phase == "Failed":
                    pods_failed += 1
                elif phase == "Pending":
                    pods_pending += 1
            
            # Determine if cluster is healthy
            healthy = (nodes_ready == nodes_total and 
                      nodes_ready > 0 and 
                      pods_failed == 0 and 
                      pods_pending == 0)
            
            return {
                "healthy": healthy,
                "nodes_ready": nodes_ready,
                "nodes_total": nodes_total,
                "pods_running": pods_running,
                "pods_failed": pods_failed,
                "pods_pending": pods_pending,
                "pods_total": pods_total
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "nodes_ready": 0,
                "nodes_total": 0,
                "pods_running": 0,
                "pods_total": 0
            }
    
    def format_health_status(self, health_data):
        """Format health data for terminal display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if health_data.get("error"):
            return f"❌ [{timestamp}] Health check failed: {health_data['error']}"
        
        nodes_status = f"{health_data['nodes_ready']}/{health_data['nodes_total']}"
        pods_status = f"{health_data['pods_running']} running"
        
        if health_data['pods_failed'] > 0:
            pods_status += f", {health_data['pods_failed']} failed"
        if health_data['pods_pending'] > 0:
            pods_status += f", {health_data['pods_pending']} pending"
        
        if health_data["healthy"]:
            icon = "✅"
            status = "Cluster healthy"
        else:
            icon = "⚠️ "
            status = "Cluster issues detected"
        
        return f"{icon} [{timestamp}] {status} - {nodes_status} nodes, {pods_status}"
    
    async def health_check_loop(self):
        """Main health check loop - runs every second."""
        print("🔄 Starting health check loop (every 1 second)")
        print("   Press Ctrl+C to stop monitoring")
        print()
        
        while self.running:
            try:
                # Get cluster health
                health_data = await self.get_basic_cluster_health()
                
                # Display status
                status_message = self.format_health_status(health_data)
                print(status_message)
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Health check loop error: {e}")
                print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Monitor error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def start_monitoring(self):
        """Start the autonomous monitoring."""
        print("🚀 Autonomous Kubernetes Monitor - Chunk 1")
        print("=" * 50)
        print(f"⏱️  Health check interval: {self.check_interval} second(s)")
        print("🎯 Chunk 1: Basic health check loop only")
        print()
        
        # Validate environment first
        print("🔧 Validating environment...")
        try:
            health_data = await self.get_basic_cluster_health()
            if health_data.get("error"):
                print(f"❌ Environment validation failed: {health_data['error']}")
                return False
            else:
                print(f"✅ Environment validated - {health_data['nodes_total']} nodes, {health_data['pods_total']} pods found")
                print()
        except Exception as e:
            print(f"❌ Environment validation failed: {e}")
            return False
        
        # Start monitoring
        self.running = True
        await self.health_check_loop()
        
        print("\n🛑 Monitoring stopped")
        return True


async def main():
    """Main function."""
    monitor = AutonomousMonitor()
    await monitor.start_monitoring()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)
