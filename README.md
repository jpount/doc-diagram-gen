# Simplified Documentation Framework

Generate comprehensive documentation for any codebase with just 5 core agents and 2 simple modes.

## 🚀 Quick Start (2 minutes)

```bash
# 1. Run setup
python3 setup_simple.py

# 2. Copy your code
cp -r /your/code codebase/my-project/

# 3. Generate Repomix (REQUIRED - 80% token savings)
repomix --config .repomix.config.json codebase/my-project/

# 4. Run analysis (choose one)
# Option A: Quick mode (automated, 1-2 hours)
python3 run_analysis.py --mode quick

# Option B: Guided mode (interactive, 3-4 hours)
# Start Claude Code and follow CLAUDE.md
```

## 📚 Two Simple Modes

### Quick Mode (Hands-off)
- **Duration**: 1-2 hours
- **Interaction**: None
- **Use when**: You want fast results without interaction
- **Works with**: CLI or n8n automation

### Guided Mode (Interactive)
- **Duration**: 3-4 hours  
- **Interaction**: Review checkpoints between phases
- **Use when**: You want to review and guide the analysis
- **Works with**: Claude Code CLI only

## 📋 Choose Your Documentation

Instead of selecting agents, simply choose what documentation you need:

- ✅ **Architecture Documentation** - System design and structure
- ✅ **Business Rules** - Domain logic and workflows
- ✅ **Security Assessment** - Vulnerabilities and fixes
- ✅ **Performance Analysis** - Bottlenecks and optimizations
- ✅ **API Documentation** - Endpoints and interfaces
- ✅ **Code Quality** - Technical debt and improvements
- ✅ **Migration Plan** - Modernization roadmap

The framework automatically determines which agents and knowledge to use.

## 🤖 Only 5 Core Agents

We've simplified from 20+ specialized agents to just 5:

1. **architect-agent** - Analyzes architecture and design
2. **developer-agent** - Assesses code quality and technical debt
3. **analyst-agent** - Extracts business logic, performance, and security insights
4. **diagram-agent** - Creates all visualizations
5. **doc-writer-agent** - Generates final documentation

Each agent dynamically loads technology-specific knowledge based on your stack.

## 🧠 Smart Knowledge System

```
framework/knowledge/
├── languages/     # Java, .NET, Python, etc.
├── frameworks/    # Spring, Angular, React, etc.
├── patterns/      # Microservices, DDD, etc.
└── domains/       # E-commerce, Banking, etc.
```

Agents automatically load relevant knowledge files based on detected technologies.

## 🔄 n8n Automation

For hands-off documentation generation:

```bash
# Start n8n
cd n8n
./start_n8n_minimal.sh

# Import workflow
# Import: n8n/workflows/simplified_quick_mode.json

# Trigger analysis
# Set project_name and run
```

## 📊 What You Get

### Output Structure
```
output/
├── docs/              # Generated documentation
│   ├── ARCHITECTURE.md
│   ├── BUSINESS-RULES.md
│   ├── SECURITY-REPORT.md
│   └── ...
├── diagrams/          # Visual diagrams
│   ├── system-architecture.mmd
│   ├── data-flow.mmd
│   └── ...
└── context/           # Single context file
    └── analysis_context.json
```

## 🎯 Key Improvements

### Before (Complex)
- 20+ specialized agents to choose from
- Complex agent selection process
- Multiple context files to manage
- 1000+ line setup script
- Confusing for new users

### After (Simple)
- Only 5 core agents
- Choose documentation types, not agents
- Single context file
- 300 line setup script
- Clear two-mode approach

## 💡 Philosophy

Inspired by [Agent-OS](https://buildermethods.com/agent-os), we've adopted:
- **Fewer, smarter agents** with contextual knowledge
- **Document-driven selection** instead of agent selection
- **Simplified context passing** with single file
- **Clear mode separation** for different use cases

## 🛠 Advanced Usage

### Custom Documentation Types

Add new documentation types in `framework/agents/core_agents.json`:

```json
"custom_type": {
  "name": "Custom Documentation",
  "agents": ["architect-agent", "analyst-agent"],
  "outputs": ["CUSTOM-DOC.md"]
}
```

### Adding Technology Support

Add knowledge files to `framework/knowledge/`:

1. Create `framework/knowledge/languages/rust.md`
2. Add detection patterns, best practices, anti-patterns
3. Framework auto-detects and uses it

## 📈 Token Efficiency

- **With Repomix**: ~50,000 tokens for medium project
- **Without Repomix**: ~250,000+ tokens (5x more!)
- **Always run Repomix first!**

## 🆘 Troubleshooting

### Repomix not found
```bash
npm install -g repomix
```

### Context not loading
```bash
# Check context file exists
ls -la output/context/analysis_context.json

# Reset context
rm -rf output/context/*
python3 setup_simple.py
```

### n8n connection issues
```bash
# Ensure host agent server is running
python3 n8n/host_agent_server.py

# Check Docker services
docker ps
```

## 🚦 Getting Started

1. **Run setup**: `python3 setup_simple.py`
2. **Choose mode**: Quick or Guided
3. **Select docs**: Pick what you need
4. **Copy code**: Place in codebase/
5. **Run Repomix**: Generate summary
6. **Start analysis**: CLI or n8n

That's it! Simple, efficient documentation generation.

---

**Version**: 2.0 (Simplified)  
**Token Savings**: 80% with Repomix  
**Time to Docs**: 1-4 hours