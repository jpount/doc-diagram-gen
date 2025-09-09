# Documentation & Diagram Generation Framework - Context Prompt

## 🎯 Repository Purpose

This is a **sophisticated documentation and diagram generation framework** that analyzes any codebase and produces comprehensive technical documentation with visual diagrams. The framework supports both **manual Claude Code execution** and **automated n8n workflow execution** without breaking either approach.

## 🚨 CRITICAL OPERATIONAL RULES - NEVER VIOLATE THESE

### 1. 🛡️ DO NOT BREAK ANYTHING
- **NEVER break the manual flow** - it must continue working in Claude Code
- **NEVER break the n8n automated workflows** - they run in production  
- **NEVER change core framework files** without understanding dependencies
- **ALWAYS test changes** before considering them complete
- **PRESERVE existing functionality** while adding enhancements

### 2. 📊 DO NOT FABRICATE DATA - ONLY USE ACTUAL COLLECTED DATA
**NEVER MAKE UP ANY OF THE FOLLOWING:**
- ❌ Specific dollar amounts ($1,000, $50.00, €100)
- ❌ Specific dates (2025-01-09, January 15, 2024, March 2023)
- ❌ Specific percentages (80%, 40-60%, 25.5%)
- ❌ Specific timings (200ms, 5 seconds, 10 minutes)  
- ❌ Specific file sizes (578KB, 2.8MB, 1.2GB)
- ❌ Specific counts (1000 users, 50 classes, 247 methods)
- ❌ Specific performance metrics not found in actual code
- ❌ Specific version numbers not in the actual codebase
- ❌ Specific server configurations not in actual config files

**ONLY USE ACTUAL DATA FROM:**
- ✅ **Codebase files** (via Read, Grep, Glob tools)
- ✅ **Repomix summaries** in `output/reports/repomix-summary.md`
- ✅ **Agent context files** in `output/context/*.json`
- ✅ **Configuration files** found in the actual codebase
- ✅ **Import statements** and dependencies in actual code

**WHEN NO DATA EXISTS, USE GENERIC TERMS:**
- ✅ High/low/moderate instead of specific percentages
- ✅ Fast/slow/extended instead of specific times
- ✅ Large/small/substantial instead of specific sizes
- ✅ Many/few/several instead of specific counts
- ✅ Recent/current/legacy instead of specific dates
- ✅ Complex/simple/moderate instead of specific metrics

### 3. 🔍 ALWAYS VALIDATE DIAGRAMS AFTER CREATION
**MANDATORY: After creating ANY `.mmd` file or `.md` file with embedded Mermaid diagrams:**

```bash
# ALWAYS run this command after diagram creation:
python3 framework/scripts/simple_mermaid_validator.py --fix
```

**The validator will:**
- ✅ **Check syntax** using actual Mermaid CLI (same as browsers)
- ✅ **Auto-fix common errors** (@ symbols, quotes, ERD syntax)
- ✅ **Report validation status** for all diagram files
- ✅ **Ensure diagrams render** correctly in document-viewer.html

**DO NOT consider diagram work complete until validation passes!**

### 4. 🚫 GENERIC TERMS ENFORCEMENT
**WHEN NO DATA EXISTS - Instead of specific values, ALWAYS use generic descriptors:**

| ❌ DO NOT USE | ✅ USE INSTEAD |
|---------------|----------------|
| 80% reduction | significant reduction |
| 200ms response time | fast response |
| $1,000 budget | substantial cost |
| 50 classes | many classes |
| January 2024 | recent timeframe |
| 2.5GB memory | large memory usage |
| 1000 users | numerous users |
| 95% accuracy | high accuracy |

## 🔧 Framework Architecture Overview

### **Execution Modes:**
- **Quick Mode**: Automated hands-off execution (1-2 hours)
  - `python3 run_analysis.py --mode quick` - Terminal automation
  - n8n workflows - Full Docker automation
- **Guided Mode**: Interactive with checkpoints (3-4 hours)
  - Manual Claude Code agent execution with user review points

### **Core Components:**
- **5 Core Agents**: architect-agent, developer-agent, analyst-agent, diagram-agent, doc-writer-agent
- **Multi-Context Architecture**: Each agent can run with different specializations
- **Technology Detection**: Auto-detects Java, .NET, Angular, etc. and loads appropriate knowledge
- **Token Optimization**: Repomix compression achieves ~80% token reduction
- **Resume Capability**: Can restart from any point without losing progress

### **Key Files:**
- `setup_simple.py` - Main setup script for new projects
- `run_analysis.py` - Automated execution engine with multi-context support
- `.claude/agents/*.md` - Agent definitions with data integrity rules
- `framework/scripts/` - Validation and utility scripts
- `n8n/` - Docker-based automation workflows

### **Output Structure:**
- `output/docs/` - Final documentation 
- `output/reports/` - Analysis reports and summaries
- `output/context/` - JSON files for agent-to-agent communication
- `output/diagrams/` - Mermaid diagrams organized by category

## ⚡ Quick Commands for Common Operations

### **Setup New Project:**
```bash
python3 setup_simple.py
```

### **Run Quick Analysis:**
```bash
# Generate Repomix summary (REQUIRED)
repomix --config .repomix.config.json codebase/project-name/

# Run automated analysis
python3 run_analysis.py --mode quick
```

### **Validate Output Quality:**
```bash
# Check for data fabrication violations
python3 framework/scripts/data_integrity_validator.py

# Validate and fix all diagrams  
python3 framework/scripts/simple_mermaid_validator.py --fix
```

### **Resume Interrupted Analysis:**
```bash
python3 run_analysis.py --mode quick --resume  # DEFAULT behavior
python3 run_analysis.py --mode quick --restart # Force full restart
```

## 🚨 WHAT TO DO IF THINGS BREAK

### **If Manual Flow Breaks:**
1. Check `.mcp.json` exists and is valid
2. Verify `CLAUDE.md` has correct agent sequence
3. Ensure `output/` directories exist
4. Run `python3 setup_simple.py` to recreate configs

### **If n8n Flow Breaks:**
1. Check Docker containers are running: `docker ps`
2. Verify host agent server: `python3 n8n/host_agent_server.py`
3. Check n8n UI accessible: http://localhost:5678
4. Restart with: `cd n8n && ./start_n8n_minimal.sh`

### **If Agents Produce Bad Output:**
1. Run data integrity validator immediately
2. Check agent context files in `output/context/`
3. Verify Repomix summary exists and is current
4. Re-run specific agents with `@agent-name` in Claude Code

## 📋 Testing Checklist

Before any changes are complete:
- [ ] Manual flow works: Agents can be run with `@agent-name`
- [ ] n8n flow works: Docker automation executes properly
- [ ] Data integrity: No fabricated values in output
- [ ] Diagrams valid: All `.mmd` files pass validation
- [ ] Resume works: Can restart analysis from any point
- [ ] Context chain: Agent-to-agent communication working

---

**Remember: This framework is used in production. Preserve existing functionality while improving capabilities. When in doubt, test thoroughly and use the existing validation scripts.**