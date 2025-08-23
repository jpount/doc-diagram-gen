# Codebase Analysis & Documentation Generation Framework

A comprehensive, reusable framework for analyzing any codebase and generating enterprise-grade documentation with visual diagrams. Optimized for Claude Code with intelligent agent orchestration and 90%+ token optimization through MCP integration.

## 🚀 Quick Start

### Cross-Platform Setup

#### Windows
```powershell
# Using PowerShell
powershell -ExecutionPolicy Bypass -File setup.ps1

# Or using Python (recommended)
python setup.py
```

#### Mac/Linux
```bash
# Using shell script
./setup.sh

# Or using Python (recommended)
python3 setup.py
```

### All Platforms
```bash
# 1. Follow the interactive prompts to:
#    - Configure target technology stack
#    - Set up MCP integration
#    - Configure codebase path

# 2. Place your codebase in the configured directory
# Windows: xcopy /E /I C:\your\code codebase\your-project
# Mac/Linux: cp -r /path/to/your/code codebase/your-project/

# 3. Start analysis in Claude Code
```

## 📂 Project Structure

```
.
├── setup.sh                    # Setup script for Mac/Linux
├── setup.py                    # Setup script for all platforms (RECOMMENDED)
├── setup.ps1                   # Setup script for Windows PowerShell
├── .mcp.json                   # MCP configuration (auto-generated)
├── .repomix.config.json        # Repomix config (auto-generated)
├── TARGET_TECH_STACK.md        # Target stack config (auto-generated)
│
├── framework/                  # Framework components (DO NOT MODIFY)
│   ├── scripts/               # Setup and utility scripts
│   │   ├── setup-tech-stack.sh
│   │   ├── setup-mcp.sh
│   │   └── test-mcp-integration.sh
│   ├── mcp-configs/           # MCP configuration templates
│   │   ├── mcp.template.json
│   │   └── repomix.config.template.json
│   ├── templates/             # Project templates
│   │   ├── TARGET_TECH_STACK.template.md
│   │   └── tech-stack-presets.yaml
│   └── docs/                  # Framework documentation
│       ├── CLAUDE_FRAMEWORK.md
│       ├── MCP_USAGE_GUIDE.md
│       └── MCP_CONFIGURATION_GUIDE.md
│
├── .claude/                    # Claude Code configuration
│   ├── agents/                # Analysis agents
│   │   ├── legacy-code-detective.md
│   │   ├── business-logic-analyst.md
│   │   ├── performance-analyst.md
│   │   ├── security-analyst.md
│   │   ├── modernization-architect.md
│   │   ├── documentation-specialist.md
│   │   ├── diagram-architect.md
│   │   ├── mcp-orchestrator.md
│   │   └── repomix-analyzer.md
│   ├── hooks/                 # Validation hooks (Python for cross-platform)
│   │   ├── mermaid_diagram_validation.py
│   │   ├── documentation_completeness_check.py
│   │   ├── business_rule_validation.py
│   │   └── (legacy .sh versions kept for compatibility)
│   └── settings.local.json    # Claude settings
│
├── codebase/                   # YOUR CODE GOES HERE
│   └── [project-name]/        # Your project to analyze
│
├── output/                     # GENERATED OUTPUT
│   ├── docs/                  # Generated documentation
│   │   ├── 00-executive-summary.md
│   │   ├── 01-archaeological-analysis.md
│   │   ├── 02-business-logic-analysis.md
│   │   ├── 03-visual-architecture.md
│   │   ├── 04-performance-analysis.md
│   │   ├── 05-security-analysis.md
│   │   └── 06-modernization-strategy.md
│   ├── diagrams/              # Generated diagrams
│   │   └── *.mermaid
│   └── reports/               # Analysis reports
│       ├── repomix-summary.md
│       └── mcp-strategy.md
│
└── .mcp-cache/                # MCP cache (auto-managed)
```

## 🎯 Key Features

### Token Optimization (90%+ Reduction)
- **Repomix**: Compresses codebase by 80%
- **Serena MCP**: Semantic search saves 60%
- **Combined**: 90-95% token reduction

### Comprehensive Analysis
- **50+ Business Rules**: Extracted with code references
- **Complete Diagrams**: Architecture, sequence, flow diagrams
- **Security Assessment**: OWASP compliance, vulnerability detection
- **Performance Analysis**: Bottlenecks, optimization opportunities
- **Migration Strategy**: Phased modernization roadmap

### Quality Assurance
- Automated diagram validation
- Business rule verification
- Documentation completeness checks
- Cross-referenced outputs

## 🤖 Available Agents

### Core Analysis Agents

| Agent | Purpose | Output Location |
|-------|---------|-----------------|
| `@mcp-orchestrator` | Coordinates MCP usage | output/reports/ |
| `@repomix-analyzer` | Analyzes compressed code | output/reports/ |
| `@legacy-code-detective` | Technology stack analysis | output/docs/01-*.md |
| `@business-logic-analyst` | Business rule extraction | output/docs/02-*.md |
| `@diagram-architect` | Visual documentation | output/diagrams/ |
| `@performance-analyst` | Performance bottlenecks | output/docs/04-*.md |
| `@security-analyst` | Security vulnerabilities | output/docs/05-*.md |
| `@modernization-architect` | Migration strategy | output/docs/06-*.md |

## 📋 Workflow

### Phase 1: Setup (One-time)

**Windows:**
```powershell
python setup.py
# or
powershell -ExecutionPolicy Bypass -File setup.ps1
```

**Mac/Linux:**
```bash
python3 setup.py
# or
./setup.sh
```

### Phase 2: MCP Pre-Analysis (Optional but Recommended)
```bash
# Generate compressed summary (all platforms)
repomix --config .repomix.config.json

# Test MCP integration
# Windows:
python framework\scripts\test_mcp_integration.py

# Mac/Linux:
python3 framework/scripts/test_mcp_integration.py
```

### Phase 3: Run Analysis Agents
In Claude Code, run agents in sequence:

```
# 1. MCP Optimization (if available)
@mcp-orchestrator
@repomix-analyzer

# 2. Core Analysis
@legacy-code-detective
@business-logic-analyst
@diagram-architect

# 3. Specialized Analysis
@performance-analyst
@security-analyst
@modernization-architect
```

### Phase 4: Review Output
- Documentation: `output/docs/`
- Diagrams: `output/diagrams/`
- Reports: `output/reports/`

## 🔧 Configuration

### Technology Stack
Configure your target technology stack:
```bash
./framework/scripts/setup-tech-stack.sh
```

Or edit `TARGET_TECH_STACK.md` directly after setup.

### MCP Configuration
The `.mcp.json` file is auto-generated during setup.
To reconfigure:
```bash
./framework/scripts/setup-mcp.sh
```

### Codebase Path
Update in `.mcp.json`:
```json
"--project",
"${PWD}/codebase/your-project-name"
```

## 🚨 Validation

Validation hooks run automatically when files are written to `output/docs/`.

To run manually:

**Windows:**
```powershell
python .claude\hooks\mermaid_diagram_validation.py
python .claude\hooks\documentation_completeness_check.py
python .claude\hooks\business_rule_validation.py
```

**Mac/Linux:**
```bash
python3 .claude/hooks/mermaid_diagram_validation.py
python3 .claude/hooks/documentation_completeness_check.py
python3 .claude/hooks/business_rule_validation.py
```

## 📊 Expected Outputs

### Documentation Deliverables
1. **Executive Summary** - High-level overview
2. **Technical Analysis** - Architecture and dependencies
3. **Business Rules Catalog** - 50+ rules with code references
4. **Visual Documentation** - Mermaid diagrams
5. **Performance Report** - Bottlenecks and optimizations
6. **Security Assessment** - Vulnerabilities and remediation
7. **Modernization Roadmap** - Phased migration strategy

### Quality Metrics
- ✅ Business Rules: Minimum 50+ extracted
- ✅ Sequence Diagrams: Complete coverage
- ✅ Code References: Every rule traceable
- ✅ Risk Assessment: Comprehensive
- ✅ Performance Metrics: Quantified

## 🆘 Troubleshooting

### MCP Not Working
```bash
# Run diagnostic test (all platforms)
python framework/scripts/test_mcp_integration.py

# Check .mcp.json exists in root
# Windows: dir .mcp.json
# Mac/Linux: ls -la .mcp.json

# Restart Claude Code after changes
```

### Repomix Issues
```bash
# Install if missing
npm install -g repomix

# Test configuration
repomix --config .repomix.config.json --dry-run
```

### Path Issues
- Ensure codebase is in `codebase/[project-name]/`
- Update `.mcp.json` with correct path
- Use absolute paths in configurations

## 📚 Documentation

### Framework Documentation
- `framework/docs/CLAUDE_FRAMEWORK.md` - Complete framework guide
- `framework/docs/MCP_USAGE_GUIDE.md` - MCP optimization strategies
- `framework/docs/MCP_CONFIGURATION_GUIDE.md` - MCP setup details

### Generated Documentation
All generated documentation goes to `output/docs/`

## 🤝 Best Practices

1. **Always run setup.sh first** - Ensures proper configuration
2. **Use MCPs when available** - 90%+ token savings
3. **Run agents in sequence** - Each builds on previous
4. **Validate outputs** - Use provided hooks
5. **Keep framework updated** - Don't modify framework/ directory

## 📝 Notes

- Framework components are in `framework/` - do not modify
- Your code goes in `codebase/`
- All output goes to `output/`
- Configuration files (`.mcp.json`, `.repomix.config.json`) stay in root
- `TARGET_TECH_STACK.md` is generated during setup

## 🔗 Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Mermaid Diagram Syntax](https://mermaid.js.org)
- [Repomix Documentation](https://github.com/repomix/repomix)
- [Serena MCP](https://github.com/oraios/serena)

---

**Framework Version**: 2.1.0  
**Platform Support**: Windows, Mac, Linux  
**Requirements**: Python 3.7+, Node.js (optional)  
**Optimized for**: Claude Code with MCP Integration  
**Token Reduction**: 90-95% with full MCP stack