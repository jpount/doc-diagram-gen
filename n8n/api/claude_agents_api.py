#!/usr/bin/env python3
"""
API endpoints for n8n to trigger Claude agents using SDK approach
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uuid
from datetime import datetime
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from n8n.services.n8n_claude_sdk_executor import ClaudeSDKAgentExecutor

app = FastAPI(title="Claude Agents API for n8n")

# Global executor instance
executor = ClaudeSDKAgentExecutor(project_root=Path.cwd().parent)

# Track sessions and tasks
sessions = {}
tasks = {}


class TriggerAgentsRequest(BaseModel):
    project_name: str
    codebase_path: str
    agents: str  # Comma-separated list
    use_correct_naming: bool = True


class StartAgentRequest(BaseModel):
    agent_name: str
    project_name: str
    codebase_path: str
    timeout: int = 180
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@app.post("/n8n/trigger-claude-agents")
async def trigger_claude_agents(request: TriggerAgentsRequest):
    """
    Trigger Claude agents with correct naming
    This is the main endpoint for n8n workflows
    """
    # Generate session ID
    session_id = f"n8n-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    # Parse agents list
    agent_list = [a.strip() for a in request.agents.split(",")]
    
    # Create session
    sessions[session_id] = {
        "session_id": session_id,
        "project_name": request.project_name,
        "codebase_path": request.codebase_path,
        "agents": agent_list,
        "status": "running",
        "started_at": datetime.now().isoformat(),
        "completed_agents": [],
        "failed_agents": [],
        "current_agent": None
    }
    
    # Start first agent asynchronously
    if agent_list:
        first_agent = agent_list[0]
        task_id = executor.start_agent_async(
            first_agent,
            session_id,
            context={"project": request.project_name}
        )
        
        sessions[session_id]["current_agent"] = first_agent
        sessions[session_id]["task_id"] = task_id
        tasks[task_id] = session_id
    
    return {
        "session_id": session_id,
        "task_id": task_id if agent_list else None,
        "agents_to_run": agent_list,
        "status": "started"
    }


@app.post("/n8n/start-agent")
async def start_agent(request: StartAgentRequest):
    """
    Start a single agent asynchronously
    """
    session_id = request.session_id or f"n8n-{uuid.uuid4().hex[:8]}"
    
    # Start agent
    task_id = executor.start_agent_async(
        request.agent_name,
        session_id,
        context=request.context
    )
    
    # Track task
    tasks[task_id] = session_id
    
    if session_id not in sessions:
        sessions[session_id] = {
            "session_id": session_id,
            "project_name": request.project_name,
            "agents": [request.agent_name],
            "status": "running",
            "current_agent": request.agent_name
        }
    else:
        sessions[session_id]["current_agent"] = request.agent_name
    
    return {
        "session_id": session_id,
        "task_id": task_id,
        "agent": request.agent_name,
        "status": "started"
    }


@app.get("/n8n/status/{session_id}")
async def get_status(session_id: str):
    """
    Get status of a session
    This is what n8n polls to check progress
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Check if current task is complete
    if "task_id" in session:
        task_status = await executor.get_agent_status(session["task_id"])
        
        if task_status.get("status") == "completed":
            result = task_status.get("result", {})
            if result.get("success"):
                session["completed_agents"].append(session["current_agent"])
            else:
                session["failed_agents"].append(session["current_agent"])
            
            # Start next agent if any
            remaining = [a for a in session["agents"] 
                        if a not in session["completed_agents"] 
                        and a not in session["failed_agents"]]
            
            if remaining:
                next_agent = remaining[0]
                new_task_id = executor.start_agent_async(
                    next_agent,
                    session_id,
                    context={"previous_results": result}
                )
                session["current_agent"] = next_agent
                session["task_id"] = new_task_id
                tasks[new_task_id] = session_id
            else:
                session["status"] = "completed"
    
    # Calculate progress
    total_agents = len(session.get("agents", []))
    completed = len(session.get("completed_agents", []))
    progress = (completed / total_agents * 100) if total_agents > 0 else 0
    
    is_complete = session["status"] == "completed"
    
    return {
        "session_id": session_id,
        "is_complete": is_complete,
        "status": session["status"],
        "progress_percentage": progress,
        "current_agent": session.get("current_agent"),
        "agents": {
            "total": total_agents,
            "completed": session.get("completed_agents", []),
            "failed": session.get("failed_agents", []),
            "remaining": [a for a in session.get("agents", []) 
                         if a not in session.get("completed_agents", []) 
                         and a not in session.get("failed_agents", [])]
        }
    }


@app.get("/n8n/session-summary/{session_id}")
async def get_session_summary(session_id: str):
    """
    Get complete summary of a session
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Get output files
    output_files = list(executor._get_output_files())
    
    return {
        "session_id": session_id,
        "status": session["status"],
        "agents_executed": session.get("completed_agents", []),
        "agents_failed": session.get("failed_agents", []),
        "files_created": output_files,
        "total_duration": 0,  # Would need to track this
        "summary": {
            "success": len(session.get("failed_agents", [])) == 0,
            "message": "Analysis completed with Claude SDK approach",
            "output_locations": {
                "documentation": "/app/output/docs/",
                "diagrams": "/app/output/diagrams/",
                "context": "/app/output/context/"
            }
        }
    }


@app.get("/n8n/agents/available")
async def get_available_agents():
    """
    List all available agents with correct naming
    """
    return {
        "agents": executor.list_available_agents(),
        "note": "All agents use 'agent-' prefix for Claude Code compatibility"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Claude Agents API",
        "sdk_executor": "active"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)