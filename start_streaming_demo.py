#!/usr/bin/env python3
"""
Start Streaming Demo

This script starts both the FastAPI backend and the autonomous monitor
to demonstrate real-time log streaming and agent status updates.
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

class StreamingDemo:
    def __init__(self):
        self.processes = []
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.running = False
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up all running processes."""
        print("🧹 Cleaning up processes...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Error cleaning up process: {e}")
    
    def start_backend(self):
        """Start the FastAPI backend."""
        print("🚀 Starting FastAPI backend...")
        
        backend_dir = Path(__file__).parent / "backend"
        
        if not backend_dir.exists():
            print("❌ Backend directory not found!")
            return False
        
        try:
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--host", "0.0.0.0", 
                "--port", "8000",
                "--reload"
            ], cwd=backend_dir)
            
            self.processes.append(process)
            print("✅ FastAPI backend started on http://localhost:8000")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_autonomous_monitor(self):
        """Start the autonomous monitor."""
        print("🤖 Starting autonomous monitor...")
        
        api_dir = Path(__file__).parent / "api"
        monitor_script = api_dir / "autonomous_monitor.py"
        
        if not monitor_script.exists():
            print("❌ Autonomous monitor script not found!")
            return False
        
        try:
            # Create reports directory if it doesn't exist
            reports_dir = Path("/root/reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            process = subprocess.Popen([
                sys.executable, str(monitor_script)
            ], cwd=api_dir)
            
            self.processes.append(process)
            print("✅ Autonomous monitor started")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start autonomous monitor: {e}")
            return False
    
    def check_dependencies(self):
        """Check if required dependencies are available."""
        print("🔍 Checking dependencies...")
        
        try:
            import aiohttp
            print("✅ aiohttp available")
        except ImportError:
            print("❌ aiohttp not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp>=3.8.0"])
        
        try:
            import fastapi
            print("✅ FastAPI available")
        except ImportError:
            print("❌ FastAPI not found. Please install backend dependencies")
            return False
        
        return True
    
    def run(self):
        """Run the streaming demo."""
        print("🎯 Kubernetes Autonomous Agent Log Streaming Demo")
        print("=" * 55)
        
        if not self.check_dependencies():
            return False
        
        # Start backend
        if not self.start_backend():
            return False
        
        # Wait for backend to start
        print("⏳ Waiting for backend to start...")
        time.sleep(3)
        
        # Start autonomous monitor
        if not self.start_autonomous_monitor():
            return False
        
        print("\n🎉 Streaming demo is running!")
        print("📊 Open http://localhost:3000 to view the frontend")
        print("🔗 Backend API: http://localhost:8000")
        print("📝 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop all services\n")
        
        # Keep running until interrupted
        try:
            while self.running:
                # Check if processes are still running
                for i, process in enumerate(self.processes[:]):
                    if process.poll() is not None:
                        print(f"⚠️  Process {i} has stopped")
                        self.processes.remove(process)
                
                if not self.processes:
                    print("❌ All processes have stopped")
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
        
        return True

def main():
    demo = StreamingDemo()
    success = demo.run()
    
    if success:
        print("👋 Demo completed successfully!")
    else:
        print("❌ Demo failed to start")
        sys.exit(1)

if __name__ == "__main__":
    main() 