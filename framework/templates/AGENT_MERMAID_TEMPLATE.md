# Universal Agent Template for Mermaid Diagram Generation

## CRITICAL: All Agents MUST Follow This Template

**This applies to ALL agents that might create diagrams**, including but not limited to:
- performance-analyst
- security-analyst  
- business-logic-analyst
- diagram-architect
- modernization-architect
- legacy-code-detective
- java-architect / dotnet-architect / angular-architect
- executive-summary
- ANY custom agents

## Required Integration for ALL Agents

### 1. Import Validation at Agent Start

```python
# At the very beginning of your agent code
import sys
from pathlib import Path

# Add framework scripts to path
framework_scripts = Path(__file__).parent.parent / 'framework' / 'scripts'
sys.path.insert(0, str(framework_scripts))

# Import validation helpers
from mermaid_agent_helper import (
    validate_before_write,
    validate_after_write,
    validate_all_outputs,
    create_diagram
)
```

### 2. ALWAYS Validate Before Writing ANY File

```python
# For ANY Write operation that might contain diagrams
def safe_write(filepath: str, content: str):
    """Safe write that validates Mermaid diagrams"""
    # Stage 1: Pre-validate and fix
    fixed_content = validate_before_write(content, filepath)
    
    # Write the fixed content
    Write(filepath, fixed_content)
    
    # Stage 2: Post-validate to ensure success
    validate_after_write(filepath)
    
    return True

# Use safe_write instead of Write
safe_write("output/docs/analysis.md", analysis_content)
safe_write("output/context/summary.md", summary_content)
safe_write("output/diagrams/architecture.mmd", diagram_content)
```

### 3. Creating New Diagrams Safely

```python
# Method 1: Create validated diagram from components
def create_performance_heatmap():
    diagram = create_diagram('graph', '''
        subgraph "Performance Heat Map"
            A[Component A<br/>🟢 50ms] --> B[Component B<br/>🔴 2000ms]
            B --> C[Component C<br/>🟡 500ms]
        end
    ''', wrap_markdown=True)
    return diagram

# Method 2: Validate existing diagram content
def fix_existing_diagram(diagram_content: str) -> str:
    # This will fix common issues
    fixed = create_diagram('auto', diagram_content, wrap_markdown=False)
    return fixed
```

### 4. Final Validation at Agent End

```python
# At the END of EVERY agent
def finalize_agent():
    """Final validation checkpoint"""
    print("\n🔍 Running final Mermaid validation...")
    
    valid, total = validate_all_outputs()
    
    if valid == total:
        print(f"✅ All {total} files with diagrams are valid!")
    else:
        print(f"⚠️ {total - valid}/{total} files may still have issues")
        # Note: The validator already attempted fixes
    
    return valid == total

# Call this before agent exits
finalize_agent()
```

## Common Patterns for Different Agent Types

### Performance/Security/Business Analysis Agents

```python
def generate_analysis():
    content = f"""
# Analysis Report

## Key Findings
{findings}

## Visualization
{create_diagram('graph', '''
    A[Start] --> B{Analysis}
    B -->|Finding 1| C[Impact High]
    B -->|Finding 2| D[Impact Low]
''', wrap_markdown=True)}

## Recommendations
{recommendations}
"""
    
    # ALWAYS use safe_write
    safe_write("output/docs/analysis.md", content)
```

### Architecture/Diagram Agents

```python
def create_architecture_diagram():
    # Build diagram with validation
    diagram_content = create_diagram('graph', '''
        subgraph "System Architecture"
            FE[Frontend] --> API[API Gateway]
            API --> SVC1[Service 1]
            API --> SVC2[Service 2]
            SVC1 --> DB[(Database)]
            SVC2 --> DB
        end
    ''', wrap_markdown=False)
    
    # Save with validation
    safe_write("output/diagrams/architecture.mmd", diagram_content)
```

### Summary/Report Agents

```python
def create_summary():
    summary = f"""
# Executive Summary

## Process Flow
{create_diagram('sequence', '''
    participant User
    participant System
    participant Database
    
    User->>System: Request
    System->>Database: Query
    Database-->>System: Data
    System-->>User: Response
''', wrap_markdown=True)}

## Next Steps
...
"""
    
    safe_write("output/context/summary.md", summary)
```

## Universal Rules ALL Agents Must Follow

### 1. File Writing Rules
- **NEVER** use raw `Write()` for .md or .mmd files
- **ALWAYS** use `safe_write()` or validate before/after
- **ALWAYS** run final validation at agent end

### 2. Diagram Creation Rules
- **ALWAYS** use `create_diagram()` for new diagrams
- **NEVER** manually construct diagram syntax without validation
- **ALWAYS** specify diagram type (graph, sequence, class, etc.)

### 3. Common Fixes Applied Automatically

| Issue | Auto-Fix |
|-------|----------|
| `\\<br/\\>` | `<br/>` |
| Multiple arrows `---->` | `-->` |
| Spaces in arrows `-- >` | `-->` |
| Unquoted participants | Adds quotes |
| Indented comments | Removes indentation |
| @ in stereotypes | Removes @ |
| Missing diagram type | Adds based on content |
| Spaces in node IDs | Replaces with underscores |
| Missing `end` for subgraph | Adds missing ends |

## Testing Your Agent's Diagrams

```python
# Add this test function to your agent
def test_agent_diagrams():
    """Test all diagrams created by this agent"""
    import subprocess
    
    # Run comprehensive test
    result = subprocess.run(
        ['python3', 'framework/scripts/test_all_mermaid_final.py', '--dir', 'output'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    return result.returncode == 0

# Run test after agent completes
if not test_agent_diagrams():
    print("⚠️ Some diagrams may have issues - check test report")
```

## Emergency Fallback

If validation modules are not available:

```python
def fallback_fix_diagram(content: str) -> str:
    """Basic fixes if validation modules unavailable"""
    import re
    
    # Apply essential fixes
    content = re.sub(r'\\<br/\\>', '<br/>', content)
    content = re.sub(r'--+>', '-->', content)
    content = re.sub(r'--\s+>', '-->', content)
    content = re.sub(r'^\s+%%', '%%', content, flags=re.MULTILINE)
    content = re.sub(r'<<@(\w+)>>', r'<<\1>>', content)
    
    return content

# Use in emergency
try:
    from mermaid_agent_helper import validate_before_write
except ImportError:
    print("Warning: Using fallback validation")
    validate_before_write = fallback_fix_diagram
```

## Compliance Checklist

Every agent must:
- [ ] Import validation helpers
- [ ] Use `safe_write()` or validate before/after Write
- [ ] Use `create_diagram()` for new diagrams  
- [ ] Run `validate_all_outputs()` at end
- [ ] Test with document-viewer.html
- [ ] Handle validation errors gracefully

## Remember

**ANY agent that writes ANY file that MIGHT contain Mermaid MUST use validation.**

This includes:
- Analysis reports (.md files)
- Context summaries (.md files)
- Standalone diagrams (.mmd files)
- Documentation (.md files)
- ANY markdown file that could have ```mermaid blocks

**No exceptions!**