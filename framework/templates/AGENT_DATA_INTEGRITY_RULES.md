# Agent Data Integrity Rules

## CRITICAL REQUIREMENT: Use Only Actual Data

**ALL AGENTS MUST FOLLOW THESE RULES:**

### 1. Data Sources (ONLY use these)
- **Actual codebase files** via Read, Grep, Glob tools
- **Repomix summary** from `output/reports/repomix-summary.md`
- **Previous agent outputs** from `output/context/*.json`
- **MCP tool results** (memory, filesystem, etc.)
- **Direct file examination** and pattern searching

### 2. PROHIBITED Actions
❌ **NEVER use hardcoded examples** like:
- Specific file names (e.g., "OrderService.java", "CustomerDAO.java")
- Specific version numbers (e.g., "Java 1.7", "Spring 3.2")
- Specific metrics (e.g., "2,847 lines", "45 complexity score")
- Specific vulnerabilities (e.g., "log4j 1.2.17 CVE-2021-44228")
- Specific performance numbers (e.g., "3.5s response time", "47 queries")

### 3. When Data Not Found
If you cannot find specific data, you MUST:
- State "Not detected in analysis"
- Or "Unable to determine from available data"
- Or "Requires runtime profiling/monitoring"
- Or "No data available in codebase"

### 4. Example Templates (Use These)

#### WRONG (Hardcoded):
```markdown
- Java 1.7 detected
- OrderService.java has 2,847 lines
- 75 business rules found
- Response time: 3.5 seconds
```

#### CORRECT (Data-driven):
```markdown
- Java version: {detected_from_pom_xml}
- Largest class: {actual_class_found} with {actual_line_count} lines
- Business rules found: {actual_count_from_analysis}
- Response time: {if_found_in_logs_else_"Not available"}
```

### 5. Validation Checklist
Before outputting any finding, ask yourself:
- [ ] Did I find this in the actual codebase?
- [ ] Can I trace this back to a specific file/search?
- [ ] Am I using placeholder data from examples?
- [ ] Is this from the repomix summary or previous agent?

### 6. Enforced Data Access Hierarchy
```python
# MANDATORY: Use this pattern for ALL data access
from data_access_utils import get_codebase_data

# This automatically follows:
# 1. Repomix (80% token reduction)
# 2. Serena MCP (60% token reduction)  
# 3. Raw codebase (last resort)
data = get_codebase_data(search_term="pattern")

# Track token usage
from token_monitor import track_tokens
track_tokens(agent_name, len(str(data))//4, 0, "Search", "repomix")
```

### 7. Required Data-Driven Implementation

**All agents MUST use the Data-Driven Template:**
- See `framework/templates/AGENT_DATA_DRIVEN_TEMPLATE.md`
- Import utilities: `data_access_utils.py` and `token_monitor.py`
- Never access `codebase/` directly without trying Repomix first
- Track all token usage with actual counts
- Report efficiency scores in context summaries

**Common Anti-Patterns to Avoid:**
- Using example class names from documentation
- Assuming version numbers without checking  
- Estimating metrics without measurement
- Using vulnerability databases without scanning
- Guessing performance numbers
- Skipping Repomix and going straight to raw files

## Enforcement & Monitoring

### Automatic Tracking
- All data access is logged to `output/reports/data-access-log.json`
- Token usage tracked in `output/reports/token-usage-log.json`
- Efficiency scores calculated automatically
- Alerts when >20% raw codebase access (inefficient)

### Validation
```python
def validate_data_driven_output(output):
    """Check if output uses actual data"""
    
    # Check for hardcoded examples
    forbidden_terms = [
        "OrderService.java", "CustomerDAO", "Java 1.7",
        "Spring 3.2", "2847 lines", "55 vulnerabilities"
    ]
    
    for term in forbidden_terms:
        if term in output:
            raise ValueError(f"Hardcoded example found: {term}")
    
    # Ensure data sources are documented
    if "Not detected" not in output and "actual" not in output.lower():
        print("Warning: Output may not be using actual data")
    
    return True
```

This is CRITICAL for accuracy. Every finding must be traceable to actual data sources with documented token efficiency.