#!/usr/bin/env python3
"""
Fix context compatibility between specialist agents and downstream agents.
This script updates agents to ensure proper context passing.
"""

import os
import sys
from pathlib import Path

def add_context_writing_to_specialist(agent_file, agent_name):
    """Add context summary writing to specialist agents"""
    
    context_template = f'''
# Write context summary for downstream agents
context_summary = {{
    "agent": "{agent_name}",
    "timestamp": datetime.now().isoformat(),
    "token_usage": get_token_usage(),  # Track actual token usage
    "summary": {{
        "key_findings": key_findings,  # Add your findings
        "priority_items": priority_items,  # Add priority items
        "warnings": warnings,  # Add warnings
        "recommendations_for_next": {{
            "business-logic-analyst": business_recommendations,
            "performance-analyst": performance_recommendations,
            "security-analyst": security_recommendations,
            "diagram-architect": diagram_recommendations
        }}
    }},
    "data": {{
        "technology_stack": technology_stack,
        "critical_files": critical_files,
        "metrics": metrics
    }}
}}

# Write to both locations for compatibility
Write("output/context/{agent_name}-summary.json", json.dumps(context_summary, indent=2))
Write("output/context/architecture-analysis-summary.json", json.dumps(context_summary, indent=2))
'''
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Check if context writing already exists
    if "architecture-analysis-summary.json" in content:
        print(f"✓ {agent_name} already has context writing")
        return False
    
    # Find where to insert (before the final Write of main document)
    if "Write(\"output/docs/01-" in content:
        # Insert before the main document write
        insertion_point = content.rfind("Write(\"output/docs/01-")
        updated_content = content[:insertion_point] + context_template + "\n" + content[insertion_point:]
        
        with open(agent_file, 'w') as f:
            f.write(updated_content)
        print(f"✅ Updated {agent_name} with context writing")
        return True
    else:
        print(f"⚠️  Could not find insertion point in {agent_name}")
        return False

def update_downstream_context_loading(agent_file, agent_name):
    """Update downstream agents to load from multiple context sources"""
    
    improved_loader = '''
def load_previous_context():
    """Load context from any architecture agent with multiple fallbacks"""
    from pathlib import Path
    import json
    
    # Try unified context first (works with any architecture agent)
    unified_context = Path("output/context/architecture-analysis-summary.json")
    if unified_context.exists():
        with open(unified_context) as f:
            return json.load(f)
    
    # Fallback to legacy-code-detective for backward compatibility
    legacy_context = Path("output/context/legacy-code-detective-summary.json")
    if legacy_context.exists():
        with open(legacy_context) as f:
            return json.load(f)
    
    # Try any specialist agent context
    for agent in ["java-architect", "angular-architect", "dotnet-architect"]:
        context_file = Path(f"output/context/{agent}-summary.json")
        if context_file.exists():
            with open(context_file) as f:
                return json.load(f)
    
    # Fallback to Serena memory if available
    try:
        return mcp__serena__read_memory("architecture_context")
    except:
        print("Note: No architecture context found, proceeding with fresh analysis")
        return None
'''
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Check if already has improved loading
    if "architecture-analysis-summary.json" in content:
        print(f"✓ {agent_name} already has improved context loading")
        return False
    
    # Replace the old loader
    if "def load_previous_context():" in content:
        # Find and replace the function
        start = content.find("def load_previous_context():")
        if start != -1:
            # Find the end of the function (next def or class)
            end = content.find("\ndef ", start + 1)
            if end == -1:
                end = content.find("\nclass ", start + 1)
            if end == -1:
                end = len(content)
            
            updated_content = content[:start] + improved_loader + content[end:]
            
            with open(agent_file, 'w') as f:
                f.write(updated_content)
            print(f"✅ Updated {agent_name} with improved context loading")
            return True
    
    print(f"ℹ️  {agent_name} doesn't have context loading function")
    return False

def main():
    """Main function to update all agents"""
    
    # Get project root
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent
    agents_dir = project_root / ".claude" / "agents"
    
    print("🔧 Fixing Agent Context Compatibility\n")
    print("=" * 50)
    
    # Specialist agents that need context writing
    specialists = [
        "java-architect.md",
        "angular-architect.md",
        "dotnet-architect.md"
    ]
    
    # Downstream agents that need improved loading
    downstream = [
        "business-logic-analyst.md",
        "performance-analyst.md",
        "security-analyst.md",
        "diagram-architect.md",
        "documentation-specialist.md",
        "modernization-architect.md"
    ]
    
    print("\n📝 Updating Specialist Agents...")
    print("-" * 30)
    updated_count = 0
    for agent in specialists:
        agent_file = agents_dir / agent
        if agent_file.exists():
            if add_context_writing_to_specialist(agent_file, agent.replace(".md", "")):
                updated_count += 1
        else:
            print(f"⚠️  {agent} not found")
    
    print(f"\n📊 Updated {updated_count} specialist agents")
    
    print("\n📥 Updating Downstream Agents...")
    print("-" * 30)
    updated_count = 0
    for agent in downstream:
        agent_file = agents_dir / agent
        if agent_file.exists():
            if update_downstream_context_loading(agent_file, agent.replace(".md", "")):
                updated_count += 1
        else:
            print(f"⚠️  {agent} not found")
    
    print(f"\n📊 Updated {updated_count} downstream agents")
    
    print("\n✅ Context compatibility fix complete!")
    print("\nNext steps:")
    print("1. Review the updated agent files")
    print("2. Test with both legacy-code-detective and specialist workflows")
    print("3. Verify context is properly passed between agents")

if __name__ == "__main__":
    main()