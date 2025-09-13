#!/usr/bin/env python3
"""
n8n Claude SDK Agent Executor
Executes Claude Code agents using proper naming convention and SDK approach
Based on test_correct_agent_names.py which works correctly
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Any, List
import subprocess
import uuid

# Use centralized logging
from .logging_config import sdk_executor_logger as logger, log_execution_start, log_execution_complete, log_exception

class ClaudeSDKAgentExecutor:
    """
    Executes Claude Code agents using the SDK approach with correct naming
    """
    
    # Current agent names with 'agent-' prefix as used in Claude Code
    AGENT_MAPPING = {
        # Current default agents (primary)
        "solution-architect": "agent-solution-architect",
        "technical-architect": "agent-technical-architect",
        "business-logic-analyst": "agent-business-logic-analyst",
        
        # Additional available agents
        "integration-specialist": "agent-integration-specialist", 
        "security-analyst": "agent-security-analyst",
        "performance-analyst": "agent-performance-analyst",
        "ui-analyst": "agent-ui-analyst",
        
        # Retired/legacy agents (for backward compatibility)
        "java-architect": "agent-java-architect",
        "dotnet-architect": "agent-dotnet-architect", 
        "angular-architect": "agent-angular-architect",
        "delphi-architect": "agent-delphi-architect",
        "php-architect": "agent-php-architect",
        
        # Support agents
        "repomix-analyzer": "agent-repomix-analyzer",
        "legacy-code-detective": "agent-legacy-code-detective"
    }
    
    def _load_agent_timeouts(self) -> dict:
        """Load agent timeouts from external JSON configuration"""
        config_path = self.project_root / "n8n" / "agent_timeouts.json"
        
        # Default timeouts as fallback
        default_timeouts = {
            "agent-solution-architect": 600,
            "agent-technical-architect": 720,
            "agent-business-logic-analyst": 480,
            "agent-integration-specialist": 300,
            "agent-security-analyst": 360,
            "agent-performance-analyst": 300,
            "agent-ui-analyst": 240,
            "agent-java-architect": 300,
            "agent-dotnet-architect": 300,
            "agent-angular-architect": 300,
            "agent-delphi-architect": 300,
            "agent-php-architect": 300,
            "agent-repomix-analyzer": 300,
            "agent-legacy-code-detective": 240
        }
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    loaded_timeouts = config.get('agent_timeouts', {})
                    # Merge with defaults for any missing agents
                    default_timeouts.update(loaded_timeouts)
                    logger.info(f"Loaded agent timeouts from {config_path}")
                    return default_timeouts
            else:
                logger.warning(f"Timeout config not found at {config_path}, using defaults")
                return default_timeouts
        except Exception as e:
            logger.error(f"Failed to load timeout config: {e}, using defaults")
            return default_timeouts
    
    def __init__(self, project_root: Path = Path("."), output_dir: Optional[Path] = None):
        self.project_root = Path(project_root)
        self.output_dir = output_dir or self.project_root / "output"
        self.context_dir = self.output_dir / "context"
        self.reports_dir = self.output_dir / "reports"
        self.docs_dir = self.output_dir / "docs"
        
        # Load agent timeouts from configuration
        self.AGENT_TIMEOUTS = self._load_agent_timeouts()
        
        # Ensure directories exist
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Track running agents
        self.running_agents = {}
        
    def get_claude_agent_name(self, agent_name: str) -> str:
        """
        Convert agent name to proper Claude Code format
        Handles both with and without 'agent-' prefix
        """
        # If already has agent- prefix, return as is
        if agent_name.startswith("agent-"):
            return agent_name
            
        # Map to correct name
        return self.AGENT_MAPPING.get(agent_name, f"agent-{agent_name}")
    
    def get_agent_timeout(self, agent_name: str) -> int:
        """Get recommended timeout for agent"""
        claude_name = self.get_claude_agent_name(agent_name)
        return self.AGENT_TIMEOUTS.get(claude_name, 120)
    
    async def _check_host_available(self) -> bool:
        """Check if host.docker.internal is available"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://host.docker.internal:8200/health", timeout=2)
                return response.status_code == 200
        except:
            return False
    
    async def execute_agent(
        self,
        agent_name: str,
        session_id: str,
        context: Optional[Dict] = None,
        timeout: Optional[int] = None,
        use_print_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a Claude Code agent using SDK approach
        
        Args:
            agent_name: Agent name (with or without 'agent-' prefix)
            session_id: Session ID for tracking
            context: Optional context to pass to agent
            timeout: Timeout in seconds (uses default if not specified)
            use_print_mode: Use --print mode for non-interactive execution
            
        Returns:
            Execution result dictionary
        """
        claude_agent_name = self.get_claude_agent_name(agent_name)
        agent_timeout = timeout or self.get_agent_timeout(agent_name)
        
        logger.info(f"Executing Claude agent: {claude_agent_name}")
        logger.info(f"Timeout: {agent_timeout}s")
        logger.info(f"Session: {session_id}")
        
        start_time = time.time()
        
        # Track files before execution
        before_files = self._get_output_files()
        
        # Build Claude command
        cmd = [
            "claude",
            "--output-format", "text",
            "--dangerously-skip-permissions"
        ]
        
        if use_print_mode:
            cmd.append("--print")
        
        # Add agent name (no additional prompt needed)
        cmd.append(claude_agent_name)
        
        try:
            # Check if we're running in Docker
            import os
            if os.path.exists('/.dockerenv'):
                # We're in Docker - call host to execute agent
                import httpx
                logger.info(f"🐳 DOCKER: Calling host to execute {claude_agent_name}")
                logger.info(f"🐳 DOCKER: Agent timeout: {agent_timeout}s")
                logger.info(f"🐳 DOCKER: Session: {session_id}")
                logger.info(f"🐳 DOCKER: Context keys: {list(context.keys()) if context else 'None'}")
                
                async with httpx.AsyncClient() as client:
                    # Use host.docker.internal on Mac/Windows or 172.17.0.1 on Linux
                    host_url = "http://host.docker.internal:8200/execute-agent"
                    logger.info(f"🐳 DOCKER: Checking host availability...")
                    if not await self._check_host_available():
                        logger.warning(f"🐳 DOCKER: host.docker.internal not available, trying Linux bridge")
                        # Fallback to Linux Docker bridge
                        host_url = "http://172.17.0.1:8200/execute-agent"
                    
                    logger.info(f"🐳 DOCKER: Using host URL: {host_url}")
                    
                    request_payload = {
                        "agent_name": agent_name,
                        "session_id": session_id,
                        "context": context,
                        "timeout": agent_timeout
                    }
                    logger.info(f"🐳 DOCKER: Request payload: {json.dumps(request_payload, indent=2)[:500]}")
                    
                    http_timeout = agent_timeout + 30  # Give extra time for network
                    logger.info(f"🐳 DOCKER: HTTP timeout: {http_timeout}s")
                    
                    try:
                        logger.info(f"🐳 DOCKER: Making POST request to {host_url}")
                        response = await client.post(
                            host_url,
                            json=request_payload,
                            timeout=http_timeout
                        )
                        
                        logger.info(f"🐳 DOCKER: Host response status: {response.status_code}")
                        logger.info(f"🐳 DOCKER: Host response headers: {dict(response.headers)}")
                        
                        if response.status_code == 200:
                            result = response.json()
                            logger.info(f"🐳 DOCKER: Host execution success: {result.get('success', False)}")
                            if not result.get('success', False):
                                logger.error(f"🐳 DOCKER: Host execution failed: {result.get('error', 'Unknown error')}")
                            return result
                        else:
                            error_text = response.text
                            logger.error(f"🐳 DOCKER: Host execution HTTP error: {response.status_code}")
                            logger.error(f"🐳 DOCKER: Host error response: {error_text}")
                            raise Exception(f"Host execution failed: {error_text}")
                            
                    except Exception as e:
                        logger.error(f"🐳 DOCKER: Exception during HTTP request: {type(e).__name__}: {e}")
                        import traceback
                        logger.error(f"🐳 DOCKER: Traceback: {traceback.format_exc()}")
                        return {
                            "success": False,
                            "agent": claude_agent_name,
                            "original_name": agent_name,
                            "session_id": session_id,
                            "error": f"Host call failed: {type(e).__name__}: {str(e)}"
                        }
            
            # Original host execution logic (when not in Docker)
            logger.info(f"🖥️  HOST: Running on host machine, executing agent directly")
            if True:  # Re-enabled for host execution
                # We're on host - execute directly
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.project_root)
                )
                
                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=agent_timeout
                )
                
                elapsed = time.time() - start_time
                
                if process.returncode == 0:
                    output = stdout.decode('utf-8')
                    
                    # Check for new files
                    after_files = self._get_output_files()
                    new_files = after_files - before_files
                    
                    # Parse agent output
                    result = self._parse_agent_output(output, new_files)
                    
                    # Write context summary
                    await self._write_context_summary(
                        claude_agent_name,
                        session_id,
                        result,
                        elapsed
                    )
                    
                    logger.info(f"Agent {claude_agent_name} completed in {elapsed:.1f}s")
                    if new_files:
                        logger.info(f"Created {len(new_files)} files")
                    
                    return {
                        "success": True,
                        "agent": claude_agent_name,
                        "original_name": agent_name,
                        "session_id": session_id,
                        "execution_time": elapsed,
                        "files_created": list(new_files),
                        "output": output[:1000] if output else "",
                        "result": result
                    }
                    
                else:
                    error = stderr.decode('utf-8')
                    logger.error(f"Agent {claude_agent_name} failed: {error}")
                    
                    return {
                        "success": False,
                        "agent": claude_agent_name,
                        "original_name": agent_name,
                        "session_id": session_id,
                        "execution_time": elapsed,
                        "error": error[:500]
                    }
                
        except asyncio.TimeoutError:
            logger.error(f"Agent {claude_agent_name} timed out after {agent_timeout}s")
            try:
                process.terminate()
                await process.wait()
            except:
                pass
                
            return {
                "success": False,
                "agent": claude_agent_name,
                "original_name": agent_name,
                "session_id": session_id,
                "error": f"Timeout after {agent_timeout}s"
            }
            
        except Exception as e:
            logger.error(f"Agent {claude_agent_name} exception: {e}")
            return {
                "success": False,
                "agent": claude_agent_name,
                "original_name": agent_name,
                "session_id": session_id,
                "error": str(e)
            }
    
    async def execute_agents_parallel(
        self,
        agent_names: List[str],
        session_id: str,
        context: Optional[Dict] = None,
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple agents in parallel
        
        Args:
            agent_names: List of agent names to execute
            session_id: Session ID for tracking
            context: Optional context to pass to agents
            max_concurrent: Maximum concurrent agents
            
        Returns:
            List of execution results
        """
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_agent(agent_name):
            async with semaphore:
                return await self.execute_agent(agent_name, session_id, context)
        
        tasks = [run_agent(agent) for agent in agent_names]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def execute_agents_sequential(
        self,
        agent_names: List[str],
        session_id: str,
        context: Optional[Dict] = None,
        pass_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute agents sequentially, optionally passing context between them
        
        Args:
            agent_names: List of agent names to execute
            session_id: Session ID for tracking
            context: Initial context
            pass_context: Whether to pass context between agents
            
        Returns:
            List of execution results
        """
        results = []
        current_context = context or {}
        
        for agent_name in agent_names:
            result = await self.execute_agent(
                agent_name,
                session_id,
                current_context if pass_context else context
            )
            
            results.append(result)
            
            # Update context for next agent if passing context
            if pass_context and result.get("success"):
                if "result" in result and "summary" in result["result"]:
                    current_context[agent_name] = result["result"]["summary"]
        
        return results
    
    def start_agent_async(
        self,
        agent_name: str,
        session_id: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        Start agent execution asynchronously (non-blocking)
        Returns task ID for tracking
        """
        task_id = str(uuid.uuid4())
        
        # Create async task
        task = asyncio.create_task(
            self.execute_agent(agent_name, session_id, context)
        )
        
        self.running_agents[task_id] = {
            "task": task,
            "agent": agent_name,
            "session_id": session_id,
            "started": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Started async agent {agent_name} with task ID {task_id}")
        
        return task_id
    
    async def get_agent_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of async agent execution"""
        if task_id not in self.running_agents:
            return {"error": "Task not found"}
        
        agent_info = self.running_agents[task_id]
        task = agent_info["task"]
        
        if task.done():
            result = await task
            del self.running_agents[task_id]
            return {
                "status": "completed",
                "result": result
            }
        else:
            return {
                "status": "running",
                "agent": agent_info["agent"],
                "session_id": agent_info["session_id"],
                "started": agent_info["started"]
            }
    
    def _get_output_files(self) -> set:
        """Get current output files"""
        files = set()
        for pattern in ["**/*.json", "**/*.md", "**/*.mermaid"]:
            files.update(
                str(f.relative_to(self.project_root))
                for f in self.output_dir.glob(pattern)
            )
        return files
    
    def _parse_agent_output(
        self,
        output: str,
        new_files: set
    ) -> Dict[str, Any]:
        """Parse agent output and extract key information"""
        result = {
            "summary": {
                "key_findings": [],
                "priority_items": [],
                "warnings": [],
                "recommendations_for_next": {}
            },
            "data": {
                "files_created": list(new_files),
                "output_preview": output[:500] if output else ""
            }
        }
        
        # Try to extract structured information from output
        # This is a simple implementation - enhance as needed
        lines = output.split('\n') if output else []
        
        for line in lines:
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                result["summary"]["key_findings"].append(line[2:])
            elif "warning" in line.lower() or "error" in line.lower():
                result["summary"]["warnings"].append(line)
        
        return result
    
    async def _write_context_summary(
        self,
        agent_name: str,
        session_id: str,
        result: Dict,
        execution_time: float
    ):
        """Write agent context summary for cross-agent communication"""
        context_file = self.context_dir / f"{agent_name}-summary.json"
        
        context_data = {
            "agent": agent_name,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_time": execution_time,
            "summary": result.get("summary", {}),
            "data": result.get("data", {})
        }
        
        with open(context_file, 'w') as f:
            json.dump(context_data, f, indent=2)
        
        logger.info(f"Context written: {context_file}")
    
    def get_agent_context(self, agent_name: str) -> Optional[Dict]:
        """Read agent context if it exists"""
        claude_name = self.get_claude_agent_name(agent_name)
        context_file = self.context_dir / f"{claude_name}-summary.json"
        
        if context_file.exists():
            with open(context_file) as f:
                return json.load(f)
        
        return None
    
    def list_available_agents(self) -> List[Dict[str, Any]]:
        """List all available agents with their timeouts"""
        agents = []
        for short_name, claude_name in self.AGENT_MAPPING.items():
            agents.append({
                "name": short_name,
                "claude_name": claude_name,
                "timeout": self.AGENT_TIMEOUTS.get(claude_name, 120)
            })
        return agents


# Example usage and testing
async def test_executor():
    """Test the Claude SDK executor"""
    executor = ClaudeSDKAgentExecutor()
    
    print("Testing Claude SDK Agent Executor")
    print("=" * 70)
    
    # Test single agent
    print("\n1. Testing single agent execution:")
    result = await executor.execute_agent(
        "solution-architect",
        "test-session-001",
        context={"project": "test"}
    )
    
    if result["success"]:
        print(f"   ✅ Success: {result['agent']}")
        print(f"   Execution time: {result['execution_time']:.1f}s")
        if result.get("files_created"):
            print(f"   Files created: {len(result['files_created'])}")
    else:
        print(f"   ❌ Failed: {result.get('error')}")
    
    # Test parallel execution
    print("\n2. Testing parallel agent execution:")
    agents = ["repomix-analyzer", "business-logic-analyst", "performance-analyst"]
    results = await executor.execute_agents_parallel(
        agents,
        "test-session-002",
        max_concurrent=2
    )
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"   {status} {result['original_name']}: {result.get('execution_time', 0):.1f}s")
    
    # Test sequential execution with context passing
    print("\n3. Testing sequential execution with context:")
    agents = ["solution-architect", "java-architect"]
    results = await executor.execute_agents_sequential(
        agents,
        "test-session-003",
        pass_context=True
    )
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"   {status} {result['original_name']}")
    
    print("\n" + "=" * 70)
    print("Test complete")


if __name__ == "__main__":
    asyncio.run(test_executor())