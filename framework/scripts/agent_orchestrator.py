#!/usr/bin/env python3
"""
Agent Orchestration Helper
Assists with planning and executing agent workflows for codebase analysis
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

class Colors:
    """Terminal colors (cross-platform)"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    @staticmethod
    def enable_windows():
        """Enable ANSI colors on Windows 10+"""
        if sys.platform == 'win32':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                Colors.disable()
    
    @staticmethod
    def disable():
        """Disable colors"""
        for attr in dir(Colors):
            if not attr.startswith('_') and attr.isupper():
                setattr(Colors, attr, '')


class AnalysisPhase(Enum):
    """Analysis workflow phases"""
    SETUP = "Setup & Configuration"
    MCP_INIT = "MCP Initialization"
    DISCOVERY = "Discovery & Archaeological Analysis"
    BUSINESS = "Business Logic Extraction"
    VISUALIZATION = "Diagram & Visualization"
    PERFORMANCE = "Performance Analysis"
    SECURITY = "Security Analysis"
    MODERNIZATION = "Modernization Strategy"
    DOCUMENTATION = "Documentation Generation"
    VALIDATION = "Validation & Quality Check"


class Agent:
    """Represents an analysis agent"""
    def __init__(self, name: str, description: str, phase: AnalysisPhase, 
                 dependencies: List[str] = None, outputs: List[str] = None):
        self.name = name
        self.description = description
        self.phase = phase
        self.dependencies = dependencies or []
        self.outputs = outputs or []
        self.status = "pending"
        self.execution_time = None
        self.notes = []
    
    def __repr__(self):
        return f"Agent({self.name}, phase={self.phase.value}, status={self.status})"


class AgentOrchestrator:
    """Orchestrates agent execution workflow"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.resolve()
        self.framework_dir = self.script_dir.parent
        self.project_root = self.framework_dir.parent
        self.agents_dir = self.project_root / ".claude" / "agents"
        
        # Enable colors
        Colors.enable_windows()
        
        # Define agent workflow
        self.agents = self.initialize_agents()
        self.workflow_phases = list(AnalysisPhase)
        
    def initialize_agents(self) -> Dict[str, Agent]:
        """Initialize all available agents with their metadata"""
        agents = {}
        
        # Phase 0: Setup
        agents["setup"] = Agent(
            "setup",
            "Initial project setup and configuration",
            AnalysisPhase.SETUP,
            dependencies=[],
            outputs=["TARGET_TECH_STACK.md", ".mcp.json", ".repomix.config.json"]
        )
        
        # Phase 1: MCP Initialization
        agents["mcp-orchestrator"] = Agent(
            "mcp-orchestrator",
            "Coordinates optimal MCP usage across all analysis phases",
            AnalysisPhase.MCP_INIT,
            dependencies=["setup"],
            outputs=["output/reports/mcp-strategy.md"]
        )
        
        agents["repomix-analyzer"] = Agent(
            "repomix-analyzer",
            "Analyzes Repomix-generated codebase summaries",
            AnalysisPhase.MCP_INIT,
            dependencies=["mcp-orchestrator"],
            outputs=["output/reports/repomix-summary.md"]
        )
        
        # Phase 2: Discovery
        agents["legacy-code-detective"] = Agent(
            "legacy-code-detective",
            "Archaeological analysis of legacy codebases",
            AnalysisPhase.DISCOVERY,
            dependencies=["repomix-analyzer"],
            outputs=["output/docs/01-archaeological-analysis.md"]
        )
        
        # Phase 3: Business Logic
        agents["business-logic-analyst"] = Agent(
            "business-logic-analyst",
            "Extracts and catalogs business rules and domain logic",
            AnalysisPhase.BUSINESS,
            dependencies=["legacy-code-detective"],
            outputs=["output/docs/02-business-logic-analysis.md"]
        )
        
        # Phase 4: Visualization
        agents["diagram-architect"] = Agent(
            "diagram-architect",
            "Creates comprehensive visual documentation",
            AnalysisPhase.VISUALIZATION,
            dependencies=["business-logic-analyst"],
            outputs=["output/docs/03-visual-architecture.md", "output/diagrams/"]
        )
        
        # Phase 5: Performance
        agents["performance-analyst"] = Agent(
            "performance-analyst",
            "Identifies performance bottlenecks and optimization opportunities",
            AnalysisPhase.PERFORMANCE,
            dependencies=["legacy-code-detective"],
            outputs=["output/docs/04-performance-analysis.md"]
        )
        
        # Phase 6: Security
        agents["security-analyst"] = Agent(
            "security-analyst",
            "Comprehensive security vulnerability assessment",
            AnalysisPhase.SECURITY,
            dependencies=["legacy-code-detective"],
            outputs=["output/docs/05-security-analysis.md"]
        )
        
        # Phase 7: Modernization
        agents["modernization-architect"] = Agent(
            "modernization-architect",
            "Creates actionable modernization roadmap",
            AnalysisPhase.MODERNIZATION,
            dependencies=["legacy-code-detective", "business-logic-analyst", 
                         "performance-analyst", "security-analyst"],
            outputs=["output/docs/06-modernization-strategy.md"]
        )
        
        # Phase 8: Documentation
        agents["documentation-specialist"] = Agent(
            "documentation-specialist",
            "Generates comprehensive technical documentation",
            AnalysisPhase.DOCUMENTATION,
            dependencies=["modernization-architect"],
            outputs=["output/docs/"]
        )
        
        # Additional specialized agents
        agents["angular-architect"] = Agent(
            "angular-architect",
            "Expert Angular architect for Angular-based applications",
            AnalysisPhase.MODERNIZATION,
            dependencies=["legacy-code-detective"],
            outputs=["output/docs/angular-migration.md"]
        )
        
        return agents
    
    def show_workflow(self):
        """Display the complete workflow"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}AGENT ORCHESTRATION WORKFLOW{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")
        
        for phase in self.workflow_phases:
            phase_agents = [a for a in self.agents.values() if a.phase == phase]
            if phase_agents:
                print(f"{Colors.BLUE}{Colors.BOLD}Phase {phase.value}:{Colors.RESET}")
                print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")
                
                for agent in phase_agents:
                    status_icon = self.get_status_icon(agent.status)
                    print(f"  {status_icon} {Colors.YELLOW}@{agent.name}{Colors.RESET}")
                    print(f"     {Colors.DIM}{agent.description}{Colors.RESET}")
                    
                    if agent.dependencies:
                        deps = ", ".join([f"@{d}" for d in agent.dependencies])
                        print(f"     {Colors.DIM}Depends on: {deps}{Colors.RESET}")
                    
                    if agent.outputs:
                        print(f"     {Colors.DIM}Outputs: {', '.join(agent.outputs)}{Colors.RESET}")
                    
                    print()
    
    def get_status_icon(self, status: str) -> str:
        """Get status icon for agent"""
        icons = {
            "pending": "⏳",
            "running": "🔄",
            "completed": "✅",
            "failed": "❌",
            "skipped": "⏭️"
        }
        return icons.get(status, "❓")
    
    def generate_execution_plan(self, target_agents: List[str] = None) -> List[str]:
        """Generate optimal execution order based on dependencies"""
        if not target_agents:
            target_agents = list(self.agents.keys())
        
        # Topological sort for dependency resolution
        visited = set()
        execution_order = []
        
        def visit(agent_name: str):
            if agent_name in visited:
                return
            
            agent = self.agents.get(agent_name)
            if not agent:
                return
            
            # Visit dependencies first
            for dep in agent.dependencies:
                visit(dep)
            
            visited.add(agent_name)
            execution_order.append(agent_name)
        
        for agent_name in target_agents:
            visit(agent_name)
        
        return execution_order
    
    def show_execution_plan(self, plan: List[str]):
        """Display execution plan"""
        print(f"\n{Colors.GREEN}{Colors.BOLD}EXECUTION PLAN{Colors.RESET}")
        print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}\n")
        
        for i, agent_name in enumerate(plan, 1):
            agent = self.agents[agent_name]
            print(f"{Colors.CYAN}{i:2d}.{Colors.RESET} {Colors.YELLOW}@{agent_name}{Colors.RESET}")
            print(f"    Phase: {agent.phase.value}")
            print(f"    {Colors.DIM}{agent.description}{Colors.RESET}")
    
    def generate_commands(self, plan: List[str]) -> List[str]:
        """Generate Claude Code commands for agent execution"""
        commands = []
        
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}CLAUDE CODE COMMANDS{Colors.RESET}")
        print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")
        print(f"{Colors.DIM}Copy and paste these commands in Claude Code:{Colors.RESET}\n")
        
        current_phase = None
        for agent_name in plan:
            agent = self.agents[agent_name]
            
            # Add phase comment if phase changes
            if agent.phase != current_phase:
                commands.append(f"\n# Phase: {agent.phase.value}")
                current_phase = agent.phase
            
            # Add agent command
            if agent_name == "setup":
                commands.append("# Run setup.py or setup.sh first")
            else:
                commands.append(f"@{agent_name}")
        
        return commands
    
    def check_prerequisites(self) -> Tuple[bool, List[str]]:
        """Check if all prerequisites are met"""
        issues = []
        
        print(f"\n{Colors.YELLOW}{Colors.BOLD}PREREQUISITE CHECK{Colors.RESET}")
        print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}\n")
        
        # Check .mcp.json
        if not (self.project_root / ".mcp.json").exists():
            issues.append("Missing .mcp.json - Run setup script first")
            print(f"{Colors.RED}❌ .mcp.json not found{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}✅ .mcp.json exists{Colors.RESET}")
        
        # Check agents directory
        if not self.agents_dir.exists():
            issues.append("Missing .claude/agents directory")
            print(f"{Colors.RED}❌ Agents directory not found{Colors.RESET}")
        else:
            agent_files = list(self.agents_dir.glob("*.md"))
            print(f"{Colors.GREEN}✅ Found {len(agent_files)} agent definitions{Colors.RESET}")
        
        # Check output directories
        output_dirs = ["output/docs", "output/diagrams", "output/reports"]
        for dir_path in output_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"{Colors.YELLOW}📁 Created {dir_path}{Colors.RESET}")
        
        # Check codebase
        codebase_dir = self.project_root / "codebase"
        if not codebase_dir.exists() or not list(codebase_dir.iterdir()):
            issues.append("No codebase found in codebase/ directory")
            print(f"{Colors.RED}❌ No codebase to analyze{Colors.RESET}")
        else:
            projects = [d.name for d in codebase_dir.iterdir() if d.is_dir()]
            print(f"{Colors.GREEN}✅ Found projects: {', '.join(projects)}{Colors.RESET}")
        
        return len(issues) == 0, issues
    
    def interactive_mode(self):
        """Interactive workflow planner"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}INTERACTIVE WORKFLOW PLANNER{Colors.RESET}")
        print(f"{Colors.DIM}Select agents to include in your analysis{Colors.RESET}\n")
        
        # Group agents by phase
        for phase in self.workflow_phases:
            phase_agents = [a for a in self.agents.values() if a.phase == phase]
            if phase_agents:
                print(f"\n{Colors.BLUE}{phase.value}:{Colors.RESET}")
                for agent in phase_agents:
                    print(f"  [{Colors.YELLOW}{agent.name}{Colors.RESET}] {agent.description}")
        
        print(f"\n{Colors.DIM}Enter agent names separated by commas (or 'all' for complete analysis):{Colors.RESET}")
        selection = input("> ").strip()
        
        if selection.lower() == "all":
            selected_agents = [a for a in self.agents.keys() if a != "setup"]
        else:
            selected_agents = [a.strip() for a in selection.split(",")]
            selected_agents = [a for a in selected_agents if a in self.agents]
        
        if not selected_agents:
            print(f"{Colors.RED}No valid agents selected{Colors.RESET}")
            return
        
        # Generate execution plan
        plan = self.generate_execution_plan(selected_agents)
        self.show_execution_plan(plan)
        
        # Generate commands
        commands = self.generate_commands(plan)
        for cmd in commands:
            print(cmd)
        
        # Save plan
        self.save_plan(plan)
    
    def save_plan(self, plan: List[str]):
        """Save execution plan to file"""
        plan_file = self.project_root / "output" / "analysis_plan.json"
        plan_data = {
            "generated": datetime.now().isoformat(),
            "agents": plan,
            "phases": {}
        }
        
        for agent_name in plan:
            agent = self.agents[agent_name]
            phase_name = agent.phase.value
            if phase_name not in plan_data["phases"]:
                plan_data["phases"][phase_name] = []
            plan_data["phases"][phase_name].append({
                "name": agent_name,
                "description": agent.description,
                "outputs": agent.outputs
            })
        
        plan_file.write_text(json.dumps(plan_data, indent=2))
        print(f"\n{Colors.GREEN}✅ Plan saved to: output/analysis_plan.json{Colors.RESET}")
    
    def run(self, mode: str = "full"):
        """Main orchestrator entry point"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("=" * 70)
        print("     CODEBASE ANALYSIS AGENT ORCHESTRATOR")
        print("=" * 70)
        print(f"{Colors.RESET}\n")
        
        # Check prerequisites
        ready, issues = self.check_prerequisites()
        if not ready:
            print(f"\n{Colors.RED}Prerequisites not met:{Colors.RESET}")
            for issue in issues:
                print(f"  • {issue}")
            return 1
        
        if mode == "workflow":
            self.show_workflow()
        elif mode == "interactive":
            self.interactive_mode()
        else:  # full mode
            # Generate complete analysis plan
            plan = self.generate_execution_plan()
            self.show_execution_plan(plan)
            
            # Generate commands
            commands = self.generate_commands(plan)
            for cmd in commands:
                print(cmd)
            
            # Save plan
            self.save_plan(plan)
        
        return 0


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agent Orchestration Helper for Codebase Analysis"
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="full",
        choices=["full", "workflow", "interactive"],
        help="Execution mode (default: full)"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    orchestrator = AgentOrchestrator()
    exit_code = orchestrator.run(args.mode)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()