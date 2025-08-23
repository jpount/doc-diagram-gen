#!/usr/bin/env python3
"""
MCP Setup and Configuration Script
Configures and validates MCP integrations for codebase analysis
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Optional, Tuple

class Colors:
    """Terminal colors (cross-platform)"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
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
        for attr in dir(Colors):
            if not attr.startswith('_') and attr.isupper():
                setattr(Colors, attr, '')


class MCPSetup:
    """MCP Setup and Configuration"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.resolve()
        self.framework_dir = self.script_dir.parent
        self.project_root = self.framework_dir.parent
        self.cache_dir = self.project_root / ".mcp-cache"
        
        # MCP configuration files
        self.mcp_json_path = self.project_root / ".mcp.json"
        self.repomix_config_path = self.project_root / ".repomix.config.json"
        self.mcp_template_path = self.framework_dir / "mcp-configs" / "mcp.template.json"
        self.repomix_template_path = self.framework_dir / "mcp-configs" / "repomix.config.template.json"
        
        # MCP availability
        self.mcp_status = {
            "repomix": False,
            "serena": False,
            "npm": False,
            "uvx": False,
            "node": False
        }
        
        # Enable colors
        Colors.enable_windows()
    
    def show_header(self):
        """Display setup header"""
        print(f"{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BLUE}║             MCP Setup and Configuration Wizard            ║{Colors.RESET}")
        print(f"{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
    
    def check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            result = subprocess.run(
                command.split() + ["--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def check_prerequisites(self):
        """Check for required tools"""
        print(f"{Colors.YELLOW}Checking prerequisites...{Colors.RESET}\n")
        
        # Check Node.js
        if self.check_command("node"):
            self.mcp_status["node"] = True
            print(f"{Colors.GREEN}✅ Node.js installed{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️  Node.js not found{Colors.RESET}")
        
        # Check npm
        if self.check_command("npm"):
            self.mcp_status["npm"] = True
            print(f"{Colors.GREEN}✅ npm installed{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️  npm not found{Colors.RESET}")
        
        # Check Python uvx (for Serena)
        if self.check_command("uvx") or self.check_command("uv"):
            self.mcp_status["uvx"] = True
            print(f"{Colors.GREEN}✅ uvx/uv installed (for Serena){Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️  uvx not found (needed for Serena MCP){Colors.RESET}")
            print(f"   Install with: {Colors.BLUE}pip install uv{Colors.RESET}")
        
        # Check Repomix
        if self.check_command("repomix"):
            self.mcp_status["repomix"] = True
            print(f"{Colors.GREEN}✅ Repomix installed{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️  Repomix not found{Colors.RESET}")
            print(f"   Install with: {Colors.BLUE}npm install -g repomix{Colors.RESET}")
    
    def install_repomix(self) -> bool:
        """Attempt to install Repomix"""
        if not self.mcp_status["npm"]:
            print(f"{Colors.RED}Cannot install Repomix without npm{Colors.RESET}")
            return False
        
        print(f"\n{Colors.YELLOW}Installing Repomix...{Colors.RESET}")
        try:
            result = subprocess.run(
                ["npm", "install", "-g", "repomix"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Repomix installed successfully{Colors.RESET}")
                self.mcp_status["repomix"] = True
                return True
            else:
                print(f"{Colors.RED}Failed to install Repomix{Colors.RESET}")
                print(f"Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"{Colors.RED}Error installing Repomix: {e}{Colors.RESET}")
            return False
    
    def create_mcp_json(self):
        """Create .mcp.json configuration"""
        print(f"\n{Colors.YELLOW}Configuring .mcp.json...{Colors.RESET}")
        
        # Check for existing file
        if self.mcp_json_path.exists():
            print(f"{Colors.GREEN}✅ .mcp.json already exists{Colors.RESET}")
            response = input("Overwrite existing configuration? (y/n): ").lower()
            if response != 'y':
                return
        
        # Get codebase path
        codebase_dir = self.project_root / "codebase"
        projects = []
        if codebase_dir.exists():
            projects = [d.name for d in codebase_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        # Determine analysis scope
        print(f"\n{Colors.CYAN}MCP Configuration Options:{Colors.RESET}")
        print("1. Analyze all repositories in codebase/ directory")
        print("2. Analyze a specific repository")
        
        choice = input("Select option (1 or 2) [1]: ").strip()
        
        if choice == "2" and projects:
            # Specific project selection
            print(f"\nFound repositories: {', '.join(projects)}")
            if len(projects) == 1:
                project_name = projects[0]
                print(f"Using: {project_name}")
            else:
                print("Enter repository name to analyze:")
                for i, proj in enumerate(projects, 1):
                    print(f"  {i}. {proj}")
                selection = input(f"Select (1-{len(projects)}): ").strip()
                try:
                    project_name = projects[int(selection) - 1]
                except (ValueError, IndexError):
                    project_name = projects[0]
            project_path = f"${{PWD}}/codebase/{project_name}"
        else:
            # Analyze entire codebase directory
            project_path = "${PWD}/codebase"
            print(f"{Colors.GREEN}✅ Will analyze all repositories in codebase/{Colors.RESET}")
        
        # Load template
        if self.mcp_template_path.exists():
            with open(self.mcp_template_path) as f:
                mcp_config = json.load(f)
        else:
            # Default configuration
            mcp_config = {
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
                            f"${{PWD}}/codebase/{project_name}"
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
        
        # Update project path in config
        if "serena" in mcp_config["mcpServers"]:
            mcp_config["mcpServers"]["serena"]["args"][-1] = project_path
        
        # Write configuration
        with open(self.mcp_json_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        print(f"{Colors.GREEN}✅ Created .mcp.json for: {project_path}{Colors.RESET}")
    
    def create_repomix_config(self):
        """Create .repomix.config.json"""
        print(f"\n{Colors.YELLOW}Configuring Repomix...{Colors.RESET}")
        
        if self.repomix_config_path.exists():
            print(f"{Colors.GREEN}✅ .repomix.config.json already exists{Colors.RESET}")
            return
        
        # Get codebase info from .mcp.json
        analyze_all = False
        project_name = "codebase"
        if self.mcp_json_path.exists():
            with open(self.mcp_json_path) as f:
                mcp_data = json.load(f)
                if "serena" in mcp_data.get("mcpServers", {}):
                    project_path = mcp_data["mcpServers"]["serena"]["args"][-1]
                    if project_path.endswith("/codebase"):
                        analyze_all = True
                        project_name = "all-repos"
                    else:
                        project_name = Path(project_path).name
        
        # Load template or use default
        if self.repomix_template_path.exists():
            with open(self.repomix_template_path) as f:
                repomix_config = json.load(f)
        else:
            repomix_config = {
                "output": {
                    "filePath": f"output/reports/{project_name}-repomix.md",
                    "style": "markdown",
                    "removeComments": False,
                    "showLineNumbers": True
                },
                "include": [
                    f"codebase/{project_name}/**/*"
                ],
                "ignore": {
                    "useGitignore": True,
                    "patterns": [
                        "**/node_modules/**",
                        "**/.git/**",
                        "**/dist/**",
                        "**/build/**",
                        "**/target/**",
                        "**/.idea/**",
                        "**/.vscode/**",
                        "**/*.log",
                        "**/*.tmp",
                        "**/coverage/**",
                        "**/.env*"
                    ]
                },
                "security": {
                    "enableSecurityCheck": True
                }
            }
        
        # Update paths based on scope
        repomix_config["output"]["filePath"] = f"output/reports/{project_name}-repomix.md"
        if analyze_all:
            repomix_config["include"] = ["codebase/**/*"]
        else:
            repomix_config["include"] = [f"codebase/{project_name}/**/*"]
        
        # Write configuration
        with open(self.repomix_config_path, 'w') as f:
            json.dump(repomix_config, f, indent=2)
        
        print(f"{Colors.GREEN}✅ Created .repomix.config.json{Colors.RESET}")
    
    def create_cache_directory(self):
        """Create MCP cache directory"""
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
            print(f"{Colors.GREEN}✅ Created cache directory: .mcp-cache/{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}✅ Cache directory exists{Colors.RESET}")
    
    def test_repomix(self):
        """Test Repomix with dry run"""
        if not self.mcp_status["repomix"]:
            print(f"{Colors.YELLOW}⚠️  Skipping Repomix test (not installed){Colors.RESET}")
            return
        
        print(f"\n{Colors.YELLOW}Testing Repomix configuration...{Colors.RESET}")
        try:
            result = subprocess.run(
                ["repomix", "--config", str(self.repomix_config_path), "--dry-run"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Repomix configuration valid{Colors.RESET}")
            else:
                print(f"{Colors.RED}❌ Repomix test failed{Colors.RESET}")
                print(f"Error: {result.stderr}")
        except Exception as e:
            print(f"{Colors.RED}Error testing Repomix: {e}{Colors.RESET}")
    
    def show_summary(self):
        """Show configuration summary"""
        print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.CYAN}MCP Setup Summary{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")
        
        # Configuration files
        print(f"{Colors.BLUE}Configuration Files:{Colors.RESET}")
        files = [
            (".mcp.json", self.mcp_json_path),
            (".repomix.config.json", self.repomix_config_path),
            (".mcp-cache/", self.cache_dir)
        ]
        
        for name, path in files:
            if path.exists():
                print(f"  {Colors.GREEN}✅ {name}{Colors.RESET}")
            else:
                print(f"  {Colors.RED}❌ {name}{Colors.RESET}")
        
        # MCP Status
        print(f"\n{Colors.BLUE}MCP Components:{Colors.RESET}")
        components = [
            ("Node.js", self.mcp_status["node"]),
            ("npm", self.mcp_status["npm"]),
            ("uvx/uv (Serena)", self.mcp_status["uvx"]),
            ("Repomix", self.mcp_status["repomix"])
        ]
        
        for name, status in components:
            icon = "✅" if status else "⚠️"
            color = Colors.GREEN if status else Colors.YELLOW
            print(f"  {color}{icon} {name}{Colors.RESET}")
        
        print(f"\n{Colors.GREEN}Setup complete!{Colors.RESET}")
        print(f"\nNext steps:")
        print(f"1. Place your code in: codebase/[project-name]/")
        print(f"2. Run: {Colors.BLUE}repomix --config .repomix.config.json{Colors.RESET}")
        print(f"3. Start analysis in Claude Code with @mcp-orchestrator")
    
    def run(self):
        """Main setup flow"""
        self.show_header()
        self.check_prerequisites()
        
        # Optional Repomix installation
        if not self.mcp_status["repomix"] and self.mcp_status["npm"]:
            response = input("\nWould you like to install Repomix? (y/n): ").lower()
            if response == 'y':
                self.install_repomix()
        
        # Create configurations
        self.create_mcp_json()
        self.create_repomix_config()
        self.create_cache_directory()
        
        # Test configuration
        self.test_repomix()
        
        # Show summary
        self.show_summary()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Setup and Configuration")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    setup = MCPSetup()
    setup.run()


if __name__ == "__main__":
    main()