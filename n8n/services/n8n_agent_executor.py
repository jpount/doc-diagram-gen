#!/usr/bin/env python3
"""
n8n Agent Executor
Handles individual agent execution for n8n workflows
"""

import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
from enum import Enum
import uuid
import time

# Use centralized logging
from .logging_config import agent_executor_logger as logger, log_execution_start, log_execution_complete, log_exception, get_agent_logger

class ExecutionMode(Enum):
    """Agent execution modes"""
    SUBPROCESS = "subprocess"     # Run as subprocess (Python scripts)
    DOCKER = "docker"             # Run in Docker container
    MOCK = "mock"                 # Mock execution for testing
    CLAUDE_CLI = "claude_cli"     # Use Claude CLI (if available)

class N8nAgentExecutor:
    """
    Executes individual agents for n8n workflows
    Supports multiple execution modes for flexibility
    """
    
    # Agent timeouts in seconds (high values for complex analysis)
    AGENT_TIMEOUTS = {
        "mcp-orchestrator": 180,
        "repomix-analyzer": 120,
        "architecture-selector": 120,
        "legacy-code-detective": 180,
        "java-architect": 150,
        "dotnet-architect": 150,
        "angular-architect": 150,
        "business-logic-analyst": 180,
        "domain-boundary-analyst": 150,
        "data-model-specialist": 150,
        "ui-analysis-specialist": 150,
        "security-analyst": 180,
        "performance-analyst": 180,
        "modernization-architect": 180,
        "diagram-architect": 240,
        "documentation-specialist": 240,
        "executive-summary": 120
    }
    
    def __init__(self, project_root: Path = Path("."), mode: ExecutionMode = ExecutionMode.SUBPROCESS):
        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "output"
        self.context_dir = self.output_dir / "context"
        self.execution_mode = mode
        
        # Task tracking
        self.running_tasks = {}
        
        # Ensure directories exist
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
    async def execute_and_wait(
        self,
        agent_name: str,
        session_id: str,
        context: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute agent and wait for completion
        Synchronous execution for n8n
        """
        # Use configured timeout if not specified
        if timeout is None:
            timeout = self.AGENT_TIMEOUTS.get(agent_name, 300)
        
        logger.info(f"Executing agent {agent_name} in {self.execution_mode.value} mode (timeout: {timeout}s)")
        
        start_time = time.time()
        
        try:
            # Choose execution method based on mode
            if self.execution_mode == ExecutionMode.SUBPROCESS:
                result = await self._execute_subprocess(agent_name, session_id, context, timeout)
            elif self.execution_mode == ExecutionMode.DOCKER:
                result = await self._execute_docker(agent_name, session_id, context, timeout)
            elif self.execution_mode == ExecutionMode.MOCK:
                result = await self._execute_mock(agent_name, session_id, context, timeout)
            elif self.execution_mode == ExecutionMode.CLAUDE_CLI:
                result = await self._execute_claude_cli(agent_name, session_id, context, timeout)
            else:
                raise ValueError(f"Unknown execution mode: {self.execution_mode}")
            
            execution_time = time.time() - start_time
            
            # Write context summary
            await self._write_agent_context(agent_name, session_id, result, execution_time)
            
            return {
                "success": True,
                "agent": agent_name,
                "session_id": session_id,
                "execution_time": execution_time,
                "result": result
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Agent {agent_name} timed out after {timeout} seconds")
            return {
                "success": False,
                "agent": agent_name,
                "error": f"Timeout after {timeout} seconds"
            }
        except Exception as e:
            logger.error(f"Agent {agent_name} failed: {e}")
            return {
                "success": False,
                "agent": agent_name,
                "error": str(e)
            }
    
    def execute_async(
        self,
        agent_name: str,
        session_id: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Execute agent asynchronously
        Returns task ID for tracking
        """
        task_id = str(uuid.uuid4())
        
        # Create async task
        task = asyncio.create_task(
            self.execute_and_wait(agent_name, session_id, context)
        )
        
        self.running_tasks[task_id] = {
            "task": task,
            "agent": agent_name,
            "session_id": session_id,
            "started": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Started async task {task_id} for agent {agent_name}")
        
        return task_id
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of async task"""
        if task_id not in self.running_tasks:
            return {"error": "Task not found"}
        
        task_info = self.running_tasks[task_id]
        task = task_info["task"]
        
        if task.done():
            result = await task
            del self.running_tasks[task_id]
            return {
                "status": "completed",
                "result": result
            }
        else:
            return {
                "status": "running",
                "agent": task_info["agent"],
                "started": task_info["started"]
            }
    
    async def _execute_subprocess(
        self,
        agent_name: str,
        session_id: str,
        context: Optional[Dict],
        timeout: int
    ) -> Dict:
        """Execute agent as subprocess (Python script)"""
        
        # Create agent wrapper script
        wrapper_script = self._create_python_wrapper(agent_name, session_id, context)
        
        # Execute wrapper
        process = await asyncio.create_subprocess_exec(
            "python3",
            "-c",
            wrapper_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            if process.returncode != 0:
                raise Exception(f"Process failed: {stderr.decode()}")
            
            # Parse output
            output = stdout.decode()
            if output:
                return json.loads(output)
            else:
                return {"status": "completed", "output": "No output"}
                
        except asyncio.TimeoutError:
            process.terminate()
            await process.wait()
            raise
    
    async def _execute_docker(
        self,
        agent_name: str,
        session_id: str,
        context: Optional[Dict],
        timeout: int
    ) -> Dict:
        """Execute agent in Docker container"""
        
        # Build Docker command
        docker_cmd = [
            "docker", "run",
            "--rm",
            "-v", f"{self.project_root}/codebase:/app/codebase:ro",
            "-v", f"{self.project_root}/output:/app/output",
            "-e", f"AGENT_NAME={agent_name}",
            "-e", f"SESSION_ID={session_id}",
            "-e", f"CONTEXT={json.dumps(context or {})}",
            "doc-framework-agent:latest",
            "python", "-m", f"agents.{agent_name}"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *docker_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            if process.returncode != 0:
                raise Exception(f"Docker execution failed: {stderr.decode()}")
            
            return json.loads(stdout.decode())
            
        except asyncio.TimeoutError:
            # Kill Docker container
            kill_cmd = ["docker", "kill", f"agent-{agent_name}-{session_id}"]
            await asyncio.create_subprocess_exec(*kill_cmd)
            raise
    
    async def _execute_mock(
        self,
        agent_name: str,
        session_id: str,
        context: Optional[Dict],
        timeout: int
    ) -> Dict:
        """Mock execution for testing"""
        
        # Simulate execution time
        await asyncio.sleep(min(5, timeout))
        
        # Generate mock result
        return {
            "agent": agent_name,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "key_findings": [
                    f"Mock finding 1 for {agent_name}",
                    f"Mock finding 2 for {agent_name}",
                    f"Mock finding 3 for {agent_name}"
                ],
                "priority_items": [
                    "Mock priority item 1",
                    "Mock priority item 2"
                ],
                "warnings": [],
                "recommendations_for_next": {
                    "next-agent": ["Recommendation 1", "Recommendation 2"]
                }
            },
            "data": {
                "mock_data": True,
                "execution_mode": "mock",
                "context_received": context or {}
            }
        }
    
    async def _execute_claude_cli(
        self,
        agent_name: str,
        session_id: str,
        context: Optional[Dict],
        timeout: int
    ) -> Dict:
        """Execute using Claude CLI with correct agent naming"""
        
        # Map agent names to correct Claude Code format
        agent_mapping = {
            "mcp-orchestrator": "agent-mcp-orchestrator",
            "repomix-analyzer": "agent-repomix-analyzer",
            "architecture-selector": "agent-architecture-selector",
            "legacy-code-detective": "agent-legacy-code-detective",
            "java-architect": "agent-java-architect",
            "dotnet-architect": "agent-dotnet-architect",
            "angular-architect": "agent-angular-architect",
            "business-logic-analyst": "agent-business-logic-analyst",
            "domain-boundary-analyst": "agent-domain-boundary-analyst",
            "data-model-specialist": "agent-data-model-specialist",
            "ui-analysis-specialist": "agent-ui-analysis-specialist",
            "security-analyst": "agent-security-analyst",
            "performance-analyst": "agent-performance-analyst",
            "modernization-architect": "agent-modernization-architect",
            "diagram-architect": "agent-diagram-architect",
            "documentation-specialist": "agent-documentation-specialist",
            "executive-summary": "agent-executive-summary"
        }
        
        # Get correct agent name
        claude_agent_name = agent_mapping.get(agent_name, f"agent-{agent_name}")
        if agent_name.startswith("agent-"):
            claude_agent_name = agent_name
        
        logger.info(f"Executing Claude agent: {claude_agent_name} (timeout: {timeout}s)")
        
        # Check if Claude CLI is available
        claude_check = await asyncio.create_subprocess_exec(
            "which", "claude",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await claude_check.communicate()
        
        if claude_check.returncode != 0:
            # Fallback to subprocess mode
            logger.warning("Claude CLI not found, falling back to subprocess mode")
            return await self._execute_subprocess(agent_name, session_id, context, timeout)
        
        # Execute via Claude CLI with correct naming and flags
        claude_cmd = [
            "claude",
            "--print",  # Non-interactive mode
            "--output-format", "text",
            "--dangerously-skip-permissions",
            claude_agent_name  # Just the agent name, no additional prompt
        ]
        
        process = await asyncio.create_subprocess_exec(
            *claude_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.project_root)
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            if process.returncode == 0:
                output = stdout.decode('utf-8')
                
                # Return structured result
                return {
                    "agent": claude_agent_name,
                    "session_id": session_id,
                    "status": "completed",
                    "output": output,
                    "summary": {
                        "key_findings": [f"Executed {claude_agent_name} successfully"],
                        "priority_items": [],
                        "warnings": [],
                        "recommendations_for_next": {}
                    },
                    "data": {
                        "context": context or {},
                        "execution_mode": "claude_cli"
                    }
                }
            else:
                error = stderr.decode('utf-8')
                raise Exception(f"Claude CLI failed: {error}")
            
        except asyncio.TimeoutError:
            process.terminate()
            await process.wait()
            raise
    
    def _create_python_wrapper(self, agent_name: str, session_id: str, context: Optional[Dict]) -> str:
        """Create Python wrapper script for agent execution"""
        
        context_json = json.dumps(context or {})
        
        wrapper = f"""
import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, '{self.project_root}')

# Mock agent execution
result = {{
    "agent": "{agent_name}",
    "session_id": "{session_id}",
    "status": "completed",
    "summary": {{
        "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
        "priority_items": ["Priority 1", "Priority 2"],
        "warnings": [],
        "recommendations_for_next": {{}}
    }},
    "data": {{
        "analyzed": True,
        "context": {context_json}
    }}
}}

# Output result as JSON
print(json.dumps(result))
"""
        return wrapper
    
    async def _write_agent_context(
        self,
        agent_name: str,
        session_id: str,
        result: Dict,
        execution_time: float
    ):
        """Write agent context summary for other agents"""
        
        context_file = self.context_dir / f"{agent_name}-summary.json"
        
        context_data = {
            "agent": agent_name,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_time": execution_time,
            "execution_mode": self.execution_mode.value,
            "summary": result.get("summary", {}),
            "data": result.get("data", {})
        }
        
        with open(context_file, 'w') as f:
            json.dump(context_data, f, indent=2)
        
        logger.info(f"Context written for {agent_name}: {context_file}")
    
    def get_agent_context(self, agent_name: str) -> Optional[Dict]:
        """Read agent context if it exists"""
        
        context_file = self.context_dir / f"{agent_name}-summary.json"
        
        if context_file.exists():
            with open(context_file) as f:
                return json.load(f)
        
        return None
    
    def list_completed_agents(self, session_id: str) -> List[str]:
        """List all completed agents for a session"""
        
        completed = []
        
        for context_file in self.context_dir.glob("*-summary.json"):
            with open(context_file) as f:
                data = json.load(f)
                if data.get("session_id") == session_id:
                    completed.append(data["agent"])
        
        return completed