# Testing Reference Card

## 🔐 Backup Information
**Backup Created:** 2025-08-23 18:46:08  
**Backup Location:** `backup_20250823_184608/`  
**Restore Script:** `backup_20250823_184608/restore.py`

## 🧪 Quick Test Commands

### 1. Test Framework Health
```bash
python3 framework/scripts/test_framework.py
```
Expected: 37/37 tests passing

### 2. Test MCP Integration
```bash
python3 framework/scripts/test_mcp_integration.py
```

### 3. Test Agent Orchestration
```bash
python3 framework/scripts/agent_orchestrator.py workflow
```

### 4. Test Setup Scripts
```bash
# Test MCP setup (interactive)
python3 framework/scripts/setup_mcp.py

# Test tech stack setup
python3 framework/scripts/setup_tech_stack.py --preset cloud-native
```

### 5. Test Notifications
```bash
# Test terminal notification
python3 .claude/hooks/notifications.py "Test message" --method terminal

# Test all notification methods
python3 .claude/hooks/notifications.py "Test complete" --method all
```

### 6. Test Mermaid Validation
```bash
python3 framework/scripts/validate_mermaid.py --output-dir output/docs
```

## 🔄 If Something Breaks

### Quick Restore Everything
```bash
cd backup_20250823_184608
python3 restore.py --component all
```

### Restore Specific Components
```bash
# Just framework
python3 backup_20250823_184608/restore.py --component framework

# Just hooks and agents
python3 backup_20250823_184608/restore.py --component claude

# Just configuration files
python3 backup_20250823_184608/restore.py --component config
```

### Manual Restore
```bash
# Restore framework
cp -r backup_20250823_184608/framework/* framework/

# Restore Claude configuration
cp -r backup_20250823_184608/.claude/* .claude/

# Restore MCP config
cp backup_20250823_184608/.mcp.json .mcp.json
```

## ✅ Testing Checklist

### Framework Structure
- [ ] All directories exist
- [ ] All Python scripts executable
- [ ] No shell scripts in hooks

### MCP Configuration
- [ ] .mcp.json uses `${PWD}/codebase` (not hardcoded)
- [ ] Repomix config generates correctly
- [ ] Can switch between all repos and specific repo

### Notifications
- [ ] Stop hook triggers notification
- [ ] User prompt hook triggers notification
- [ ] Logs written to `logs/notifications.log`

### Multi-Repository Support
- [ ] Can configure for all repositories
- [ ] Can configure for specific repository
- [ ] Repomix creates single combined file

### Documentation Generation
- [ ] Agents can be invoked
- [ ] Validation hooks run on file write
- [ ] Output goes to correct directories

## 📊 Current State Summary

### What's Changed
1. **All scripts are Python** - No shell scripts in hooks
2. **No hardcoded repos** - Uses `${PWD}/codebase`
3. **Generic notifications** - Single notifications.py for all hooks
4. **Organized framework** - All framework files in framework/
5. **Multi-repo support** - Can analyze multiple repositories

### Configuration
- **MCP Path:** `${PWD}/codebase` (all repos)
- **Hooks:** 6 Python hooks
- **Agents:** 10 specialized agents
- **Scripts:** 11 Python scripts

## 🚨 Important Notes

1. **Restart Claude Code** after changing .mcp.json
2. **Backup is timestamped** - Don't delete until testing complete
3. **Output directory** not backed up (it's generated content)
4. **Codebase directory** not backed up (it's your test data)

## 📝 Test Log

Use this space to track your tests:

- [ ] Framework test: ___________
- [ ] MCP test: ___________
- [ ] Notification test: ___________
- [ ] Agent test: ___________
- [ ] Setup script test: ___________

---
**Remember:** Your backup is safe in `backup_20250823_184608/` - you can always restore!