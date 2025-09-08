#!/usr/bin/env python3
"""
Agent-based selection for setup.py
"""

import json
from pathlib import Path
from typing import Dict, List

class Colors:
    """Console colors for better readability"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def configure_agent_selection(framework_dir: Path, modernization_enabled: bool = False):
    """Configure which agents should run"""
    print()
    print(f"{Colors.MAGENTA}Step 1c: Select Analysis Agents{Colors.RESET}")
    print("-" * 40)
    
    # Load agent configuration
    agent_config_file = framework_dir / "configs" / "agent-config.json"
    
    if not agent_config_file.exists():
        print(f"{Colors.YELLOW}⚠ Agent configuration file not found{Colors.RESET}")
        print(f"{Colors.BLUE}ℹ Using default agent selection{Colors.RESET}")
        return create_default_selection()
    
    with open(agent_config_file, 'r') as f:
        agent_config = json.load(f)['agent_configuration']
    
    print(f"{Colors.CYAN}Select which analysis agents to run:{Colors.RESET}")
    print()
    
    # Mandatory agents (always shown as selected)
    print(f"{Colors.GREEN}Mandatory Agents (Always Run):{Colors.RESET}")
    print("  [✓] mcp-orchestrator - Token optimization")
    print("  [✓] repomix-analyzer - Compressed codebase analysis")
    print("  [✓] diagram-architect - Visual documentation")
    print()
    
    # Analysis agents by category
    selected_agents = []
    all_agents = {}
    
    # Architecture Analysis
    print(f"{Colors.BLUE}Architecture Analysis:{Colors.RESET}")
    print("  [1] legacy-code-detective - Deep codebase analysis (Recommended)")
    print("      → Generates: System Architecture, Technical Debt Report")
    all_agents['1'] = 'legacy-code-detective'
    
    # Business Logic
    print()
    print(f"{Colors.BLUE}Business Logic:{Colors.RESET}")
    print("  [2] business-logic-analyst - Extract business rules")
    print("      → Generates: Business Rules Catalog")
    all_agents['2'] = 'business-logic-analyst'
    
    # Data & API
    print()
    print(f"{Colors.BLUE}Data & API Analysis:{Colors.RESET}")
    print("  [3] ui-analysis-specialist - Frontend and API analysis")
    print("      → Generates: API Documentation")
    print("  [4] data-model-specialist - Database schema analysis")
    print("      → Generates: Database Schema")
    all_agents['3'] = 'ui-analysis-specialist'
    all_agents['4'] = 'data-model-specialist'
    
    # Quality & Security
    print()
    print(f"{Colors.BLUE}Quality & Security:{Colors.RESET}")
    print("  [5] security-analyst - Security vulnerabilities")
    print("      → Generates: Security Analysis")
    print("  [6] performance-analyst - Performance bottlenecks")
    print("      → Generates: Performance Analysis")
    all_agents['5'] = 'security-analyst'
    all_agents['6'] = 'performance-analyst'
    
    # Technology Specific (Optional)
    print()
    print(f"{Colors.YELLOW}Technology-Specific Architects (Optional):{Colors.RESET}")
    print("  [7] java-architect - Java/Spring analysis")
    print("  [8] dotnet-architect - .NET/C# analysis")
    print("  [9] angular-architect - Angular analysis")
    all_agents['7'] = 'java-architect'
    all_agents['8'] = 'dotnet-architect'
    all_agents['9'] = 'angular-architect'
    
    # Modernization (if enabled)
    if modernization_enabled:
        print()
        print(f"{Colors.YELLOW}Modernization:{Colors.RESET}")
        print("  [10] modernization-architect - Migration strategy")
        print("       → Generates: Migration Roadmap")
        print("  [11] domain-boundary-analyst - Domain boundaries")
        print("       → Generates: Domain Boundaries")
        all_agents['10'] = 'modernization-architect'
        all_agents['11'] = 'domain-boundary-analyst'
    
    # Documentation Synthesis
    print()
    print(f"{Colors.MAGENTA}Documentation Synthesis:{Colors.RESET}")
    print("  [D] documentation-specialist - Generate consolidated documents")
    print("      → Synthesizes all findings into final documentation")
    print("  [E] executive-summary - High-level summary for stakeholders")
    all_agents['D'] = 'documentation-specialist'
    all_agents['E'] = 'executive-summary'
    
    print()
    print(f"{Colors.CYAN}Selection Options:{Colors.RESET}")
    print("1. Quick (Essential agents only: 1,2,3,5,6)")
    print("2. Standard (Recommended: 1,2,3,5,6,D)")
    print("3. Comprehensive (All analysis: 1,2,3,4,5,6,D,E)")
    print("4. Custom (Choose specific agents)")
    print("5. Minimal (Architecture only: 1)")
    print()
    
    while True:
        choice = input(f"Select option (1-5) [{Colors.GREEN}2{Colors.RESET}]: ").strip() or "2"
        if choice in ["1", "2", "3", "4", "5"]:
            break
        print(f"{Colors.RED}Invalid choice. Please enter 1-5.{Colors.RESET}")
    
    if choice == "1":  # Quick
        selected_agents = ['legacy-code-detective', 'business-logic-analyst', 
                          'ui-analysis-specialist', 'security-analyst', 'performance-analyst']
        print(f"{Colors.GREEN}✓ Quick analysis agents selected{Colors.RESET}")
    
    elif choice == "2":  # Standard (Recommended)
        selected_agents = ['legacy-code-detective', 'business-logic-analyst', 
                          'ui-analysis-specialist', 'security-analyst', 
                          'performance-analyst', 'documentation-specialist']
        print(f"{Colors.GREEN}✓ Standard analysis agents selected{Colors.RESET}")
    
    elif choice == "3":  # Comprehensive
        selected_agents = ['legacy-code-detective', 'business-logic-analyst', 
                          'ui-analysis-specialist', 'data-model-specialist',
                          'security-analyst', 'performance-analyst',
                          'documentation-specialist', 'executive-summary']
        print(f"{Colors.GREEN}✓ Comprehensive analysis agents selected{Colors.RESET}")
    
    elif choice == "4":  # Custom
        print()
        print(f"{Colors.CYAN}Enter agent numbers/letters separated by commas (e.g., 1,2,5,D):{Colors.RESET}")
        selections = input("Agents: ").strip().upper().split(',')
        
        for sel in selections:
            sel = sel.strip()
            if sel in all_agents:
                selected_agents.append(all_agents[sel])
        
        print(f"{Colors.GREEN}✓ Custom selection: {', '.join(selected_agents)}{Colors.RESET}")
    
    elif choice == "5":  # Minimal
        selected_agents = ['legacy-code-detective']
        print(f"{Colors.GREEN}✓ Minimal analysis agents selected{Colors.RESET}")
    
    # Ask about auto-detection
    print()
    print(f"{Colors.CYAN}Technology Auto-Detection:{Colors.RESET}")
    print("Should technology-specific architects (Java, .NET, Angular) be")
    print("automatically added if their technologies are detected?")
    print()
    
    auto_detect = input(f"Enable auto-detection? (y/n) [{Colors.YELLOW}n{Colors.RESET}]: ").strip().lower()
    auto_detect_enabled = auto_detect == 'y'
    
    if auto_detect_enabled:
        print(f"{Colors.GREEN}✓ Auto-detection enabled{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}✓ Auto-detection disabled (only selected agents will run){Colors.RESET}")
    
    # Create the configuration
    config = create_agent_configuration(selected_agents, auto_detect_enabled, modernization_enabled)
    
    # Show summary
    print()
    print(f"{Colors.MAGENTA}Selected Configuration:{Colors.RESET}")
    print(f"  Mandatory agents: 3 (always run)")
    print(f"  Selected agents: {len(selected_agents)}")
    print(f"  Auto-detection: {'Enabled' if auto_detect_enabled else 'Disabled'}")
    print(f"  Total agents: {3 + len(selected_agents)} (plus auto-detected if enabled)")
    
    return config

def create_agent_configuration(selected_agents: List[str], auto_detect: bool, modernization: bool) -> Dict:
    """Create the agent configuration for selected-agents.json"""
    
    # Technology architects configuration
    tech_architects = {
        "java-architect": {
            "enabled": "java-architect" in selected_agents,
            "auto_detect_condition": "*.java files present",
            "selected_by_user": "java-architect" in selected_agents
        },
        "dotnet-architect": {
            "enabled": "dotnet-architect" in selected_agents,
            "auto_detect_condition": "*.cs files present",
            "selected_by_user": "dotnet-architect" in selected_agents
        },
        "angular-architect": {
            "enabled": "angular-architect" in selected_agents,
            "auto_detect_condition": "angular.json or *.component.ts present",
            "selected_by_user": "angular-architect" in selected_agents
        }
    }
    
    # Remove tech architects from main list if present
    analysis_agents = [a for a in selected_agents 
                      if a not in ['java-architect', 'dotnet-architect', 'angular-architect',
                                  'documentation-specialist', 'executive-summary']]
    
    # Build complete sequence
    complete_sequence = ['mcp-orchestrator', 'repomix-analyzer']
    complete_sequence.extend(analysis_agents)
    complete_sequence.append('diagram-architect')
    
    # Add documentation agents if selected
    if 'documentation-specialist' in selected_agents:
        complete_sequence.append('documentation-specialist')
    if 'executive-summary' in selected_agents:
        complete_sequence.append('executive-summary')
    
    # Determine parallel groups based on selected agents
    parallel_groups = []
    parallel_candidates = ['business-logic-analyst', 'security-analyst', 'performance-analyst']
    parallel_group = [a for a in parallel_candidates if a in analysis_agents]
    if len(parallel_group) > 1:
        parallel_groups.append(parallel_group)
    
    config = {
        "description": "User-selected agents configuration (shared between manual and n8n modes)",
        "created": "2024-01-01T00:00:00Z",
        "mode": "SUPERVISED",
        "workflow_type": "custom",
        "settings": {
            "auto_detect_architects": auto_detect,
            "description": "If true, automatically add java-architect, dotnet-architect, or angular-architect based on detected technologies. If false, only run explicitly selected agents."
        },
        "mandatory_agents": {
            "description": "These agents ALWAYS run regardless of selection",
            "agents": [
                "mcp-orchestrator",
                "repomix-analyzer",
                "diagram-architect"
            ]
        },
        "selected_analysis_agents": {
            "description": "User-selected agents that contribute to documentation quality",
            "agents": analysis_agents
        },
        "technology_architects": {
            "description": "Technology-specific architects (only used if explicitly selected or auto-detection enabled)",
            "agents": tech_architects
        },
        "optional_agents": {
            "description": "Other agents that could be enabled",
            "agents": []
        },
        "complete_agent_sequence": complete_sequence,
        "documentation_synthesis": {
            "documentation_specialist": 'documentation-specialist' in selected_agents,
            "executive_summary": 'executive-summary' in selected_agents
        },
        "execution_settings": {
            "parallel_execution": len(parallel_groups) > 0,
            "parallel_groups": parallel_groups,
            "estimated_time_minutes": len(complete_sequence) * 15,
            "token_optimization": "repomix-first"
        }
    }
    
    return config

def create_default_selection() -> Dict:
    """Create a default selection if config file is missing"""
    return create_agent_configuration(
        ['legacy-code-detective', 'business-logic-analyst', 'ui-analysis-specialist', 
         'security-analyst', 'performance-analyst'],
        auto_detect=False,
        modernization=False
    )

if __name__ == "__main__":
    # Test the agent selection
    framework_dir = Path(__file__).parent.parent
    config = configure_agent_selection(framework_dir, modernization_enabled=False)
    
    # Save to file
    output_file = Path("output/context/selected-agents.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n{Colors.GREEN}✓ Configuration saved to {output_file}{Colors.RESET}")