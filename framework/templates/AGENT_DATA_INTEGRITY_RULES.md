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

### 6. Data Flow Pattern
```
1. Check repomix summary first (most efficient)
2. Check previous agent context files
3. Use Grep/Glob to find patterns
4. Use Read to examine specific files
5. If not found, report "Not detected"
```

### 7. Common Anti-Patterns to Avoid
- Using example class names from documentation
- Assuming version numbers without checking
- Estimating metrics without measurement
- Using vulnerability databases without scanning
- Guessing performance numbers

## Enforcement
This is CRITICAL for accuracy. Agents that use hardcoded data will produce incorrect analysis and misleading recommendations. Every finding must be traceable to actual data sources.