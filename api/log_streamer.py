#!/usr/bin/env python3
"""
Log Streaming Service for Autonomous Monitor

This service captures logs from the autonomous monitor and streams them
to the FastAPI backend for real-time display in the frontend.
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
import os

class LogStreamer:
    """Streams autonomous monitor logs to FastAPI backend"""
    
    def __init__(self, backend_url: str = "http://localhost:8001"):
        self.backend_url = backend_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
        # Log buffer for cases when backend is unavailable
        self.log_buffer: List[Dict] = []
        self.max_buffer_size = 100
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_log_entry(self, 
                           agent_id: str,
                           log_level: str,
                           message: str,
                           source: str,
                           details: Optional[Dict] = None):
        """Send a log entry to the backend"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": agent_id,
            "log_level": log_level,
            "message": message,
            "source": source,
            "details": details or {}
        }
        
        try:
            if self.session:
                async with self.session.post(
                    f"{self.backend_url}/api/agents/logs/add",
                    json=log_entry,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        # Successfully sent, clear any buffered logs
                        if self.log_buffer:
                            await self._flush_buffer()
                    else:
                        self.logger.warning(f"Failed to send log: {response.status}")
                        self._buffer_log(log_entry)
            else:
                self._buffer_log(log_entry)
                
        except Exception as e:
            self.logger.error(f"Error sending log entry: {e}")
            self._buffer_log(log_entry)
    
    async def send_status_update(self,
                               agent_id: str,
                               status: str,
                               issues_count: int,
                               nodes_ready: int,
                               nodes_total: int,
                               pods_running: int,
                               pods_total: int):
        """Send agent status update to backend"""
        status_update = {
            "agent_id": agent_id,
            "status": status,
            "issues_count": issues_count,
            "nodes_ready": nodes_ready,
            "nodes_total": nodes_total,
            "pods_running": pods_running,
            "pods_total": pods_total,
            "last_update": datetime.utcnow().isoformat()
        }
        
        try:
            if self.session:
                async with self.session.post(
                    f"{self.backend_url}/api/agents/status/update",
                    json=status_update,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status != 200:
                        self.logger.warning(f"Failed to send status update: {response.status}")
        except Exception as e:
            self.logger.error(f"Error sending status update: {e}")
    
    def _buffer_log(self, log_entry: Dict):
        """Buffer log entry when backend is unavailable"""
        self.log_buffer.append(log_entry)
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer.pop(0)  # Remove oldest entry
    
    async def _flush_buffer(self):
        """Flush buffered logs to backend"""
        for log_entry in self.log_buffer:
            try:
                if self.session:
                    async with self.session.post(
                        f"{self.backend_url}/api/agents/logs/add",
                        json=log_entry,
                        timeout=aiohttp.ClientTimeout(total=2)
                    ) as response:
                        if response.status != 200:
                            break  # Stop flushing if backend issues
            except Exception:
                break  # Stop flushing on error
        
        self.log_buffer.clear()

class AutonomousMonitorStreamer:
    """Specialized streamer for autonomous monitor logs"""
    
    def __init__(self, backend_url: str = "http://localhost:8001"):
        self.streamer = LogStreamer(backend_url)
        self.agent_id = "autonomous_monitor"
        
    async def __aenter__(self):
        await self.streamer.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.streamer.__aexit__(exc_type, exc_val, exc_tb)
    
    async def log_issues_detected(self, issues_count: int, issues_summary: List[str]):
        """Log when issues are detected"""
        message = f"🚨 ISSUES DETECTED! Triggering autonomous investigation... {issues_count} total issues found"
        details = {
            "issues_count": issues_count,
            "issues_summary": issues_summary[:3]  # Top 3 issues
        }
        
        await self.streamer.send_log_entry(
            agent_id=self.agent_id,
            log_level="warn",
            message=message,
            source="autonomous_monitor",
            details=details
        )
    
    async def log_investigation_start(self, report_filename: str):
        """Log investigation start"""
        message = f"🤖 Starting deterministic investigation... Report will be saved to: {report_filename}"
        
        await self.streamer.send_log_entry(
            agent_id=self.agent_id,
            log_level="info",
            message=message,
            source="deterministic_investigator",
            details={"report_file": report_filename}
        )
    
    async def log_investigation_complete(self, success: bool, findings_count: int = 0):
        """Log investigation completion"""
        if success:
            message = f"✅ Investigation complete! {findings_count} findings identified"
            log_level = "info"
        else:
            message = "❌ Investigation failed or incomplete"
            log_level = "error"
        
        await self.streamer.send_log_entry(
            agent_id=self.agent_id,
            log_level=log_level,
            message=message,
            source="deterministic_investigator",
            details={"findings_count": findings_count}
        )
    
    async def log_health_status(self, 
                              health_data: Dict,
                              status_message: str):
        """Log periodic health status"""
        # Extract status for backend
        status = "healthy"
        if health_data.get('critical_issues', 0) > 0:
            status = "critical_issues"
        elif health_data.get('high_issues', 0) > 0:
            status = "high_issues"
        elif health_data.get('total_issues', 0) > 0:
            status = "issues_detected"
        
        # Send status update
        await self.streamer.send_status_update(
            agent_id=self.agent_id,
            status=status,
            issues_count=health_data.get('total_issues', 0),
            nodes_ready=health_data.get('nodes_ready', 0),
            nodes_total=health_data.get('nodes_total', 0),
            pods_running=health_data.get('pods_running', 0),
            pods_total=health_data.get('pods_total', 0)
        )
        
        # Send log entry for status message
        log_level = "info"
        if "CRITICAL" in status_message:
            log_level = "error"
        elif "HIGH" in status_message:
            log_level = "warn"
        
        await self.streamer.send_log_entry(
            agent_id=self.agent_id,
            log_level=log_level,
            message=status_message,
            source="autonomous_monitor",
            details=health_data
        )

# Singleton instance for easy access
_global_streamer: Optional[AutonomousMonitorStreamer] = None

async def get_streamer() -> AutonomousMonitorStreamer:
    """Get global streamer instance"""
    global _global_streamer
    if _global_streamer is None:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8001")
        _global_streamer = AutonomousMonitorStreamer(backend_url)
        await _global_streamer.__aenter__()
    return _global_streamer

async def cleanup_streamer():
    """Cleanup global streamer"""
    global _global_streamer
    if _global_streamer:
        await _global_streamer.__aexit__(None, None, None)
        _global_streamer = None 