#!/usr/bin/env python3
"""
Configuration Reader for n8n Workflows
Maps document selections to required agents
"""

import json
from pathlib import Path
from typing import List, Dict, Set

class N8nConfigReader:
    """
    Reads the documentation configuration and determines which agents to run
    based on user selections from setup.py
    """
    
    # Mapping of documents to their required agents
    DOCUMENT_TO_AGENTS = {
        "SYSTEM-ARCHITECTURE.md": ["architect-agent", "developer-agent"],
        "TECHNICAL-DEBT-REPORT.md": ["developer-agent"],
        "API-DOCUMENTATION.md": ["architect-agent", "architect-agent"],
        "BUSINESS-RULES-CATALOG.md": ["analyst-agent"],
        "SECURITY-ANALYSIS.md": ["analyst-agent"],
        "PERFORMANCE-ANALYSIS.md": ["analyst-agent"],
        "DATABASE-SCHEMA.md": ["architect-agent"],
        "DEVELOPER-GUIDE.md": ["developer-agent"],
        "CONFIGURATION-GUIDE.md": ["developer-agent"],
        "DEPLOYMENT-GUIDE.md": ["developer-agent"],
        "TESTING-GUIDE.md": ["developer-agent"],
        "TROUBLESHOOTING-GUIDE.md": ["developer-agent"],
        # Modernization documents
        "MIGRATION-ROADMAP.md": ["analyst-agent", "analyst-agent"],
        "LEGACY-SYSTEM-ANALYSIS.md": ["developer-agent"],
        "TRANSFORMATION-STRATEGY.md": ["analyst-agent"],
        "TECHNOLOGY-MIGRATION-GUIDE.md": ["analyst-agent"]
    }
    
    # Always run these agents first (discovery phase)
    REQUIRED_DISCOVERY_AGENTS = [
        "mcp-orchestrator",      # Token optimization
        "repomix-analyzer",       # Compressed codebase analysis
        "architect-agent"   # Technology detection
    ]
    
    # Always run these agents last (documentation phase)
    REQUIRED_FINAL_AGENTS = [
        "diagram-agent",          # Visual documentation
        "doc-writer-agent",   # Generate selected documents
        "doc-writer-agent"           # Executive overview
    ]
    
    def __init__(self, project_root: Path = Path(".")):
        self.project_root = Path(project_root)
        self.config_file = self.project_root / "framework" / "configs" / "documentation-config.json"
        self.user_config_file = self.project_root / "output" / "context" / "user-config.json"
        
    def read_documentation_config(self) -> Dict:
        """Read the documentation configuration file"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
            
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def read_user_config(self) -> Dict:
        """Read user-specific configuration if it exists"""
        if self.user_config_file.exists():
            with open(self.user_config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_enabled_documents(self) -> List[str]:
        """Get list of documents that are enabled"""
        config = self.read_documentation_config()
        user_config = self.read_user_config()
        
        enabled_docs = []
        
        # Check default documents
        for doc_name, doc_info in config['documentation']['default_documents'].items():
            # Check user override first, then default
            if user_config.get('documents', {}).get(doc_name, {}).get('enabled', doc_info['enabled']):
                enabled_docs.append(doc_name)
        
        # Check optional documents  
        for doc_name, doc_info in config['documentation']['optional_documents'].items():
            if user_config.get('documents', {}).get(doc_name, {}).get('enabled', doc_info['enabled']):
                enabled_docs.append(doc_name)
        
        # Check modernization documents if enabled
        if user_config.get('modernization_enabled', False):
            for doc_name, doc_info in config['documentation']['modernization_documents'].items():
                if doc_name != 'description':
                    if user_config.get('documents', {}).get(doc_name, {}).get('enabled', doc_info.get('enabled', False)):
                        enabled_docs.append(doc_name)
        
        return enabled_docs
    
    def get_required_agents(self) -> List[str]:
        """Get the complete list of agents to run based on enabled documents"""
        enabled_docs = self.get_enabled_documents()
        
        # Start with discovery agents
        agents = self.REQUIRED_DISCOVERY_AGENTS.copy()
        
        # Collect unique agents needed for enabled documents
        analysis_agents = set()
        for doc in enabled_docs:
            if doc in self.DOCUMENT_TO_AGENTS:
                for agent in self.DOCUMENT_TO_AGENTS[doc]:
                    analysis_agents.add(agent)
        
        # Add technology-specific architects based on architecture-selector results
        # This will be determined dynamically after architecture-selector runs
        
        # Add analysis agents in proper order
        agent_order = [
            "developer-agent",
            "java-architect",
            "dotnet-architect", 
            "angular-architect",
            "analyst-agent",
            "architect-agent",
            "architect-agent",
            "analyst-agent",
            "analyst-agent",
            "analyst-agent",
            "analyst-agent"
        ]
        
        for agent in agent_order:
            if agent in analysis_agents:
                agents.append(agent)
        
        # Add final agents
        agents.extend(self.REQUIRED_FINAL_AGENTS)
        
        return agents
    
    def get_parallel_groups(self) -> List[List[str]]:
        """Get groups of agents that can run in parallel"""
        # These agents can run in parallel as they don't depend on each other
        return [
            ["analyst-agent", "analyst-agent", "analyst-agent"],
            ["architect-agent", "architect-agent"]
        ]
    
    def get_workflow_config(self, workflow_type: str = "quick_analysis") -> Dict:
        """Get complete workflow configuration based on document selection"""
        agents = self.get_required_agents()
        
        # Filter agents based on workflow type
        if workflow_type == "quick_analysis":
            # Quick analysis - only essential agents
            essential = self.REQUIRED_DISCOVERY_AGENTS.copy()
            
            # Add only the most important analysis agents
            if "analyst-agent" in agents:
                essential.append("analyst-agent")
            if "developer-agent" in agents:
                essential.append("developer-agent")
            
            # Always add diagram and documentation
            essential.extend(["diagram-agent", "doc-writer-agent"])
            
            agents = essential
            parallel_groups = []  # No parallel for quick analysis
            
        elif workflow_type == "comprehensive":
            # Use full agent list with parallel execution
            parallel_groups = self.get_parallel_groups()
            
        elif workflow_type == "security_focus":
            # Security-focused workflow
            agents = self.REQUIRED_DISCOVERY_AGENTS + ["analyst-agent"] + self.REQUIRED_FINAL_AGENTS
            parallel_groups = []
            
        elif workflow_type == "performance_focus":
            # Performance-focused workflow
            agents = self.REQUIRED_DISCOVERY_AGENTS + ["analyst-agent"] + self.REQUIRED_FINAL_AGENTS
            parallel_groups = []
        
        else:
            # Default comprehensive
            parallel_groups = self.get_parallel_groups()
        
        return {
            "agents": agents,
            "parallel_groups": parallel_groups,
            "timeout": 7200 if workflow_type == "quick_analysis" else 14400,
            "checkpoints": [] if workflow_type == "quick_analysis" else ["discovery_review", "analysis_review"]
        }
    
    def save_user_config(self, config: Dict):
        """Save user configuration for n8n to use"""
        self.user_config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.user_config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_agent_description(self, agent_name: str) -> str:
        """Get description of what an agent does"""
        descriptions = {
            "mcp-orchestrator": "Optimize token usage with MCP tools",
            "repomix-analyzer": "Analyze compressed codebase summary",
            "architect-agent": "Detect technologies and recommend specialists",
            "developer-agent": "Deep dive into codebase structure",
            "java-architect": "Java/Spring/J2EE specific analysis",
            "dotnet-architect": ".NET/C#/ASP.NET specific analysis",
            "angular-architect": "Angular/AngularJS specific analysis",
            "analyst-agent": "Extract business rules and logic",
            "analyst-agent": "Security vulnerabilities and compliance",
            "analyst-agent": "Performance bottlenecks and optimization",
            "architect-agent": "Frontend technology and UI/UX analysis",
            "architect-agent": "Database and data architecture analysis",
            "analyst-agent": "Domain boundaries for modernization",
            "analyst-agent": "Migration strategy and roadmap",
            "diagram-agent": "Create visual documentation",
            "doc-writer-agent": "Generate comprehensive documentation",
            "doc-writer-agent": "High-level summary for stakeholders"
        }
        return descriptions.get(agent_name, f"Run {agent_name} agent")

if __name__ == "__main__":
    # Test the configuration reader
    reader = N8nConfigReader()
    
    print("Enabled Documents:")
    for doc in reader.get_enabled_documents():
        print(f"  - {doc}")
    
    print("\nRequired Agents:")
    for agent in reader.get_required_agents():
        print(f"  - {agent}: {reader.get_agent_description(agent)}")
    
    print("\nWorkflow Configurations:")
    for workflow_type in ["quick_analysis", "comprehensive", "security_focus"]:
        config = reader.get_workflow_config(workflow_type)
        print(f"\n{workflow_type}:")
        print(f"  Agents: {len(config['agents'])}")
        print(f"  Parallel groups: {len(config['parallel_groups'])}")
        print(f"  Timeout: {config['timeout']}s")