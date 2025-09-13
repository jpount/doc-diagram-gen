#!/usr/bin/env python3
"""
Stop n8n Documentation Framework
Stops Docker containers and optionally cleans up data
"""

import sys
import subprocess
import argparse
import os
import signal
import requests
import time
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
    """Check if Docker is available"""
    result = run_command("docker --version", "Checking Docker", check=False)
    return result and result.returncode == 0

def stop_containers(remove=False, remove_storage=False):
    """Stop Docker containers"""
    docker_dir = Path("n8n/docker")
    if not docker_dir.exists():
        print("❌ Docker directory not found at n8n/docker/")
        return False
    
    # Stop containers
    if remove_storage:
        action = "Stopping containers and removing storage volumes"
        cmd = f"cd {docker_dir} && docker-compose down -v"
    elif remove:
        action = "Stopping and removing containers"
        cmd = f"cd {docker_dir} && docker-compose down"
    else:
        action = "Stopping containers"
        cmd = f"cd {docker_dir} && docker-compose stop"
    
    result = run_command(cmd, action)
    
    if not result:
        return False
    
    print("✅ Containers stopped successfully")
    return True

def cleanup_data():
    """Remove Docker volumes and data"""
    print("🧹 Cleaning up data volumes...")
    
    docker_dir = Path("n8n/docker")
    
    # Remove volumes
    result = run_command(
        f"cd {docker_dir} && docker-compose down -v",
        "Removing Docker volumes"
    )
    
    if result:
        print("✅ Data volumes cleaned up")
    else:
        print("⚠️  Failed to clean up volumes")

def cleanup_images():
    """Remove Docker images"""
    print("🧹 Cleaning up Docker images...")
    
    images = [
        "n8nio/n8n:latest",
        "redis:7-alpine"
    ]
    
    for image in images:
        run_command(f"docker rmi {image}", f"Removing {image}", check=False)
    
    # Remove custom built images
    run_command(
        "docker image prune -f --filter label=project=doc-framework",
        "Removing custom built images",
        check=False
    )
    
    print("✅ Images cleaned up")

def show_status():
    """Show current container status"""
    print("\n" + "="*50)
    print("📊 FINAL STATUS")
    print("="*50)
    
    result = run_command(
        "docker-compose -f n8n/docker/docker-compose.yml ps -a",
        "Container status",
        check=False
    )
    
    if not result or not result.stdout.strip():
        print("✅ No containers running")
    
    # Show volumes
    result = run_command(
        "docker volume ls | grep -E '(n8n|redis|doc-framework)'",
        "Remaining volumes",
        check=False
    )

def check_host_server_running():
    """Check if host agent server is running"""
    try:
        response = requests.get("http://localhost:8200/health", timeout=2)
        if response.status_code == 200 and "Host Agent Executor" in response.text:
            return True
    except requests.exceptions.RequestException:
        pass
    return False

def stop_host_agent_server():
    """Stop the host agent server"""
    print("🛑 Stopping Host Agent Server...")
    
    # Check if running
    if not check_host_server_running():
        print("✅ Host Agent Server is not running")
        return True
    
    # Try multiple methods to stop the server
    stopped = False
    
    # Method 1: Try to stop using PID file
    pid_file = Path(".host_server.pid")
    if pid_file.exists():
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            os.kill(pid, signal.SIGTERM)
            pid_file.unlink()  # Remove PID file
            
            # Wait and verify it stopped
            time.sleep(2)
            if not check_host_server_running():
                print("✅ Host Agent Server stopped successfully (via PID file)")
                stopped = True
                
        except (ValueError, ProcessLookupError, FileNotFoundError):
            pass
    
    # Method 2: Find by port and kill process
    if not stopped:
        try:
            result = subprocess.run(
                ["lsof", "-ti", ":8200"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"   Killed process {pid} using port 8200")
                    except (ProcessLookupError, ValueError):
                        pass
                        
                time.sleep(2)
                if not check_host_server_running():
                    print("✅ Host Agent Server stopped successfully (via port)")
                    stopped = True
        except Exception:
            pass
    
    # Method 3: Fallback to pkill
    if not stopped:
        try:
            result = subprocess.run(
                ["pkill", "-f", "host_agent_server.py"],
                capture_output=True,
                check=False
            )
            
            time.sleep(2)
            if not check_host_server_running():
                print("✅ Host Agent Server stopped successfully (via pkill)")
                stopped = True
            else:
                print("⚠️  Host Agent Server may still be running")
                
        except Exception as e:
            print(f"⚠️  Could not stop Host Agent Server: {e}")
    
    return True  # Don't fail the whole script if we can't stop it

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Stop n8n Documentation Framework")
    parser.add_argument(
        "--remove", "-r",
        action="store_true",
        help="Remove containers (docker-compose down instead of stop)"
    )
    parser.add_argument(
        "--remove-storage", "-s",
        action="store_true",
        help="Remove containers and storage volumes (docker-compose down -v)"
    )
    parser.add_argument(
        "--clean-data", "-d",
        action="store_true", 
        help="Remove all data volumes (WARNING: This deletes all workflows and data)"
    )
    parser.add_argument(
        "--clean-images", "-i",
        action="store_true",
        help="Remove Docker images to free up space"
    )
    parser.add_argument(
        "--full-cleanup", "-f",
        action="store_true",
        help="Full cleanup: remove containers, volumes, and images"
    )
    
    args = parser.parse_args()
    
    print("🛑 n8n Documentation Framework Shutdown")
    print("="*50)
    
    # Check Docker
    if not check_docker():
        print("❌ Docker is not available")
        sys.exit(1)
    
    # Full cleanup mode
    if args.full_cleanup:
        args.remove = True
        args.clean_data = True
        args.clean_images = True
        print("🧹 Full cleanup mode enabled")
    
    # Warn about data destruction
    if args.clean_data or args.full_cleanup or args.remove_storage:
        print("⚠️  WARNING: This will delete all workflow data and Redis cache!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Cancelled")
            sys.exit(0)
    
    # Stop host agent server first
    stop_host_agent_server()
    
    # Stop containers
    if not stop_containers(remove=args.remove, remove_storage=args.remove_storage):
        print("❌ Failed to stop containers")
        sys.exit(1)
    
    # Clean up data volumes
    if args.clean_data or args.full_cleanup:
        cleanup_data()
    
    # Clean up images
    if args.clean_images or args.full_cleanup:
        cleanup_images()
    
    # Show final status
    show_status()
    
    print("\n✅ n8n Documentation Framework stopped successfully!")
    
    if not (args.clean_data or args.full_cleanup or args.remove_storage):
        print("💡 Your workflow data has been preserved")
        print("💡 Use --remove-storage to remove containers and storage volumes")
        print("💡 Use --clean-data to remove all data, --clean-images to remove images")
    
    print("💡 Run 'python3 start_n8n.py' to start the services again")

if __name__ == "__main__":
    main()