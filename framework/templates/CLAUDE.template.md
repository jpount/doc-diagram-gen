# Project Configuration for Claude Code

## Project Overview
- **Project Name:** {{PROJECT_NAME}}
- **Analysis Mode:** {{ANALYSIS_MODE}}
- **Documentation Mode:** {{DOCUMENTATION_MODE}}
- **Codebase Location:** codebase/{{PROJECT_PATH}}
- **Framework Version:** 2.0

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
- ❌ **Hardcoded class names** (OrderService, CustomerDAO, PaymentProcessor)

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

**VALIDATE DATA INTEGRITY:**
```bash
# Check for hardcoded examples after any agent work:
python3 framework/scripts/data_integrity_validator.py
```

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

### 5. 📋 EXPLICIT DATA UNAVAILABILITY DISCLOSURE
**WHEN NO RELEVANT DATA CAN BE FOUND:**
- ✅ **Explicitly state**: "Data not available" or "No data found in codebase"
- ✅ **Be specific**: "No performance metrics found in logs" 
- ✅ **Suggest action**: "Run performance profiling to gather this data"
- ❌ **NEVER fabricate** placeholder data to fill gaps
- ❌ **NEVER estimate** without actual basis

**Examples:**
```markdown
## Performance Analysis
- Database response times: Data not available
- Memory usage patterns: No profiling data found  
- Recommendation: Configure application monitoring to collect this data

## Security Assessment  
- Vulnerability count: No security scan results available
- Compliance status: Data not available - recommend security audit
```

## Analysis Configuration

### Current Settings
- **Analysis Focus:** {{ANALYSIS_FOCUS}}
- **Modernization:** {{MODERNIZATION_ENABLED}}
- **User Interaction:** {{USER_INTERACTION}}
- **Repomix:** {{REPOMIX_STATUS}}
- **Token Strategy:** Repomix-first (80% reduction)

{{MODERNIZATION_CONSTRAINTS}}

## Quick Commands

### 🔴 CRITICAL: Start Analysis
```bash
# 1. Generate Repomix summary (REQUIRED FOR EFFICIENCY)
repomix --config .repomix.config.json codebase/{{PROJECT_PATH}}/

# 2. Verify Repomix output exists
ls -la output/reports/repomix-summary.md

# 3. Check token monitor
python3 framework/scripts/token_monitor.py report

# 4. Start analysis in Claude Code with agents below
```

## Technology Stack
{{TECHNOLOGY_STACK}}

## Available Agents

### Core Analysis Agents (Simplified - Only 7 Total)
- `@mcp-orchestrator` - Coordinate MCP usage and strategy
- `@repomix-analyzer` - Analyze compressed codebase summary  
- `@architect-agent` - System architecture analysis with tech-specific knowledge
- `@developer-agent` - Code quality assessment with language-specific patterns
- `@analyst-agent` - Business logic + Performance + Security + Modernization analysis
- `@diagram-agent` - All visualization needs with full Mermaid validation
- `@doc-writer-agent` - Documentation generation and synthesis

### Knowledge Loading System
Each agent automatically loads technology-specific knowledge:
- Language patterns from `framework/knowledge/languages/`
- Framework patterns from `framework/knowledge/frameworks/`  
- Generic fallback if specific knowledge unavailable

{{MODERNIZATION_AGENTS}}

## Workflow for {{DOCUMENTATION_MODE}} Mode

{{WORKFLOW_STEPS}}

## Output Locations
- **Documentation:** `output/docs/`
- **Diagrams:** `output/diagrams/`
- **Reports:** `output/reports/`
- **Context Summaries:** `output/context/`

## MCP Tools Available
{{MCP_TOOLS}}

## Token Budget Guidelines
- **Project Size:** {{PROJECT_SIZE}}
- **Total Budget:** {{TOKEN_BUDGET}}
- **With Repomix:** ~50,000 tokens (80% reduction)
- **Without Repomix:** ~250,000+ tokens (5x more!)

## Key Files to Review
- `ANALYSIS_MODE.md` - Current analysis configuration
- `DOCUMENTATION_MODE.md` - Documentation generation settings
{{TARGET_TECH_STACK_FILE}}
- `framework/docs/USER_INTERACTION_GUIDE.md` - User interaction guidance
- `framework/docs/MODERNIZATION_CONSTRAINTS.md` - Agent modernization guidelines
- `framework/docs/DATA_DRIVEN_ENFORCEMENT.md` - **CRITICAL: Data integrity enforcement rules**
- `framework/templates/CONTEXT_SUMMARY_SCHEMA.md` - Agent communication format

## Project-Specific Notes
{{PROJECT_NOTES}}

## Troubleshooting

### MCPs Not Available
1. Ensure `.mcp.json` exists in project root
2. Restart Claude Code after configuration
3. Check MCP logs in Claude Code settings
4. Verify MCP servers are installed (npm/uvx)

### Analysis Issues
1. **FIRST**: Ensure Repomix summary exists
   - `ls -la output/reports/repomix-summary.md`
   - If missing: `repomix --config .repomix.config.json codebase/{{PROJECT_PATH}}/`
2. Check token usage efficiency
   - `python3 framework/scripts/token_monitor.py report`
   - Should show >80% Repomix usage
3. Ensure codebase is in `codebase/{{PROJECT_PATH}}/`
4. Check agent output in `output/docs/`

## Next Steps
{{NEXT_STEPS}}

---
*Generated by setup on {{SETUP_DATE}}*