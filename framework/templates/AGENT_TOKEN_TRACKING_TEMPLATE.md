# Agent Token Tracking Template

## Token Usage Monitoring Integration

All agents should integrate token tracking to monitor efficiency and stay within budgets.

## Implementation Pattern

### Agent Header with Token Tracking

```python
# At the start of your agent execution
import sys
from pathlib import Path

# Add framework scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "framework" / "scripts"))

from token_monitor import (
    init_monitor, 
    track_tokens, 
    estimate_tokens,
    check_ccusage,
    display_token_report
)

# Initialize monitor for this agent
monitor = init_monitor(project_size="medium", model="claude-3-sonnet")
agent_name = "your-agent-name"
```

### Track Major Operations

```python
def analyze_codebase():
    """Example function with token tracking"""
    
    # Track data reads
    repomix_content = Read("output/reports/repomix-summary.md")
    track_tokens(
        agent=agent_name,
        input_tokens=estimate_tokens(repomix_content),
        output_tokens=0,
        phase="Loading Repomix",
        data_source="repomix"
    )
    
    # Track analysis operations
    analysis_start = check_ccusage(agent_name)  # Capture current usage
    
    # Do your analysis...
    results = perform_analysis(repomix_content)
    
    # Track output generation
    track_tokens(
        agent=agent_name,
        input_tokens=0,
        output_tokens=estimate_tokens(results),
        phase="Generating results",
        data_source="repomix"
    )
    
    return results
```

### Check Token Budget

```python
def check_budget_status():
    """Check if within token budget"""
    summary = get_token_summary()
    
    if summary and "overall" in summary:
        budget_used = summary["overall"]["budget_used"]
        remaining = summary["overall"]["budget_remaining"]
        
        # Parse percentage
        used_pct = float(budget_used.rstrip('%'))
        
        if used_pct > 90:
            print(f"⚠️ CRITICAL: {budget_used} of token budget used!")
            print(f"   Only {remaining:,} tokens remaining")
            # Consider early termination or optimization
            
        elif used_pct > 75:
            print(f"⚠️ WARNING: {budget_used} of budget used")
            # Switch to more aggressive optimization
```

## Token Tracking Best Practices

### 1. Track All Major Data Access

```python
# GOOD: Track each data access with source
content = get_codebase_data(search_term="pattern")
track_tokens(
    agent=agent_name,
    input_tokens=estimate_tokens(str(content)),
    output_tokens=0,
    phase="Pattern search",
    data_source="repomix"  # or "serena" or "raw"
)

# BAD: Access without tracking
content = Read("codebase/large_file.java")  # No tracking!
```

### 2. Use Efficiency Metrics

```python
def optimize_based_on_efficiency():
    """Adjust strategy based on efficiency"""
    summary = get_token_summary()
    efficiency = summary["overall"]["efficiency_score"]
    
    if efficiency < 50:  # Poor efficiency
        print("🔴 Poor token efficiency detected")
        print("Switching to Repomix-only mode...")
        # Only use Repomix data
        
    elif efficiency < 75:  # Moderate efficiency
        print("🟡 Moderate efficiency")
        # Limit Serena usage
        
    else:  # Good efficiency
        print("✅ Good token efficiency")
        # Continue normal operation
```

### 3. Report at Agent Completion

```python
def complete_agent_execution():
    """Final reporting at agent completion"""
    
    # Get final summary
    summary = get_token_summary()
    
    # Write to context for next agents
    context_summary = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "token_usage": {
            "input": summary["by_agent"][agent_name]["input"],
            "output": summary["by_agent"][agent_name]["output"],
            "total": summary["by_agent"][agent_name]["total"],
            "efficiency": summary["overall"]["efficiency_score"],
            "cost_usd": summary["by_agent"][agent_name]["cost"]
        }
    }
    
    Write(f"output/context/{agent_name}-summary.json", 
          json.dumps(context_summary, indent=2))
    
    # Display final report
    print("\n" + "="*50)
    print(f"Token Usage Report for {agent_name}")
    print("="*50)
    display_token_report()
```

## Command Line Usage

### Check Current Usage
```bash
python framework/scripts/token_monitor.py report
```

### Initialize for Large Project
```bash
python framework/scripts/token_monitor.py init large claude-3-opus
```

### Check ccusage Integration
```bash
python framework/scripts/token_monitor.py check
```

## Integration with Context Summaries

```python
# Include token metrics in context summary
context_summary = {
    "agent": agent_name,
    "timestamp": datetime.now().isoformat(),
    "token_usage": {
        "input": 28500,
        "output": 8200,
        "total": 36700,
        "efficiency_score": 85.5,
        "data_sources": {
            "repomix": 30000,
            "serena": 5000,
            "raw": 1700
        }
    },
    "summary": {
        # ... rest of summary
    }
}
```

## Monitoring Thresholds

### Token Budget Alerts

| Level | Threshold | Action |
|-------|-----------|--------|
| ✅ Green | <50% | Normal operation |
| 🟡 Yellow | 50-75% | Optimize data access |
| 🟠 Orange | 75-90% | Aggressive optimization |
| 🔴 Red | >90% | Critical - consider stopping |

### Efficiency Score Thresholds

| Score | Meaning | Action |
|-------|---------|--------|
| 80-100% | Excellent | Continue current approach |
| 60-79% | Good | Minor optimizations |
| 40-59% | Fair | Check Repomix completeness |
| 20-39% | Poor | Regenerate Repomix |
| <20% | Critical | Stop using raw access |

## Example: Complete Agent with Tracking

```python
---
name: example-agent
description: Example agent with full token tracking
tools: Read, Write, Glob, Grep
---

import json
from datetime import datetime
from pathlib import Path

# Import token monitoring
sys.path.insert(0, str(Path(__file__).parent.parent / "framework" / "scripts"))
from token_monitor import *
from data_access_utils import get_codebase_data

# Initialize
monitor = init_monitor("medium", "claude-3-sonnet")
agent_name = "example-agent"

def main():
    """Main agent execution with token tracking"""
    
    print(f"Starting {agent_name}...")
    
    # Phase 1: Load context (track tokens)
    print("Phase 1: Loading context...")
    context = load_previous_context()
    track_tokens(agent_name, estimate_tokens(str(context)), 0, 
                "Loading context", "repomix")
    
    # Check budget before proceeding
    check_budget_status()
    
    # Phase 2: Analysis (with efficiency check)
    print("Phase 2: Analyzing...")
    data = get_codebase_data(search_term="business_logic")
    track_tokens(agent_name, estimate_tokens(str(data)), 0,
                "Business logic search", determine_source(data))
    
    # Check efficiency
    summary = get_token_summary()
    if summary["overall"]["efficiency_score"] < 50:
        print("⚠️ Low efficiency - optimizing approach...")
        # Switch to Repomix-only mode
    
    # Phase 3: Generate output
    print("Phase 3: Generating output...")
    output = generate_analysis(data)
    track_tokens(agent_name, 0, estimate_tokens(output),
                "Output generation", "")
    
    # Save output
    Write("output/docs/analysis.md", output)
    
    # Final report
    complete_agent_execution()
    
    print(f"✅ {agent_name} completed successfully")

def determine_source(data):
    """Determine data source from response"""
    if "repomix" in str(data).lower():
        return "repomix"
    elif hasattr(data, '__module__') and 'serena' in str(data.__module__):
        return "serena"
    else:
        return "raw"

# Execute
if __name__ == "__main__":
    main()
```

## Quick Reference

```python
# Import
from token_monitor import *

# Initialize (once per agent)
monitor = init_monitor("medium", "claude-3-sonnet")

# Track tokens
track_tokens(agent, input, output, phase, source)

# Estimate from text
tokens = estimate_tokens(text)

# Check ccusage
usage = check_ccusage(agent)

# Get summary
summary = get_token_summary()

# Display report
display_token_report()
```

This template ensures consistent token tracking across all agents for optimal efficiency.