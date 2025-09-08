#!/usr/bin/env python3
"""
Simplified Context Management
Single context file that agents append to, rather than multiple files
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

class SimplifiedContext:
    """Manages a single, cumulative context file for all agents"""
    
    def __init__(self, project_root: Path = Path(".")):
        self.project_root = Path(project_root)
        self.context_file = self.project_root / "output" / "context" / "analysis_context.json"
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize or load existing context
        if self.context_file.exists():
            self.load_context()
        else:
            self.initialize_context()
    
    def initialize_context(self):
        """Initialize a new context file"""
        self.context = {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started": datetime.now().isoformat(),
            "project_info": {},
            "tech_stack": [],
            "agents_completed": [],
            "findings": {},
            "recommendations": {},
            "metrics": {
                "total_tokens": 0,
                "total_time": 0
            }
        }
        self.save_context()
    
    def load_context(self):
        """Load existing context"""
        with open(self.context_file, 'r') as f:
            self.context = json.load(f)
    
    def save_context(self):
        """Save context to file"""
        with open(self.context_file, 'w') as f:
            json.dump(self.context, f, indent=2)
    
    def add_agent_findings(self, agent_name: str, findings: Dict[str, Any]):
        """Add findings from an agent"""
        # Mark agent as completed
        if agent_name not in self.context["agents_completed"]:
            self.context["agents_completed"].append(agent_name)
        
        # Add findings
        self.context["findings"][agent_name] = {
            "timestamp": datetime.now().isoformat(),
            "data": findings
        }
        
        # Update metrics if provided
        if "token_usage" in findings:
            self.context["metrics"]["total_tokens"] += findings["token_usage"].get("total", 0)
        
        self.save_context()
    
    def get_previous_findings(self, agent_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get findings from previous agents"""
        if agent_names is None:
            return self.context["findings"]
        
        return {
            agent: self.context["findings"].get(agent, {})
            for agent in agent_names
            if agent in self.context["findings"]
        }
    
    def update_tech_stack(self, technologies: List[str]):
        """Update detected technology stack"""
        for tech in technologies:
            if tech not in self.context["tech_stack"]:
                self.context["tech_stack"].append(tech)
        self.save_context()
    
    def add_recommendations(self, agent_name: str, recommendations: Dict[str, List[str]]):
        """Add recommendations from an agent"""
        self.context["recommendations"][agent_name] = recommendations
        self.save_context()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis"""
        return {
            "session_id": self.context["session_id"],
            "agents_completed": self.context["agents_completed"],
            "tech_stack": self.context["tech_stack"],
            "total_findings": len(self.context["findings"]),
            "total_tokens": self.context["metrics"]["total_tokens"]
        }


# Agent-specific helper functions

def architect_agent_update(context: SimplifiedContext, analysis_results: Dict):
    """Update context with architect agent findings"""
    findings = {
        "architecture_type": analysis_results.get("architecture_type", "unknown"),
        "components": analysis_results.get("components", []),
        "layers": analysis_results.get("layers", []),
        "dependencies": analysis_results.get("dependencies", []),
        "integration_points": analysis_results.get("integration_points", []),
        "token_usage": analysis_results.get("token_usage", {})
    }
    
    context.add_agent_findings("architect-agent", findings)
    
    # Update tech stack if detected
    if "technologies" in analysis_results:
        context.update_tech_stack(analysis_results["technologies"])
    
    # Add recommendations for next agents
    recommendations = {
        "developer-agent": ["Focus on " + c for c in analysis_results.get("problem_components", [])],
        "analyst-agent": ["Analyze " + s for s in analysis_results.get("critical_services", [])]
    }
    context.add_recommendations("architect-agent", recommendations)


def developer_agent_update(context: SimplifiedContext, analysis_results: Dict):
    """Update context with developer agent findings"""
    findings = {
        "code_quality_score": analysis_results.get("quality_score", 0),
        "technical_debt_items": analysis_results.get("debt_items", []),
        "anti_patterns": analysis_results.get("anti_patterns", []),
        "refactoring_suggestions": analysis_results.get("suggestions", []),
        "test_coverage": analysis_results.get("test_coverage", "unknown"),
        "token_usage": analysis_results.get("token_usage", {})
    }
    
    context.add_agent_findings("developer-agent", findings)


def analyst_agent_update(context: SimplifiedContext, analysis_results: Dict):
    """Update context with analyst agent findings"""
    findings = {
        "business_rules": analysis_results.get("business_rules", []),
        "performance_issues": analysis_results.get("performance_issues", []),
        "security_vulnerabilities": analysis_results.get("security_issues", []),
        "data_flows": analysis_results.get("data_flows", []),
        "domain_model": analysis_results.get("domain_model", {}),
        "token_usage": analysis_results.get("token_usage", {})
    }
    
    context.add_agent_findings("analyst-agent", findings)
    
    # Add visualization recommendations
    recommendations = {
        "diagram-agent": [
            "Create sequence diagram for: " + f for f in analysis_results.get("critical_flows", [])
        ]
    }
    context.add_recommendations("analyst-agent", recommendations)


def diagram_agent_update(context: SimplifiedContext, diagrams_created: List[str]):
    """Update context with diagram agent output"""
    findings = {
        "diagrams_created": diagrams_created,
        "diagram_types": [d.split("_")[0] for d in diagrams_created],
        "output_location": "output/diagrams/"
    }
    
    context.add_agent_findings("diagram-agent", findings)


def doc_writer_agent_update(context: SimplifiedContext, documents_created: List[str]):
    """Update context with documentation writer output"""
    findings = {
        "documents_created": documents_created,
        "output_location": "output/docs/",
        "summary": "Documentation generation complete"
    }
    
    context.add_agent_findings("doc-writer-agent", findings)


# Example usage for agents
if __name__ == "__main__":
    # Example of how agents would use this
    context = SimplifiedContext()
    
    # Architect agent example
    architect_results = {
        "architecture_type": "microservices",
        "components": ["api-gateway", "user-service", "order-service"],
        "technologies": ["Java", "Spring Boot", "PostgreSQL"],
        "problem_components": ["order-service"],
        "critical_services": ["payment-processor"],
        "token_usage": {"total": 15000}
    }
    architect_agent_update(context, architect_results)
    
    # Get context for next agent
    previous = context.get_previous_findings(["architect-agent"])
    print(json.dumps(previous, indent=2))
    
    # Get summary
    summary = context.get_summary()
    print(json.dumps(summary, indent=2))