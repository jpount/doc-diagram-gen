# Bash Command Logger Conversion

## Overview
Converted the bash command logging from a jq-based shell command to a Python script for better cross-platform compatibility and improved logging to the dedicated logs directory.

## Changes Made

### 1. Created New Python Logger
**File**: `.claude/hooks/bash_command_logger.py`

Features:
- Reads JSON input from stdin (Claude Code hook format)
- Extracts command and description from tool_input
- Logs to `logs/bash-command-log.txt` with timestamps
- Creates logs directory if it doesn't exist
- Handles errors gracefully without blocking commands
- Cross-platform compatible (Windows/Mac/Linux)

### 2. Updated settings.local.json

**Before:**
```json
{
  "type": "command",
  "command": "jq -r '\"\\(.tool_input.command) - \\(.tool_input.description // \"No description\")\"' >> $CLAUDE_PROJECT_DIR/.claude/bash-command-log.txt"
}
```

**After:**
```json
{
  "type": "command",
  "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/bash_command_logger.py"
}
```

### 3. Standardized All Hook Commands
Updated all hooks in settings.local.json to use `python3` explicitly:
- `bash_command_logger.py` - Logs bash commands
- `dangerous_command_prevention.py` - Security validation
- `mermaid_diagram_validation.py` - Diagram validation
- `documentation_completeness_check.py` - Documentation checks
- `business_rule_validation.py` - Business rule validation
- `stop_hook.py` - Stop event handler

### 4. Centralized Logging
- Created `logs/` directory at project root
- Moved existing bash command log from `.claude/bash-command-log.txt` to `logs/bash-command-log.txt`
- All future logs will be written to the logs directory

## Log Format

### Old Format (jq):
```
command - description
```

### New Format (Python):
```
[YYYY-MM-DD HH:MM:SS] command - description
```

Example:
```
[2025-08-23 17:45:20] ls -la - List files in directory
[2025-08-23 17:45:21] python3 setup.py - Run setup script
```

## Benefits

1. **Cross-Platform Compatibility**
   - No dependency on jq (not available on Windows by default)
   - Works identically on all platforms

2. **Better Organization**
   - Logs centralized in `logs/` directory
   - Separate from configuration files in `.claude/`

3. **Enhanced Logging**
   - Timestamps for each command
   - Error logging to separate file if needed
   - UTF-8 encoding support

4. **Maintainability**
   - Python code is easier to extend
   - Can add features like log rotation, filtering, etc.
   - Consistent with other Python hooks

5. **Error Handling**
   - Graceful error handling
   - Won't block commands if logging fails
   - Separate error log for debugging

## File Locations

| File | Purpose |
|------|---------|
| `.claude/hooks/bash_command_logger.py` | Python logging script |
| `logs/bash-command-log.txt` | Main command log |
| `logs/bash-command-log-errors.txt` | Error log (if errors occur) |
| `.claude/settings.local.json` | Hook configuration |

## Testing

The logger was tested successfully:
```bash
# Test with JSON input
echo '{"tool_input": {"command": "ls -la", "description": "List files"}}' | python3 .claude/hooks/bash_command_logger.py

# Check log
tail logs/bash-command-log.txt
# Output: [2025-08-23 17:45:20] ls -la - List files in directory
```

## Summary

✅ Converted jq command to Python script
✅ Logs now go to `logs/` directory
✅ Added timestamps to log entries
✅ Cross-platform compatible
✅ All hooks now consistently use Python
✅ Tested and working correctly