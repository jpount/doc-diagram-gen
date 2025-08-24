# MCP Configuration Guide

## Complete Setup for Model Context Protocol Integration

This guide ensures proper MCP configuration for Claude Code to achieve 90%+ token optimization.

## Table of Contents
1. [Required Files](#required-files)
2. [File Configurations](#file-configurations)
3. [Troubleshooting](#troubleshooting)
4. [Verification](#verification)

## Required Files

### 1. `.mcp.json` (PROJECT ROOT - CRITICAL)
**Location**: `/Users/jp/work/xxx/doc-diagram-gen/.mcp.json`
**Purpose**: Defines MCP servers for Claude Code to recognize and use

```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena",
        "start-mcp-server",
        "--context",
        "ide-assistant",
        "--project",
        "${PWD}/codebase"
      ],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "${PWD}"
      ],
      "env": {}
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ],
      "env": {}
    }
  }
}
```

### 2. `.claude/settings.local.json`
**Location**: `/Users/jp/work/xxx/doc-diagram-gen/.claude/settings.local.json`
**Purpose**: Claude Code project settings

```json
{
  "enableAllProjectMcpServers": false,
  "enabledMcpjsonServers": [
    "filesystem",
    "memory"
  ],
  "agentDirectories": [
    ".claude/agents"
  ]
}
```

**Important Notes:**
- **Default MCPs**: Only `filesystem` and `memory` are enabled by default (no installation required)
- **Serena**: NOT included by default - it's optional and requires uvx/uv
- **Selective enablement**: `enableAllProjectMcpServers: false` means only explicitly listed MCPs are enabled
- **To enable Serena**: Add `"serena"` to the array AND remove `"disabled": true` from `.mcp.json`

### 3. `.repomix.config.json`
**Location**: `/Users/jp/work/xxx/doc-diagram-gen/.repomix.config.json`
**Purpose**: Repomix compression configuration

Already configured and ready to use.

## File Configurations

### Updating Project Path in .mcp.json

When analyzing a different codebase, update the Serena project path:

```json
"--project",
"${PWD}/codebase/your-project-name"  // Change this line
```

### Common Project Paths

| Project | Path Configuration |
|---------|-------------------|
| All Repositories | `"${PWD}/codebase"` |
| Specific Repository | `"${PWD}/codebase/repo-name"` |
| Generic | `"${PWD}/codebase"` |
| Custom | `"${PWD}/path/to/your/code"` |

## Installation Requirements

### 1. Serena MCP (Optional - for 60% token reduction)
```bash
# Only required if you want to enable Serena
# Requires Python and uv/uvx
pip install uv
# Or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Repomix
```bash
# Requires Node.js
npm install -g repomix
```

### 3. Node.js MCP Servers
```bash
# Automatically installed via npx
# No manual installation needed
```

## Troubleshooting

### Issue: "MCP server 'serena' not found"

**Solution 1**: Ensure `.mcp.json` exists in project root
```bash
ls -la .mcp.json
```

**Solution 2**: Restart Claude Code after creating `.mcp.json`

**Solution 3**: Check uvx is installed
```bash
which uvx || pip install uv
```

### Issue: "Cannot find codebase"

**Solution**: Update the project path in `.mcp.json`:
```json
"--project",
"${PWD}/actual/path/to/code"
```

### Issue: "Repomix command not found"

**Solution**: Install Repomix globally
```bash
npm install -g repomix
```

### Issue: "npx not found"

**Solution**: Install Node.js
```bash
# macOS
brew install node

# Linux
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Verification

### Quick Test
```bash
# Run the test script
./test-mcp-integration.sh
```

### Manual Verification

1. **Check .mcp.json exists**:
```bash
cat .mcp.json | jq .
```

2. **Verify Serena path**:
```bash
grep -A2 "serena" .mcp.json | grep project
```

3. **Test Repomix**:
```bash
repomix --version
```

4. **Check Claude settings**:
```bash
cat .claude/settings.local.json | jq .enabledMcpjsonServers
```

## Usage in Claude Code

### After Configuration

1. **Restart Claude Code** to load MCP configurations

2. **Verify MCPs are available**:
   - Type `@` in Claude Code
   - You should see available MCPs like `@serena`

3. **Use Serena**:
```
@serena activate ./codebase
@serena onboarding
```

4. **Run Repomix**:
```bash
repomix --config .repomix.config.json
```

5. **Start analysis**:
```
@mcp-orchestrator
@repomix-analyzer
```

## Best Practices

### 1. Always Configure Before Analysis
```bash
# Setup sequence
./setup-mcp.sh
./test-mcp-integration.sh
```

### 2. Update Paths for New Projects
Edit `.mcp.json` when switching projects:
```json
"--project",
"${PWD}/codebase/new-project"
```

### 3. Cache Management
Clear cache when switching projects:
```bash
rm -rf .mcp-cache/*
```

### 4. Token Optimization Priority
1. Always run Repomix first (80% reduction)
2. Use Serena for searches (60% reduction)
3. Combine both for 90%+ savings

## Common Configurations

### Enterprise Java Project
```json
{
  "mcpServers": {
    "serena": {
      "args": [
        "...",
        "--project",
        "${PWD}/codebase/enterprise-app",
        "--context",
        "java-enterprise"
      ]
    }
  }
}
```

### Microservices Project
```json
{
  "mcpServers": {
    "serena": {
      "args": [
        "...",
        "--project",
        "${PWD}/codebase/microservices",
        "--context",
        "microservices"
      ]
    }
  }
}
```

### Monorepo Project
```json
{
  "mcpServers": {
    "serena": {
      "args": [
        "...",
        "--project",
        "${PWD}/codebase",
        "--context",
        "monorepo"
      ]
    }
  }
}
```

## Support

For issues or questions:
1. Check `docs/MCP_USAGE_GUIDE.md`
2. Run `./test-mcp-integration.sh` for diagnostics
3. Review `.mcp.json` configuration
4. Ensure all dependencies are installed

---

**Remember**: The `.mcp.json` file in the project root is CRITICAL for MCP recognition in Claude Code!