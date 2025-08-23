# Multi-Repository Support Guide

## Overview
The framework is designed to be completely reusable and can analyze any codebase or multiple repositories. This guide explains how to configure and use the framework with different repository structures.

## Repository Structure

The framework expects repositories to be placed in the `codebase/` directory:

```
doc-diagram-gen/
├── codebase/
│   ├── repo1/          # First repository
│   ├── repo2/          # Second repository
│   ├── repo3/          # Third repository
│   └── ...             # Any number of repositories
├── framework/          # Framework files (don't modify)
├── output/             # Generated documentation
└── .mcp.json          # MCP configuration
```

## Configuration Options

### Option 1: Analyze All Repositories
Configure MCP to analyze all repositories in the codebase directory:

```json
{
  "mcpServers": {
    "serena": {
      "args": [
        ...
        "--project",
        "${PWD}/codebase"
      ]
    }
  }
}
```

**Benefits:**
- Analyze multiple related repositories together
- Cross-repository dependency analysis
- Comprehensive documentation across all projects
- Single analysis run for entire codebase

### Option 2: Analyze Specific Repository
Configure MCP to analyze a specific repository:

```json
{
  "mcpServers": {
    "serena": {
      "args": [
        ...
        "--project",
        "${PWD}/codebase/specific-repo"
      ]
    }
  }
}
```

**Benefits:**
- Focused analysis on single project
- Faster analysis for large codebases
- Repository-specific documentation
- Lower memory usage

## Setup Process

### Using the Setup Script

The `setup_mcp.py` script now supports multi-repository configuration:

```bash
python3 framework/scripts/setup_mcp.py
```

You'll be prompted with:
```
MCP Configuration Options:
1. Analyze all repositories in codebase/ directory
2. Analyze a specific repository

Select option (1 or 2) [1]: 
```

### Manual Configuration

1. **Copy the example configuration:**
   ```bash
   cp framework/mcp-configs/mcp.example.json .mcp.json
   ```

2. **Edit .mcp.json:**
   - For all repositories: Use `"${PWD}/codebase"`
   - For specific repo: Use `"${PWD}/codebase/repo-name"`

3. **Update .repomix.config.json:**
   - For all repositories:
     ```json
     "include": ["codebase/**/*"]
     ```
   - For specific repo:
     ```json
     "include": ["codebase/repo-name/**/*"]
     ```

## Working with Multiple Repositories

### Adding a New Repository

1. **Clone or copy the repository:**
   ```bash
   # Clone from git
   git clone https://github.com/org/repo.git codebase/repo-name
   
   # Or copy existing code
   cp -r /path/to/repo codebase/repo-name
   ```

2. **Update configuration (if analyzing specific repo):**
   ```bash
   python3 framework/scripts/setup_mcp.py
   # Select option 2 and choose the new repository
   ```

### Switching Between Repositories

To switch analysis focus between repositories:

1. **Run the setup script:**
   ```bash
   python3 framework/scripts/setup_mcp.py
   ```

2. **Choose option 2** and select the repository to analyze

3. **Restart Claude Code** to apply the new configuration

### Analyzing Multiple Repositories Together

1. **Place all repositories in codebase/:**
   ```bash
   codebase/
   ├── frontend-app/
   ├── backend-api/
   ├── shared-libs/
   └── mobile-app/
   ```

2. **Configure for all repositories:**
   ```bash
   python3 framework/scripts/setup_mcp.py
   # Select option 1
   ```

3. **Run analysis agents** - they will analyze all repositories as a unified system

## Agent Behavior with Multiple Repositories

### When Analyzing All Repositories

Agents will:
- Identify cross-repository dependencies
- Generate unified architecture diagrams
- Extract business rules from all repos
- Create comprehensive migration strategy
- Document inter-service communication

### When Analyzing Specific Repository

Agents will:
- Focus on single repository structure
- Generate repository-specific documentation
- Identify external dependencies
- Create targeted migration plan
- Document repository boundaries

## Repomix Integration

### How Repomix Works
Repomix combines all source files from the configured scope into a **single markdown file**. This is ideal for:
- Token optimization (80% reduction)
- Unified analysis across multiple repositories
- Complete codebase context in one file

### Repomix Output Examples

#### For All Repositories
```bash
repomix --config .repomix.config.json
```
Creates: `output/reports/all-repos-repomix.md` containing:
- All files from all repositories in codebase/
- Combined into one searchable document
- Organized by repository and file path
- Perfect for cross-repository analysis

#### For Specific Repository
```bash
repomix --config .repomix.config.json
```
Creates: `output/reports/[repo-name]-repomix.md` containing:
- All files from the specific repository
- Single document for focused analysis
- Repository-specific context

### Repomix Configuration

#### Analyzing Multiple Repositories
```json
{
  "output": {
    "filePath": "output/reports/all-repos-repomix.md",
    "style": "markdown"
  },
  "include": [
    "codebase/**/*"
  ],
  "ignore": {
    "patterns": [
      "**/node_modules/**",
      "**/dist/**",
      "**/build/**"
    ]
  }
}
```

This creates **one combined file** with all repositories, making it easy for agents to:
- See the complete system architecture
- Identify cross-repository dependencies
- Analyze shared patterns
- Generate unified documentation

## Output Organization

### Documentation Structure
```
output/
├── docs/
│   ├── 00-executive-summary.md
│   ├── 01-archaeological-analysis.md
│   ├── 02-business-logic-analysis.md
│   ├── 03-visual-architecture.md
│   ├── 04-performance-analysis.md
│   ├── 05-security-analysis.md
│   └── 06-modernization-strategy.md
├── diagrams/
│   ├── architecture/
│   ├── sequence/
│   └── flow/
└── reports/
    ├── all-repos-repomix.md      # Combined codebase (if analyzing all)
    └── [repo-name]-repomix.md    # Single repo (if specific)
```

## Best Practices

### Repository Organization

1. **Use clear naming conventions:**
   ```
   codebase/
   ├── frontend-angular/
   ├── backend-springboot/
   ├── database-scripts/
   └── mobile-react-native/
   ```

2. **Group related repositories:**
   ```
   codebase/
   ├── microservices/
   │   ├── user-service/
   │   ├── order-service/
   │   └── payment-service/
   └── libraries/
       ├── common-utils/
       └── shared-models/
   ```

3. **Exclude build artifacts:**
   Add to `.repomix.config.json`:
   ```json
   "ignore": {
     "patterns": [
       "**/node_modules/**",
       "**/target/**",
       "**/dist/**",
       "**/build/**"
     ]
   }
   ```

### Configuration Management

1. **Version control configurations:**
   ```bash
   # Save your configuration
   cp .mcp.json .mcp.json.backup
   cp .repomix.config.json .repomix.config.json.backup
   ```

2. **Repository-specific configs:**
   ```bash
   # Create named configurations
   cp .mcp.json .mcp.frontend.json
   cp .mcp.json .mcp.backend.json
   ```

3. **Quick switching:**
   ```bash
   # Switch to frontend analysis
   cp .mcp.frontend.json .mcp.json
   ```

## Examples

### Example 1: Microservices Architecture
```
codebase/
├── api-gateway/
├── user-service/
├── product-service/
├── order-service/
└── notification-service/
```

Configure to analyze all services together:
```json
"--project": "${PWD}/codebase"
```

### Example 2: Monorepo Structure
```
codebase/
└── monorepo/
    ├── packages/
    ├── apps/
    └── libs/
```

Configure for the monorepo:
```json
"--project": "${PWD}/codebase/monorepo"
```

### Example 3: Multiple Independent Projects
```
codebase/
├── legacy-system/
├── new-platform/
└── migration-tools/
```

Analyze each independently by switching configuration.

## Troubleshooting

### Issue: "No codebase found"
**Solution:** Ensure repositories are in `codebase/` directory

### Issue: "daytrader hardcoded in .mcp.json"
**Solution:** Run `python3 framework/scripts/setup_mcp.py` to reconfigure

### Issue: "Analysis missing some repositories"
**Solution:** Check if configured for all repos (`codebase`) vs specific repo

### Issue: "Output files overwriting"
**Solution:** Output files are named based on configuration - backup previous outputs if needed

## Migration from Hardcoded Configuration

If you have an existing `.mcp.json` with hardcoded paths (e.g., `daytrader`):

1. **Backup existing configuration:**
   ```bash
   cp .mcp.json .mcp.json.old
   ```

2. **Reconfigure:**
   ```bash
   python3 framework/scripts/setup_mcp.py
   ```

3. **Choose your analysis scope:**
   - Option 1: Analyze all repositories
   - Option 2: Analyze specific repository

4. **Restart Claude Code** to apply changes

## Summary

The framework now fully supports:
- ✅ Multiple repositories in `codebase/` directory
- ✅ Flexible configuration for all or specific repos
- ✅ No hardcoded repository names
- ✅ Easy switching between analysis scopes
- ✅ Reusable for any codebase structure
- ✅ Cross-repository analysis capabilities