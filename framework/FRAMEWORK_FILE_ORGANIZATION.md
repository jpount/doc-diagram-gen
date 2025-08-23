# Framework File Organization

## Overview
All framework-related files are kept in the `framework/` directory to maintain clean separation between the framework and project-specific files.

## Directory Structure

```
framework/
├── docs/                           # Framework documentation
│   ├── CLAUDE_FRAMEWORK.md
│   ├── MCP_USAGE_GUIDE.md
│   └── MCP_CONFIGURATION_GUIDE.md
│
├── mcp-configs/                    # MCP configuration files
│   ├── mcp.template.json          # Template for setup script
│   ├── mcp.example.json           # Example configuration (NEW LOCATION)
│   ├── repomix.config.template.json
│   └── mcp-config.yaml
│
├── scripts/                        # Framework scripts (Python only)
│   ├── agent_orchestrator.py
│   ├── setup_mcp.py
│   ├── setup_tech_stack.py
│   ├── test_framework.py
│   ├── test_mcp_integration.py
│   └── validate_mermaid.py
│
└── templates/                      # Configuration templates
    ├── TARGET_TECH_STACK.template.md
    └── tech-stack-presets.yaml
```

## File Locations

### Framework Files (Stay in framework/)
These files are part of the framework and should not be modified:
- All scripts in `framework/scripts/`
- All templates in `framework/templates/`
- All MCP configs in `framework/mcp-configs/`
- All documentation in `framework/docs/`

### Generated Files (Go to project root)
These files are generated from templates and placed at the project root:
- `.mcp.json` - Generated from `framework/mcp-configs/mcp.template.json`
- `.repomix.config.json` - Generated from `framework/mcp-configs/repomix.config.template.json`
- `TARGET_TECH_STACK.md` - Generated from `framework/templates/TARGET_TECH_STACK.template.md`

### Project Files (Project root)
These are project-specific:
- `.claude/` - Agents and hooks
- `codebase/` - Your repositories
- `output/` - Generated documentation
- `logs/` - Log files

## Using Example Configuration

To use the example MCP configuration:

```bash
# Copy from framework to project root
cp framework/mcp-configs/mcp.example.json .mcp.json

# Edit as needed
nano .mcp.json
```

## Benefits of This Organization

1. **Clean Separation**: Framework files are isolated from project files
2. **Easy Updates**: Framework can be updated without affecting project files
3. **Reusability**: Entire framework directory can be copied to new projects
4. **No Confusion**: Clear distinction between templates and actual configs
5. **Version Control**: Framework can be versioned separately

## Important Notes

- **Never edit files in framework/** - They are templates and examples
- **Always work with generated files** at project root
- **Use setup scripts** to generate configurations from templates
- **Keep framework intact** for easy updates and portability

## Summary

The framework directory contains:
- ✅ All templates and examples
- ✅ All setup and utility scripts
- ✅ All framework documentation
- ✅ `mcp.example.json` (moved from root)

The project root contains:
- ✅ Generated configuration files
- ✅ Project-specific code and data
- ✅ Output and logs