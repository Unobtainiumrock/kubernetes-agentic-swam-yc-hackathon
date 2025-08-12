"""
Autonomous monitoring API endpoints.
"""

import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from ..schemas import HealthResponse

# Import the moved autonomous monitor
try:
    from ..services.autonomous_monitor import AutonomousMonitor
    MONITOR_AVAILABLE = True
except ImportError:
    MONITOR_AVAILABLE = False

router = APIRouter()

class MonitorConfig(BaseModel):
    safe_mode: bool = True
    auto_investigate: bool = True
    check_interval: int = 30
    backend_url: str = "http://localhost:8000"

class MonitorStatus(BaseModel):
    status: str
    is_running: bool
    config: Optional[MonitorConfig] = None

# Global monitor instance
autonomous_monitor = None
monitor_task = None

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check for monitoring service"""
    return HealthResponse(
        status="ok" if MONITOR_AVAILABLE else "limited", 
        service="monitoring-api", 
        version="0.1.0"
    )

@router.post("/start")
async def start_monitoring(config: MonitorConfig, background_tasks: BackgroundTasks):
    """Start the autonomous monitor"""
    global autonomous_monitor, monitor_task
    
    if not MONITOR_AVAILABLE:
        raise HTTPException(status_code=503, detail="Autonomous monitor not available")
    
    if monitor_task and not monitor_task.done():
        raise HTTPException(status_code=409, detail="Monitor already running")
    
    # Initialize monitor with config
    autonomous_monitor = AutonomousMonitor(
        safe_mode=config.safe_mode,
        auto_investigate=config.auto_investigate,
        check_interval=config.check_interval,
        backend_url=config.backend_url
    )
    
    # Start monitoring in background
    background_tasks.add_task(run_autonomous_monitor)
    
    return {"status": "started", "message": "Autonomous monitoring started"}

@router.post("/stop")
async def stop_monitoring():
    """Stop the autonomous monitor"""
    global monitor_task, autonomous_monitor
    
    if monitor_task and not monitor_task.done():
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        monitor_task = None
        autonomous_monitor = None
        return {"status": "stopped", "message": "Autonomous monitoring stopped"}
    else:
        raise HTTPException(status_code=409, detail="Monitor not running")

@router.get("/status", response_model=MonitorStatus)
async def get_monitor_status() -> MonitorStatus:
    """Get current monitor status"""
    global monitor_task, autonomous_monitor
    
    is_running = monitor_task is not None and not monitor_task.done()
    
    config = None
    if autonomous_monitor:
        config = MonitorConfig(
            safe_mode=autonomous_monitor.safe_mode,
            auto_investigate=autonomous_monitor.auto_investigate,
            check_interval=autonomous_monitor.check_interval,
            backend_url=autonomous_monitor.backend_url
        )
    
    return MonitorStatus(
        status="running" if is_running else "stopped",
        is_running=is_running,
        config=config
    )

async def run_autonomous_monitor():
    """Background task to run the autonomous monitor"""
    global autonomous_monitor, monitor_task
    
    try:
        if autonomous_monitor:
            await autonomous_monitor.start_monitoring()
    except asyncio.CancelledError:
        # Monitor was stopped
        pass
    except Exception as e:
        # Monitor failed
        print(f"Autonomous monitor failed: {e}")
    finally:
        monitor_task = None
        autonomous_monitor = None 