#!/usr/bin/env python3
"""
Token Tracking Hook for Claude Code
Automatically tracks token usage during agent execution
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Add framework scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "framework" / "scripts"))

try:
    from token_monitor import track_tokens, estimate_tokens, get_token_summary
except ImportError:
    print("Warning: Token monitor not available")
    sys.exit(0)

def extract_agent_name(context):
    """Extract agent name from execution context"""
    # Try to get from environment or context
    # This would need to be adapted based on how Claude Code passes context
    return context.get("agent", "unknown")

def estimate_from_tool_use(tool_name, args):
    """Estimate tokens based on tool usage"""
    estimates = {
        "Read": 500,  # Average file read
        "Write": 200,  # Average file write
        "Grep": 300,  # Search operation
        "Glob": 100,  # File listing
        "Bash": 150,  # Command execution
        "mcp__serena": 200,  # MCP call
        "WebSearch": 1000,  # Web content
    }
    
    base_estimate = estimates.get(tool_name, 100)
    
    # Adjust based on arguments
    if "content" in args:
        base_estimate += estimate_tokens(args["content"])
    if "file_path" in args and "repomix" in str(args.get("file_path", "")).lower():
        # Repomix files are large but efficient
        base_estimate = base_estimate * 0.2
    
    return int(base_estimate)

def determine_data_source(tool_name, args):
    """Determine data source from tool usage"""
    if "repomix" in str(args).lower():
        return "repomix"
    elif tool_name.startswith("mcp__serena"):
        return "serena"
    elif "codebase/" in str(args):
        return "raw"
    else:
        return ""

def main():
    """Main hook execution"""
    # Read hook context (this would be provided by Claude Code)
    context = {}
    try:
        # Claude Code might pass context via stdin or environment
        if not sys.stdin.isatty():
            context = json.loads(sys.stdin.read())
    except:
        pass
    
    # Get current agent
    agent = extract_agent_name(context)
    
    # Check for tool usage patterns in recent output
    if "tool_use" in context:
        tool = context["tool_use"]
        tool_name = tool.get("name", "")
        tool_args = tool.get("args", {})
        
        # Estimate tokens
        input_tokens = estimate_from_tool_use(tool_name, tool_args)
        output_tokens = int(input_tokens * 0.3)  # Rough estimate
        
        # Determine source
        data_source = determine_data_source(tool_name, tool_args)
        
        # Track usage
        track_tokens(
            agent=agent,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            phase=f"Tool: {tool_name}",
            data_source=data_source
        )
        
        # Alert if using raw codebase
        if data_source == "raw":
            print(f"⚠️ Raw codebase access detected in {tool_name}")
            print("   Consider using Repomix for better efficiency")
    
    # Periodic summary (every 10 operations)
    summary = get_token_summary()
    if summary and "overall" in summary:
        total = summary["overall"]["total_tokens"]
        if total > 0 and total % 10000 < 1000:  # Every 10k tokens
            efficiency = summary["overall"]["efficiency_score"]
            budget_used = summary["overall"]["budget_used"]
            print(f"\n📊 Token Update: {total:,} used ({budget_used}), Efficiency: {efficiency}%")

if __name__ == "__main__":
    main()