#!/usr/bin/env python3
"""
Host Agent Server - Runs on host machine to execute Claude agents
This server listens for requests from Docker and executes agents locally
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import sys
from pathlib import Path
import uvicorn

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from n8n.services.n8n_claude_sdk_executor import ClaudeSDKAgentExecutor
from n8n.services.logging_config import host_server_logger as logger, log_execution_start, log_execution_complete, log_exception

app = FastAPI(title="Host Agent Executor", description="Executes Claude agents on host machine")

# Initialize executor
PROJECT_ROOT = Path(__file__).parent.parent  # /Users/jp/work/agent-docs/doc-diagram-gen
executor = ClaudeSDKAgentExecutor(project_root=PROJECT_ROOT)

class AgentExecutionRequest(BaseModel):
    agent_name: str
    session_id: str
    context: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None


class ParallelExecutionRequest(BaseModel):
    agents: List[str]
    session_id: str
    context: Optional[Dict[str, Any]] = None
    max_concurrent: int = 3
    timeout: Optional[int] = None


@app.post("/execute-agent")
async def execute_agent(request: AgentExecutionRequest):
    """
    Execute a Claude agent on the host machine
    This endpoint is called by Docker containers
    """
    logger.info(f"🖥️  HOST: Received request to execute agent: {request.agent_name}")
    logger.info(f"🖥️  HOST: Session ID: {request.session_id}")
    logger.info(f"🖥️  HOST: Timeout: {request.timeout}s")
    logger.info(f"🖥️  HOST: Context keys: {list(request.context.keys()) if request.context else 'None'}")
    logger.info(f"🖥️  HOST: Project root: {PROJECT_ROOT}")
    
    try:
        # Execute agent using SDK approach on host
        logger.info(f"🖥️  HOST: Starting agent execution...")
        result = await executor.execute_agent(
            agent_name=request.agent_name,
            session_id=request.session_id,
            context=request.context,
            timeout=request.timeout,
            use_print_mode=True
        )
        
        logger.info(f"🖥️  HOST: Agent {request.agent_name} execution completed")
        
        if result is None:
            logger.error(f"🖥️  HOST: Execution returned None - this indicates an executor initialization issue")
            return {
                "success": False,
                "agent": request.agent_name,
                "session_id": request.session_id,
                "error": "Executor returned None - possible initialization issue"
            }
        
        logger.info(f"🖥️  HOST: Execution success: {result.get('success')}")
        logger.info(f"🖥️  HOST: Execution time: {result.get('execution_time', 'N/A')}s")
        if not result.get('success'):
            logger.error(f"🖥️  HOST: Execution error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"🖥️  HOST: Failed to execute agent {request.agent_name}: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"🖥️  HOST: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Host Agent Executor"}


@app.post("/execute-parallel")
async def execute_parallel(request: ParallelExecutionRequest):
    """
    Execute multiple Claude agents in parallel on the host machine
    """
    logger.info(f"Received request to execute {len(request.agents)} agents in parallel")
    
    try:
        # Execute agents in parallel with max concurrency
        results = await executor.execute_agents_parallel(
            agent_names=request.agents,
            session_id=request.session_id,
            context=request.context,
            max_concurrent=request.max_concurrent
        )
        
        # Summary
        successful = sum(1 for r in results if r.get("success"))
        logger.info(f"Parallel execution complete: {successful}/{len(results)} succeeded")
        
        return {
            "success": successful > 0,
            "total": len(results),
            "successful": successful,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Failed to execute agents in parallel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/available-agents")
async def get_available_agents():
    """List available agents"""
    return {"agents": executor.list_available_agents()}


if __name__ == "__main__":
    print("=" * 70)
    print("HOST AGENT SERVER")
    print("=" * 70)
    print(f"Starting server on http://localhost:8200")
    print(f"Project root: {PROJECT_ROOT}")
    print("\nThis server executes Claude agents on the host machine")
    print("Docker containers should call this API to trigger agents")
    print("=" * 70)
    
    # Run server on port 8200 (different from Docker's 8100)
    uvicorn.run(app, host="0.0.0.0", port=8200)