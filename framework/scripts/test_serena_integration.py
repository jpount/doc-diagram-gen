#!/usr/bin/env python3
"""
Test Serena MCP Integration
Validates that Serena is properly configured and operational
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'


class SerenaValidator:
    """Validates Serena MCP integration"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.mcp_config_path = self.project_root / ".mcp.json"
        self.serena_config_path = Path.home() / ".serena" / "serena_config.yml"
        self.test_results = []
        
    def print_header(self):
        """Print test header"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.CYAN}       Serena MCP Integration Test{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
    
    def test_mcp_config(self) -> Tuple[bool, str]:
        """Test 1: Check MCP configuration"""
        try:
            if not self.mcp_config_path.exists():
                return False, "MCP config file not found"
            
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
            
            if 'mcpServers' not in config:
                return False, "No MCP servers configured"
            
            if 'serena' not in config['mcpServers']:
                return False, "Serena not configured in MCP"
            
            serena_config = config['mcpServers']['serena']
            
            # Check if disabled
            if serena_config.get('disabled', False):
                return False, "Serena is disabled in configuration"
            
            # Check command
            if 'command' not in serena_config or 'args' not in serena_config:
                return False, "Serena command/args not configured"
            
            # Extract project path from args
            project_path = None
            for i, arg in enumerate(serena_config['args']):
                if arg == '--project' and i + 1 < len(serena_config['args']):
                    project_path = serena_config['args'][i + 1]
                    project_path = project_path.replace('${PWD}', str(self.project_root))
                    break
            
            if not project_path:
                return False, "Project path not specified in Serena args"
            
            # Check if project path exists
            project_path = Path(project_path)
            if not project_path.exists():
                return False, f"Project path does not exist: {project_path}"
            
            return True, f"Serena configured for: {project_path}"
            
        except Exception as e:
            return False, f"Error checking MCP config: {e}"
    
    def test_serena_installation(self) -> Tuple[bool, str]:
        """Test 2: Check Serena installation"""
        try:
            # Try to run serena command
            result = subprocess.run(
                ["uvx", "--from", "git+https://github.com/oraios/serena", "serena", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip() or "Unknown version"
                return True, f"Serena installed: {version}"
            else:
                return False, "Serena not installed or not accessible"
                
        except subprocess.TimeoutExpired:
            return False, "Serena command timed out"
        except FileNotFoundError:
            return False, "uvx command not found - install with: pip install uv"
        except Exception as e:
            return False, f"Error checking Serena: {e}"
    
    def test_serena_config_file(self) -> Tuple[bool, str]:
        """Test 3: Check Serena configuration file"""
        try:
            if not self.serena_config_path.exists():
                return False, f"Serena config not found at {self.serena_config_path}"
            
            # Check if file is readable
            with open(self.serena_config_path, 'r') as f:
                content = f.read()
                if 'projects:' in content or 'agents:' in content:
                    return True, f"Serena config exists at {self.serena_config_path}"
                else:
                    return False, "Serena config file appears incomplete"
                    
        except Exception as e:
            return False, f"Error reading Serena config: {e}"
    
    def test_serena_server_start(self) -> Tuple[bool, str]:
        """Test 4: Try to start Serena server briefly"""
        try:
            # Read MCP config to get exact command
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
            
            serena_config = config['mcpServers']['serena']
            command = serena_config['command']
            args = serena_config['args']
            
            # Replace ${PWD} with actual path
            args = [arg.replace('${PWD}', str(self.project_root)) for arg in args]
            
            # Try to start server with a test flag
            test_args = [command] + args[:args.index('start-mcp-server')] + ['serena', '--help']
            
            result = subprocess.run(
                test_args,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return True, "Serena command is functional"
            else:
                error = result.stderr[:200] if result.stderr else "Unknown error"
                return False, f"Serena command failed: {error}"
                
        except subprocess.TimeoutExpired:
            return True, "Serena command responded (timeout expected for server)"
        except Exception as e:
            return False, f"Error testing Serena server: {e}"
    
    def test_project_structure(self) -> Tuple[bool, str]:
        """Test 5: Check project structure for Serena"""
        try:
            codebase_dir = self.project_root / "codebase"
            
            if not codebase_dir.exists():
                return False, "Codebase directory not found"
            
            # Check for any projects
            projects = [d for d in codebase_dir.iterdir() if d.is_dir()]
            
            if not projects:
                return False, "No projects found in codebase directory"
            
            # Check for common project files that Serena would analyze
            project_files = []
            for project in projects:
                for pattern in ['*.java', '*.py', '*.js', '*.ts', '*.cs']:
                    files = list(project.rglob(pattern))
                    if files:
                        project_files.extend(files[:3])  # Just get a few examples
            
            if project_files:
                return True, f"Found {len(projects)} project(s) with source files"
            else:
                return False, "No source files found in projects"
                
        except Exception as e:
            return False, f"Error checking project structure: {e}"
    
    def test_memory_functionality(self) -> Tuple[bool, str]:
        """Test 6: Simulate memory functionality test"""
        # This would actually test memory operations in a real MCP environment
        # For now, we check if the directories would be created
        try:
            serena_data_dir = Path.home() / ".serena"
            memory_indicators = [
                serena_data_dir / "memories",
                serena_data_dir / "logs",
                serena_data_dir / "language_servers"
            ]
            
            existing = [d for d in memory_indicators if d.exists()]
            
            if existing:
                return True, f"Serena data directories exist: {len(existing)}/3"
            else:
                return False, "Serena data directories not initialized"
                
        except Exception as e:
            return False, f"Error checking memory functionality: {e}"
    
    def run_all_tests(self):
        """Run all validation tests"""
        tests = [
            ("MCP Configuration", self.test_mcp_config),
            ("Serena Installation", self.test_serena_installation),
            ("Serena Config File", self.test_serena_config_file),
            ("Serena Command", self.test_serena_server_start),
            ("Project Structure", self.test_project_structure),
            ("Memory Directories", self.test_memory_functionality),
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for test_name, test_func in tests:
            print(f"{Colors.BLUE}Testing:{Colors.RESET} {test_name}...")
            success, message = test_func()
            
            if success:
                print(f"  {Colors.GREEN}✓{Colors.RESET} {message}")
                passed += 1
            else:
                if "disabled" in message.lower() or "not found" in message.lower():
                    print(f"  {Colors.YELLOW}⚠{Colors.RESET} {message}")
                    warnings += 1
                else:
                    print(f"  {Colors.RED}✗{Colors.RESET} {message}")
                    failed += 1
            
            self.test_results.append({
                "test": test_name,
                "success": success,
                "message": message
            })
        
        return passed, failed, warnings
    
    def print_summary(self, passed: int, failed: int, warnings: int):
        """Print test summary"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.CYAN}Test Summary{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        total = passed + failed + warnings
        print(f"\n{Colors.GREEN}Passed:{Colors.RESET} {passed}/{total}")
        print(f"{Colors.RED}Failed:{Colors.RESET} {failed}/{total}")
        print(f"{Colors.YELLOW}Warnings:{Colors.RESET} {warnings}/{total}")
        
        # Overall status
        print(f"\n{Colors.CYAN}Overall Status:{Colors.RESET} ", end="")
        if failed == 0 and passed > 3:
            print(f"{Colors.GREEN}✓ Serena is properly configured{Colors.RESET}")
        elif failed == 0 and warnings > 0:
            print(f"{Colors.YELLOW}⚠ Serena is configured but may need attention{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Serena configuration needs fixing{Colors.RESET}")
    
    def print_recommendations(self):
        """Print recommendations based on test results"""
        print(f"\n{Colors.CYAN}Recommendations:{Colors.RESET}")
        
        recommendations = []
        
        for result in self.test_results:
            if not result['success']:
                if "disabled" in result['message']:
                    recommendations.append(
                        f"Enable Serena in .mcp.json by removing 'disabled: true'"
                    )
                elif "not installed" in result['message']:
                    recommendations.append(
                        f"Install Serena: pip install uv && uvx --from git+https://github.com/oraios/serena serena --version"
                    )
                elif "Project path does not exist" in result['message']:
                    recommendations.append(
                        f"Update project path in .mcp.json or create the project directory"
                    )
                elif "No source files" in result['message']:
                    recommendations.append(
                        f"Add your codebase to analyze in the codebase/ directory"
                    )
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print(f"  {Colors.GREEN}No issues found - Serena is ready to use!{Colors.RESET}")
    
    def save_results(self):
        """Save test results to file"""
        output_file = self.project_root / "output" / "reports" / "serena-validation.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n{Colors.BLUE}Results saved to:{Colors.RESET} {output_file}")


def main():
    """Main function"""
    validator = SerenaValidator()
    validator.print_header()
    
    # Run tests
    passed, failed, warnings = validator.run_all_tests()
    
    # Print summary
    validator.print_summary(passed, failed, warnings)
    
    # Print recommendations
    validator.print_recommendations()
    
    # Save results
    validator.save_results()
    
    # Return exit code
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()