# Framework Structure Guide

## Directory Organization

### Root Level (Working Directory)
Files that belong at the root level:
- `setup.sh` - Master setup script (entry point)
- `README.md` - Main documentation
- `.mcp.json` - MCP configuration (MUST be at root for Claude Code)
- `.repomix.config.json` - Repomix configuration (generated during setup)
- `TARGET_TECH_STACK.md` - Target technology configuration (generated during setup)
- `.gitignore` - Version control configuration
- `STRUCTURE.md` - This file

### Framework Directory
**Path**: `framework/`  
**Purpose**: Contains all framework components (DO NOT MODIFY)

```
framework/
├── scripts/                    # Setup and utility scripts
│   ├── setup-tech-stack.sh    # Technology stack configuration
│   ├── setup-mcp.sh           # MCP setup and validation
│   └── test-mcp-integration.sh # MCP diagnostic tool
│
├── mcp-configs/               # MCP configuration templates
│   ├── mcp.template.json     # Template for .mcp.json
│   ├── mcp.example.json      # Example .mcp.json configuration
│   ├── repomix.config.template.json # Template for Repomix
│   └── mcp-config.yaml       # MCP orchestration config
│
├── templates/                 # Project templates
│   ├── TARGET_TECH_STACK.template.md # Tech stack template
│   └── tech-stack-presets.yaml      # Preset configurations
│
└── docs/                      # Framework documentation
    ├── CLAUDE_FRAMEWORK.md    # Complete framework guide
    ├── MCP_USAGE_GUIDE.md     # MCP optimization strategies
    └── MCP_CONFIGURATION_GUIDE.md # MCP setup details
```

### Claude Configuration
**Path**: `.claude/`  
**Purpose**: Claude Code agents and hooks

```
.claude/
├── agents/                    # Analysis agents
│   ├── mcp-orchestrator.md   # MCP coordination
│   ├── repomix-analyzer.md   # Compressed code analysis
│   ├── legacy-code-detective.md
│   ├── business-logic-analyst.md
│   ├── performance-analyst.md
│   ├── security-analyst.md
│   ├── modernization-architect.md
│   ├── documentation-specialist.md
│   └── diagram-architect.md
│
├── hooks/                     # Validation hooks
│   ├── mermaid-diagram-validation.sh
│   ├── documentation-completeness-check.sh
│   └── business-rule-validation.sh
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
│   ├── 00-executive-summary.md
│   ├── 01-archaeological-analysis.md
│   ├── 02-business-logic-analysis.md
│   ├── 03-visual-architecture.md
│   ├── 04-performance-analysis.md
│   ├── 05-security-analysis.md
│   └── 06-modernization-strategy.md
│
├── diagrams/                  # Generated diagrams
│   ├── architecture/
│   ├── sequence/
│   └── flow/
│
└── reports/                   # Analysis reports
    ├── repomix-summary.md    # Compressed codebase
    ├── mcp-strategy.md       # MCP optimization plan
    └── token-metrics.json    # Token usage statistics
```

### Cache Directory
**Path**: `.mcp-cache/`  
**Purpose**: MCP cache for token optimization (auto-managed)

```
.mcp-cache/
├── repomix/                  # Repomix cache
├── serena/                   # Serena memories
└── sourcegraph/              # Pattern cache
```

## File Types by Location

### Framework Files (Read-only)
- Scripts: `framework/scripts/*.sh`
- Templates: `framework/templates/*`
- Configs: `framework/mcp-configs/*`
- Docs: `framework/docs/*.md`

### Configuration Files (User-editable)
- `.mcp.json` - Edit to change project paths
- `TARGET_TECH_STACK.md` - Edit to change target stack
- `.repomix.config.json` - Edit for custom compression

### Generated Files (Do not edit)
- `output/**/*` - All analysis outputs
- `.mcp-cache/**/*` - Cache files

### User Files
- `codebase/**/*` - Your code to analyze

## Setup Flow

1. **Initial Setup**
   ```bash
   ./setup.sh
   ```
   Creates: `.mcp.json`, `.repomix.config.json`, `TARGET_TECH_STACK.md`

2. **Place Code**
   ```bash
   cp -r /your/code codebase/project-name/
   ```

3. **Run Analysis**
   - Agents write to `output/`
   - Cache stored in `.mcp-cache/`

## Important Notes

### Why .mcp.json Must Be at Root
Claude Code looks for `.mcp.json` in the project root directory. It cannot be in a subdirectory or it won't be recognized.

### Why Configuration Files Stay at Root
- `.mcp.json` - Required by Claude Code
- `.repomix.config.json` - Expected by Repomix CLI
- `TARGET_TECH_STACK.md` - Referenced by agents

### Framework Isolation
The `framework/` directory contains all reusable components. This separation ensures:
- Clear distinction between framework and project files
- Easy updates without affecting user data
- Portable framework that can be copied to new projects

### Output Organization
All generated content goes to `output/` with subdirectories for:
- `docs/` - Markdown documentation
- `diagrams/` - Mermaid diagram files
- `reports/` - Analysis reports and summaries

This structure keeps generated content separate from both the framework and the source code being analyzed.