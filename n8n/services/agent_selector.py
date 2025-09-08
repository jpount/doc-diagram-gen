#!/usr/bin/env python3
"""
Agent Selector for n8n Workflows
Determines which agents to run based on configuration and optional auto-detection
"""

import json
from pathlib import Path
from typing import List, Dict

class AgentSelector:
    """
    Reads selected-agents.json and determines final agent list
    Respects auto-detection setting for technology architects
    """
    
    def __init__(self, project_root: Path = Path(".")):
        self.project_root = Path(project_root)
        self.config_file = self.project_root / "output" / "context" / "selected-agents.json"
        self.codebase_dir = self.project_root / "codebase"
        
    def load_config(self) -> Dict:
        """Load the selected agents configuration"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def detect_technologies(self) -> List[str]:
        """Detect which technology-specific architects might be needed"""
        detected = []
        
        # Only detect if codebase directory exists
        if not self.codebase_dir.exists():
            return detected
        
        # Check for Java
        java_files = list(self.codebase_dir.rglob("*.java"))
        if java_files:
            detected.append("java-architect")
        
        # Check for .NET
        cs_files = list(self.codebase_dir.rglob("*.cs"))
        if cs_files:
            detected.append("dotnet-architect")
        
        # Check for Angular
        angular_json = list(self.codebase_dir.rglob("angular.json"))
        component_ts = list(self.codebase_dir.rglob("*.component.ts"))
        if angular_json or component_ts:
            detected.append("angular-architect")
        
        return detected
    
    def get_final_agent_list(self) -> List[str]:
        """Get the final list of agents to run"""
        config = self.load_config()
        
        # Start with mandatory agents
        agents = config['mandatory_agents']['agents'].copy()
        
        # Add selected analysis agents
        agents.extend(config['selected_analysis_agents']['agents'])
        
        # Handle technology architects
        auto_detect = config['settings']['auto_detect_architects']
        tech_architects = config['technology_architects']['agents']
        
        if auto_detect:
            # Auto-detection is enabled - detect and add architects
            detected = self.detect_technologies()
            for architect in detected:
                if architect not in agents:
                    agents.insert(2, architect)  # Insert after repomix-analyzer
                    print(f"Auto-detected and added: {architect}")
        else:
            # Auto-detection disabled - only add if explicitly selected by user
            for architect_name, architect_config in tech_architects.items():
                if architect_config.get('selected_by_user', False):
                    if architect_name not in agents:
                        agents.insert(2, architect_name)
                        print(f"User-selected architect: {architect_name}")
        
        # Ensure diagram-architect is at the end if not already there
        if "diagram-agent" in agents:
            agents.remove("diagram-agent")
        agents.append("diagram-agent")
        
        return agents
    
    def get_parallel_groups(self) -> List[List[str]]:
        """Get parallel execution groups"""
        config = self.load_config()
        return config['execution_settings']['parallel_groups']
    
    def print_configuration(self):
        """Print the current configuration for debugging"""
        config = self.load_config()
        
        print("=" * 60)
        print("AGENT CONFIGURATION")
        print("=" * 60)
        
        print(f"\nAuto-Detection: {'ENABLED' if config['settings']['auto_detect_architects'] else 'DISABLED'}")
        
        print("\nMandatory Agents (always run):")
        for agent in config['mandatory_agents']['agents']:
            print(f"  ✓ {agent}")
        
        print("\nSelected Analysis Agents:")
        for agent in config['selected_analysis_agents']['agents']:
            print(f"  ✓ {agent}")
        
        print("\nTechnology Architects:")
        for name, arch_config in config['technology_architects']['agents'].items():
            status = "✓" if arch_config.get('selected_by_user', False) else "✗"
            auto = " (auto-detect)" if config['settings']['auto_detect_architects'] else ""
            print(f"  {status} {name}{auto}")
        
        if config['settings']['auto_detect_architects']:
            detected = self.detect_technologies()
            if detected:
                print(f"\nAuto-Detected Technologies:")
                for tech in detected:
                    print(f"  🔍 {tech}")
        
        print("\nFinal Agent Sequence:")
        final_agents = self.get_final_agent_list()
        for i, agent in enumerate(final_agents, 1):
            print(f"  {i}. {agent}")
        
        print("\nExpected Documents:")
        for doc in config['expected_documents']:
            print(f"  📄 {doc}")
        
        print("=" * 60)

if __name__ == "__main__":
    # Test the agent selector
    selector = AgentSelector()
    
    try:
        selector.print_configuration()
        
        print("\n\nFinal agent list for n8n:")
        agents = selector.get_final_agent_list()
        print(json.dumps(agents, indent=2))
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run setup.py first to create the configuration")