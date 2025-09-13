#!/usr/bin/env python3
"""
Start n8n Documentation Framework
Starts the Docker containers and validates the setup
"""

import sys
import subprocess
import time
import json
import requests
import os
import signal
from pathlib import Path

def run_command(cmd, description, check=True):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        if result.stdout.strip():
            print(f"   {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        return None

def check_docker():
    """Check if Docker is running"""
    print("🔍 Checking Docker...")
    result = run_command("docker --version", "Checking Docker version", check=False)
    if not result or result.returncode != 0:
        print("❌ Docker is not available. Please install Docker Desktop.")
        return False
    
    result = run_command("docker info", "Checking Docker daemon", check=False)
    if not result or result.returncode != 0:
        print("❌ Docker daemon is not running. Please start Docker Desktop.")
        return False
    
    print("✅ Docker is ready")
    return True

def check_config():
    """Check if required configuration files exist"""
    print("🔍 Checking configuration...")
    
    config_file = Path("analysis_config.json")
    if not config_file.exists():
        print("⚠️  analysis_config.json not found, creating default...")
        default_config = {
            "project_name": "daytrader",
            "mode": "hands-off", 
            "selected_agents": [
                "repomix-analyzer",
                "solution-architect", 
                "technical-architect",
                "business-logic-analyst"
            ],
            "framework_version": "2.1"
        }
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        print("✅ Created default analysis_config.json")
    else:
        print("✅ analysis_config.json found")
    
    docker_compose = Path("n8n/docker/docker-compose.yml")
    if not docker_compose.exists():
        print("❌ Docker compose file not found at n8n/docker/docker-compose.yml")
        return False
    
    print("✅ Configuration files ready")
    return True

def start_containers():
    """Start Docker containers"""
    print("🚀 Starting Docker containers...")
    
    # Change to docker directory
    docker_dir = Path("n8n/docker")
    if not docker_dir.exists():
        print("❌ Docker directory not found")
        return False
    
    # Start containers
    result = run_command(
        f"cd {docker_dir} && docker-compose up -d",
        "Starting containers with docker-compose"
    )
    
    if not result:
        return False
    
    print("✅ Containers started successfully")
    return True

def wait_for_services():
    """Wait for services to be ready"""
    services = [
        {"name": "API Server", "url": "http://localhost:8100/health", "timeout": 60},
        {"name": "n8n", "url": "http://localhost:5678", "timeout": 90},
        {"name": "Redis", "url": "http://localhost:8100/n8n/info", "timeout": 30}
    ]
    
    for service in services:
        print(f"⏳ Waiting for {service['name']} to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < service['timeout']:
            try:
                response = requests.get(service['url'], timeout=5)
                if response.status_code == 200:
                    print(f"✅ {service['name']} is ready")
                    break
            except requests.exceptions.RequestException:
                pass
            
            print(f"   Still waiting... ({int(time.time() - start_time)}s)")
            time.sleep(3)
        else:
            print(f"⚠️  {service['name']} didn't respond within {service['timeout']}s")
    
    print("🎉 All services are running!")

def show_status():
    """Show running containers and access URLs"""
    print("\n" + "="*50)
    print("📊 DOCKER STATUS")
    print("="*50)
    
    run_command("docker-compose -f n8n/docker/docker-compose.yml ps", "Container status")
    
    print("\n" + "="*50)
    print("🌐 ACCESS URLS")
    print("="*50)
    print("n8n Workflow UI:    http://localhost:5678")
    print("  Username: admin")
    print("  Password: changeme")
    print("")
    print("API Server:         http://localhost:8100")
    print("Health Check:       http://localhost:8100/health")
    print("n8n Integration:    http://localhost:8100/n8n/info")
    print("")
    print("Redis:              localhost:6379")
    print("Host Agent Server:  http://localhost:8200")

def check_host_server_running():
    """Check if host agent server is already running"""
    try:
        response = requests.get("http://localhost:8200/health", timeout=2)
        if response.status_code == 200 and "Host Agent Executor" in response.text:
            return True
    except requests.exceptions.RequestException:
        pass
    return False

def start_host_agent_server():
    """Start the host agent server"""
    print("🚀 Starting Host Agent Server...")
    
    # Kill any existing processes first
    try:
        result = subprocess.run(
            ["pkill", "-f", "host_agent_server.py"],
            capture_output=True,
            check=False
        )
        if result.returncode == 0:
            print("   Stopped existing host agent server")
            time.sleep(1)  # Give it time to stop
    except Exception:
        pass
    
    # Check if still running after kill attempt
    if check_host_server_running():
        print("⚠️  Host Agent Server still running, attempting to use existing instance")
        return True
    
    # Find the server file
    server_file = Path("n8n/host_agent_server.py")
    if not server_file.exists():
        print("❌ Host agent server not found at n8n/host_agent_server.py")
        return False
    
    # Start server in background
    try:
        cmd = [sys.executable, str(server_file)]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True  # This detaches it from the parent
        )
        
        # Save PID for later cleanup
        pid_file = Path(".host_server.pid")
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        # Wait a moment and check if it started
        time.sleep(3)
        if check_host_server_running():
            print("✅ Host Agent Server started successfully")
            return True
        else:
            print("❌ Host Agent Server failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start Host Agent Server: {e}")
        return False

def main():
    """Main execution function"""
    print("🔧 n8n Documentation Framework Startup")
    print("="*50)
    
    # Pre-flight checks
    if not check_docker():
        sys.exit(1)
    
    if not check_config():
        sys.exit(1)
    
    # Start host agent server first
    if not start_host_agent_server():
        print("❌ Failed to start Host Agent Server")
        sys.exit(1)
    
    # Start containers
    if not start_containers():
        print("❌ Failed to start containers")
        sys.exit(1)
    
    # Wait for readiness
    wait_for_services()
    
    # Show status
    show_status()
    
    print("\n🎉 n8n Documentation Framework is ready!")
    print("💡 Run 'python3 stop_n8n.py' to stop the services")

if __name__ == "__main__":
    main()