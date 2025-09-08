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
            "quick_analysis": "Fast automated analysis",
            "comprehensive": "Full analysis with all agents",
            "security_focus": "Security-focused analysis",
            "performance_focus": "Performance optimization analysis",
            "modernization": "Legacy modernization analysis"
        }
    }

@app.post("/n8n/trigger")
async def n8n_trigger_workflow(trigger: N8nWorkflowTrigger, background_tasks: BackgroundTasks):
    """
    Main n8n trigger endpoint - starts analysis workflows
    Designed for n8n HTTP Request node
    """
    try:
        # Import session manager (path adjusted for Docker)
        import sys
        sys.path.append(str(PROJECT_ROOT))
        from framework.scripts.session_manager import SessionManager
        from n8n.services.n8n_workflow_executor import N8nWorkflowExecutor
        
        session_manager = SessionManager(PROJECT_ROOT)
        executor = N8nWorkflowExecutor(PROJECT_ROOT)
        
        # Create session
        session_id = session_manager.start_new_session(
            project_name=trigger.project_name,
            mode="N8N_AUTOMATED"
        )
        
        # Store n8n callback URL
        if trigger.callback_url:
            session_manager.add_user_selection("n8n_callback", trigger.callback_url)
        
        # Start workflow execution in background
        background_tasks.add_task(
            executor.execute_n8n_workflow,
            workflow_type=trigger.workflow_type,
            session_id=session_id,
            options=trigger.options,
            callback_url=trigger.callback_url
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "workflow_type": trigger.workflow_type,
            "status": "started",
            "message": f"Workflow {trigger.workflow_type} started successfully",
            "monitor_url": f"http://{API_HOST}:{API_PORT}/n8n/status/{session_id}"
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
        from framework.scripts.session_manager import SessionManager
        
        session_manager = SessionManager(PROJECT_ROOT)
        session = session_manager.load_existing_session()
        
        if not session or session.get("session_id") != session_id:
            return {
                "success": False,
                "error": "Session not found",
                "session_id": session_id
            }
        
        status = session_manager.get_session_status()
        
        # Calculate overall progress
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
    List agents in n8n-friendly format
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
        
        return {
            "success": True,
            "agents": agents,
            "groups": {
                "discovery": ["mcp-orchestrator", "repomix-analyzer", "architect-agent"],
                "analysis": ["analyst-agent"],
                "documentation": ["diagram-agent", "doc-writer-agent"]
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/n8n/workflows/templates")
async def n8n_get_workflow_templates():
    """
    Get pre-configured workflow templates for n8n
    """
    return {
        "success": True,
        "templates": [
            {
                "id": "quick_analysis",
                "name": "Quick Analysis",
                "description": "Fast automated analysis (1-2 hours)",
                "agents": ["mcp-orchestrator", "repomix-analyzer", "architect-agent", "analyst-agent", "diagram-agent"],
                "parallel_groups": []
            },
            {
                "id": "comprehensive",
                "name": "Comprehensive Analysis",
                "description": "Full analysis with all agents",
                "agents": ["mcp-orchestrator", "repomix-analyzer", "architect-agent", "developer-agent", "analyst-agent", "diagram-agent", "doc-writer-agent"],
                "parallel_groups": []
            },
            {
                "id": "security_focus",
                "name": "Security Analysis",
                "description": "Security-focused analysis",
                "agents": ["mcp-orchestrator", "repomix-analyzer", "analyst-agent", "doc-writer-agent"],
                "parallel_groups": []
            }
        ]
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
        "project_root": str(PROJECT_ROOT)
    }

if __name__ == "__main__":
    import uvicorn
    print(f"Starting n8n API server on {API_HOST}:{API_PORT}")
    print(f"Project root: {PROJECT_ROOT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT, reload=True)