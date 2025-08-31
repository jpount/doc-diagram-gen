# Testing Reference Guide

## 🧪 Quick Test Commands

### 1. Test Framework Health
```bash
python3 framework/scripts/test_framework.py
```
Verifies all framework components are in place and working.

### 2. Test MCP Integration
```bash
python3 framework/scripts/test_mcp_integration.py
```
Checks MCP configuration and availability.

### 3. Test Mermaid Validation System
```bash
# Validate all diagrams
python3 framework/scripts/smart_mermaid_validator.py output/

# Validate and auto-fix
python3 framework/scripts/smart_mermaid_validator.py output/ --fix

# Final comprehensive check
python3 framework/scripts/mermaid_final_check.py output/

# Test in browser
# Open framework/document-viewer.html in browser
# Load output/ directory to view all diagrams
```

### 4. Test Setup Scripts
```bash
# Test MCP setup
python3 framework/scripts/setup_mcp.py

# Test tech stack setup
python3 framework/scripts/setup_tech_stack.py --preset cloud-native
```

### 5. Test Agent Orchestration
```bash
# Show workflow
python3 framework/scripts/agent_orchestrator.py workflow

# In Claude Code, test agents:
@mcp-orchestrator
@repomix-analyzer
@architecture-selector
```

## ✅ Testing Checklist

### Framework Structure
- [ ] All directories exist (`framework/`, `.claude/`, `output/`, `codebase/`)
- [ ] All Python scripts are executable
- [ ] Configuration templates are in place

### MCP Configuration
- [ ] `.mcp.json` exists at root (git-ignored)
- [ ] Uses `${PWD}/codebase` path (not hardcoded)
- [ ] Repomix config generates correctly
- [ ] MCPs restart after configuration changes

### Mermaid Validation
- [ ] Smart validator fixes common errors
- [ ] Pre-write hook prevents broken diagrams
- [ ] Final check validates all output
- [ ] Document viewer renders diagrams correctly

### Documentation Generation
- [ ] Agents can be invoked in Claude Code
- [ ] Output goes to correct directories
- [ ] Context summaries are created
- [ ] Diagrams are valid Mermaid syntax

## 📊 Current System Status

### What's Working
1. **Smart Mermaid Validation** - 3-layer system with intelligent fixing
2. **Clean Structure** - Organized framework with clear separation
3. **Git-Ignored Configs** - Personal settings don't pollute repository
4. **Cross-Platform Support** - Python scripts work everywhere
5. **Browser Validation** - Visual verification with document-viewer.html

### Key Scripts
- `smart_mermaid_validator.py` - Main validation with error-based fixing
- `mermaid_pre_write_hook.py` - Pre-write validation
- `mermaid_final_check.py` - Final validation pass
- `test_mcp_integration.py` - MCP diagnostic
- `setup_mcp.py` - MCP configuration
- `agent_orchestrator.py` - Agent workflow

### Configuration Files (Git-Ignored)
- `.mcp.json` - MCP configuration
- `.repomix.config.json` - Repomix settings
- `CLAUDE.md` - Project configuration
- `ANALYSIS_MODE.md` - Analysis mode
- `DOCUMENTATION_MODE.md` - Documentation mode
- `TARGET_TECH_STACK.md` - Target technology

## 🔄 Common Issues & Solutions

### Mermaid Diagrams Not Rendering
```bash
# Auto-fix all diagrams
python3 framework/scripts/smart_mermaid_validator.py output/ --fix

# Check specific file
python3 framework/scripts/smart_mermaid_validator.py output/diagrams/example.mmd
```

### MCP Not Available
```bash
# Check configuration
cat .mcp.json

# Test integration
python3 framework/scripts/test_mcp_integration.py

# Restart Claude Code after changes
```

### Agents Not Working
```bash
# Check agent files exist
ls -la .claude/agents/

# In Claude Code:
# 1. Ensure .mcp.json is at root
# 2. Restart Claude Code
# 3. Try @mcp-orchestrator first
```

## 🚨 Important Notes

1. **Restart Claude Code** after changing `.mcp.json`
2. **Configuration files are git-ignored** - they're personal to each developer
3. **Output directory** contains generated content - can be deleted and regenerated
4. **Archive directory** contains old scripts - kept for reference only

## 📝 Test Results Log

Use this to track your testing:

- [ ] Framework test passed: ___________
- [ ] MCP integration working: ___________
- [ ] Mermaid validation working: ___________
- [ ] Agents responding: ___________
- [ ] Output generation successful: ___________

---

**Framework Version**: 2.1.0  
**Last Updated**: 2025-08-24  
**Status**: ✅ All Systems Operational