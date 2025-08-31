#!/usr/bin/env python3
"""
Session Manager for SUPERVISED Mode
Handles session persistence across Claude Code sessions
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

class SessionManager:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.context_dir = self.project_root / "output" / "context"
        self.progress_file = self.context_dir / "session-progress.json"
        self.context_dir.mkdir(parents=True, exist_ok=True)

    def start_new_session(self, project_name: str, mode: str = "SUPERVISED") -> str:
        """Start a new analysis session"""
        session_id = str(uuid.uuid4())
        
        progress_data = {
            "session_id": session_id,
            "project_name": project_name,
            "mode": mode,
            "started": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "progress": {
                "phase": "discovery",
                "required_sequence_complete": False,
                "completed_agents": [],
                "running_agents": [],
                "pending_agents": [
                    "mcp-orchestrator",
                    "repomix-analyzer", 
                    "architecture-selector"
                ],
                "failed_agents": [],
                "skipped_agents": []
            },
            "user_selections": {},
            "checkpoints": {
                "discovery_review": "pending",
                "business_logic_review": "pending",
                "diagram_planning": "pending", 
                "final_review": "pending"
            }
        }
        
        self._save_progress(progress_data)
        return session_id

    def load_existing_session(self) -> Optional[Dict[str, Any]]:
        """Load existing session if available"""
        if not self.progress_file.exists():
            return None
            
        try:
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def update_agent_status(self, agent_name: str, status: str) -> None:
        """Update agent status: completed, running, failed"""
        progress = self.load_existing_session()
        if not progress:
            return
            
        # Remove from all status lists
        for status_list in ['completed_agents', 'running_agents', 'pending_agents', 'failed_agents']:
            if agent_name in progress['progress'][status_list]:
                progress['progress'][status_list].remove(agent_name)
        
        # Add to appropriate status list
        if status == "completed":
            progress['progress']['completed_agents'].append(agent_name)
        elif status == "running":
            progress['progress']['running_agents'].append(agent_name)
        elif status == "failed":
            progress['progress']['failed_agents'].append(agent_name)
        elif status == "pending":
            progress['progress']['pending_agents'].append(agent_name)
            
        # Check if required sequence is complete
        required_agents = ["mcp-orchestrator", "repomix-analyzer", "architecture-selector"]
        if all(agent in progress['progress']['completed_agents'] for agent in required_agents):
            progress['progress']['required_sequence_complete'] = True
            progress['progress']['phase'] = "analysis"
            
        progress['last_updated'] = datetime.now(timezone.utc).isoformat()
        self._save_progress(progress)

    def update_checkpoint(self, checkpoint_name: str, status: str) -> None:
        """Update checkpoint status: completed, pending, skipped"""
        progress = self.load_existing_session()
        if not progress:
            return
            
        progress['checkpoints'][checkpoint_name] = status
        progress['last_updated'] = datetime.now(timezone.utc).isoformat()
        self._save_progress(progress)

    def add_user_selection(self, key: str, value: Any) -> None:
        """Add user selection to session"""
        progress = self.load_existing_session()
        if not progress:
            return
            
        progress['user_selections'][key] = value
        progress['last_updated'] = datetime.now(timezone.utc).isoformat()
        self._save_progress(progress)

    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status for display"""
        progress = self.load_existing_session()
        if not progress:
            return {"status": "no_session"}
            
        return {
            "status": "active_session",
            "session_id": progress['session_id'],
            "project_name": progress['project_name'],
            "mode": progress['mode'],
            "phase": progress['progress']['phase'],
            "completed_agents": progress['progress']['completed_agents'],
            "running_agents": progress['progress']['running_agents'],
            "pending_agents": progress['progress']['pending_agents'],
            "failed_agents": progress['progress']['failed_agents'],
            "required_sequence_complete": progress['progress']['required_sequence_complete'],
            "next_checkpoint": self._get_next_checkpoint(progress),
            "last_updated": progress['last_updated']
        }

    def get_next_recommendations(self) -> Dict[str, List[str]]:
        """Get recommendations for next steps"""
        progress = self.load_existing_session()
        if not progress:
            return {"actions": ["Start new session"]}
            
        recommendations = {"actions": []}
        
        if not progress['progress']['required_sequence_complete']:
            # Still in required sequence
            pending_required = [agent for agent in ["mcp-orchestrator", "repomix-analyzer", "architecture-selector"] 
                              if agent not in progress['progress']['completed_agents']]
            recommendations["actions"].append(f"Complete required sequence: {', '.join(pending_required)}")
        else:
            # Can run parallel agents
            if progress['progress']['pending_agents']:
                recommendations["actions"].append("Run any of the pending agents in parallel")
                recommendations["parallel_options"] = progress['progress']['pending_agents']
            
            # Check for checkpoints
            next_checkpoint = self._get_next_checkpoint(progress)
            if next_checkpoint:
                recommendations["actions"].append(f"Complete checkpoint: {next_checkpoint}")
                
        return recommendations

    def add_agents_to_pending(self, agent_names: List[str]) -> None:
        """Add agents to pending list (typically after architecture-selector)"""
        progress = self.load_existing_session()
        if not progress:
            return
            
        for agent in agent_names:
            if agent not in progress['progress']['pending_agents']:
                progress['progress']['pending_agents'].append(agent)
                
        progress['last_updated'] = datetime.now(timezone.utc).isoformat()
        self._save_progress(progress)

    def _save_progress(self, progress_data: Dict[str, Any]) -> None:
        """Save progress data to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(progress_data, f, indent=2)

    def _get_next_checkpoint(self, progress: Dict[str, Any]) -> Optional[str]:
        """Get the next pending checkpoint"""
        for checkpoint, status in progress['checkpoints'].items():
            if status == "pending":
                return checkpoint
        return None

def display_session_status():
    """CLI function to display current session status"""
    manager = SessionManager()
    status = manager.get_session_status()
    
    if status["status"] == "no_session":
        print("No active session found. Start analysis to create a new session.")
        return
        
    print(f"""
📊 Current Session Status
========================
Project: {status['project_name']}
Mode: {status['mode']}
Phase: {status['phase']}
Session ID: {status['session_id'][:8]}...

✅ Completed Agents ({len(status['completed_agents'])}):
{chr(10).join(f"   - {agent}" for agent in status['completed_agents'])}

🏃 Running Agents ({len(status['running_agents'])}):
{chr(10).join(f"   - {agent}" for agent in status['running_agents'])}

⏳ Pending Agents ({len(status['pending_agents'])}):
{chr(10).join(f"   - {agent}" for agent in status['pending_agents'])}

{f"❌ Failed Agents ({len(status['failed_agents'])}):" + chr(10) + chr(10).join(f"   - {agent}" for agent in status['failed_agents']) if status['failed_agents'] else ""}

Required Sequence: {'✅ Complete' if status['required_sequence_complete'] else '⏳ In Progress'}
Last Updated: {status['last_updated']}
""")
    
    # Show recommendations
    recommendations = manager.get_next_recommendations()
    if recommendations["actions"]:
        print("🎯 Next Steps:")
        for action in recommendations["actions"]:
            print(f"   - {action}")
            
        if "parallel_options" in recommendations:
            print(f"\n   Available for parallel execution:")
            for agent in recommendations["parallel_options"]:
                print(f"      @{agent}")

if __name__ == "__main__":
    display_session_status()