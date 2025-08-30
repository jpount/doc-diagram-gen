# Agent Data Access Pattern - Enforced Fallback Hierarchy

## CRITICAL: Data Access Priority Order

All agents MUST follow this strict hierarchy when accessing codebase data:

1. **Repomix Summary** (Primary - 80% token reduction)
2. **Serena MCP** (Secondary - 60% token reduction)  
3. **Raw Codebase** (Last Resort - 0% token reduction)

## Implementation Pattern

### Standard Data Access Function

```python
def get_codebase_data(pattern=None, file_path=None, search_term=None):
    """
    Universal data access function with enforced fallback hierarchy.
    
    PRIORITY ORDER:
    1. Repomix summary (if available)
    2. Serena MCP (if available and Repomix insufficient)
    3. Raw codebase (only if both above fail)
    """
    from pathlib import Path
    
    # ============================
    # LEVEL 1: Try Repomix First
    # ============================
    repomix_sources = [
        "output/reports/repomix-summary.md",
        "output/reports/repomix-analysis.md",
        "codebase/repomix-output.md"
    ]
    
    for repomix_file in repomix_sources:
        if Path(repomix_file).exists():
            print(f"✅ Using Repomix summary: {repomix_file}")
            content = Read(repomix_file)
            
            # If searching for specific content
            if search_term:
                if search_term.lower() in content.lower():
                    return extract_relevant_section(content, search_term)
            
            # If looking for specific file
            if file_path and file_path in content:
                return extract_file_content(content, file_path)
            
            # If pattern matching
            if pattern and matches_pattern(content, pattern):
                return extract_pattern_matches(content, pattern)
            
            # Return full Repomix if no specific search
            if not search_term and not file_path and not pattern:
                return content
    
    # ============================
    # LEVEL 2: Fallback to Serena
    # ============================
    try:
        print("⚠️ Repomix not sufficient, trying Serena MCP...")
        
        # Ensure Serena is activated
        if not hasattr(get_codebase_data, '_serena_activated'):
            try:
                mcp__serena__activate_project("codebase")
                mcp__serena__onboarding()
                get_codebase_data._serena_activated = True
            except:
                print("❌ Serena activation failed")
        
        # Use Serena for targeted search
        if search_term:
            results = mcp__serena__search_for_pattern(search_term)
            if results:
                print(f"✅ Found via Serena: {len(results)} matches")
                return results
        
        if file_path:
            symbols = mcp__serena__find_symbol(file_path)
            if symbols:
                print(f"✅ Found via Serena: {file_path}")
                return symbols
        
        if pattern:
            matches = mcp__serena__search_for_pattern(pattern)
            if matches:
                print(f"✅ Found via Serena: {len(matches)} pattern matches")
                return matches
                
    except Exception as e:
        print(f"❌ Serena MCP not available: {e}")
    
    # ============================
    # LEVEL 3: Last Resort - Raw Codebase
    # ============================
    print("⚠️ WARNING: Falling back to raw codebase access (high token usage)")
    print("Consider generating Repomix summary first: repomix --config .repomix.config.json")
    
    # Log this fallback for monitoring
    log_fallback_usage("raw_codebase", pattern or file_path or search_term)
    
    if file_path:
        return Read(file_path)
    
    if pattern:
        files = Glob(f"codebase/**/{pattern}")
        return files
    
    if search_term:
        results = Grep(search_term, path="codebase")
        return results
    
    # Should never reach here without parameters
    raise ValueError("No search parameters provided")
```

### Helper Functions

```python
def extract_relevant_section(content, search_term):
    """Extract relevant section from Repomix content"""
    lines = content.split('\n')
    relevant_lines = []
    context_size = 50  # Lines before/after match
    
    for i, line in enumerate(lines):
        if search_term.lower() in line.lower():
            start = max(0, i - context_size)
            end = min(len(lines), i + context_size)
            relevant_lines.extend(lines[start:end])
    
    return '\n'.join(relevant_lines)

def extract_file_content(repomix_content, file_path):
    """Extract specific file content from Repomix summary"""
    import re
    
    # Repomix uses markdown code blocks with file paths
    pattern = f"```.*{file_path}.*?\n(.*?)```"
    matches = re.findall(pattern, repomix_content, re.DOTALL)
    
    if matches:
        return '\n'.join(matches)
    return None

def matches_pattern(content, pattern):
    """Check if content matches pattern"""
    import re
    return bool(re.search(pattern, content, re.IGNORECASE))

def extract_pattern_matches(content, pattern):
    """Extract all pattern matches from content"""
    import re
    return re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)

def log_fallback_usage(level, query):
    """Log when fallback to raw codebase occurs"""
    from datetime import datetime
    import json
    from pathlib import Path
    
    log_file = Path("output/reports/data-access-log.json")
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "fallback_level": level,
        "query": str(query),
        "agent": "current_agent_name"  # Replace with actual agent
    }
    
    # Append to log
    logs = []
    if log_file.exists():
        with open(log_file) as f:
            logs = json.load(f)
    
    logs.append(log_entry)
    
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    # Alert if too many raw accesses
    raw_count = sum(1 for log in logs if log['fallback_level'] == 'raw_codebase')
    if raw_count > 10:
        print(f"⚠️ WARNING: {raw_count} raw codebase accesses - consider regenerating Repomix")
```

## Usage Examples

### Example 1: Finding Technology Stack

```python
# This will automatically try Repomix first, then Serena, then raw
tech_data = get_codebase_data(search_term="springframework")
```

### Example 2: Reading Specific File

```python
# Will extract from Repomix if available, avoiding full file read
pom_content = get_codebase_data(file_path="pom.xml")
```

### Example 3: Pattern Search

```python
# Searches efficiently through compressed data first
sql_queries = get_codebase_data(pattern=r"SELECT.*FROM.*WHERE")
```

## Integration Instructions

### For Agent Updates

Replace direct codebase access patterns:

```python
# OLD - Direct raw access
content = Read("codebase/src/main/java/Service.java")
files = Glob("codebase/**/*.java")
results = Grep("pattern", path="codebase")

# NEW - Use fallback hierarchy
content = get_codebase_data(file_path="src/main/java/Service.java")
files = get_codebase_data(pattern="*.java")
results = get_codebase_data(search_term="pattern")
```

## Monitoring & Optimization

### Check Data Access Efficiency

```python
def analyze_data_access_efficiency():
    """Analyze how often we're falling back to raw access"""
    from pathlib import Path
    import json
    
    log_file = Path("output/reports/data-access-log.json")
    if not log_file.exists():
        print("No data access log found")
        return
    
    with open(log_file) as f:
        logs = json.load(f)
    
    total = len(logs)
    by_level = {}
    for log in logs:
        level = log['fallback_level']
        by_level[level] = by_level.get(level, 0) + 1
    
    print(f"Data Access Statistics ({total} total accesses):")
    print(f"  Repomix: {by_level.get('repomix', 0)} ({by_level.get('repomix', 0)*100/total:.1f}%)")
    print(f"  Serena: {by_level.get('serena', 0)} ({by_level.get('serena', 0)*100/total:.1f}%)")
    print(f"  Raw: {by_level.get('raw_codebase', 0)} ({by_level.get('raw_codebase', 0)*100/total:.1f}%)")
    
    if by_level.get('raw_codebase', 0) > total * 0.2:
        print("\n⚠️ WARNING: Over 20% raw access - regenerate Repomix summary!")
```

## Best Practices

1. **Always Generate Repomix First**
   ```bash
   repomix --config .repomix.config.json codebase/
   ```

2. **Check Repomix Completeness**
   - Ensure Repomix includes all relevant files
   - Verify security scan results are included
   - Check token metrics are captured

3. **Configure Serena Properly**
   - Activate project at agent start
   - Use onboarding for initial indexing
   - Write findings to memory for other agents

4. **Monitor Fallback Usage**
   - Review data-access-log.json regularly
   - Regenerate Repomix if too many raw accesses
   - Optimize search patterns for better Repomix utilization

## Enforcement

All agents MUST:
1. Import and use `get_codebase_data()` function
2. Never directly access `codebase/` without trying Repomix first
3. Log any raw codebase access for monitoring
4. Alert user when falling back to raw access

This pattern ensures maximum token efficiency while maintaining data accuracy.