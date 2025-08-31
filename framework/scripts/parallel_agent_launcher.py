#!/usr/bin/env python3
"""
Parallel Agent Launcher
Helps coordinate running multiple agents in separate Claude Code sessions
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

class ParallelAgentCoordinator:
    def __init__(self):
        self.project_root = Path.cwd()
        self.context_dir = self.project_root / "output" / "context"
        self.progress_file = self.context_dir / "session-progress.json"
        self.parallel_file = self.context_dir / "parallel-execution.json"
        
    def check_prerequisites(self) -> bool:
        """Check if required agents have completed"""
        if not self.progress_file.exists():
            print("❌ No session found. Run setup first.")
            return False
            
        with open(self.progress_file) as f:
            data = json.load(f)
            
        required = ["mcp-orchestrator", "repomix-analyzer", "architecture-selector"]
        completed = data["progress"]["completed_agents"]
        
        if not all(agent in completed for agent in required):
            missing = [a for a in required if a not in completed]
            print(f"❌ Must complete first: {', '.join(missing)}")
            return False
            
        print("✅ Prerequisites complete - agents can run in parallel")
        return True
        
    def get_recommended_groups(self) -> Dict[str, List[str]]:
        """Get recommended parallel agent groups"""
        groups = {
            "core_analysis": [
                "business-logic-analyst",
                "security-analyst",
                "performance-analyst"
            ],
            "specialized_analysis": [
                "ui-analysis-specialist",
                "data-model-specialist",
                "domain-boundary-analyst"
            ],
            "documentation": [
                "diagram-architect",
                "documentation-specialist",
                "executive-summary"
            ]
        }
        
        # Check architecture-selector recommendations
        arch_summary = self.context_dir / "architecture-selector-summary.json"
        if arch_summary.exists():
            with open(arch_summary) as f:
                arch_data = json.load(f)
                if "recommendations" in arch_data.get("data", {}):
                    specialists = arch_data["data"]["recommendations"].get("specialist_architects", [])
                    if specialists:
                        groups["specialized_analysis"].extend(specialists)
                        
        return groups
        
    def create_parallel_session(self, agents: List[str]) -> str:
        """Create a parallel execution session"""
        session_id = f"parallel-{int(time.time())}"
        
        parallel_data = {
            "session_id": session_id,
            "started": datetime.now(timezone.utc).isoformat(),
            "agents": agents,
            "status": {agent: "pending" for agent in agents},
            "instructions": self._generate_instructions(agents)
        }
        
        with open(self.parallel_file, 'w') as f:
            json.dump(parallel_data, f, indent=2)
            
        return session_id
        
    def _generate_instructions(self, agents: List[str]) -> List[str]:
        """Generate instructions for running agents in parallel"""
        instructions = [
            "PARALLEL EXECUTION INSTRUCTIONS:",
            "================================",
            "",
            "To run these agents in parallel, you need to open multiple Claude Code sessions.",
            "",
            "Option 1: Multiple Browser Tabs/Windows",
            "----------------------------------------",
        ]
        
        for i, agent in enumerate(agents, 1):
            instructions.append(f"{i}. Open a new Claude Code tab/window")
            instructions.append(f"   Run: @{agent}")
            instructions.append(f"   This agent will:")
            instructions.append(f"   - Read from: output/context/*-summary.json")
            instructions.append(f"   - Write to: output/context/{agent}-summary.json")
            instructions.append("")
            
        instructions.extend([
            "Option 2: Sequential with Context Reset",
            "----------------------------------------",
            "If you can't open multiple sessions, run each agent with a context reset between:",
            ""
        ])
        
        for agent in agents:
            instructions.append(f"1. Run: @{agent}")
            instructions.append(f"2. After completion, use /clear or start new conversation")
            instructions.append(f"3. Continue with next agent")
            instructions.append("")
            
        instructions.extend([
            "Monitoring Progress:",
            "--------------------",
            "In any Claude Code session, run: /status",
            "Or run: python3 framework/scripts/parallel_agent_launcher.py --status",
            "",
            "Each agent will update its status in the context files when complete."
        ])
        
        return instructions
        
    def monitor_progress(self) -> Dict[str, str]:
        """Monitor parallel execution progress"""
        if not self.parallel_file.exists():
            return {"error": "No parallel execution in progress"}
            
        with open(self.parallel_file) as f:
            parallel_data = json.load(f)
            
        agents = parallel_data["agents"]
        status = {}
        
        for agent in agents:
            summary_file = self.context_dir / f"{agent}-summary.json"
            if summary_file.exists():
                # Check if file was created after parallel session started
                mtime = datetime.fromtimestamp(summary_file.stat().st_mtime, timezone.utc)
                start_time = datetime.fromisoformat(parallel_data["started"])
                
                if mtime > start_time:
                    status[agent] = "completed"
                else:
                    status[agent] = "pending (old file exists)"
            else:
                status[agent] = "pending"
                
        # Update parallel session file
        parallel_data["status"] = status
        with open(self.parallel_file, 'w') as f:
            json.dump(parallel_data, f, indent=2)
            
        return status
        
    def display_status(self):
        """Display current parallel execution status"""
        status = self.monitor_progress()
        
        if "error" in status:
            print(status["error"])
            return
            
        print("\n📊 Parallel Execution Status")
        print("=" * 40)
        
        completed = [a for a, s in status.items() if s == "completed"]
        pending = [a for a, s in status.items() if "pending" in s]
        
        if completed:
            print(f"\n✅ Completed ({len(completed)}):")
            for agent in completed:
                print(f"   - {agent}")
                
        if pending:
            print(f"\n⏳ Pending ({len(pending)}):")
            for agent in pending:
                print(f"   - {agent}")
                
        print(f"\nProgress: {len(completed)}/{len(status)} agents complete")
        
        if len(completed) == len(status):
            print("\n🎉 All agents complete! Run /status to see full results.")
            

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Parallel Agent Launcher")
    parser.add_argument("--check", action="store_true", help="Check prerequisites")
    parser.add_argument("--status", action="store_true", help="Show parallel execution status")
    parser.add_argument("--launch", nargs="+", help="Launch parallel session with specified agents")
    parser.add_argument("--groups", action="store_true", help="Show recommended agent groups")
    
    args = parser.parse_args()
    
    coordinator = ParallelAgentCoordinator()
    
    if args.check:
        coordinator.check_prerequisites()
        
    elif args.status:
        coordinator.display_status()
        
    elif args.groups:
        groups = coordinator.get_recommended_groups()
        print("\n🎯 Recommended Parallel Agent Groups\n")
        for group_name, agents in groups.items():
            print(f"{group_name.replace('_', ' ').title()}:")
            for agent in agents:
                print(f"  - {agent}")
            print()
            
    elif args.launch:
        if coordinator.check_prerequisites():
            session_id = coordinator.create_parallel_session(args.launch)
            print(f"\n✅ Created parallel session: {session_id}\n")
            
            with open(coordinator.parallel_file) as f:
                data = json.load(f)
                for line in data["instructions"]:
                    print(line)
    else:
        parser.print_help()
        

if __name__ == "__main__":
    main()