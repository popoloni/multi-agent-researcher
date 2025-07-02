#!/usr/bin/env python3
"""
Cross-platform Multi-Agent Researcher Control Script

This script provides cross-platform support for starting, stopping, and managing
the Multi-Agent Researcher services on Windows, macOS, and Linux.
"""

import os
import sys
import time
import signal
import subprocess
import platform
import requests
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any

# Configuration
OLLAMA_PORT = 11434
API_PORT = 12000
FRONTEND_PORT = 12001

class ServiceManager:
    """Cross-platform service manager for Multi-Agent Researcher"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.processes = {}
        
    def check_service(self, service_name: str, port: int, endpoint: str = "") -> bool:
        """Check if a service is running on the specified port"""
        try:
            url = f"http://localhost:{port}/{endpoint}"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def find_process_by_port(self, port: int) -> Optional[int]:
        """Find process ID using a specific port"""
        try:
            if self.system == "windows":
                cmd = f"netstat -ano | findstr :{port}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                return int(parts[-1])
            else:
                cmd = f"lsof -ti:{port}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    return int(result.stdout.strip().split('\n')[0])
        except:
            pass
        return None
    
    def kill_process(self, pid: int) -> bool:
        """Kill a process by PID"""
        try:
            if self.system == "windows":
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, check=True)
            else:
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process already terminated
            return True
        except:
            return False
    
    def start_ollama(self) -> bool:
        """Start Ollama service"""
        if self.check_service("Ollama", OLLAMA_PORT, "api/version"):
            print("  Ollama already running")
            return True
        
        try:
            print("  Starting Ollama...")
            if self.system == "windows":
                # On Windows, start Ollama as a background service
                process = subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                # On Unix-like systems
                process = subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid
                )
            
            self.processes['ollama'] = process
            
            # Wait for Ollama to start
            for _ in range(30):  # Wait up to 30 seconds
                if self.check_service("Ollama", OLLAMA_PORT, "api/version"):
                    print("  ✅ Ollama started successfully")
                    return True
                time.sleep(1)
            
            print("  ❌ Ollama failed to start within timeout")
            return False
            
        except FileNotFoundError:
            print("  ❌ Ollama not found. Please install Ollama first.")
            return False
        except Exception as e:
            print(f"  ❌ Failed to start Ollama: {e}")
            return False
    
    def start_backend(self) -> bool:
        """Start the backend API"""
        if self.check_service("Backend API", API_PORT, "health"):
            print("  Backend API already running")
            return True
        
        try:
            print("  Starting Backend API...")
            
            # Ensure we're in the correct directory
            os.chdir(Path(__file__).parent)
            
            # Start the backend
            if self.system == "windows":
                process = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "app.main:app", 
                     "--host", "0.0.0.0", "--port", str(API_PORT)],
                    stdout=open("server.log", "w"),
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                process = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "app.main:app", 
                     "--host", "0.0.0.0", "--port", str(API_PORT)],
                    stdout=open("server.log", "w"),
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid
                )
            
            self.processes['backend'] = process
            
            # Wait for backend to start
            for _ in range(30):  # Wait up to 30 seconds
                if self.check_service("Backend API", API_PORT, "health"):
                    print("  ✅ Backend API started successfully")
                    return True
                time.sleep(1)
            
            print("  ❌ Backend API failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"  ❌ Failed to start Backend API: {e}")
            return False
    
    def start_frontend(self) -> bool:
        """Start the frontend"""
        if self.check_service("Frontend", FRONTEND_PORT):
            print("  Frontend already running")
            return True
        
        try:
            print("  Starting Frontend...")
            
            frontend_dir = Path(__file__).parent / "frontend"
            if not frontend_dir.exists():
                print("  ❌ Frontend directory not found")
                return False
            
            os.chdir(frontend_dir)
            
            # Check if node_modules exists
            if not (frontend_dir / "node_modules").exists():
                print("  Installing frontend dependencies...")
                subprocess.run(["npm", "install"], check=True)
            
            # Start the frontend
            env = os.environ.copy()
            env["PORT"] = str(FRONTEND_PORT)
            env["HOST"] = "0.0.0.0"
            env["DANGEROUSLY_DISABLE_HOST_CHECK"] = "true"
            
            if self.system == "windows":
                process = subprocess.Popen(
                    ["npm", "start"],
                    stdout=open("../frontend.log", "w"),
                    stderr=subprocess.STDOUT,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
            else:
                process = subprocess.Popen(
                    ["npm", "start"],
                    stdout=open("../frontend.log", "w"),
                    stderr=subprocess.STDOUT,
                    env=env,
                    preexec_fn=os.setsid
                )
            
            self.processes['frontend'] = process
            
            # Wait for frontend to start
            for _ in range(60):  # Wait up to 60 seconds for frontend
                if self.check_service("Frontend", FRONTEND_PORT):
                    print("  ✅ Frontend started successfully")
                    return True
                time.sleep(1)
            
            print("  ❌ Frontend failed to start within timeout")
            return False
            
        except FileNotFoundError:
            print("  ❌ npm not found. Please install Node.js and npm.")
            return False
        except Exception as e:
            print(f"  ❌ Failed to start Frontend: {e}")
            return False
    
    def stop_service_by_port(self, service_name: str, port: int) -> bool:
        """Stop a service by finding and killing the process using the port"""
        pid = self.find_process_by_port(port)
        if pid:
            print(f"  Stopping {service_name} (PID: {pid})...")
            return self.kill_process(pid)
        else:
            print(f"  {service_name} not running")
            return True
    
    def stop_all_services(self):
        """Stop all services"""
        print("🛑 Stopping all services...")
        
        # Stop services by port
        self.stop_service_by_port("Frontend", FRONTEND_PORT)
        self.stop_service_by_port("Backend API", API_PORT)
        self.stop_service_by_port("Ollama", OLLAMA_PORT)
        
        # Stop processes we started
        for name, process in self.processes.items():
            try:
                if process.poll() is None:  # Process is still running
                    print(f"  Terminating {name}...")
                    if self.system == "windows":
                        process.terminate()
                    else:
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill if necessary
                        if self.system == "windows":
                            process.kill()
                        else:
                            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            except:
                pass
        
        self.processes.clear()
        time.sleep(2)
        
        # Verify all services are stopped
        all_stopped = (
            not self.check_service("Ollama", OLLAMA_PORT, "api/version") and
            not self.check_service("Backend API", API_PORT, "health") and
            not self.check_service("Frontend", FRONTEND_PORT)
        )
        
        if all_stopped:
            print("✅ All services successfully stopped")
        else:
            print("⚠️ Some services may still be running")
    
    def show_status(self):
        """Display status of all services"""
        print("\n📊 Multi-Agent Researcher Status:")
        print("==================================")
        
        # Check Ollama
        if self.check_service("Ollama", OLLAMA_PORT, "api/version"):
            print(f"✅ Ollama: Running on port {OLLAMA_PORT}")
            try:
                response = requests.get(f"http://localhost:{OLLAMA_PORT}/api/version", timeout=5)
                version_data = response.json()
                print(f"   Version: {version_data.get('version', 'Unknown')}")
            except:
                pass
        else:
            print("❌ Ollama: Not running")
        
        # Check Backend API
        if self.check_service("Backend API", API_PORT, "health"):
            print(f"✅ Backend API: Running on port {API_PORT}")
            try:
                response = requests.get(f"http://localhost:{API_PORT}/health", timeout=5)
                health_data = response.json()
                print(f"   Status: {health_data.get('status', 'Unknown')}")
            except:
                pass
        else:
            print("❌ Backend API: Not running")
        
        # Check Frontend
        if self.check_service("Frontend", FRONTEND_PORT):
            print(f"✅ Frontend: Running on port {FRONTEND_PORT}")
        else:
            print("❌ Frontend: Not running")
        
        print("\n📝 Access URLs:")
        print(f"  - Backend API: http://localhost:{API_PORT}")
        print(f"  - Frontend UI: http://localhost:{FRONTEND_PORT}")
        print(f"  - API Documentation: http://localhost:{API_PORT}/docs")
        print(f"  - Monitoring Dashboard: http://localhost:{API_PORT}/api/monitoring/dashboard")
        
        print("\n📋 Log Files:")
        print("  - Backend: server.log")
        print("  - Ollama: ollama.log")
        print("  - Frontend: frontend.log")
        
        print("\n💡 Commands:")
        print("  - Start all: python start_all.py")
        print("  - Stop all: python start_all.py --stop")
        print("  - Check status: python start_all.py --status")
        print("  - Restart all: python start_all.py --restart")
    
    def start_all_services(self):
        """Start all services"""
        print("🚀 Starting all services...")
        
        success = True
        
        # Start Ollama first
        if not self.start_ollama():
            success = False
        
        # Start Backend API
        if not self.start_backend():
            success = False
        
        # Start Frontend
        if not self.start_frontend():
            success = False
        
        if success:
            print("\n🎉 All services started successfully!")
            self.show_status()
        else:
            print("\n❌ Some services failed to start. Check the logs for details.")
    
    def restart_all_services(self):
        """Restart all services"""
        print("🔄 Restarting all services...")
        self.stop_all_services()
        time.sleep(3)
        self.start_all_services()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Multi-Agent Researcher Service Manager")
    parser.add_argument("--stop", action="store_true", help="Stop all services")
    parser.add_argument("--status", action="store_true", help="Show service status")
    parser.add_argument("--restart", action="store_true", help="Restart all services")
    
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\n\n🛑 Received interrupt signal. Stopping all services...")
        manager.stop_all_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.stop:
            manager.stop_all_services()
        elif args.status:
            manager.show_status()
        elif args.restart:
            manager.restart_all_services()
        else:
            # Default: start all services
            manager.start_all_services()
            
            # Keep script running to allow easy termination
            print("\nPress Ctrl+C to stop all services when done")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                pass
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()