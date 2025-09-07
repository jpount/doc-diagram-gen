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
        "SYSTEM-ARCHITECTURE.md": ["architecture-selector", "legacy-code-detective"],
        "TECHNICAL-DEBT-REPORT.md": ["legacy-code-detective"],
        "API-DOCUMENTATION.md": ["ui-analysis-specialist", "data-model-specialist"],
        "BUSINESS-RULES-CATALOG.md": ["business-logic-analyst"],
        "SECURITY-ANALYSIS.md": ["security-analyst"],
        "PERFORMANCE-ANALYSIS.md": ["performance-analyst"],
        "DATABASE-SCHEMA.md": ["data-model-specialist"],
        "DEVELOPER-GUIDE.md": ["legacy-code-detective"],
        "CONFIGURATION-GUIDE.md": ["legacy-code-detective"],
        "DEPLOYMENT-GUIDE.md": ["legacy-code-detective"],
        "TESTING-GUIDE.md": ["legacy-code-detective"],
        "TROUBLESHOOTING-GUIDE.md": ["legacy-code-detective"],
        # Modernization documents
        "MIGRATION-ROADMAP.md": ["modernization-architect", "domain-boundary-analyst"],
        "LEGACY-SYSTEM-ANALYSIS.md": ["legacy-code-detective"],
        "TRANSFORMATION-STRATEGY.md": ["modernization-architect"],
        "TECHNOLOGY-MIGRATION-GUIDE.md": ["modernization-architect"]
    }
    
    # Always run these agents first (discovery phase)
    REQUIRED_DISCOVERY_AGENTS = [
        "mcp-orchestrator",      # Token optimization
        "repomix-analyzer",       # Compressed codebase analysis
        "architecture-selector"   # Technology detection
    ]
    
    # Always run these agents last (documentation phase)
    REQUIRED_FINAL_AGENTS = [
        "diagram-architect",          # Visual documentation
        "documentation-specialist",   # Generate selected documents
        "executive-summary"           # Executive overview
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
            "legacy-code-detective",
            "java-architect",
            "dotnet-architect", 
            "angular-architect",
            "business-logic-analyst",
            "ui-analysis-specialist",
            "data-model-specialist",
            "domain-boundary-analyst",
            "security-analyst",
            "performance-analyst",
            "modernization-architect"
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
            ["business-logic-analyst", "security-analyst", "performance-analyst"],
            ["ui-analysis-specialist", "data-model-specialist"]
        ]
    
    def get_workflow_config(self, workflow_type: str = "quick_analysis") -> Dict:
        """Get complete workflow configuration based on document selection"""
        agents = self.get_required_agents()
        
        # Filter agents based on workflow type
        if workflow_type == "quick_analysis":
            # Quick analysis - only essential agents
            essential = self.REQUIRED_DISCOVERY_AGENTS.copy()
            
            # Add only the most important analysis agents
            if "business-logic-analyst" in agents:
                essential.append("business-logic-analyst")
            if "legacy-code-detective" in agents:
                essential.append("legacy-code-detective")
            
            # Always add diagram and documentation
            essential.extend(["diagram-architect", "documentation-specialist"])
            
            agents = essential
            parallel_groups = []  # No parallel for quick analysis
            
        elif workflow_type == "comprehensive":
            # Use full agent list with parallel execution
            parallel_groups = self.get_parallel_groups()
            
        elif workflow_type == "security_focus":
            # Security-focused workflow
            agents = self.REQUIRED_DISCOVERY_AGENTS + ["security-analyst"] + self.REQUIRED_FINAL_AGENTS
            parallel_groups = []
            
        elif workflow_type == "performance_focus":
            # Performance-focused workflow
            agents = self.REQUIRED_DISCOVERY_AGENTS + ["performance-analyst"] + self.REQUIRED_FINAL_AGENTS
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
            "architecture-selector": "Detect technologies and recommend specialists",
            "legacy-code-detective": "Deep dive into codebase structure",
            "java-architect": "Java/Spring/J2EE specific analysis",
            "dotnet-architect": ".NET/C#/ASP.NET specific analysis",
            "angular-architect": "Angular/AngularJS specific analysis",
            "business-logic-analyst": "Extract business rules and logic",
            "security-analyst": "Security vulnerabilities and compliance",
            "performance-analyst": "Performance bottlenecks and optimization",
            "ui-analysis-specialist": "Frontend technology and UI/UX analysis",
            "data-model-specialist": "Database and data architecture analysis",
            "domain-boundary-analyst": "Domain boundaries for modernization",
            "modernization-architect": "Migration strategy and roadmap",
            "diagram-architect": "Create visual documentation",
            "documentation-specialist": "Generate comprehensive documentation",
            "executive-summary": "High-level summary for stakeholders"
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