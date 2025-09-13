# Documentation & Diagram Generation Framework

A streamlined framework for analyzing codebases and generating comprehensive documentation, architecture diagrams, and technical insights. Optimized for Claude Code with intelligent agent orchestration.

## Overview

This framework analyzes your codebase using specialized AI agents to produce:
- **Technical Documentation**: Complete system analysis and architecture documentation
- **Visual Diagrams**: Mermaid-based architecture, flow, and component diagrams  
- **Business Logic Analysis**: Extracted business rules and domain insights
- **Performance & Security Analysis**: Bottlenecks, vulnerabilities, and optimization opportunities

### Key Features
- **Intelligent Agent System**: Specialized agents for different analysis tasks
- **Token Optimization**: 80% token reduction via Repomix compression
- **Progressive Analysis**: Agents build context from previous outputs
- **Automated Workflow**: Hands-off execution with progress tracking

## 🚀 Quick Start

### 1. Place Your Code
```bash
# Copy your codebase to the analysis directory
cp -r /path/to/your/code codebase/project-name/
```

### 2. Generate Repomix Summary (Required)
```bash
# Create compressed codebase summary (80% token reduction)
repomix --config .repomix.config.json codebase/project-name/

# Verify output exists
ls -la output/reports/repomix-summary.md
```

### 3. Run Analysis Agents
```bash
# Using the analysis configuration (recommended)
python3 -c "from run_analysis import run_analysis; import json; config = json.load(open('analysis_config.json')); run_analysis(config['selected_agents'])"

# Or run agents individually in Claude Code:
@repomix-analyzer
@solution-architect
@performance-analyst
```

## Available Agents

### Current Configuration (3 Selected)
Based on `analysis_config.json`:
- **`@repomix-analyzer`** - Analyzes Repomix-generated codebase summaries (REQUIRED - ALWAYS FIRST)
- **`@solution-architect`** - Comprehensive C4 model analysis + technical + deployment + integration architecture
- **`@performance-analyst`** - Performance bottlenecks, memory leaks, scalability issues

### Additional Available Agents
- `@integration-specialist` - APIs, messaging, event-driven architecture  
- `@security-analyst` - OWASP Top 10, vulnerabilities, compliance
- `@business-logic-analyst` - Business rules, domain logic, process flows
- `@ui-analyst` - Frontend analysis, UI/UX assessment
- `@delphi-architect` - Delphi/Object Pascal specialist
- `@php-architect` - PHP application specialist
- `@java-architect` - Java/Spring/J2EE specialist  
- `@dotnet-architect` - .NET/C#/ASP.NET specialist
- `@angular-architect` - Angular/AngularJS specialist

## Agent Data Flow

### Critical Workflow Rules
All agents follow this priority:
1. **PRIMARY**: Read `output/reports/repomix-summary.md` (compressed codebase)
2. **SECONDARY**: Read `output/context/*.json` (previous agent outputs) 
3. **FALLBACK**: Access raw codebase only if needed

### Context Chain
```
repomix-summary.md 
    ↓
repomix-analyzer-summary.json
    ↓  
solution-architect-summary.json
    ↓
specialist agents read all previous contexts
```

## Project Structure

```
├── CLAUDE.md                   # Project configuration for Claude Code
├── analysis_config.json        # Selected agents and project settings
├── .repomix.config.json        # Repomix compression configuration
├── run_analysis.py             # Python script for automated agent execution
│
├── .claude/agents/             # AI agent definitions
│   ├── repomix-analyzer.md
│   ├── solution-architect.md  
│   ├── performance-analyst.md
│   └── [other-agents].md
│
├── codebase/                   # YOUR CODE GOES HERE
│   └── daytrader/             # Target project (configurable)
│
├── output/                     # GENERATED OUTPUT
│   ├── docs/                  # Generated documentation
│   ├── diagrams/              # Mermaid diagrams
│   ├── context/               # Agent context files
│   └── reports/               # Analysis reports
│
└── framework/                  # Framework components
    ├── scripts/               # Automation scripts  
    └── templates/             # Configuration templates
```

## Expected Outputs

### Documentation (`output/docs/`)
- **Architecture Analysis**: Complete system design and component relationships
- **Performance Assessment**: Bottlenecks, memory issues, scalability analysis  
- **Business Logic Documentation**: Extracted rules and domain processes
- **Security Analysis**: Vulnerabilities and compliance assessment
- **Integration Patterns**: APIs, messaging, and data flows

### Diagrams (`output/diagrams/`)
- **C4 Architecture Models**: Context, Container, Component, Code diagrams
- **Process Flow Diagrams**: Business workflows and data flows
- **Component Relationship Maps**: System architecture visualization
- **Performance Heat Maps**: Bottleneck identification diagrams

### Context Files (`output/context/`)
- **Agent Summaries**: JSON files with key findings for downstream agents
- **Progressive Knowledge**: Each agent builds on previous analysis
- **Token Optimization**: Efficient context sharing between agents

## Automation Options

### Option 1: Python Script (Recommended)
```bash
# Run all configured agents automatically
python3 -c "from run_analysis import run_analysis; import json; config = json.load(open('analysis_config.json')); run_analysis(config['selected_agents'])"
```

### Option 2: Manual Execution in Claude Code
Run agents individually:
```bash
@repomix-analyzer        # Always first
@solution-architect      # Core architecture analysis  
@performance-analyst     # Performance bottlenecks
```

### Option 3: n8n Workflow
```bash
# Hands-off automation with n8n
python3 n8n/run_hands_off_analysis.py
```

## Token Optimization Strategy

The framework uses **Repomix compression** to achieve 80% token reduction:

1. **Generate Repomix Summary**: Creates `output/reports/repomix-summary.md`
2. **Agent Priority System**: Agents check Repomix → Context → Raw codebase
3. **Progressive Context**: Each agent creates summary JSON for downstream agents
4. **Efficient Analysis**: Dramatic reduction in token usage and costs

### Without Repomix:
- ❌ 5-10x more tokens used
- ❌ Higher costs and slower analysis  
- ❌ May hit token limits on large codebases

### With Repomix:
- ✅ 80% token reduction
- ✅ Faster analysis  
- ✅ Lower costs
- ✅ Handles large codebases efficiently

## Configuration Files

### `analysis_config.json` 
Contains project configuration and selected agents:
```json
{
  "project_name": "daytrader",
  "mode": "hands-off", 
  "selected_agents": [
    "repomix-analyzer",
    "solution-architect", 
    "performance-analyst"
  ]
}
```

### `CLAUDE.md`
Contains agent execution instructions and workflow rules.

### `.repomix.config.json` 
Configures which files to include/exclude during compression.

## Troubleshooting

### Common Issues

1. **Missing Repomix Summary**
   ```
   ❌ Repomix summary not found: output/reports/repomix-summary.md
   ```
   **Solution**: Run `repomix --config .repomix.config.json codebase/daytrader/`

2. **Agent Execution Failures**
   - Ensure Claude Code is installed and accessible
   - Verify agent names match those in `.claude/agents/`
   - Check that `output/` directories exist

3. **Large Codebase Issues**
   - Ensure Repomix summary was generated successfully
   - Check `.repomix.config.json` excludes unnecessary files
   - Consider running agents individually rather than in batch

## Requirements

- **Claude Code CLI**: [Installation guide](https://claude.ai/code)
- **Python 3.7+**: For automation scripts
- **Repomix**: `npm install -g repomix` (for token optimization)
- **Your codebase**: Place in `codebase/[project-name]/`

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Mermaid Diagram Syntax](https://mermaid.js.org) 
- [Repomix Documentation](https://github.com/repomix/repomix)

---

**Framework Focus**: Documentation and diagram generation  
**Token Optimization**: 80% reduction via Repomix compression  
**Automation**: Python scripts + n8n workflow integration  
**Target Project**: `daytrader` (configurable in `analysis_config.json`)