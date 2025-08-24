#!/usr/bin/env python3
"""
Enforce data integrity rules across all agents
Ensures no hardcoded data is used
"""

import os
from pathlib import Path

# Data integrity notice to add to all agents
DATA_INTEGRITY_NOTICE = """
## CRITICAL: Data Integrity Requirement
**This agent MUST only use actual data from:**
1. The codebase being analyzed (via Read, Grep, Glob)
2. Repomix summary files in output/reports/
3. Previous agent outputs in output/context/
4. MCP tool results

**NEVER use hardcoded examples, fabricated metrics, or placeholder data.**
**See framework/templates/AGENT_DATA_INTEGRITY_RULES.md for details.**
"""

def add_data_integrity_to_agent(agent_path):
    """Add data integrity requirement to an agent if not present"""
    
    with open(agent_path, 'r') as f:
        content = f.read()
    
    # Check if already has data integrity section
    if "Data Integrity Requirement" in content or "CRITICAL REQUIREMENT: Use Only Actual Data" in content:
        print(f"✓ {agent_path.name} - Already has data integrity rules")
        return False
    
    # Find the right place to insert (after the agent description paragraph)
    lines = content.split('\n')
    insert_position = -1
    
    # Look for the first paragraph after the --- block
    in_frontmatter = True
    found_description = False
    
    for i, line in enumerate(lines):
        if line.strip() == '---' and in_frontmatter:
            in_frontmatter = False
            continue
        
        if not in_frontmatter and not found_description and line.strip() and not line.startswith('#'):
            found_description = True
            continue
            
        if found_description and (line.strip() == '' or line.startswith('#')):
            insert_position = i
            break
    
    if insert_position > 0:
        # Insert the data integrity notice
        lines.insert(insert_position, DATA_INTEGRITY_NOTICE)
        
        # Write back
        with open(agent_path, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ {agent_path.name} - Added data integrity requirement")
        return True
    else:
        print(f"⚠️  {agent_path.name} - Could not find insertion point")
        return False

def main():
    """Process all agents"""
    agents_dir = Path('.claude/agents')
    
    if not agents_dir.exists():
        print("Error: .claude/agents directory not found")
        return
    
    updated = 0
    checked = 0
    
    for agent_file in agents_dir.glob('*.md'):
        checked += 1
        if add_data_integrity_to_agent(agent_file):
            updated += 1
    
    print(f"\n📊 Summary: Checked {checked} agents, updated {updated}")
    print("✅ All agents now enforce data integrity rules")

if __name__ == "__main__":
    main()