#!/usr/bin/env python3
"""
Dynamic CLAUDE.md Generator
Reads available agents from filesystem and generates CLAUDE.md with actual agent list
"""

import os
import json
from pathlib import Path
from datetime import datetime

def get_available_agents(agents_dir):
    """Get list of available agents from .claude/agents/"""
    available_agents = []
    
    if agents_dir.exists():
        agent_files = list(agents_dir.glob("*.md"))
        for agent_file in agent_files:
            if agent_file.name != ".DS_Store":
                agent_name = agent_file.stem
                # Read agent description from file
                try:
                    with open(agent_file, 'r') as f:
                        lines = f.readlines()
                        description = "No description available"
                        for line in lines:
                            if line.startswith('description:'):
                                description = line.split('description:')[1].strip()
                                break
                        available_agents.append({
                            'name': agent_name,
                            'description': description
                        })
                except Exception as e:
                    available_agents.append({
                        'name': agent_name,
                        'description': "No description available"
                    })
    
    return sorted(available_agents, key=lambda x: x['name'])

def generate_claude_md(project_name="daytrader"):
    """Generate CLAUDE.md with dynamic agent list"""
    
    script_dir = Path(__file__).parent.parent.parent
    agents_dir = script_dir / ".claude" / "agents"
    
    # Get available agents
    agents = get_available_agents(agents_dir)
    
    # Generate agent list dynamically
    agent_list = ""
    agent_sequence = ""
    
    if agents:
        # Always show repomix-analyzer first if available
        repomix_agent = next((agent for agent in agents if agent['name'] == 'repomix-analyzer'), None)
        if repomix_agent:
            agent_list += f"- `@{repomix_agent['name']}` - {repomix_agent['description']} (ALWAYS FIRST)\n"
            agent_sequence += f"@{repomix_agent['name']}\n\n"
            agents.remove(repomix_agent)
        
        # Add remaining agents
        for i, agent in enumerate(agents, 2):
            agent_list += f"- `@{agent['name']}` - {agent['description']}\n"
            agent_sequence += f"# {i}. Technology-specific analysis\n@{agent['name']}\n\n"
    else:
        agent_list = "- No agents found in .claude/agents/\n"
        agent_sequence = "# No agents available\n"
    
    # Generate CLAUDE.md content
    content = f"""# Project Configuration for Claude Code

## Project Overview
- **Project Name:** {project_name}  
- **Framework Mode:** Simplified Documentation & Diagram Generation
- **Codebase Location:** codebase/{project_name}
- **Framework Version:** 2.1 (Simplified)

## Core Workflow

### 🔴 STEP 1: Generate Repomix Summary (REQUIRED)
```bash
# Generate compressed codebase summary (80% token reduction)
repomix --config .repomix.config.json codebase/{project_name}/

# Verify output exists
ls -la output/reports/repomix-summary.md
```

### ⚡ STEP 2: Run Analysis Agents in Sequence
```bash
# 1. Process Repomix summary
{agent_sequence.strip()}
```

## Available Agents

### Current Agents ({len(agents) + (1 if repomix_agent else 0)} Available)
{agent_list}

## Agent Data Flow Rules

### 🔴 CRITICAL: All Agents Must Follow This Priority
1. **PRIMARY**: Read `output/reports/repomix-summary.md` (compressed codebase)
2. **SECONDARY**: Read `output/context/*.json` (previous agent outputs) 
3. **FALLBACK**: Access raw codebase only if needed

### Critical Rules for ALL Agents
⚠️ **SEE**: `framework/templates/CRITICAL_RULES.md` for complete rules

**Key requirements:**
- NO hardcoded data or fabricated metrics
- NO Serena MCP tools - use JSON context files only
- ALL Mermaid diagrams MUST validate with zero errors before completion
- State "Not detected" for missing information

### Required Agent Outputs
Each agent MUST produce:
- `output/context/{{agent-name}}-summary.json` - Context for next agents
- `output/docs/{{number}}-{{agent-name}}.md` - Documentation 
- `output/diagrams/{{agent-name}}-*.mmd` - Diagrams (if applicable)

## Output Locations
- **Documentation:** `output/docs/`
- **Diagrams:** `output/diagrams/`
- **Context Summaries:** `output/context/` 
- **Reports:** `output/reports/`

## Token Optimization Strategy
- **Repomix Summary:** ~50,000 tokens (80% reduction from raw codebase)
- **Context Chain:** Agents read previous summaries for efficiency
- **Raw Access:** Only when compressed data insufficient

## Troubleshooting

### Missing Repomix Summary
```bash
# Generate Repomix summary first
repomix --config .repomix.config.json codebase/{project_name}/

# Verify output exists
ls -la output/reports/repomix-summary.md
```

### Agent Context Issues
```bash
# Check context files exist
ls -la output/context/

# Agents should read previous contexts before accessing raw code
```

## Quick Start
1. Generate Repomix: `repomix --config .repomix.config.json codebase/{project_name}/`
2. Run agents in sequence: {' → '.join([f'`@{agent["name"]}`' for agent in ([repomix_agent] if repomix_agent else []) + agents])}
3. Review outputs in `output/docs/` and `output/diagrams/`

---
*Generated dynamically on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    return content

def main():
    """Main entry point"""
    import sys
    
    script_dir = Path(__file__).parent.parent.parent
    claude_file = script_dir / "CLAUDE.md"
    
    # Get project name from command line or existing file
    project_name = "daytrader"  # default
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
    elif claude_file.exists():
        try:
            with open(claude_file, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if '**Project Name:**' in line:
                        project_name = line.split('**Project Name:**')[1].strip()
                        break
        except:
            pass
    
    # Generate new CLAUDE.md content
    new_content = generate_claude_md(project_name)
    
    # Write to CLAUDE.md
    with open(claude_file, 'w') as f:
        f.write(new_content)
    
    print(f"✓ Generated CLAUDE.md with dynamic agent list")
    print(f"  Project: {project_name}")
    
    # List detected agents
    agents_dir = script_dir / ".claude" / "agents"
    agents = get_available_agents(agents_dir)
    print(f"  Agents: {len(agents)} detected")
    for agent in agents:
        print(f"    - @{agent['name']}")

if __name__ == "__main__":
    main()