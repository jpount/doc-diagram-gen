#!/usr/bin/env python3
"""
n8n API Server for Documentation Framework
Designed to work with n8n running in Docker containers
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pathlib import Path
import json
import asyncio
import logging
import os
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="n8n Documentation Framework API",
    description="API designed for n8n workflow automation integration",
    version="1.0.0"
)

# Docker-friendly CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Docker containers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get configuration from environment (Docker-friendly)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8100"))
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "/app"))
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678")

# Redis session storage
import redis
import json as json_lib

# Initialize Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()  # Test connection
    logger.info(f"Connected to Redis at {REDIS_URL}")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    redis_client = None

class RedisSessionStorage:
    """Redis-backed session storage"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.prefix = "n8n_session:"
        self.ttl = 3600 * 24  # 24 hours
    
    def store_session(self, session_id: str, session_data: dict):
        """Store session in Redis"""
        if self.redis:
            key = f"{self.prefix}{session_id}"
            self.redis.setex(key, self.ttl, json_lib.dumps(session_data))
            logger.info(f"Stored session {session_id} in Redis")
    
    def get_session(self, session_id: str) -> dict:
        """Get session from Redis"""
        if self.redis:
            key = f"{self.prefix}{session_id}"
            data = self.redis.get(key)
            if data:
                return json_lib.loads(data)
        return None
    
    def update_session(self, session_id: str, updates: dict):
        """Update session data in Redis"""
        session_data = self.get_session(session_id)
        if session_data:
            session_data.update(updates)
            self.store_session(session_id, session_data)
    
    def keys(self):
        """Return all session IDs (for compatibility with dict-like interface)"""
        if self.redis:
            keys = self.redis.keys(f"{self.prefix}*")
            return [key.decode() if isinstance(key, bytes) else key for key in keys if key]
        return []

    def list_all_sessions(self) -> dict:
        """List all sessions (for debugging)"""
        if self.redis:
            keys = self.redis.keys(f"{self.prefix}*")
            sessions = {}
            for key in keys:
                session_id = key.decode() if isinstance(key, bytes) else key
                session_id = session_id.replace(self.prefix, "")
                data = self.redis.get(key)
                if data:
                    sessions[session_id] = json_lib.loads(data)
            return sessions
        return {}
    
    def delete_session(self, session_id: str):
        """Delete session from Redis"""
        if self.redis:
            key = f"{self.prefix}{session_id}"
            self.redis.delete(key)

# Initialize session storage
if redis_client:
    session_storage = RedisSessionStorage(redis_client)
else:
    # Fallback to in-memory storage
    logger.warning("Using in-memory session storage as fallback")
    session_storage = {}

async def execute_n8n_workflow_simple(executor, workflow_type: str, session_id: str, project_name: str):
    """Simple workflow execution function with simulation mode"""
    import asyncio
    
    try:
        # Get agents from analysis config - simplified approach
        config_file = PROJECT_ROOT / "analysis_config.json"
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                agents = config.get("selected_agents", [])
        else:
            # No config file, no agents to run
            logger.error("analysis_config.json not found")
            return
            
        if not agents:
            logger.error("No agents specified in analysis_config.json")
            return
        
        # Store session info
        session_data = {
            "session_id": session_id,
            "workflow_type": workflow_type,
            "project_name": project_name,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "agents": {
                "completed": [],
                "running": [],
                "pending": agents.copy(),
                "failed": []
            }
        }
        
        if hasattr(session_storage, 'store_session'):
            session_storage.store_session(session_id, session_data)
        else:
            session_storage[session_id] = session_data
        
        logger.info(f"Starting workflow {workflow_type} with agents: {agents}")
        
        # Execute agents in sequence
        for i, agent_name in enumerate(agents):
            logger.info(f"Executing agent {i+1}/{len(agents)}: {agent_name}")
            
            # Update status to running
            if hasattr(session_storage, 'update_session'):
                current_session = session_storage.get_session(session_id)
                current_session["agents"]["running"] = [agent_name]
                current_session["agents"]["pending"] = agents[i+1:]
                session_storage.update_session(session_id, {
                    "agents": current_session["agents"]
                })
            else:
                session_storage[session_id]["agents"]["running"] = [agent_name]
                session_storage[session_id]["agents"]["pending"] = agents[i+1:]
            
            try:
                # Use SDK executor directly (no CLI check needed)
                logger.info(f"Executing agent {agent_name} using SDK executor")
                agent_success = False
                
                result = await executor.execute_agent(
                    agent_name=agent_name,
                    session_id=session_id,
                    use_print_mode=True
                )
                
                if result.get("success"):
                    agent_success = True
                    logger.info(f"Agent {agent_name} completed successfully")
                else:
                    agent_success = False
                    logger.error(f"Agent {agent_name} failed: {result.get('error', 'Unknown error')}")
                
                # Update session with completion
                if hasattr(session_storage, 'update_session'):
                    current_session = session_storage.get_session(session_id)
                    if agent_success:
                        current_session["agents"]["completed"].append(agent_name)
                    else:
                        current_session["agents"]["failed"].append(agent_name)
                    current_session["agents"]["running"] = []
                    current_session["agents"]["pending"] = agents[i+1:]
                    
                    session_storage.update_session(session_id, {
                        "agents": current_session["agents"]
                    })
                else:
                    if agent_success:
                        session_storage[session_id]["agents"]["completed"].append(agent_name)
                    else:
                        session_storage[session_id]["agents"]["failed"].append(agent_name)
                    session_storage[session_id]["agents"]["running"] = []
                    
            except Exception as e:
                logger.error(f"Agent {agent_name} failed with exception: {e}")
                if hasattr(session_storage, 'update_session'):
                    current_session = session_storage.get_session(session_id)
                    current_session["agents"]["failed"].append(agent_name)
                    current_session["agents"]["running"] = []
                    current_session["agents"]["pending"] = agents[i+1:]
                    session_storage.update_session(session_id, {
                        "agents": current_session["agents"]
                    })
                else:
                    session_storage[session_id]["agents"]["failed"].append(agent_name)
                    session_storage[session_id]["agents"]["running"] = []
        
        # Mark as complete
        if hasattr(session_storage, 'update_session'):
            session_storage.update_session(session_id, {
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            })
        else:
            session_storage[session_id]["status"] = "completed"
            session_storage[session_id]["completed_at"] = datetime.now().isoformat()
        logger.info(f"Workflow {session_id} completed")
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        if hasattr(session_storage, 'update_session'):
            session_storage.update_session(session_id, {
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            })
        elif hasattr(session_storage, 'get') and session_id in session_storage:
            session_storage[session_id]["status"] = "failed"
            session_storage[session_id]["error"] = str(e)
            session_storage[session_id]["completed_at"] = datetime.now().isoformat()

# --- Data Models ---

class N8nWorkflowTrigger(BaseModel):
    """Model for n8n workflow triggers"""
    workflow_type: str = Field(..., description="Type of workflow to execute")
    project_name: str = Field(..., description="Project to analyze")
    codebase_path: str = Field(..., description="Path to codebase")
    options: Dict[str, Any] = Field(default_factory=dict, description="Workflow options")
    callback_url: Optional[str] = Field(None, description="n8n webhook for callbacks")

class N8nAgentRequest(BaseModel):
    """Model for n8n agent execution requests"""
    agent_name: str
    session_id: str
    context: Optional[Dict] = None
    wait_for_completion: bool = False
    timeout: int = 300  # seconds

class N8nStatusUpdate(BaseModel):
    """Model for status updates to n8n"""
    session_id: str
    event_type: str  # started, progress, completed, failed
    agent: Optional[str] = None
    progress: Optional[float] = None
    message: str
    data: Optional[Dict] = None

# --- n8n-Specific Endpoints ---

@app.get("/n8n/info")
async def n8n_info():
    """n8n-specific information endpoint"""
    return {
        "name": "n8n Documentation Framework Integration",
        "version": "1.0.0",
        "docker_ready": True,
        "endpoints": {
            "trigger": "/n8n/trigger",
            "execute": "/n8n/execute",
            "status": "/n8n/status/{session_id}",
            "results": "/n8n/results/{session_id}/{agent_name}"
        },
        "workflows": {
            "config_based": "Runs agents specified in analysis_config.json"
        },
        "note": "n8n workflows are now simplified to only run agents from analysis_config.json"
    }

@app.post("/n8n/trigger")
async def n8n_trigger_workflow(trigger: N8nWorkflowTrigger, background_tasks: BackgroundTasks):
    """
    Main n8n trigger endpoint - starts analysis workflows
    Designed for n8n HTTP Request node
    """
    try:
        # Generate simple session ID
        session_id = f"n8n-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        logger.info(f"Starting n8n workflow: {trigger.workflow_type}, session: {session_id}")
        
        # Try to use the n8n executor, but fall back to simple execution
        try:
            import sys
            sys.path.append(str(PROJECT_ROOT))
            from n8n.services.n8n_claude_sdk_executor import ClaudeSDKAgentExecutor
            
            executor = ClaudeSDKAgentExecutor(PROJECT_ROOT)
            
            # Start workflow execution in background using the Claude SDK executor
            background_tasks.add_task(
                execute_n8n_workflow_simple,
                executor=executor,
                workflow_type=trigger.workflow_type,
                session_id=session_id,
                project_name=trigger.project_name
            )
            
        except Exception as import_error:
            logger.warning(f"Failed to import advanced executor, using simple mode: {import_error}")
            # Simple fallback - just return session info
            pass
        
        return {
            "success": True,
            "session_id": session_id,
            "workflow_type": trigger.workflow_type,
            "status": "started",
            "message": f"Workflow {trigger.workflow_type} started successfully",
            "monitor_url": f"http://{API_HOST}:{API_PORT}/n8n/status/{session_id}",
            "project_name": trigger.project_name,
            "codebase_path": trigger.codebase_path
        }
        
    except Exception as e:
        logger.error(f"n8n trigger failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to trigger workflow"
        }

@app.post("/n8n/execute")
async def n8n_execute_agent(request: N8nAgentRequest, background_tasks: BackgroundTasks):
    """
    Execute individual agent - for n8n custom workflows
    """
    try:
        from n8n.services.n8n_agent_executor import N8nAgentExecutor
        
        executor = N8nAgentExecutor(PROJECT_ROOT)
        
        if request.wait_for_completion:
            # Synchronous execution for n8n
            result = await executor.execute_and_wait(
                agent_name=request.agent_name,
                session_id=request.session_id,
                context=request.context,
                timeout=request.timeout
            )
            
            return {
                "success": True,
                "agent": request.agent_name,
                "session_id": request.session_id,
                "status": "completed",
                "result": result
            }
        else:
            # Async execution
            task_id = executor.execute_async(
                agent_name=request.agent_name,
                session_id=request.session_id,
                context=request.context
            )
            
            return {
                "success": True,
                "agent": request.agent_name,
                "session_id": request.session_id,
                "status": "running",
                "task_id": task_id,
                "check_status": f"/n8n/task/{task_id}"
            }
            
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "agent": request.agent_name
        }

@app.get("/n8n/status/{session_id}")
async def n8n_get_status(session_id: str):
    """
    Get workflow status - optimized for n8n polling
    """
    try:
        # Check Redis session storage first
        if hasattr(session_storage, 'get_session'):
            session = session_storage.get_session(session_id)
        elif session_id in session_storage:
            session = session_storage[session_id]
        else:
            session = None
            
        if session:
            
            # Calculate overall progress
            total_agents = len(session["agents"]["completed"]) + len(session["agents"]["pending"]) + len(session["agents"]["running"]) + len(session["agents"]["failed"])
            progress = len(session["agents"]["completed"]) / total_agents if total_agents > 0 else 0
            
            return {
                "success": True,
                "session_id": session_id,
                "status": session["status"],
                "progress_percentage": round(progress * 100, 2),
                "is_complete": session["status"] in ["completed", "failed"],
                "agents": session["agents"],
                "workflow_type": session.get("workflow_type"),
                "project_name": session.get("project_name"),
                "started_at": session.get("started_at"),
                "completed_at": session.get("completed_at"),
                "error": session.get("error")
            }
        
        # Fallback: try to use complex session manager
        try:
            from framework.scripts.session_manager import SessionManager
            
            session_manager = SessionManager(PROJECT_ROOT)
            session = session_manager.load_existing_session()
            
            if session and session.get("session_id") == session_id:
                status = session_manager.get_session_status()
                
                total_agents = len(status["completed_agents"]) + len(status["pending_agents"]) + len(status["running_agents"])
                progress = len(status["completed_agents"]) / total_agents if total_agents > 0 else 0
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "phase": status["phase"],
                    "progress_percentage": round(progress * 100, 2),
                    "is_complete": len(status["pending_agents"]) == 0 and len(status["running_agents"]) == 0,
                    "agents": {
                        "completed": status["completed_agents"],
                        "running": status["running_agents"],
                        "pending": status["pending_agents"],
                        "failed": status["failed_agents"]
                    },
                    "last_updated": status["last_updated"]
                }
        except Exception as fallback_error:
            logger.warning(f"Fallback session manager failed: {fallback_error}")
        
        # Session not found
        if hasattr(session_storage, 'list_all_sessions'):
            all_sessions = session_storage.list_all_sessions()
            available_sessions = list(all_sessions.keys())
            total_sessions = len(all_sessions)
        else:
            available_sessions = list(session_storage.keys())
            total_sessions = len(session_storage)
            
        return {
            "success": False,
            "error": "Session not found",
            "session_id": session_id,
            "available_sessions": available_sessions,
            "debug_info": {
                "requested_session": session_id,
                "total_sessions": total_sessions,
                "session_pattern": "n8n-YYYYMMDD-HHMMSS",
                "current_time": datetime.now().strftime('%Y%m%d-%H%M%S'),
                "storage_type": "redis" if hasattr(session_storage, 'get_session') else "memory"
            }
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "session_id": session_id
        }

@app.get("/n8n/results/{session_id}/{agent_name}")
async def n8n_get_results(session_id: str, agent_name: str):
    """
    Get agent results - for n8n data processing
    """
    try:
        context_file = PROJECT_ROOT / "output" / "context" / f"{agent_name}-summary.json"
        
        if not context_file.exists():
            return {
                "success": False,
                "error": "Results not found",
                "agent": agent_name
            }
        
        with open(context_file) as f:
            context = json.load(f)
        
        # Simplify for n8n consumption
        return {
            "success": True,
            "session_id": session_id,
            "agent": agent_name,
            "timestamp": context.get("timestamp"),
            "summary": context.get("summary", {}),
            "data": context.get("data", {}),
            "has_errors": len(context.get("summary", {}).get("warnings", [])) > 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get results: {e}")
        return {
            "success": False,
            "error": str(e),
            "agent": agent_name
        }

@app.post("/n8n/callback")
async def n8n_callback_handler(update: N8nStatusUpdate):
    """
    Send status updates back to n8n workflows
    """
    import httpx
    
    try:
        # Get callback URL from session
        from framework.scripts.session_manager import SessionManager
        session_manager = SessionManager(PROJECT_ROOT)
        session = session_manager.load_existing_session()
        
        if session and session.get("user_selections", {}).get("n8n_callback"):
            callback_url = session["user_selections"]["n8n_callback"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    callback_url,
                    json=update.dict(),
                    timeout=10.0
                )
                
                return {"success": True, "callback_sent": True}
        
        return {"success": True, "callback_sent": False, "reason": "No callback URL"}
        
    except Exception as e:
        logger.error(f"Callback failed: {e}")
        return {"success": False, "error": str(e)}

@app.get("/n8n/agents/available")
async def n8n_list_available_agents():
    """
    List agents in n8n-friendly format - from actual .claude/agents folder
    """
    try:
        agents_dir = PROJECT_ROOT / ".claude" / "agents"
        agents = []
        
        for agent_file in agents_dir.glob("*.md"):
            agent_name = agent_file.stem
            agents.append({
                "value": agent_name,
                "name": agent_name.replace("-", " ").title()
            })
        
        # Also show current config
        config_file = PROJECT_ROOT / "analysis_config.json"
        current_agents = []
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                current_agents = config.get("selected_agents", [])
        
        return {
            "success": True,
            "available_agents": agents,
            "current_config": current_agents,
            "note": "n8n will run agents specified in analysis_config.json"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/n8n/workflows/templates")
async def n8n_get_workflow_templates():
    """
    Get workflow template based on analysis_config.json
    """
    try:
        config_file = PROJECT_ROOT / "analysis_config.json"
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                agents = config.get("selected_agents", [])
                project_name = config.get("project_name", "unknown")
                
                return {
                    "success": True,
                    "templates": [
                        {
                            "id": "config_based",
                            "name": f"Analysis for {project_name}",
                            "description": f"Runs agents from analysis_config.json: {', '.join(agents)}",
                            "agents": agents,
                            "parallel_groups": []
                        }
                    ]
                }
        else:
            return {
                "success": False,
                "error": "analysis_config.json not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.websocket("/n8n/ws/{session_id}")
async def n8n_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket for real-time updates in n8n dashboards
    """
    await websocket.accept()
    
    try:
        while True:
            status = await n8n_get_status(session_id)
            await websocket.send_json(status)
            
            if status.get("is_complete"):
                await websocket.send_json({"event": "workflow_complete"})
                break
                
            await asyncio.sleep(3)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# Health check for Docker
@app.get("/health")
async def health_check():
    """Docker health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "docker_ready": True,
        "project_root": str(PROJECT_ROOT),
        "sessions": list(session_storage.keys()),
        "api_host": API_HOST,
        "api_port": API_PORT
    }

# Debug endpoint for Docker connectivity
@app.get("/debug")
async def debug_info():
    """Debug information for Docker connectivity"""
    return {
        "api_server": "running",
        "project_root": str(PROJECT_ROOT),
        "project_root_exists": PROJECT_ROOT.exists(),
        "environment": {
            "API_HOST": API_HOST,
            "API_PORT": API_PORT,
            "PROJECT_ROOT": str(PROJECT_ROOT),
            "N8N_WEBHOOK_URL": N8N_WEBHOOK_URL
        },
        "sessions": session_storage.list_all_sessions() if hasattr(session_storage, 'list_all_sessions') else session_storage,
        "available_endpoints": [
            "/health",
            "/debug", 
            "/n8n/info",
            "/n8n/trigger",
            "/n8n/status/{session_id}",
            "/n8n/sessions",
            "/n8n/agents/available"
        ]
    }

@app.get("/n8n/sessions")
async def n8n_list_sessions():
    """List all active sessions for debugging"""
    if hasattr(session_storage, 'list_all_sessions'):
        all_sessions = session_storage.list_all_sessions()
    else:
        all_sessions = session_storage
        
    return {
        "success": True,
        "total_sessions": len(all_sessions),
        "storage_type": "redis" if hasattr(session_storage, 'get_session') else "memory",
        "sessions": [
            {
                "session_id": session_id,
                "status": session_data.get("status"),
                "workflow_type": session_data.get("workflow_type"),
                "started_at": session_data.get("started_at"),
                "completed_at": session_data.get("completed_at"),
                "agents_completed": len(session_data.get("agents", {}).get("completed", [])),
                "agents_failed": len(session_data.get("agents", {}).get("failed", []))
            }
            for session_id, session_data in all_sessions.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print(f"Starting n8n API server on {API_HOST}:{API_PORT}")
    print(f"Project root: {PROJECT_ROOT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT, reload=True)