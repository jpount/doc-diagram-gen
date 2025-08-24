# Framework Structure Guide

## Directory Organization

### Root Level (Working Directory)
Files that belong at the root level:
- `setup.sh` / `setup.py` / `setup.ps1` - Setup scripts for different platforms
- `README.md` - Main documentation
- `STRUCTURE.md` - This file
- `TESTING_REFERENCE.md` - Testing and validation guide
- `.gitignore` - Version control configuration

Auto-generated files (git-ignored):
- `.mcp.json` - MCP configuration (MUST be at root for Claude Code)
- `.repomix.config.json` - Repomix configuration
- `CLAUDE.md` - Project configuration for Claude Code
- `ANALYSIS_MODE.md` - Analysis mode configuration
- `DOCUMENTATION_MODE.md` - Documentation mode configuration
- `TARGET_TECH_STACK.md` - Target technology configuration (modernization only)

### Framework Directory
**Path**: `framework/`  
**Purpose**: Contains all framework components (DO NOT MODIFY)

```
framework/
├── scripts/                    # Core scripts
│   ├── smart_mermaid_validator.py     # Intelligent Mermaid validation
│   ├── mermaid_pre_write_hook.py      # Pre-write validation
│   ├── mermaid_final_check.py         # Final validation pass
│   ├── simple_mermaid_validator.py    # Basic validation (backup)
│   ├── setup_mcp.py                   # MCP setup
│   ├── setup_tech_stack.py            # Tech stack configuration
│   ├── test_mcp_integration.py        # MCP diagnostic
│   ├── test_framework.py              # Framework health check
│   └── agent_orchestrator.py          # Agent workflow coordinator
│
├── mcp-configs/               # MCP configuration templates
│   ├── mcp.template.json     # Template for .mcp.json
│   ├── mcp.example.json      # Example configuration
│   └── repomix.config.template.json
│
├── templates/                 # Project templates
│   ├── CLAUDE.template.md
│   ├── ANALYSIS_MODE.template.md
│   ├── DOCUMENTATION_MODE.template.md
│   ├── TARGET_TECH_STACK.template.md
│   ├── CONTEXT_SUMMARY_SCHEMA.md
│   └── tech-stack-presets.yaml
│
├── docs/                      # Framework documentation
│   ├── CLAUDE_FRAMEWORK.md           # Complete framework guide
│   ├── MERMAID_COMPLETE_GUIDE.md     # Comprehensive Mermaid guide
│   ├── MERMAID_STRICT_RULES.md       # Quick reference rules
│   ├── MCP_USAGE_GUIDE.md            # MCP optimization
│   ├── MCP_CONFIGURATION_GUIDE.md    # MCP setup details
│   └── USER_INTERACTION_GUIDE.md     # User interaction patterns
│
└── document-viewer.html       # Browser-based diagram viewer
```

### Claude Configuration
**Path**: `.claude/`  
**Purpose**: Claude Code agents and hooks

```
.claude/
├── agents/                    # Analysis agents
│   ├── mcp-orchestrator.md          # MCP coordination
│   ├── repomix-analyzer.md          # Compressed code analysis
│   ├── architecture-selector.md     # Technology detection
│   ├── java-architect.md             # Java specialist
│   ├── angular-architect.md         # Angular specialist
│   ├── dotnet-architect.md          # .NET specialist
│   ├── legacy-code-detective.md     # Generic analysis
│   ├── business-logic-analyst.md    # Business rule extraction
│   ├── performance-analyst.md       # Performance analysis
│   ├── security-analyst.md          # Security assessment
│   ├── diagram-architect.md         # Visual documentation
│   ├── documentation-specialist.md  # Documentation generation
│   └── modernization-architect.md   # Migration planning
│
├── hooks/                     # Validation hooks
│   └── simple_mermaid_validation.py # Pre-write validation
│
└── settings.local.json        # Claude Code settings
```

### Input Directory
**Path**: `codebase/`  
**Purpose**: Place your code to analyze here

```
codebase/
└── [project-name]/           # Your project directory
    └── ... (your code)
```

### Output Directory
**Path**: `output/`  
**Purpose**: All generated documentation and reports

```
output/
├── docs/                      # Generated documentation
│   ├── 00-agent-selection-report.md
│   ├── 01-[technology]-analysis.md
│   ├── 02-business-logic-analysis.md
│   ├── 03-visual-architecture.md
│   ├── 04-performance-analysis.md
│   ├── 05-security-analysis.md
│   └── 06-modernization-strategy.md
│
├── diagrams/                  # Generated diagrams (.mmd files)
│   ├── architecture/
│   ├── data/
│   ├── migration/
│   ├── performance/
│   └── process/
│
├── context/                   # Agent context summaries
│   └── *-summary.json
│
└── reports/                   # Analysis reports
    ├── repomix-summary.md
    └── mermaid_final_check_report.json
```

### Archive Directory
**Path**: `.archive/`  
**Purpose**: Old scripts and documentation (git-ignored)

```
.archive/
├── old_mermaid_validators/    # 24+ old validation scripts
└── old_mermaid_docs/          # Redundant documentation
```

### Cache Directory
**Path**: `.mcp-cache/`  
**Purpose**: MCP cache for token optimization (auto-managed, git-ignored)

## File Types by Location

### Framework Files (Read-only)
- Scripts: `framework/scripts/*.py`
- Templates: `framework/templates/*`
- Configs: `framework/mcp-configs/*`
- Docs: `framework/docs/*.md`

### Configuration Files (Auto-generated, git-ignored)
- `.mcp.json` - MCP configuration
- `.repomix.config.json` - Repomix config
- `CLAUDE.md` - Project settings
- `ANALYSIS_MODE.md` - Analysis mode
- `DOCUMENTATION_MODE.md` - Documentation mode
- `TARGET_TECH_STACK.md` - Target technology

### Generated Files (Do not edit)
- `output/**/*` - All analysis outputs
- `.mcp-cache/**/*` - Cache files

### User Files
- `codebase/**/*` - Your code to analyze

## Setup Flow

1. **Initial Setup**
   ```bash
   python3 setup.py  # or ./setup.sh or powershell setup.ps1
   ```
   Creates configuration files

2. **Place Code**
   ```bash
   cp -r /your/code codebase/project-name/
   ```

3. **Optional: Generate Repomix**
   ```bash
   repomix --config .repomix.config.json codebase/
   ```

4. **Run Analysis in Claude Code**
   - Use @agent-name to invoke agents
   - Outputs go to `output/`

5. **Validate Diagrams**
   ```bash
   python3 framework/scripts/mermaid_final_check.py output/
   ```

## Important Notes

### Why .mcp.json Must Be at Root
Claude Code looks for `.mcp.json` in the project root directory. It cannot be in a subdirectory.

### Git-Ignored Configuration
Configuration files are auto-generated and personalized, so they're git-ignored:
- Each developer gets their own settings
- No merge conflicts from personal configurations
- Clean repository without generated files

### Framework Isolation
The `framework/` directory contains all reusable components:
- Clear distinction between framework and project files
- Easy updates without affecting user data
- Portable framework for new projects

### Mermaid Validation System
Three-layer validation ensures perfect diagrams:
1. **Prevention**: Strict rules in `MERMAID_STRICT_RULES.md`
2. **Validation**: Smart validator with error-based fixing
3. **Verification**: Browser-based viewer for final check

This structure keeps the framework clean, maintainable, and user-friendly.