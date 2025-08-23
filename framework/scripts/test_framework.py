#!/usr/bin/env python3
"""
Comprehensive Framework Test Harness
Tests all framework components: agents, hooks, validation, and MCP integration
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

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


class FrameworkTestHarness:
    """Comprehensive test harness for the documentation framework"""
    
    def __init__(self, verbose: bool = False):
        self.script_dir = Path(__file__).parent.resolve()
        self.framework_dir = self.script_dir.parent
        self.project_root = self.framework_dir.parent
        self.verbose = verbose
        
        # Test results tracking
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        
        # Enable colors
        Colors.enable_windows()
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with color"""
        if not self.verbose and level == "DEBUG":
            return
            
        color_map = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "DEBUG": Colors.CYAN
        }
        
        color = color_map.get(level, Colors.RESET)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {level}: {message}{Colors.RESET}")
    
    def run_all_tests(self) -> int:
        """Run all framework tests"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("=" * 70)
        print("          FRAMEWORK COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"{Colors.RESET}\n")
        
        # Test categories
        test_categories = [
            ("Framework Structure", self.test_framework_structure),
            ("Agent Definitions", self.test_agents),
            ("Hook Implementations", self.test_hooks),
            ("Validation Scripts", self.test_validation_scripts),
            ("MCP Configuration", self.test_mcp_configuration),
            ("Template System", self.test_templates),
            ("Documentation", self.test_documentation),
            ("Cross-Platform Compatibility", self.test_cross_platform),
        ]
        
        for category_name, test_func in test_categories:
            self.run_test_category(category_name, test_func)
        
        # Show final summary
        self.show_summary()
        
        return 0 if self.tests_failed == 0 else 1
    
    def run_test_category(self, name: str, test_func):
        """Run a category of tests"""
        print(f"\n{Colors.BLUE}▶ Testing: {name}{Colors.RESET}")
        print("-" * 50)
        
        try:
            test_func()
        except Exception as e:
            self.log(f"Category '{name}' failed: {e}", "ERROR")
            self.tests_failed += 1
    
    def test_framework_structure(self):
        """Test framework directory structure"""
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
            "codebase",
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            self.tests_run += 1
            
            if full_path.exists() and full_path.is_dir():
                self.tests_passed += 1
                self.log(f"✓ Directory exists: {dir_path}", "SUCCESS")
            else:
                self.tests_failed += 1
                self.log(f"✗ Missing directory: {dir_path}", "ERROR")
                self.test_results.append(f"Missing: {dir_path}")
    
    def test_agents(self):
        """Test agent definition files"""
        agents_dir = self.project_root / ".claude" / "agents"
        
        required_agents = [
            "legacy-code-detective.md",
            "business-logic-analyst.md",
            "diagram-architect.md",
            "performance-analyst.md",
            "security-analyst.md",
            "modernization-architect.md",
            "documentation-specialist.md",
            "mcp-orchestrator.md",
            "repomix-analyzer.md",
        ]
        
        for agent_file in required_agents:
            agent_path = agents_dir / agent_file
            self.tests_run += 1
            
            if agent_path.exists():
                # Validate agent structure
                content = agent_path.read_text()
                if "---" in content and "name:" in content and "tools:" in content:
                    self.tests_passed += 1
                    self.log(f"✓ Valid agent: {agent_file}", "SUCCESS")
                else:
                    self.tests_failed += 1
                    self.log(f"✗ Invalid agent format: {agent_file}", "ERROR")
            else:
                self.tests_failed += 1
                self.log(f"✗ Missing agent: {agent_file}", "ERROR")
    
    def test_hooks(self):
        """Test hook implementations"""
        hooks_dir = self.project_root / ".claude" / "hooks"
        
        required_hooks = [
            ("mermaid_diagram_validation.py", "python"),
            ("documentation_completeness_check.py", "python"),
            ("business_rule_validation.py", "python"),
            ("dangerous_command_prevention.py", "python"),
        ]
        
        for hook_file, hook_type in required_hooks:
            hook_path = hooks_dir / hook_file
            self.tests_run += 1
            
            if hook_path.exists():
                # Test if hook is executable (Python)
                if hook_type == "python":
                    try:
                        result = subprocess.run(
                            [sys.executable, str(hook_path), "--help"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode in [0, 1]:  # Some hooks exit with 1 on help
                            self.tests_passed += 1
                            self.log(f"✓ Executable hook: {hook_file}", "SUCCESS")
                        else:
                            self.tests_failed += 1
                            self.log(f"✗ Hook execution failed: {hook_file}", "ERROR")
                    except Exception as e:
                        self.tests_failed += 1
                        self.log(f"✗ Hook error: {hook_file} - {e}", "ERROR")
            else:
                self.tests_failed += 1
                self.log(f"✗ Missing hook: {hook_file}", "ERROR")
    
    def test_validation_scripts(self):
        """Test validation scripts"""
        scripts_dir = self.framework_dir / "scripts"
        
        validation_scripts = [
            "validate_mermaid.py",
            "test_mcp_integration.py",
        ]
        
        for script_file in validation_scripts:
            script_path = scripts_dir / script_file
            self.tests_run += 1
            
            if script_path.exists():
                # Test if script can be imported
                try:
                    result = subprocess.run(
                        [sys.executable, str(script_path), "--help"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        self.tests_passed += 1
                        self.log(f"✓ Valid script: {script_file}", "SUCCESS")
                    else:
                        self.tests_failed += 1
                        self.log(f"✗ Script error: {script_file}", "ERROR")
                except Exception as e:
                    self.tests_failed += 1
                    self.log(f"✗ Script failed: {script_file} - {e}", "ERROR")
            else:
                self.tests_failed += 1
                self.log(f"✗ Missing script: {script_file}", "ERROR")
    
    def test_mcp_configuration(self):
        """Test MCP configuration files"""
        self.tests_run += 1
        
        # Check .mcp.json
        mcp_json = self.project_root / ".mcp.json"
        if mcp_json.exists():
            try:
                with open(mcp_json) as f:
                    config = json.load(f)
                
                if "mcpServers" in config:
                    self.tests_passed += 1
                    self.log("✓ Valid .mcp.json configuration", "SUCCESS")
                    
                    # Check for key MCPs
                    servers = config.get("mcpServers", {})
                    for mcp_name in ["serena", "filesystem", "memory"]:
                        if mcp_name in servers:
                            self.log(f"  ✓ {mcp_name} MCP configured", "DEBUG")
                else:
                    self.tests_failed += 1
                    self.log("✗ Invalid .mcp.json structure", "ERROR")
            except json.JSONDecodeError:
                self.tests_failed += 1
                self.log("✗ .mcp.json is not valid JSON", "ERROR")
        else:
            self.tests_failed += 1
            self.log("✗ .mcp.json not found", "ERROR")
        
        # Check settings.local.json
        self.tests_run += 1
        settings_file = self.project_root / ".claude" / "settings.local.json"
        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    settings = json.load(f)
                
                if "hooks" in settings and "agentDirectories" in settings:
                    self.tests_passed += 1
                    self.log("✓ Valid settings.local.json", "SUCCESS")
                else:
                    self.tests_failed += 1
                    self.log("✗ Incomplete settings.local.json", "ERROR")
            except json.JSONDecodeError:
                self.tests_failed += 1
                self.log("✗ settings.local.json is not valid JSON", "ERROR")
        else:
            self.tests_failed += 1
            self.log("✗ settings.local.json not found", "ERROR")
    
    def test_templates(self):
        """Test template system"""
        templates_dir = self.framework_dir / "templates"
        
        required_templates = [
            "TARGET_TECH_STACK.template.md",
            "tech-stack-presets.yaml",
        ]
        
        for template_file in required_templates:
            template_path = templates_dir / template_file
            self.tests_run += 1
            
            if template_path.exists():
                content = template_path.read_text()
                if "{{" in content or template_file.endswith(".yaml"):
                    self.tests_passed += 1
                    self.log(f"✓ Valid template: {template_file}", "SUCCESS")
                else:
                    self.tests_failed += 1
                    self.log(f"✗ Invalid template format: {template_file}", "ERROR")
            else:
                self.tests_failed += 1
                self.log(f"✗ Missing template: {template_file}", "ERROR")
    
    def test_documentation(self):
        """Test framework documentation"""
        docs_dir = self.framework_dir / "docs"
        
        required_docs = [
            "CLAUDE_FRAMEWORK.md",
            "MCP_USAGE_GUIDE.md",
            "MCP_CONFIGURATION_GUIDE.md",
        ]
        
        for doc_file in required_docs:
            doc_path = docs_dir / doc_file
            self.tests_run += 1
            
            if doc_path.exists():
                content = doc_path.read_text()
                if len(content) > 100:  # Basic content check
                    self.tests_passed += 1
                    self.log(f"✓ Documentation exists: {doc_file}", "SUCCESS")
                else:
                    self.tests_failed += 1
                    self.log(f"✗ Documentation empty: {doc_file}", "ERROR")
            else:
                self.tests_failed += 1
                self.log(f"✗ Missing documentation: {doc_file}", "ERROR")
    
    def test_cross_platform(self):
        """Test cross-platform compatibility"""
        self.tests_run += 1
        
        # Check Python version
        if sys.version_info >= (3, 7):
            self.tests_passed += 1
            self.log(f"✓ Python {sys.version.split()[0]} meets requirements", "SUCCESS")
        else:
            self.tests_failed += 1
            self.log(f"✗ Python {sys.version.split()[0]} too old (need 3.7+)", "ERROR")
        
        # Check platform-specific scripts
        self.tests_run += 1
        if sys.platform == "win32":
            setup_script = self.project_root / "setup.ps1"
        else:
            setup_script = self.project_root / "setup.sh"
        
        if setup_script.exists() or (self.project_root / "setup.py").exists():
            self.tests_passed += 1
            self.log("✓ Platform-appropriate setup script available", "SUCCESS")
        else:
            self.tests_failed += 1
            self.log("✗ No setup script for current platform", "ERROR")
    
    def test_sample_mermaid_diagram(self):
        """Test Mermaid diagram validation with sample"""
        self.tests_run += 1
        
        # Create temporary test file
        test_content = """
# Test Document

## Architecture Diagram

```mermaid
graph TB
    A[Frontend] --> B[API Gateway]
    B --> C[Service 1]
    B --> D[Service 2]
    C --> E[(Database)]
    D --> E
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant System
    User->>System: Request
    System->>User: Response
```
"""
        
        # Write test file
        test_file = self.project_root / "output" / "docs" / "test_diagram.md"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(test_content)
        
        # Run validator
        validator_script = self.framework_dir / "scripts" / "validate_mermaid.py"
        if validator_script.exists():
            result = subprocess.run(
                [sys.executable, str(validator_script), "--output-dir", str(test_file.parent)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.tests_passed += 1
                self.log("✓ Mermaid validation works correctly", "SUCCESS")
            else:
                self.tests_failed += 1
                self.log("✗ Mermaid validation failed", "ERROR")
        
        # Cleanup
        test_file.unlink(missing_ok=True)
    
    def show_summary(self):
        """Display test summary"""
        print(f"\n{Colors.CYAN}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")
        
        # Calculate percentage
        pass_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        # Choose color based on pass rate
        if pass_rate >= 90:
            status_color = Colors.GREEN
            status_emoji = "✅"
            status_text = "EXCELLENT"
        elif pass_rate >= 70:
            status_color = Colors.YELLOW
            status_emoji = "⚠️"
            status_text = "GOOD"
        else:
            status_color = Colors.RED
            status_emoji = "❌"
            status_text = "NEEDS ATTENTION"
        
        print(f"Total Tests Run: {self.tests_run}")
        print(f"{Colors.GREEN}Passed: {self.tests_passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.tests_failed}{Colors.RESET}")
        print(f"Pass Rate: {status_color}{pass_rate:.1f}%{Colors.RESET}")
        print(f"\nStatus: {status_emoji} {status_color}{status_text}{Colors.RESET}")
        
        if self.test_results:
            print(f"\n{Colors.YELLOW}Issues Found:{Colors.RESET}")
            for issue in self.test_results[:10]:  # Show first 10 issues
                print(f"  • {issue}")
            if len(self.test_results) > 10:
                print(f"  ... and {len(self.test_results) - 10} more")
        
        print(f"\n{Colors.CYAN}{'=' * 70}{Colors.RESET}")
        
        if self.tests_failed == 0:
            print(f"{Colors.GREEN}🎉 All tests passed! Framework is ready to use.{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠️  Some tests failed. Review issues above.{Colors.RESET}")
            print(f"Run setup scripts to fix missing components:")
            print(f"  • Python: python setup.py")
            print(f"  • Mac/Linux: ./setup.sh")
            print(f"  • Windows: powershell -ExecutionPolicy Bypass -File setup.ps1")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Framework Test Harness")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Enable verbose output")
    parser.add_argument("--no-color", action="store_true",
                       help="Disable colored output")
    
    args = parser.parse_args()
    
    if args.no_color:
        Colors.disable()
    
    # Run tests
    harness = FrameworkTestHarness(verbose=args.verbose)
    exit_code = harness.run_all_tests()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()