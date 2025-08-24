# MCP Troubleshooting Guide

## Issue: MCPs Not Available in Claude Code

### Quick Checklist

1. **✓ Verify .mcp.json exists** 
   - Located at: `/Users/jp/work/xxx/doc-diagram-gen/.mcp.json`
   - Status: EXISTS ✓

2. **Restart Claude Code**
   - MCPs are loaded when Claude Code starts
   - **Action Required**: Close and reopen Claude Code completely
   - Open the project folder directly: `File > Open Folder > /Users/jp/work/xxx/doc-diagram-gen`

3. **Check Claude Code is opening the correct directory**
   - Claude Code must open the directory containing .mcp.json
   - NOT a parent or child directory
   - The folder path in Claude Code should be: `/Users/jp/work/xxx/doc-diagram-gen`

4. **Verify MCP Server Dependencies**
   ```bash
   # Check if npm is installed
   npm --version
   
   # Check if uvx/uv is installed (for Serena)
   uvx --version
   # or
   uv --version
   ```

5. **Test MCP Configuration**
   ```bash
   # From project root
   python3 framework/scripts/test_mcp_integration.py
   ```

### Steps to Enable MCPs

1. **Close Claude Code completely**

2. **Open Terminal and navigate to project**
   ```bash
   cd /Users/jp/work/xxx/doc-diagram-gen
   ```

3. **Verify .mcp.json is valid JSON**
   ```bash
   python3 -m json.tool .mcp.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON"
   ```

4. **Open Claude Code with the project folder**
   ```bash
   # If you have Claude Code CLI installed
   claude /Users/jp/work/xxx/doc-diagram-gen
   
   # Or open Claude Code and use File > Open Folder
   ```

5. **Check MCP availability**
   - In Claude Code, type: `/mcp`
   - You should see available MCPs listed

### If MCPs Still Don't Appear

1. **Check Claude Code Settings**
   - Open Claude Code settings
   - Look for MCP or Model Context Protocol section
   - Ensure MCPs are enabled

2. **Check for Error Messages**
   - Open Claude Code developer console (if available)
   - Look for MCP-related errors

3. **Verify Node.js MCP Servers**
   ```bash
   # Test filesystem MCP
   npx -y @modelcontextprotocol/server-filesystem --help
   
   # Test memory MCP
   npx -y @modelcontextprotocol/server-memory --help
   ```

4. **Verify Python MCP (Serena)**
   ```bash
   # Test if uvx can run Serena
   uvx --from git+https://github.com/oraios/serena serena --help
   ```

### Common Issues and Solutions

#### Issue: "No MCP servers configured"
**Solution**: Ensure you opened the folder containing .mcp.json, not a parent/child folder

#### Issue: MCP servers fail to start
**Solution**: Check the server logs in Claude Code and ensure dependencies are installed

#### Issue: .mcp.json changes not detected
**Solution**: Restart Claude Code after modifying .mcp.json

### Manual MCP Test

Test if MCP servers can run manually:

```bash
# Test filesystem MCP
npx -y @modelcontextprotocol/server-filesystem /Users/jp/work/xxx/doc-diagram-gen

# If this works, the issue is with Claude Code loading, not the MCP configuration
```

### Current Configuration Status

- **CLAUDE.md**: ✓ Created
- **.mcp.json**: ✓ Exists at project root
- **Project**: daytrader
- **Analysis Mode**: DOCUMENTATION_ONLY
- **Documentation Mode**: GUIDED (assumed)

### Next Steps After MCPs Are Working

1. Run: `repomix --config .repomix.config.json codebase/daytrader/`
2. In Claude Code with MCPs available:
   - Use `@serena` to activate the project
   - Use `@mcp-orchestrator` to begin analysis
   - Follow the workflow in CLAUDE.md

### Need More Help?

1. Check `framework/docs/MCP_CONFIGURATION_GUIDE.md`
2. Run `python3 framework/scripts/test_mcp_integration.py` for detailed diagnostics
3. Ensure Claude Code is up to date

---
*Note: The most common issue is that Claude Code needs to be restarted after .mcp.json is created or modified.*