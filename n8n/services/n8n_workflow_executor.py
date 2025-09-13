#!/usr/bin/env python3
"""
n8n Workflow Executor
Executes documentation analysis workflows triggered by n8n
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from enum import Enum
import httpx

# Use centralized logging
from n8n.services.logging_config import executor_logger as logger, log_execution_start, log_execution_complete, log_exception, get_session_logger

class N8nWorkflowType(Enum):
    """Pre-defined n8n workflow types"""
    QUICK = "quick_analysis"
    COMPREHENSIVE = "comprehensive"
    SECURITY = "security_focus"
    PERFORMANCE = "performance_focus"
    MODERNIZATION = "modernization"
    CUSTOM = "custom"

class N8nWorkflowExecutor:
    """
    Executes analysis workflows for n8n integration
    Handles both pre-defined and custom workflows
    """
    
    def __init__(self, project_root: Path = Path(".")):
        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "output"
        self.context_dir = self.output_dir / "context"
        self.n8n_config_dir = self.project_root / "n8n" / "config"
        
        # Session manager for tracking
        import sys
        sys.path.append(str(self.project_root))
        from framework.scripts.session_manager import SessionManager
        self.session_manager = SessionManager(self.project_root)
        
        # Agent selector for configuration-based agent selection
        from n8n.services.agent_selector import AgentSelector
        self.agent_selector = AgentSelector(self.project_root)
        
        # Load workflow definitions AFTER agent_selector is initialized
        self.workflow_definitions = self._load_workflow_definitions()
        
    def _load_workflow_definitions(self) -> Dict:
        """Load pre-defined workflow configurations from user selection"""
        # First try to load user-selected agents
        selected_agents_file = self.context_dir / "selected-agents.json"
        
        if selected_agents_file.exists():
            with open(selected_agents_file, 'r') as f:
                user_config = json.load(f)
                
            # Build workflow from user selection with agent selector
            # This respects the auto_detect_architects setting
            complete_sequence = self.agent_selector.get_final_agent_list()
            parallel_groups = self.agent_selector.get_parallel_groups()
            
            # Quick analysis: mandatory + first 2 selected agents
            quick_agents = ["repomix-analyzer", "solution-architect"]
            selected = user_config.get('selected_analysis_agents', {}).get('agents', [])
            if selected:
                quick_agents.extend(selected[:1])  # Add first selected agent
            else:
                quick_agents.append("technical-architect")
            
            definitions = {
                N8nWorkflowType.QUICK: {
                    "name": "Quick Analysis",
                    "agents": quick_agents,
                    "parallel_groups": [],
                    "timeout": 3600,  # 1 hour
                    "checkpoints": []
                },
                N8nWorkflowType.COMPREHENSIVE: {
                    "name": "Comprehensive Analysis",
                    "agents": complete_sequence,  # Full user-selected sequence
                    "parallel_groups": parallel_groups,
                    "timeout": 14400,  # 4 hours
                    "checkpoints": ["discovery_review", "analysis_review", "documentation_review"]
                },
                N8nWorkflowType.SECURITY: {
                    "name": "Security-Focused Analysis",
                    "agents": [
                        "repomix-analyzer",
                        "solution-architect",
                        "security-analyst",
                        "technical-architect"
                    ],
                "parallel_groups": [],
                "timeout": 7200,  # 2 hours
                "checkpoints": []
            },
            N8nWorkflowType.PERFORMANCE: {
                "name": "Performance-Focused Analysis",
                "agents": [
                    "repomix-analyzer",
                    "solution-architect",
                    "performance-analyst",
                    "technical-architect"
                ],
                "parallel_groups": [],
                "timeout": 7200,  # 2 hours
                "checkpoints": []
            },
            N8nWorkflowType.MODERNIZATION: {
                "name": "Modernization Analysis",
                "agents": [
                    "repomix-analyzer",
                    "solution-architect",
                    "technical-architect",
                    "business-logic-analyst",
                    "performance-analyst",
                    "security-analyst",
                    "integration-specialist"
                ],
                "parallel_groups": [
                    ["performance-analyst", "security-analyst"]
                ],
                "timeout": 10800,  # 3 hours
                "checkpoints": ["architecture_review", "modernization_strategy_review"]
            }
        }
        
        # Load custom definitions if they exist
        custom_file = self.n8n_config_dir / "n8n_workflows.json"
        if custom_file.exists():
            with open(custom_file) as f:
                custom = json.load(f)
                definitions.update(custom)
        
        return definitions
    
    async def execute_n8n_workflow(
        self,
        workflow_type: str,
        session_id: str,
        options: Dict[str, Any] = None,
        callback_url: Optional[str] = None
    ):
        """
        Execute a complete workflow for n8n
        """
        try:
            logger.info(f"Starting n8n workflow: {workflow_type} for session: {session_id}")
            
            # Get workflow definition
            workflow_def = self._get_workflow_definition(workflow_type, options)
            
            # Send initial callback
            if callback_url:
                await self._send_n8n_callback(
                    callback_url,
                    session_id,
                    "workflow_started",
                    {"workflow": workflow_type, "agents": workflow_def["agents"]}
                )
            
            # Execute agents in sequence with parallel groups
            for item in self._create_execution_plan(workflow_def):
                if isinstance(item, list):
                    # Parallel group
                    await self._execute_parallel_group(item, session_id, callback_url)
                else:
                    # Single agent
                    await self._execute_single_agent(item, session_id, callback_url)
                
                # Check for checkpoints
                if item in workflow_def.get("checkpoints", []):
                    await self._handle_checkpoint(item, session_id, callback_url)
            
            # Send completion callback
            if callback_url:
                await self._send_n8n_callback(
                    callback_url,
                    session_id,
                    "workflow_completed",
                    {"workflow": workflow_type, "status": "success"}
                )
            
            logger.info(f"Workflow {workflow_type} completed successfully")
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            
            if callback_url:
                await self._send_n8n_callback(
                    callback_url,
                    session_id,
                    "workflow_failed",
                    {"workflow": workflow_type, "error": str(e)}
                )
            
            raise
    
    def _get_workflow_definition(self, workflow_type: str, options: Dict = None) -> Dict:
        """Get workflow definition with options override"""
        if workflow_type == "custom" and options:
            return {
                "name": options.get("name", "Custom Workflow"),
                "agents": options.get("agents", []),
                "parallel_groups": options.get("parallel_groups", []),
                "timeout": options.get("timeout", 7200),
                "checkpoints": options.get("checkpoints", [])
            }
        
        workflow_type_enum = N8nWorkflowType(workflow_type)
        return self.workflow_definitions.get(workflow_type_enum, {})
    
    def _create_execution_plan(self, workflow_def: Dict) -> List:
        """Create execution plan with parallel groups"""
        plan = []
        agents = workflow_def["agents"].copy()
        parallel_groups = workflow_def.get("parallel_groups", [])
        
        for agent in workflow_def["agents"]:
            # Check if agent is in a parallel group
            in_group = False
            for group in parallel_groups:
                if agent in group:
                    in_group = True
                    # Add the entire group if it's the first member
                    if group not in plan and all(a in agents for a in group):
                        plan.append(group)
                        for a in group:
                            agents.remove(a)
                    break
            
            if not in_group and agent in agents:
                plan.append(agent)
                agents.remove(agent)
        
        return plan
    
    async def _execute_single_agent(
        self,
        agent_name: str,
        session_id: str,
        callback_url: Optional[str] = None
    ):
        """Execute a single agent"""
        logger.info(f"Executing agent: {agent_name}")
        
        # Update status
        self.session_manager.update_agent_status(agent_name, "running")
        
        # Send callback
        if callback_url:
            await self._send_n8n_callback(
                callback_url,
                session_id,
                "agent_started",
                {"agent": agent_name}
            )
        
        try:
            # Use the Claude SDK executor approach that works
            from n8n.services.n8n_claude_sdk_executor import ClaudeSDKAgentExecutor
            
            sdk_executor = ClaudeSDKAgentExecutor(
                project_root=self.project_root,
                output_dir=self.output_dir
            )
            
            # Execute agent with SDK approach using correct naming
            session = self.session_manager.load_existing_session()
            project_name = session.get("project_name", "unknown") if session else "unknown"
            
            result = await sdk_executor.execute_agent(
                agent_name=agent_name,
                session_id=session_id,
                context={"workflow": "n8n", "project": project_name},
                timeout=600,  # 10 minute timeout
                use_print_mode=True  # Use print mode for non-interactive execution
            )
            
            if not result.get("success"):
                # Don't fall back to mock - fail properly
                error_msg = f"Claude SDK execution failed for {agent_name}: {result.get('error')}"
                logger.error(error_msg)
                
                # Create a proper failure result
                result = {
                    "success": False,
                    "agent": agent_name,
                    "error": error_msg,
                    "note": "Claude CLI is not available in Docker container. Run agents on host machine."
                }
                
                # Mark as failed and continue
                self.session_manager.update_agent_status(agent_name, "failed")
                raise Exception(error_msg)
            
            # Update status
            self.session_manager.update_agent_status(agent_name, "completed")
            
            # Send callback
            if callback_url:
                await self._send_n8n_callback(
                    callback_url,
                    session_id,
                    "agent_completed",
                    {"agent": agent_name, "result": result}
                )
            
            logger.info(f"Agent {agent_name} completed successfully")
            
        except Exception as e:
            logger.error(f"Agent {agent_name} failed: {e}")
            self.session_manager.update_agent_status(agent_name, "failed")
            
            if callback_url:
                await self._send_n8n_callback(
                    callback_url,
                    session_id,
                    "agent_failed",
                    {"agent": agent_name, "error": str(e)}
                )
            
            raise
    
    async def _execute_parallel_group(
        self,
        agents: List[str],
        session_id: str,
        callback_url: Optional[str] = None
    ):
        """Execute multiple agents in parallel"""
        logger.info(f"Executing parallel group: {agents}")
        
        # Send callback
        if callback_url:
            await self._send_n8n_callback(
                callback_url,
                session_id,
                "parallel_group_started",
                {"agents": agents}
            )
        
        # Create tasks for parallel execution
        tasks = []
        for agent in agents:
            task = asyncio.create_task(
                self._execute_single_agent(agent, session_id, None)
            )
            tasks.append(task)
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        failed = []
        for agent, result in zip(agents, results):
            if isinstance(result, Exception):
                failed.append(agent)
                logger.error(f"Agent {agent} failed in parallel group: {result}")
        
        # Send callback
        if callback_url:
            await self._send_n8n_callback(
                callback_url,
                session_id,
                "parallel_group_completed",
                {"agents": agents, "failed": failed}
            )
        
        if failed:
            raise Exception(f"Parallel group execution failed for: {failed}")
        
        logger.info(f"Parallel group completed: {agents}")
    
    async def _handle_checkpoint(
        self,
        checkpoint_name: str,
        session_id: str,
        callback_url: Optional[str] = None
    ):
        """Handle workflow checkpoint for n8n decision"""
        logger.info(f"Checkpoint reached: {checkpoint_name}")
        
        # Update checkpoint status
        self.session_manager.update_checkpoint(checkpoint_name, "pending")
        
        if callback_url:
            # Send checkpoint callback and wait for response
            await self._send_n8n_callback(
                callback_url,
                session_id,
                "checkpoint_reached",
                {
                    "checkpoint": checkpoint_name,
                    "requires_decision": True,
                    "continue_url": f"/n8n/checkpoint/{session_id}/{checkpoint_name}/continue"
                }
            )
            
            # In automated mode, we continue by default
            # n8n can override by calling the checkpoint endpoint
            await asyncio.sleep(5)  # Give n8n time to respond
        
        # Mark checkpoint as completed
        self.session_manager.update_checkpoint(checkpoint_name, "completed")
    
    async def _send_n8n_callback(
        self,
        callback_url: str,
        session_id: str,
        event_type: str,
        data: Dict[str, Any]
    ):
        """Send callback to n8n webhook"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "session_id": session_id,
                    "event_type": event_type,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "data": data
                }
                
                response = await client.post(
                    callback_url,
                    json=payload,
                    timeout=10.0
                )
                
                logger.info(f"Callback sent to n8n: {event_type}")
                
        except Exception as e:
            logger.warning(f"Failed to send callback to n8n: {e}")
    
    def get_workflow_status(self, session_id: str) -> Dict:
        """Get current workflow status"""
        session = self.session_manager.load_existing_session()
        
        if not session or session.get("session_id") != session_id:
            return {"error": "Session not found"}
        
        status = self.session_manager.get_session_status()
        
        # Calculate progress
        total = len(status["completed_agents"]) + len(status["pending_agents"]) + len(status["running_agents"])
        progress = len(status["completed_agents"]) / total if total > 0 else 0
        
        return {
            "session_id": session_id,
            "progress": round(progress * 100, 2),
            "phase": status["phase"],
            "agents": {
                "completed": status["completed_agents"],
                "running": status["running_agents"],
                "pending": status["pending_agents"],
                "failed": status["failed_agents"]
            },
            "is_complete": len(status["pending_agents"]) == 0 and len(status["running_agents"]) == 0
        }
    
    def get_available_workflows(self) -> List[Dict]:
        """Get list of available workflows for n8n"""
        workflows = []
        
        for workflow_type in N8nWorkflowType:
            if workflow_type in self.workflow_definitions:
                def_data = self.workflow_definitions[workflow_type]
                workflows.append({
                    "id": workflow_type.value,
                    "name": def_data["name"],
                    "agents": def_data["agents"],
                    "estimated_time": def_data["timeout"] // 60,  # in minutes
                    "has_checkpoints": len(def_data.get("checkpoints", [])) > 0,
                    "supports_parallel": len(def_data.get("parallel_groups", [])) > 0
                })
        
        return workflows