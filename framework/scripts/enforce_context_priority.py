#!/usr/bin/env python3
"""
Ensure all agents prioritize loading context over scanning codebase
This minimizes token usage when running agents in separate windows
"""

import os
from pathlib import Path

# Template for context loading that should be in EVERY agent
CONTEXT_LOADING_TEMPLATE = '''
### Phase 0: MANDATORY Context Loading (Token Optimization)
```python
# CRITICAL: Always load existing context first to minimize token usage
import json
from pathlib import Path

def load_all_available_context():
    """Load context from all sources - MUST run before any analysis"""
    context = {}
    
    # Priority 1: Repomix summary (most efficient - 80% token reduction)
    repomix_files = [
        "output/reports/repomix-summary.md",
        "output/reports/repomix-analysis.md"
    ]
    for file in repomix_files:
        if Path(file).exists():
            context['repomix'] = Read(file)
            print(f"✅ Found Repomix summary - using compressed analysis")
            break
    
    # Priority 2: Architecture analysis context (shared by all architecture agents)
    arch_context = Path("output/context/architecture-analysis-summary.json")
    if arch_context.exists():
        with open(arch_context) as f:
            context['architecture'] = json.load(f)
            print(f"✅ Found architecture context - using existing analysis")
    
    # Priority 3: Load all other agent summaries
    context_dir = Path("output/context")
    if context_dir.exists():
        for summary_file in context_dir.glob("*-summary.json"):
            agent_name = summary_file.stem.replace('-summary', '')
            if agent_name not in ['architecture-analysis']:  # Skip already loaded
                try:
                    with open(summary_file) as f:
                        context[agent_name] = json.load(f)
                except:
                    pass
    
    # Priority 4: MCP memory (if available)
    try:
        memory_nodes = mcp__memory__open_nodes([
            "repomix_summary", 
            "architecture_context",
            "business_rules",
            "performance_analysis",
            "security_findings"
        ])
        if memory_nodes:
            context['memory'] = memory_nodes
            print("✅ Found MCP memory context")
    except:
        pass
    
    return context

# MANDATORY: Load context before ANY analysis
existing_context = load_all_available_context()

if not existing_context:
    print("⚠️ WARNING: No context found - will need to scan codebase (high token usage)")
    print("  Recommendation: Run repomix-analyzer and architecture agents first")
else:
    print(f"✅ Using existing context from {len(existing_context)} sources - minimal token usage")
    
    # Extract commonly needed data
    if 'architecture' in existing_context:
        tech_stack = existing_context['architecture'].get('data', {}).get('technology_stack', {})
        critical_files = existing_context['architecture'].get('data', {}).get('critical_files', [])
        known_issues = existing_context['architecture'].get('data', {}).get('issues_by_severity', {})
        print(f"  Found: {len(critical_files)} critical files, {len(known_issues)} issue categories")
```
'''

def check_agent_has_context_loading(agent_path):
    """Check if agent properly loads context"""
    with open(agent_path, 'r') as f:
        content = f.read()
    
    indicators = [
        "Phase 0: MANDATORY Context Loading",
        "load_all_available_context",
        "load_previous_context", 
        "load_security_context",
        "load_all_context"
    ]
    
    return any(indicator in content for indicator in indicators)

def add_context_loading_to_agent(agent_path):
    """Add context loading section if missing"""
    
    with open(agent_path, 'r') as f:
        content = f.read()
    
    if check_agent_has_context_loading(agent_path):
        return False
    
    # Find where to insert (after data integrity section, before first workflow phase)
    lines = content.split('\n')
    insert_position = -1
    
    for i, line in enumerate(lines):
        if '## Claude Code Optimized' in line or '## Analysis Workflow' in line or '### Phase 1:' in line:
            insert_position = i
            break
    
    if insert_position > 0:
        # Insert context loading before the workflow
        lines.insert(insert_position, CONTEXT_LOADING_TEMPLATE)
        lines.insert(insert_position, "## Context-First Analysis Workflow\n")
        
        with open(agent_path, 'w') as f:
            f.write('\n'.join(lines))
        
        return True
    
    return False

def main():
    """Update all agents to prioritize context loading"""
    
    agents_dir = Path('.claude/agents')
    
    if not agents_dir.exists():
        print("Error: .claude/agents directory not found")
        return
    
    # Agents that MUST load context first
    priority_agents = [
        'performance-analyst.md',
        'security-analyst.md',
        'business-logic-analyst.md',
        'diagram-architect.md',
        'documentation-specialist.md',
        'modernization-architect.md'
    ]
    
    updated = 0
    
    for agent_file in priority_agents:
        agent_path = agents_dir / agent_file
        if agent_path.exists():
            if check_agent_has_context_loading(agent_path):
                print(f"✓ {agent_file} - Already loads context properly")
            else:
                if add_context_loading_to_agent(agent_path):
                    print(f"✅ {agent_file} - Added context loading")
                    updated += 1
                else:
                    print(f"⚠️ {agent_file} - Could not add context loading")
    
    print(f"\n📊 Summary: Updated {updated} agents")
    print("✅ All agents now prioritize context over codebase scanning")
    print("\n💡 Best practice for multi-window usage:")
    print("  1. Run repomix-analyzer first (creates compressed summary)")
    print("  2. Run architecture-selector (determines needed agents)")
    print("  3. Run specialist architects (create shared context)")
    print("  4. Other agents use shared context (minimal tokens)")

if __name__ == "__main__":
    main()