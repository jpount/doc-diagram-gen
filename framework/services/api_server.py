#!/usr/bin/env python3
"""
API Server for n8n Integration
Provides REST endpoints for workflow automation while maintaining manual operation capability
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pathlib import Path
import json
import asyncio
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Documentation Framework API",
    description="API for automated codebase analysis and documentation generation",
    version="1.0.0"
)

# Enable CORS for n8n
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for your n8n instance
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import local modules (these will be created next)
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from framework.services.agent_executor import AgentExecutor
from framework.orchestration.workflow_manager import WorkflowManager
from framework.scripts.session_manager import SessionManager

# Initialize services
executor = AgentExecutor()
workflow_manager = WorkflowManager()
session_manager = SessionManager()

# --- Data Models ---

class ExecutionMode(str, Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"
    HYBRID = "hybrid"

class WorkflowMode(str, Enum):
    QUICK = "quick"
    GUIDED = "guided"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"

class WorkflowStartRequest(BaseModel):
    project_name: str = Field(..., description="Name of the project to analyze")
    codebase_path: str = Field(..., description="Path to the codebase")
    workflow_mode: WorkflowMode = Field(WorkflowMode.GUIDED, description="Workflow execution mode")
    execution_mode: ExecutionMode = Field(ExecutionMode.AUTOMATED, description="Execution mode")
    custom_agents: Optional[List[str]] = Field(None, description="Custom agent list for CUSTOM mode")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for status updates")
    
class AgentExecuteRequest(BaseModel):
    agent_name: str = Field(..., description="Name of the agent to execute")
    session_id: str = Field(..., description="Session ID for the analysis")
    context_data: Optional[Dict] = Field(None, description="Additional context for the agent")
    async_execution: bool = Field(True, description="Execute asynchronously")
    
class WorkflowStatusResponse(BaseModel):
    session_id: str
    status: str
    phase: str
    progress: Dict[str, Any]
    completed_agents: List[str]
    pending_agents: List[str]
    failed_agents: List[str]
    last_updated: str

# --- Endpoints ---

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Documentation Framework API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "workflow": "/api/workflow",
            "agents": "/api/agent",
            "context": "/api/context",
            "monitoring": "/api/monitor"
        }
    }

@app.post("/api/workflow/start")
async def start_workflow(request: WorkflowStartRequest, background_tasks: BackgroundTasks):
    """
    Start a new analysis workflow
    
    This endpoint initializes a new analysis session and optionally starts execution.
    Perfect for n8n webhook trigger.
    """
    try:
        # Create new session
        session_id = session_manager.start_new_session(
            project_name=request.project_name,
            mode=request.execution_mode.value.upper()
        )
        
        # Configure workflow based on mode
        if request.workflow_mode == WorkflowMode.CUSTOM:
            agents = request.custom_agents or []
        else:
            agents = workflow_manager.get_workflow_agents(request.workflow_mode.value)
        
        # Store webhook URL if provided
        if request.webhook_url:
            session_manager.add_user_selection("webhook_url", request.webhook_url)
        
        # Start execution if automated
        if request.execution_mode in [ExecutionMode.AUTOMATED, ExecutionMode.HYBRID]:
            background_tasks.add_task(
                workflow_manager.execute_workflow,
                session_id=session_id,
                agents=agents,
                mode=request.execution_mode.value
            )
        
        return {
            "session_id": session_id,
            "status": "started",
            "mode": request.workflow_mode.value,
            "agents": agents,
            "message": "Workflow initialized successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to start workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/execute/{agent_name}")
async def execute_agent(agent_name: str, request: AgentExecuteRequest, background_tasks: BackgroundTasks):
    """
    Execute a specific agent
    
    This allows n8n to execute individual agents with full control over sequencing.
    """
    try:
        # Validate session
        session = session_manager.load_existing_session()
        if not session or session.get("session_id") != request.session_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update agent status to running
        session_manager.update_agent_status(agent_name, "running")
        
        if request.async_execution:
            # Execute asynchronously
            background_tasks.add_task(
                executor.execute_agent,
                agent_name=agent_name,
                session_id=request.session_id,
                context=request.context_data
            )
            
            return {
                "status": "started",
                "agent": agent_name,
                "session_id": request.session_id,
                "execution_mode": "async",
                "message": f"Agent {agent_name} execution started"
            }
        else:
            # Execute synchronously (blocks until complete)
            result = await executor.execute_agent_sync(
                agent_name=agent_name,
                session_id=request.session_id,
                context=request.context_data
            )
            
            return {
                "status": "completed",
                "agent": agent_name,
                "session_id": request.session_id,
                "execution_mode": "sync",
                "result": result
            }
            
    except Exception as e:
        logger.error(f"Failed to execute agent {agent_name}: {e}")
        session_manager.update_agent_status(agent_name, "failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflow/status/{session_id}")
async def get_workflow_status(session_id: str) -> WorkflowStatusResponse:
    """
    Get current workflow status
    
    n8n can poll this endpoint to check progress and make decisions.
    """
    try:
        session = session_manager.load_existing_session()
        if not session or session.get("session_id") != session_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        status = session_manager.get_session_status()
        
        return WorkflowStatusResponse(
            session_id=session_id,
            status="active" if status["running_agents"] else "idle",
            phase=status["phase"],
            progress=session["progress"],
            completed_agents=status["completed_agents"],
            pending_agents=status["pending_agents"],
            failed_agents=status["failed_agents"],
            last_updated=status["last_updated"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get status for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/context/{agent_name}")
async def get_agent_context(agent_name: str):
    """
    Get context/output from a specific agent
    
    n8n can use this to retrieve agent results for decision making.
    """
    try:
        context_file = Path(f"output/context/{agent_name}-summary.json")
        
        if not context_file.exists():
            raise HTTPException(status_code=404, detail=f"No context found for agent {agent_name}")
        
        with open(context_file) as f:
            context = json.load(f)
        
        return context
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Context not found for agent {agent_name}")
    except Exception as e:
        logger.error(f"Failed to get context for agent {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/workflow/templates")
async def get_workflow_templates():
    """
    Get available workflow templates
    
    n8n can use this to dynamically populate workflow options.
    """
    try:
        templates = workflow_manager.get_workflow_templates()
        
        return {
            "templates": templates,
            "modes": [mode.value for mode in WorkflowMode],
            "execution_modes": [mode.value for mode in ExecutionMode]
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflow/checkpoint/{session_id}")
async def handle_checkpoint(session_id: str, decision: Dict[str, Any]):
    """
    Handle workflow checkpoints (for GUIDED mode)
    
    n8n can use this to provide user decisions at checkpoints.
    """
    try:
        session = session_manager.load_existing_session()
        if not session or session.get("session_id") != session_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Process checkpoint decision
        checkpoint_name = decision.get("checkpoint")
        user_input = decision.get("input")
        
        session_manager.update_checkpoint(checkpoint_name, "completed")
        session_manager.add_user_selection(checkpoint_name, user_input)
        
        # Resume workflow if waiting
        workflow_manager.resume_from_checkpoint(session_id, checkpoint_name, user_input)
        
        return {
            "status": "checkpoint_processed",
            "checkpoint": checkpoint_name,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Failed to handle checkpoint for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents")
async def list_agents():
    """
    List all available agents with their metadata
    
    n8n can use this to dynamically build agent execution nodes.
    """
    try:
        agents_dir = Path(".claude/agents")
        agents = []
        
        for agent_file in agents_dir.glob("*.md"):
            agent_name = agent_file.stem
            
            # Parse agent metadata from file
            with open(agent_file) as f:
                content = f.read()
                lines = content.split('\n')
                
                # Extract metadata from frontmatter
                description = ""
                tools = []
                for line in lines:
                    if line.startswith("description:"):
                        description = line.replace("description:", "").strip()
                    elif line.startswith("tools:"):
                        tools = [t.strip() for t in line.replace("tools:", "").split(",")]
                
                agents.append({
                    "name": agent_name,
                    "description": description,
                    "tools": tools,
                    "file": str(agent_file)
                })
        
        return {"agents": agents, "count": len(agents)}
        
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workflow/parallel")
async def create_parallel_execution(agents: List[str], session_id: str):
    """
    Create a parallel execution group
    
    n8n can use this to execute multiple agents in parallel.
    """
    try:
        # Create parallel execution tasks
        tasks = workflow_manager.create_parallel_group(agents, session_id)
        
        return {
            "status": "parallel_group_created",
            "agents": agents,
            "session_id": session_id,
            "task_ids": tasks
        }
        
    except Exception as e:
        logger.error(f"Failed to create parallel execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/monitor/{session_id}")
async def websocket_monitor(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time monitoring
    
    n8n or dashboards can connect to get live updates.
    """
    await websocket.accept()
    
    try:
        while True:
            # Get current status
            status = session_manager.get_session_status()
            
            if status.get("session_id") == session_id:
                await websocket.send_json(status)
            
            # Wait before next update
            await asyncio.sleep(2)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.post("/api/webhook/n8n")
async def n8n_webhook(request: Request):
    """
    Generic webhook endpoint for n8n
    
    Handles various n8n events and triggers.
    """
    try:
        body = await request.json()
        
        # Process n8n webhook based on event type
        event_type = body.get("event")
        
        if event_type == "workflow_start":
            # Start a new workflow
            return await start_workflow(WorkflowStartRequest(**body.get("data", {})), BackgroundTasks())
        
        elif event_type == "agent_execute":
            # Execute specific agent
            agent_name = body.get("agent")
            return await execute_agent(agent_name, AgentExecuteRequest(**body.get("data", {})), BackgroundTasks())
        
        elif event_type == "checkpoint_decision":
            # Handle checkpoint
            session_id = body.get("session_id")
            return await handle_checkpoint(session_id, body.get("decision", {}))
        
        else:
            return {"status": "unknown_event", "event": event_type}
            
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)