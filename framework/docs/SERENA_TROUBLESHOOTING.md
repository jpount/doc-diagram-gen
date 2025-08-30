# Serena MCP Troubleshooting Guide

## Overview
Serena MCP provides semantic code analysis and memory sharing capabilities for the framework, offering 60% token reduction through intelligent caching and search. This guide helps resolve common issues.

## Quick Status Check

Run the validation test to check Serena status:
```bash
python3 framework/scripts/test_serena_integration.py
```

## Common Issues and Solutions

### 1. Serena is Disabled in Configuration

**Symptom:** 
- Agents can't access `mcp__serena__` tools
- Log shows "Serena is disabled in configuration"

**Solution:**
Edit `.mcp.json` and change:
```json
"serena": {
  ...
  "disabled": true,  // Remove this line or set to false
  ...
}
```

Then restart Claude Code.

### 2. Project Path Not Found

**Symptom:**
- Log shows: "Project path /path/to/codebase/daytrader does not exist"

**Solution:**
1. Check your codebase directory exists:
   ```bash
   ls -la codebase/
   ```

2. Update `.mcp.json` with correct path:
   ```json
   "args": [
     ...
     "--project",
     "${PWD}/codebase/your-actual-project"  // Update this
   ]
   ```

### 3. Java Language Server Errors

**Symptom:**
- Log shows: "Cannot run program '/usr/libexec/java_home': error=0, posix_spawn failed"
- Java-specific features don't work

**Impact:** 
- ✅ Memory operations still work
- ✅ Pattern search still works
- ❌ Java symbol analysis doesn't work

**Solutions:**

**Option A: Fix Java (if needed for Java projects)**
```bash
# Install Java on macOS
brew install openjdk@21

# Link Java
sudo ln -sfn $(brew --prefix)/opt/openjdk@21/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-21.jdk
```

**Option B: Disable Java language server (recommended for non-Java projects)**
Edit `~/.serena/serena_config.yml`:
```yaml
language_server:
  enabled: false  # Disable language server
```

### 4. Serena Not Installed

**Symptom:**
- "Serena not installed or not accessible"

**Solution:**
```bash
# Install uv first
pip install uv

# Test Serena installation
uvx --from git+https://github.com/oraios/serena serena --version
```

### 5. Memory Operations Not Working

**Symptom:**
- `mcp__serena__write_memory()` fails
- `mcp__serena__read_memory()` returns nothing

**Solution:**
1. Check Serena data directory:
   ```bash
   ls -la ~/.serena/
   ```

2. If missing, create it:
   ```bash
   mkdir -p ~/.serena/memories
   ```

3. Check permissions:
   ```bash
   chmod 755 ~/.serena
   chmod 755 ~/.serena/memories
   ```

### 6. Serena Server Won't Start

**Symptom:**
- MCP server fails to initialize
- Claude Code shows Serena as unavailable

**Solution:**
1. Check for port conflicts:
   ```bash
   lsof -i :24282  # Default Serena dashboard port
   ```

2. Kill any existing Serena processes:
   ```bash
   pkill -f serena
   ```

3. Clear Serena cache:
   ```bash
   rm -rf ~/.serena/language_servers/static/EclipseJDTLS/workspaces/*
   ```

4. Restart Claude Code

### 7. Token Reduction Not Working

**Symptom:**
- Agents still using high token counts despite Serena being enabled

**Diagnosis:**
Check if agents are using Serena properly:
```bash
# Check data access log
cat output/reports/data-access-log.json | grep fallback_level
```

**Solution:**
Ensure agents are using the data access hierarchy:
1. First check for Repomix summary
2. Then try Serena MCP
3. Only use raw codebase as last resort

## Verifying Serena is Working

### Test 1: Check MCP Tools in Claude Code
In Claude Code chat, type:
```
What MCP tools are available?
```

You should see tools like:
- `mcp__serena__write_memory`
- `mcp__serena__read_memory`
- `mcp__serena__list_memories`
- `mcp__serena__search_for_pattern`

### Test 2: Memory Test
In Claude Code, try:
```python
# Write test memory
mcp__serena__write_memory("test", {"status": "working"})

# Read it back
mcp__serena__read_memory("test")
```

### Test 3: Search Test
```python
# Search for patterns
mcp__serena__search_for_pattern("class.*Service")
```

## Performance Tips

### 1. Optimize Memory Usage
- Clear old memories periodically:
  ```bash
  rm -rf ~/.serena/memories/old_project_*
  ```

### 2. Reduce Language Server Load
- For non-Java projects, disable the Java language server
- Limit project scope to specific directories

### 3. Use Selective Activation
- Only activate Serena for projects that need it
- Disable in `.mcp.json` when not needed

## Integration with Framework

### Agent Usage Pattern
Agents should follow this hierarchy:
```python
# 1. Try Repomix first (80% reduction)
if repomix_exists:
    data = read_repomix_summary()

# 2. Try Serena (60% reduction)  
elif serena_available:
    data = mcp__serena__search_for_pattern()

# 3. Raw codebase (last resort)
else:
    data = Read("codebase/file.java")
```

### Memory Sharing Between Agents
```python
# Agent 1 writes findings
mcp__serena__write_memory("tech_stack", {
    "languages": ["Java", "JavaScript"],
    "frameworks": ["Spring", "React"]
})

# Agent 2 reads findings
stack = mcp__serena__read_memory("tech_stack")
```

## Monitoring and Logs

### Serena Logs Location
```bash
# Today's logs
ls ~/.serena/logs/$(date +%Y-%m-%d)/

# View latest log
tail -f ~/.serena/logs/$(date +%Y-%m-%d)/mcp_*.txt
```

### Framework Integration Logs
```bash
# Data access patterns
cat output/reports/data-access-log.json

# Token usage
cat output/reports/token-usage-log.json
```

## When to Use Serena vs Repomix

| Feature | Repomix | Serena |
|---------|---------|--------|
| Token Reduction | 80% | 60% |
| Setup Required | Generate summary | Auto-indexes |
| Best For | Initial analysis | Symbol search |
| Memory Sharing | No | Yes |
| Pattern Search | Limited | Advanced |
| Language Support | All | Best for Java |

## Getting Help

1. **Run validation test:**
   ```bash
   python3 framework/scripts/test_serena_integration.py
   ```

2. **Check MCP integration:**
   ```bash
   python3 framework/scripts/test_mcp_integration.py
   ```

3. **View Serena dashboard:**
   Open http://127.0.0.1:24282/dashboard/index.html when Serena is running

4. **Report issues:**
   - Framework issues: Create issue in framework repo
   - Serena issues: https://github.com/oraios/serena/issues

## Summary

Serena provides valuable token reduction and memory sharing capabilities. While Java language server issues are common on macOS, they don't affect the core memory and search features that the framework needs. 

For best results:
1. Use Repomix as primary (80% reduction)
2. Use Serena as fallback (60% reduction)
3. Only access raw codebase when necessary

The framework will work with or without Serena, but having it enabled provides better token efficiency and agent coordination through shared memory.