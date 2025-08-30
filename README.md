# Codebase Analysis & Documentation Generation Framework

A comprehensive framework for analyzing existing codebases and generating complete documentation, architecture diagrams, and improvement recommendations. Primary focus is on understanding and documenting your current system, with optional modernization planning capabilities.

## Primary Goals

### 📚 Documentation & Analysis (Default Mode)
- **Comprehensive Documentation**: Generate complete technical documentation for your existing codebase
- **Architecture Visualization**: Create detailed diagrams showing system structure and data flows
- **Technical Debt Analysis**: Identify and catalog technical debt with improvement recommendations
- **Performance Analysis**: Find bottlenecks and optimization opportunities
- **Security Assessment**: Discover vulnerabilities and security improvements
- **Business Logic Extraction**: Document business rules and domain logic

### 🚀 Optional Modernization Planning
- Available as an add-on feature when needed
- Creates migration roadmaps and target architectures
- Requires additional configuration (TARGET_TECH_STACK.md)

## Key Features

### 🎯 Quality-First Approach
- **Flexible Token Usage**: Prioritizes documentation quality over strict token limits
- **Context Management**: Dual-layer context system (memory + files) for resilience
- **Progressive Refinement**: Each agent builds on previous findings efficiently

### 🔄 Three Documentation Modes
1. **QUICK**: Fully automated, fast analysis (1-2 hours)
2. **GUIDED**: Interactive with user checkpoints for accuracy (3-4 hours) - Recommended
3. **TEMPLATE**: Generates templates for manual completion (highest accuracy)

### 💾 Token Optimization Strategy
- **Primary**: Repomix compression (80% reduction) - REQUIRED
- **Fallback**: Serena MCP (60% reduction) - Optional
- **Last Resort**: Raw codebase access - Avoid!
- All agents follow strict hierarchy: Repomix → Serena → Raw

Optimized for Claude Code with intelligent agent orchestration. **Repomix is MANDATORY for token efficiency** - reducing usage by 80%.

## 🚀 Quick Start

### 🔴 CRITICAL: Generate Repomix First!
```bash
# Step 1: Run setup
python3 setup.py  # or ./setup.sh

# Step 2: Place your code
cp -r /your/code codebase/project-name/

# Step 3: Generate Repomix (REQUIRED for efficiency)
repomix --config .repomix.config.json codebase/project-name/

# Step 4: Start Claude Code and run agents
```

### ⚡ Agent Workflow in Claude Code
```bash
# After Repomix is generated, run these agents:
@mcp-orchestrator           # Token optimization
@repomix-analyzer          # Analyze compressed codebase
@architecture-selector     # Detect your tech stack
@[technology]-architect    # Run recommended specialists
@business-logic-analyst    # Extract business rules
@performance-analyst       # Find bottlenecks
@security-analyst         # Security assessment
@diagram-architect        # Create diagrams
@documentation-specialist # Generate final docs
```

### Setup Process

```bash
# Run interactive setup (all platforms)
python3 setup.py  # Mac/Linux
python setup.py   # Windows
```

#### Setup will:
1. ✅ **Configure Repomix** (STRONGLY RECOMMENDED)
   - 80% token reduction
   - Critical for efficiency
   - Installs if not present

2. 🔵 **Configure Serena MCP** (Optional)
   - Disabled by default
   - Enable only if needed as fallback
   - 60% token reduction (less than Repomix)

3. 📋 **Set Analysis Mode**
   - Documentation only (default)
   - With modernization (optional)

### 🔴 CRITICAL: Generate Repomix Summary

**BEFORE starting any analysis:**

```bash
# 1. Place your code
cp -r /path/to/your/code codebase/your-project/

# 2. Generate Repomix summary (REQUIRED)
repomix --config .repomix.config.json codebase/your-project/

# 3. Verify output exists
ls -la output/reports/repomix-summary.md
```

⚠️ **Without Repomix:**
- 5-10x more tokens used
- Higher costs
- Slower analysis
- May hit token limits

## 📂 Project Structure

```
.
├── setup.sh                    # Setup script for Mac/Linux
├── setup.py                    # Setup script for all platforms (RECOMMENDED)
├── setup.ps1                   # Setup script for Windows PowerShell
├── .mcp.json                   # MCP configuration (auto-generated, git-ignored)
├── .repomix.config.json        # Repomix config (auto-generated, git-ignored)
├── ANALYSIS_MODE.md            # Analysis mode config (auto-generated, git-ignored)
├── CLAUDE.md                   # Project config for Claude Code (auto-generated, git-ignored)
├── DOCUMENTATION_MODE.md       # Documentation mode config (auto-generated, git-ignored)
├── TARGET_TECH_STACK.md        # Target stack config (only for modernization modes, git-ignored)
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
│   │   ├── ANALYSIS_MODE.template.md
│   │   ├── DOCUMENTATION_MODE.template.md
│   │   ├── CONTEXT_SUMMARY_SCHEMA.md
│   │   ├── TOKEN_BUDGET_CONFIG.yaml
│   │   ├── TARGET_TECH_STACK.template.md
│   │   └── tech-stack-presets.yaml
│   └── docs/                  # Framework documentation
│       ├── CLAUDE_FRAMEWORK.md
│       ├── USER_INTERACTION_GUIDE.md
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
│   │   └── simple_mermaid_validation.py  # Pre-write Mermaid validation
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
│   ├── context/               # Agent context summaries (for efficiency)
│   │   ├── legacy-code-detective-summary.json
│   │   ├── business-logic-analyst-summary.json
│   │   └── [agent-name]-summary.json
│   ├── diagrams/              # Generated diagrams
│   │   └── *.mermaid
│   └── reports/               # Analysis reports
│       ├── repomix-summary.md
│       └── mcp-strategy.md
│
└── .mcp-cache/                # MCP cache (auto-managed)
```

## 🎯 Key Features

### 🚀 Technology-Specific Analysis (NEW!)
- **Smart Detection**: `@architecture-selector` automatically identifies your tech stack
- **Specialist Agents**: Dedicated architects for Java, .NET, and Angular
- **Better Results**: Technology-specific patterns, anti-patterns, and best practices
- **Parallel Execution**: Run backend and frontend specialists simultaneously

### Token Optimization (Up to 90% Reduction)
- **Default (Raw Codebase)**: Direct file access, no optimization needed
- **Repomix (Optional)**: Compresses codebase by 80% - if generated, agents will use it automatically
- **Serena MCP (Optional)**: Semantic search saves 60% - for advanced symbol analysis
- **Combined (All Optional Tools)**: 90-95% token reduction

**How It Works:**
1. Agents first check for Repomix summary (`output/reports/repomix-summary.md`)
2. If Repomix exists, agents use it for initial analysis (80% token savings)
3. If no Repomix, agents read directly from `codebase/` directory
4. Serena (if enabled) provides semantic search on top of either approach

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

| Agent | Purpose | Output Location | When to Use |
|-------|---------|-----------------|-------------|
| `@mcp-orchestrator` | Coordinates MCP usage | output/reports/ | Always run first for token optimization |
| `@repomix-analyzer` | Analyzes compressed code | output/reports/ | After MCP orchestrator |
| **`@architecture-selector`** | **Detects technologies & recommends specialists** | **output/docs/00-agent-selection-report.md** | **Run BEFORE any analysis agents** |
| `@java-architect` | Java/Spring/J2EE analysis with visual indicators | output/docs/01-java-*.md | When Java detected |
| `@dotnet-architect` | .NET/C#/ASP.NET analysis | output/docs/01-dotnet-*.md | When .NET detected |
| `@angular-architect` | Angular/AngularJS analysis | output/docs/01-angular-*.md | When Angular detected |
| `@legacy-code-detective` | Generic technology analysis | output/docs/01-*.md | ONLY for unknown/5+ technologies |
| `@business-logic-analyst` | Business rule extraction | output/docs/02-*.md | Always run |
| `@diagram-architect` | Visual documentation | output/diagrams/ | Always run |
| `@performance-analyst` | Performance bottlenecks | output/docs/04-*.md | Always run |
| `@security-analyst` | Security vulnerabilities | output/docs/05-*.md | Always run |
| `@modernization-architect` | Migration strategy | output/docs/06-*.md | For modernization projects |
| `@documentation-specialist` | Comprehensive documentation | output/docs/*.md | Always run last |

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

### Phase 2: Pre-Analysis Setup (Optional)
```bash
# Optional: Generate compressed summary for token optimization (all platforms)
repomix --config .repomix.config.json

# Test MCP integration (shows which MCPs are available)
# Windows:
python framework\scripts\test_mcp_integration.py

# Mac/Linux:
python3 framework/scripts/test_mcp_integration.py
```

### Phase 3: Run Analysis Agents
In Claude Code, run agents in sequence:

#### 🎯 Recommended Workflow (with Specialist Agents)
```
# 1. Optional: MCP Optimization (if Repomix/Serena enabled)
@mcp-orchestrator
@repomix-analyzer

# 2. Technology Detection (IMPORTANT: Run this first!)
@architecture-selector    # Detects technologies and recommends specialists

# 3. Technology-Specific Analysis (based on detection results)
# Example for Java + Angular application:
@java-architect  # Backend analysis with visual indicators (if Java detected)
@angular-architect       # Frontend analysis (if Angular detected)
# Run these in parallel for faster analysis

# 4. Cross-Cutting Analysis (always run these)
@business-logic-analyst
@performance-analyst
@security-analyst

# 5. Documentation Generation
@diagram-architect
@modernization-architect  # If doing modernization
@documentation-specialist  
```

#### Alternative: Generic Workflow (for unknown codebases)
```
# Only use this if architecture-selector finds 5+ technologies
# or completely unknown tech stack
@legacy-code-detective   # Generic analysis
@business-logic-analyst
@diagram-architect
@performance-analyst
@security-analyst
@modernization-architect
@documentation-specialist
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
The `.mcp.json` file is auto-generated during setup with Serena disabled by default.

To enable Serena for semantic code analysis (60% token reduction):
1. Edit `.mcp.json` and remove the `"disabled": true` line from the serena section
2. Edit `.claude/settings.local.json` and either:
   - Set `"enableAllProjectMcpServers": true` to enable all MCPs, OR
   - Add `"serena"` to the `"enabledMcpjsonServers"` array

To reconfigure from scratch:
```bash
python3 framework/scripts/setup_mcp.py
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
python .claude\hooks\simple_mermaid_validation.py
python .claude\hooks\documentation_completeness_check.py
python .claude\hooks\business_rule_validation.py
```

**Mac/Linux:**
```bash
python3 .claude/hooks/simple_mermaid_validation.py
python3 .claude/hooks/documentation_completeness_check.py
python3 .claude/hooks/business_rule_validation.py
```

## 📊 Expected Outputs

### Documentation Deliverables
1. **Agent Selection Report** - Technology detection and specialist recommendations
2. **Technology-Specific Analysis** - Deep dive by Java/Angular/.NET architects
3. **Business Rules Catalog** - 50+ rules with code references
4. **Visual Documentation** - Mermaid diagrams
5. **Performance Report** - Bottlenecks and optimizations
6. **Security Assessment** - Vulnerabilities and remediation
7. **Modernization Roadmap** - Phased migration strategy
8. **Executive Summary** - High-level overview

### Quality Metrics
- ✅ Business Rules: Minimum 50+ extracted
- ✅ Sequence Diagrams: Complete coverage
- ✅ Code References: Every rule traceable
- ✅ Risk Assessment: Comprehensive
- ✅ Performance Metrics: Quantified

## 🆘 Troubleshooting

### Architecture Selector Not Finding Technologies
```bash
# Check if codebase is in correct location
ls -la codebase/

# Manually check for technology indicators
find codebase -name "*.java" | head -5  # Java files
find codebase -name "*.cs" | head -5    # .NET files
find codebase -name "*.ts" -o -name "angular.json" | head -5  # Angular files

# If technologies found but selector missed them, run specialists directly:
@java-architect  # For Java code (with visual indicators)
@angular-architect   # For Angular code
```

### Mermaid Diagram Issues
```bash
# Validate and auto-fix all diagrams
python3 framework/scripts/smart_mermaid_validator.py output/ --fix

# Run final check
python3 framework/scripts/mermaid_final_check.py output/

# Test in browser
# Open framework/document-viewer.html and load your output directory
```

### MCP Not Working
```bash
# Run diagnostic test (all platforms)
python3 framework/scripts/test_mcp_integration.py

# Check .mcp.json exists in root
ls -la .mcp.json

# Restart Claude Code after changes
```

### Serena Not Available
Serena is disabled by default. To enable:
1. Remove `"disabled": true` from serena section in `.mcp.json`
2. Restart Claude Code
3. Serena will be available as `@serena` in Claude Code

### Repomix Issues
```bash
# Install if missing
npm install -g repomix

# Generate repomix summary for your codebase only
repomix --config .repomix.config.json codebase/

# Or for a specific project
repomix --config .repomix.config.json codebase/daytrader/
```

### Path Issues
- Ensure codebase is in `codebase/[project-name]/`
- Update `.mcp.json` with correct path
- Use absolute paths in configurations

## 📚 Documentation

### Framework Documentation
- `framework/docs/CLAUDE_FRAMEWORK.md` - Complete framework guide
- `framework/docs/MERMAID_COMPLETE_GUIDE.md` - Comprehensive Mermaid validation guide
- `framework/docs/MERMAID_STRICT_RULES.md` - Quick reference for diagram rules
- `framework/docs/MCP_USAGE_GUIDE.md` - MCP optimization strategies
- `framework/docs/MCP_CONFIGURATION_GUIDE.md` - MCP setup details

### Generated Documentation
All generated documentation goes to `output/docs/`

## 🤝 Best Practices

1. **Always run setup.sh first** - Ensures proper configuration
2. **Run @architecture-selector early** - Identifies which specialists to use
3. **Use specialist agents** - Better results than generic legacy-code-detective
4. **Run specialists in parallel** - Java and Angular architects can run simultaneously
5. **Use MCPs when available** - 90%+ token savings
6. **Validate outputs** - Use provided hooks
7. **Keep framework updated** - Don't modify framework/ directory

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