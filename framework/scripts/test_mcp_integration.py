#!/usr/bin/env python3
"""
MCP Integration Test Script
Cross-platform testing for MCP configurations
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

class Colors:
    """Terminal colors (cross-platform)"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    @staticmethod
    def enable_windows():
        """Enable ANSI colors on Windows 10+"""
        if sys.platform == 'win32':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                Colors.disable()
    
    @staticmethod
    def disable():
        """Disable colors"""
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.RESET = ''

class MCPIntegrationTest:
    """Tests MCP integration and configuration"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.resolve()
        self.project_root = self.script_dir.parent.parent
        self.errors = []
        self.warnings = []
        self.successes = []
        
        # Enable colors
        Colors.enable_windows()
    
    def run_tests(self) -> int:
        """Run all integration tests"""
        print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BLUE}║              MCP Integration Test Suite                   ║{Colors.RESET}")
        print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
        
        # Run tests
        self.test_mcp_json()
        print()
        self.test_claude_settings()
        print()
        self.test_repomix()
        print()
        self.test_nodejs_mcps()
        print()
        self.test_python_requirements()
        print()
        self.test_project_structure()
        print()
        self.test_codebase_configuration()
        print()
        
        # Show summary
        self.show_summary()
        
        # Return exit code
        return 1 if self.errors else 0
    
    def test_mcp_json(self):
        """Test .mcp.json configuration"""
        print(f"{Colors.YELLOW}Test 1: Checking .mcp.json configuration...{Colors.RESET}")
        
        mcp_file = self.project_root / ".mcp.json"
        
        if not mcp_file.exists():
            self.errors.append(".mcp.json not found - MCPs won't work without it!")
            print(f"{Colors.RED}❌ .mcp.json not found{Colors.RESET}")
            print(f"   Run: python setup.py or ./setup.sh to create it")
            return
        
        self.successes.append(".mcp.json exists")
        print(f"{Colors.GREEN}✅ .mcp.json exists{Colors.RESET}")
        
        # Validate JSON syntax
        try:
            with open(mcp_file, 'r') as f:
                mcp_config = json.load(f)
            self.successes.append(".mcp.json is valid JSON")
            print(f"{Colors.GREEN}✅ .mcp.json is valid JSON{Colors.RESET}")
        except json.JSONDecodeError as e:
            self.errors.append(f".mcp.json has invalid JSON: {e}")
            print(f"{Colors.RED}❌ .mcp.json has invalid JSON syntax{Colors.RESET}")
            return
        
        # Check for required MCPs
        if 'mcpServers' in mcp_config:
            if 'serena' in mcp_config['mcpServers']:
                self.successes.append("Serena MCP configured")
                print(f"{Colors.GREEN}✅ Serena MCP configured{Colors.RESET}")
            else:
                self.warnings.append("Serena MCP not configured")
                print(f"{Colors.YELLOW}⚠️  Serena MCP not configured{Colors.RESET}")
            
            # Check other useful MCPs
            for mcp in ['filesystem', 'memory', 'fetch']:
                if mcp in mcp_config['mcpServers']:
                    print(f"   ✓ {mcp} MCP configured")
    
    def test_claude_settings(self):
        """Test Claude Code settings"""
        print(f"{Colors.YELLOW}Test 2: Checking Claude Code settings...{Colors.RESET}")
        
        settings_file = self.project_root / ".claude" / "settings.local.json"
        
        if not settings_file.exists():
            self.warnings.append("settings.local.json not found")
            print(f"{Colors.YELLOW}⚠️  settings.local.json not found{Colors.RESET}")
            return
        
        print(f"{Colors.GREEN}✅ settings.local.json exists{Colors.RESET}")
        
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            
            # Check if MCPs are enabled
            if settings.get('enableAllProjectMcpServers'):
                self.successes.append("MCPs enabled in settings")
                print(f"{Colors.GREEN}✅ MCPs enabled in settings{Colors.RESET}")
            elif 'serena' in settings.get('enabledMcpjsonServers', []):
                self.successes.append("Serena enabled in settings")
                print(f"{Colors.GREEN}✅ Serena enabled in settings{Colors.RESET}")
            else:
                self.warnings.append("MCPs may not be properly enabled")
                print(f"{Colors.YELLOW}⚠️  MCPs may not be properly enabled{Colors.RESET}")
            
            # Check hooks are Python
            if 'hooks' in settings:
                python_hooks = 0
                shell_hooks = 0
                for hook_type in settings['hooks'].values():
                    for hook_config in hook_type:
                        for hook in hook_config.get('hooks', []):
                            cmd = hook.get('command', '')
                            if 'python' in cmd or '.py' in cmd:
                                python_hooks += 1
                            elif '.sh' in cmd:
                                shell_hooks += 1
                
                if python_hooks > 0:
                    print(f"   ✓ {python_hooks} Python hooks configured (cross-platform)")
                if shell_hooks > 0:
                    print(f"   ⚠️  {shell_hooks} shell hooks found (not cross-platform)")
        
        except Exception as e:
            self.warnings.append(f"Error reading settings: {e}")
    
    def test_repomix(self):
        """Test Repomix installation and configuration"""
        print(f"{Colors.YELLOW}Test 3: Testing Repomix...{Colors.RESET}")
        
        # Check if Repomix is installed
        repomix_available = self.check_command("repomix --version")
        
        if repomix_available:
            self.successes.append("Repomix installed")
            print(f"{Colors.GREEN}✅ Repomix installed{Colors.RESET}")
        else:
            self.warnings.append("Repomix not installed")
            print(f"{Colors.YELLOW}⚠️  Repomix not installed{Colors.RESET}")
            print("   Install with: npm install -g repomix")
        
        # Check Repomix config
        repomix_config = self.project_root / ".repomix.config.json"
        
        if repomix_config.exists():
            self.successes.append("Repomix config exists")
            print(f"{Colors.GREEN}✅ Repomix config exists{Colors.RESET}")
            
            # Test Repomix if available
            if repomix_available and (self.project_root / "codebase").exists():
                print("   Testing Repomix availability...")
                try:
                    result = subprocess.run(
                        ["repomix", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print(f"   {Colors.GREEN}✅ Repomix test successful{Colors.RESET}")
                    else:
                        print(f"   {Colors.YELLOW}⚠️  Repomix test failed{Colors.RESET}")
                except Exception:
                    print(f"   {Colors.YELLOW}⚠️  Could not test Repomix{Colors.RESET}")
        else:
            self.warnings.append(".repomix.config.json not found")
            print(f"{Colors.YELLOW}⚠️  .repomix.config.json not found{Colors.RESET}")
    
    def test_nodejs_mcps(self):
        """Test Node.js MCP availability"""
        print(f"{Colors.YELLOW}Test 4: Checking Node.js MCP servers...{Colors.RESET}")
        
        # Check for npx
        if self.check_command("npx --version"):
            self.successes.append("npx available")
            print(f"{Colors.GREEN}✅ npx available for MCP servers{Colors.RESET}")
            
            # Test specific MCPs
            mcps_to_test = [
                "@modelcontextprotocol/server-filesystem",
                "@modelcontextprotocol/server-memory"
            ]
            
            for mcp in mcps_to_test:
                # Note: We can't actually test these without installing
                # Just check if npx is available
                print(f"   ℹ️  {mcp.split('/')[-1]} (will install on first use)")
        else:
            self.warnings.append("npx not available - Node.js MCPs won't work")
            print(f"{Colors.YELLOW}⚠️  npx not available - Node.js MCPs won't work{Colors.RESET}")
            print("   Install Node.js from: https://nodejs.org")
    
    def test_python_requirements(self):
        """Test Python and related requirements"""
        print(f"{Colors.YELLOW}Test 5: Checking Python requirements...{Colors.RESET}")
        
        # Check Python version
        if sys.version_info >= (3, 7):
            self.successes.append(f"Python {sys.version.split()[0]} available")
            print(f"{Colors.GREEN}✅ Python {sys.version.split()[0]} available{Colors.RESET}")
        else:
            self.errors.append(f"Python {sys.version.split()[0]} too old (need 3.7+)")
            print(f"{Colors.RED}❌ Python version too old (need 3.7+){Colors.RESET}")
        
        # Check for uv/uvx (for Serena)
        if self.check_command("uvx --version") or self.check_command("uv --version"):
            print(f"{Colors.GREEN}✅ uvx/uv available for Serena{Colors.RESET}")
        else:
            self.warnings.append("uvx not found - Serena may not work")
            print(f"{Colors.YELLOW}⚠️  uvx not found - Serena may not work{Colors.RESET}")
            print("   Install with: pip install uv")
    
    def test_project_structure(self):
        """Test project directory structure"""
        print(f"{Colors.YELLOW}Test 6: Checking project structure...{Colors.RESET}")
        
        required_dirs = [
            ".claude",
            ".claude/agents",
            ".claude/hooks",
            "framework",
            "framework/scripts",
            "framework/mcp-configs",
            "framework/templates",
            "framework/docs",
            "output",
            "output/docs",
            "output/diagrams",
            "output/reports",
            ".mcp-cache"
        ]
        
        all_exist = True
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                print(f"{Colors.GREEN}✅ {dir_path} exists{Colors.RESET}")
            else:
                all_exist = False
                self.warnings.append(f"{dir_path} missing")
                print(f"{Colors.YELLOW}⚠️  {dir_path} missing{Colors.RESET}")
        
        if all_exist:
            self.successes.append("All required directories exist")
    
    def test_codebase_configuration(self):
        """Test codebase path configuration"""
        print(f"{Colors.YELLOW}Test 7: Checking codebase configuration...{Colors.RESET}")
        
        codebase_dir = self.project_root / "codebase"
        
        if not codebase_dir.exists():
            self.warnings.append("codebase directory missing")
            print(f"{Colors.YELLOW}⚠️  No codebase directory{Colors.RESET}")
            print("   Create with: mkdir codebase")
            return
        
        # Check for projects
        projects = [d for d in codebase_dir.iterdir() if d.is_dir()]
        
        if projects:
            print(f"{Colors.GREEN}✅ Found {len(projects)} project(s) in codebase/{Colors.RESET}")
            for project in projects[:3]:  # Show first 3
                print(f"   - {project.name}")
            
            # Check if .mcp.json is configured
            mcp_file = self.project_root / ".mcp.json"
            if mcp_file.exists():
                with open(mcp_file, 'r') as f:
                    content = f.read()
                    
                # Check if codebase path is configured
                if "${PWD}/codebase" in content or "codebase" in content:
                    print(f"{Colors.GREEN}✅ .mcp.json configured for codebase directory{Colors.RESET}")
                    
                    # Check if specific project is configured
                    for project in projects:
                        if project.name in content:
                            print(f"{Colors.GREEN}✅ Project '{project.name}' specifically configured{Colors.RESET}")
                            break
                    else:
                        print(f"{Colors.BLUE}ℹ️  .mcp.json points to entire codebase/ directory{Colors.RESET}")
                        print(f"   This will analyze all projects: {', '.join([p.name for p in projects[:3]])}")
                        if len(projects) == 1:
                            print(f"   To target only '{projects[0].name}', update Serena's --project arg to:")
                            print(f"   ${{PWD}}/codebase/{projects[0].name}")
                else:
                    self.warnings.append("Codebase path not found in .mcp.json")
                    print(f"{Colors.YELLOW}⚠️  Codebase path not configured in .mcp.json{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️  No projects found in codebase/{Colors.RESET}")
            print("   Place your code in: codebase/[project-name]/")
    
    def check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            cmd_parts = command.split()
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def show_summary(self):
        """Display test summary"""
        print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BLUE}║                    Test Summary                           ║{Colors.RESET}")
        print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
        
        # Count results
        success_count = len(self.successes)
        warning_count = len(self.warnings)
        error_count = len(self.errors)
        
        print(f"Results:")
        print(f"  {Colors.GREEN}✅ Passed: {success_count}{Colors.RESET}")
        print(f"  {Colors.YELLOW}⚠️  Warnings: {warning_count}{Colors.RESET}")
        print(f"  {Colors.RED}❌ Errors: {error_count}{Colors.RESET}")
        
        if self.errors:
            print(f"\n{Colors.RED}Critical issues found. Please fix:{Colors.RESET}")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}Warnings (optional improvements):{Colors.RESET}")
            for warning in self.warnings[:5]:  # Show first 5
                print(f"  • {warning}")
        
        # Final verdict
        if error_count > 0:
            print(f"\n{Colors.RED}❌ Critical issues must be fixed for MCPs to work{Colors.RESET}")
            print("\nRecommended actions:")
            print("1. Run: python setup.py")
            print("2. Ensure .mcp.json exists in project root")
            print("3. Install missing tools")
        elif warning_count > 5:
            print(f"\n{Colors.YELLOW}⚠️  MCP integration partially configured{Colors.RESET}")
            print("\nRecommended actions:")
            print("1. Install Repomix: npm install -g repomix")
            print("2. Install uvx: pip install uv")
            print("3. Verify project path in .mcp.json")
        else:
            print(f"\n{Colors.GREEN}✅ MCP integration properly configured!{Colors.RESET}")
            print("\nYou can now:")
            print("1. Run: repomix --config .repomix.config.json codebase/")
            print("2. Use @mcp-orchestrator in Claude Code")
            print("3. Access Serena with @serena commands")
        
        print(f"\nFor detailed setup: see framework/docs/MCP_USAGE_GUIDE.md")

def main():
    """Main entry point"""
    tester = MCPIntegrationTest()
    exit_code = tester.run_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()