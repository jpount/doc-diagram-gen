#!/usr/bin/env python3
"""
Master Setup Script for Codebase Analysis Framework
Cross-platform setup wizard for Windows, Mac, and Linux
"""

import os
import sys
import json
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Color codes for terminal output
class Colors:
    """Terminal color codes that work cross-platform"""
    RED = '\033[91m' if platform.system() != 'Windows' else ''
    GREEN = '\033[92m' if platform.system() != 'Windows' else ''
    YELLOW = '\033[93m' if platform.system() != 'Windows' else ''
    BLUE = '\033[94m' if platform.system() != 'Windows' else ''
    MAGENTA = '\033[95m' if platform.system() != 'Windows' else ''
    CYAN = '\033[96m' if platform.system() != 'Windows' else ''
    RESET = '\033[0m' if platform.system() != 'Windows' else ''
    
    @staticmethod
    def enable_windows_colors():
        """Enable ANSI colors on Windows 10+"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                # Update color codes for Windows
                Colors.RED = '\033[91m'
                Colors.GREEN = '\033[92m'
                Colors.YELLOW = '\033[93m'
                Colors.BLUE = '\033[94m'
                Colors.MAGENTA = '\033[95m'
                Colors.CYAN = '\033[96m'
                Colors.RESET = '\033[0m'
            except:
                pass  # Fallback to no colors

class FrameworkSetup:
    """Main setup class for the framework"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.resolve()
        self.framework_dir = self.script_dir / "framework"
        self.output_dir = self.script_dir / "output"
        self.codebase_dir = self.script_dir / "codebase"
        self.cache_dir = self.script_dir / ".mcp-cache"
        self.project_name = None
        
        # Enable colors on Windows
        Colors.enable_windows_colors()
    
    def show_banner(self):
        """Display welcome banner"""
        self.clear_screen()
        print(f"{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.CYAN}║     Codebase Analysis & Documentation Framework           ║{Colors.RESET}")
        print(f"{Colors.CYAN}║                    Setup Wizard                           ║{Colors.RESET}")
        print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
        print(f"{Colors.BLUE}This wizard will help you set up the framework for analyzing{Colors.RESET}")
        print(f"{Colors.BLUE}your codebase and generating comprehensive documentation.{Colors.RESET}")
        print()
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version.split()[0]}")
        print()
    
    def clear_screen(self):
        """Clear terminal screen (cross-platform)"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
    
    def check_prerequisites(self) -> bool:
        """Check for required tools"""
        print(f"{Colors.YELLOW}Checking prerequisites...{Colors.RESET}")
        
        missing_tools = []
        optional_tools = []
        
        # Check Python version
        if sys.version_info < (3, 7):
            missing_tools.append("Python 3.7+")
        
        # Check for Node.js (optional but recommended)
        if not self.check_command("node --version"):
            optional_tools.append("Node.js (for Repomix and MCPs)")
        
        # Check for npm (optional but recommended)
        if not self.check_command("npm --version"):
            optional_tools.append("npm (for installing Repomix)")
        
        # Check for git (optional)
        if not self.check_command("git --version"):
            optional_tools.append("git (for version control)")
        
        if missing_tools:
            print(f"{Colors.RED}Missing required tools:{Colors.RESET}")
            for tool in missing_tools:
                print(f"  - {tool}")
            print("\nPlease install missing tools and run setup again.")
            return False
        
        if optional_tools:
            print(f"{Colors.YELLOW}Optional tools not found:{Colors.RESET}")
            for tool in optional_tools:
                print(f"  - {tool}")
            print(f"\n{Colors.BLUE}These tools enhance functionality but are not required.{Colors.RESET}")
        
        print(f"{Colors.GREEN}✓ Prerequisites check complete{Colors.RESET}")
        print()
        return True
    
    def check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run(
                command.split(), 
                capture_output=True, 
                check=False,
                shell=platform.system() == 'Windows'
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def setup_project_structure(self):
        """Create necessary directories"""
        print(f"{Colors.YELLOW}Setting up project structure...{Colors.RESET}")
        
        directories = [
            self.codebase_dir,
            self.output_dir / "docs",
            self.output_dir / "diagrams",
            self.output_dir / "reports",
            self.output_dir / "context",  # For agent context summaries
            self.cache_dir,
            self.cache_dir / "repomix",
            self.cache_dir / "serena",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ Created: {directory.relative_to(self.script_dir)}")
        
        print(f"{Colors.GREEN}✓ Project structure created{Colors.RESET}")
        print()
    
    def copy_mcp_templates(self):
        """Set up MCP configuration files"""
        print(f"{Colors.YELLOW}Setting up MCP configuration...{Colors.RESET}")
        
        # Copy .mcp.json template
        mcp_file = self.script_dir / ".mcp.json"
        mcp_template = self.framework_dir / "mcp-configs" / "mcp.template.json"
        
        if not mcp_file.exists() and mcp_template.exists():
            shutil.copy2(mcp_template, mcp_file)
            print(f"{Colors.GREEN}✓ Created .mcp.json from template{Colors.RESET}")
        elif mcp_file.exists():
            print(f"{Colors.BLUE}ℹ .mcp.json already exists{Colors.RESET}")
        
        # Copy Repomix config template
        repomix_file = self.script_dir / ".repomix.config.json"
        repomix_template = self.framework_dir / "mcp-configs" / "repomix.config.template.json"
        
        if not repomix_file.exists() and repomix_template.exists():
            shutil.copy2(repomix_template, repomix_file)
            print(f"{Colors.GREEN}✓ Created .repomix.config.json from template{Colors.RESET}")
        elif repomix_file.exists():
            print(f"{Colors.BLUE}ℹ .repomix.config.json already exists{Colors.RESET}")
        
        print()
    
    def configure_codebase_path(self):
        """Configure the codebase path in .mcp.json"""
        print(f"{Colors.YELLOW}Configuring codebase path...{Colors.RESET}")
        
        # Check for existing projects
        if self.codebase_dir.exists():
            projects = [d.name for d in self.codebase_dir.iterdir() if d.is_dir()]
            
            if projects:
                print("Found existing project(s):")
                for proj in projects:
                    print(f"  - {proj}")
                
                use_existing = input(f"\nUse existing project '{projects[0]}'? (y/n): ").lower()
                if use_existing == 'y':
                    self.project_name = projects[0]
                else:
                    self.project_name = input("Enter new project name: ").strip()
            else:
                print("No existing projects found.")
                self.project_name = input("Enter project name (will be created in codebase/): ").strip()
        
        # Update .mcp.json with the project path
        if self.project_name:
            mcp_file = self.script_dir / ".mcp.json"
            if mcp_file.exists():
                try:
                    with open(mcp_file, 'r') as f:
                        mcp_config = json.load(f)
                    
                    # Update Serena project path
                    if 'mcpServers' in mcp_config and 'serena' in mcp_config['mcpServers']:
                        args = mcp_config['mcpServers']['serena']['args']
                        for i, arg in enumerate(args):
                            if arg == '${PWD}/codebase':
                                args[i] = f'${{PWD}}/codebase/{self.project_name}'
                                break
                    
                    with open(mcp_file, 'w') as f:
                        json.dump(mcp_config, f, indent=2)
                    
                    print(f"{Colors.GREEN}✓ Updated .mcp.json with project: codebase/{self.project_name}{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.YELLOW}⚠ Could not update .mcp.json: {e}{Colors.RESET}")
        
        print()
    
    def configure_analysis_mode(self):
        """Configure analysis mode (documentation-only vs modernization)"""
        print(f"{Colors.MAGENTA}Step 1: Configure Analysis Mode{Colors.RESET}")
        print("-" * 40)
        
        print(f"{Colors.CYAN}What is your primary goal for this analysis?{Colors.RESET}")
        print()
        print(f"{Colors.GREEN}1. Documentation & Analysis Only (Default){Colors.RESET}")
        print("   - Generate comprehensive documentation for existing codebase")
        print("   - Create architecture diagrams and visualizations")
        print("   - Analyze technical debt, performance, and security")
        print("   - Provide improvement recommendations for current stack")
        print()
        print(f"{Colors.BLUE}2. Documentation + Modernization Planning{Colors.RESET}")
        print("   - Everything from option 1, plus:")
        print("   - Create modernization strategy and roadmap")
        print("   - Design target architecture")
        print("   - Plan migration phases")
        print("   - Requires target technology stack configuration")
        print()
        print(f"{Colors.YELLOW}3. Full Modernization with AI Assistance{Colors.RESET}")
        print("   - Everything from option 2, plus:")
        print("   - Claude Code suggests technology choices")
        print("   - Interactive modernization planning")
        print("   - Automated gap analysis")
        print()
        
        while True:
            choice = input(f"Select mode (1-3) [{Colors.GREEN}1{Colors.RESET}]: ").strip() or "1"
            if choice in ["1", "2", "3"]:
                break
            print(f"{Colors.RED}Invalid choice. Please enter 1, 2, or 3.{Colors.RESET}")
        
        modes = {
            "1": "DOCUMENTATION_ONLY",
            "2": "DOCUMENTATION_WITH_MODERNIZATION",
            "3": "FULL_MODERNIZATION_ASSISTED"
        }
        
        selected_mode = modes[choice]
        
        # Create ANALYSIS_MODE.md from template
        template_file = self.framework_dir / "templates" / "ANALYSIS_MODE.template.md"
        output_file = self.script_dir / "ANALYSIS_MODE.md"
        
        if template_file.exists():
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Replace placeholder with selected mode
            content = content.replace("{{ANALYSIS_MODE}}", selected_mode)
            
            with open(output_file, 'w') as f:
                f.write(content)
            
            print(f"{Colors.GREEN}✓ Analysis mode set to: {selected_mode}{Colors.RESET}")
            
            # Now configure documentation mode
            self.configure_documentation_mode()
            
            # Only run tech stack setup if modernization mode is selected
            if choice in ["2", "3"]:
                print()
                self.run_tech_stack_setup(ai_assisted=(choice == "3"))
        else:
            print(f"{Colors.YELLOW}⚠ Analysis mode template not found, using default mode{Colors.RESET}")
        
        print()
    
    def configure_documentation_mode(self):
        """Configure documentation generation mode"""
        print()
        print(f"{Colors.MAGENTA}Step 1b: Configure Documentation Mode{Colors.RESET}")
        print("-" * 40)
        
        print(f"{Colors.CYAN}How should documentation be generated?{Colors.RESET}")
        print()
        print(f"{Colors.YELLOW}1. QUICK Mode{Colors.RESET}")
        print("   - Fully automated, no user interaction")
        print("   - Fast (1-2 hours for medium projects)")
        print("   - Good for initial exploration")
        print()
        print(f"{Colors.GREEN}2. GUIDED Mode (Recommended){Colors.RESET}")
        print("   - Interactive checkpoints for validation")
        print("   - Captures business context and domain knowledge")
        print("   - Best balance of automation and accuracy")
        print()
        print(f"{Colors.BLUE}3. TEMPLATE Mode{Colors.RESET}")
        print("   - Generates templates for manual completion")
        print("   - Maximum accuracy but requires more effort")
        print("   - Best for compliance/audit documentation")
        print()
        
        while True:
            choice = input(f"Select mode (1-3) [{Colors.GREEN}2{Colors.RESET}]: ").strip() or "2"
            if choice in ["1", "2", "3"]:
                break
            print(f"{Colors.RED}Invalid choice. Please enter 1, 2, or 3.{Colors.RESET}")
        
        modes = {
            "1": "QUICK",
            "2": "GUIDED",
            "3": "TEMPLATE"
        }
        
        selected_mode = modes[choice]
        
        # Create DOCUMENTATION_MODE.md from template
        template_file = self.framework_dir / "templates" / "DOCUMENTATION_MODE.template.md"
        output_file = self.script_dir / "DOCUMENTATION_MODE.md"
        
        if template_file.exists():
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Replace placeholder with selected mode
            content = content.replace("{{DOCUMENTATION_MODE}}", selected_mode)
            
            with open(output_file, 'w') as f:
                f.write(content)
            
            print(f"{Colors.GREEN}✓ Documentation mode set to: {selected_mode}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠ Documentation mode template not found, using default (GUIDED){Colors.RESET}")
        
        print()
    
    def run_tech_stack_setup(self, ai_assisted=False):
        """Run technology stack configuration"""
        print(f"{Colors.MAGENTA}Step 1c: Configure Target Technology Stack{Colors.RESET}")
        print("-" * 40)
        
        if ai_assisted:
            print(f"{Colors.CYAN}AI-assisted mode: Claude Code will help suggest technology choices{Colors.RESET}")
        
        # Check for Python script first
        tech_script_py = self.framework_dir / "scripts" / "setup_tech_stack.py"
        tech_script_sh = self.framework_dir / "scripts" / "setup-tech-stack.sh"
        tech_script_ps1 = self.framework_dir / "scripts" / "setup-tech-stack.ps1"
        
        if tech_script_py.exists():
            subprocess.run([sys.executable, str(tech_script_py)])
        elif platform.system() == 'Windows' and tech_script_ps1.exists():
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(tech_script_ps1)])
        elif tech_script_sh.exists() and platform.system() != 'Windows':
            subprocess.run(["bash", str(tech_script_sh)])
        else:
            print(f"{Colors.YELLOW}⚠ Technology stack setup script not found{Colors.RESET}")
            self.create_default_tech_stack()
        
        print()
    
    def create_default_tech_stack(self):
        """Create a default TARGET_TECH_STACK.md"""
        print(f"{Colors.YELLOW}Creating default technology stack configuration...{Colors.RESET}")
        
        template_file = self.framework_dir / "templates" / "TARGET_TECH_STACK.template.md"
        output_file = self.script_dir / "TARGET_TECH_STACK.md"
        
        if template_file.exists():
            shutil.copy2(template_file, output_file)
            print(f"{Colors.GREEN}✓ Created TARGET_TECH_STACK.md from template{Colors.RESET}")
            print(f"{Colors.BLUE}ℹ Edit TARGET_TECH_STACK.md to customize your target stack{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ Template not found{Colors.RESET}")
    
    def generate_claude_md(self):
        """Generate CLAUDE.md from template based on configuration"""
        print(f"{Colors.MAGENTA}Generating CLAUDE.md configuration...{Colors.RESET}")
        
        template_file = self.framework_dir / "templates" / "CLAUDE.template.md"
        output_file = self.script_dir / "CLAUDE.md"
        
        if not template_file.exists():
            print(f"{Colors.YELLOW}⚠ CLAUDE.md template not found{Colors.RESET}")
            return
        
        # Read current configurations
        analysis_mode = "DOCUMENTATION_ONLY"
        documentation_mode = "GUIDED"
        
        # Read analysis mode
        analysis_mode_file = self.script_dir / "ANALYSIS_MODE.md"
        if analysis_mode_file.exists():
            with open(analysis_mode_file, 'r') as f:
                content = f.read()
                if "Mode:** DOCUMENTATION_WITH_MODERNIZATION" in content:
                    analysis_mode = "DOCUMENTATION_WITH_MODERNIZATION"
                elif "Mode:** FULL_MODERNIZATION_ASSISTED" in content:
                    analysis_mode = "FULL_MODERNIZATION_ASSISTED"
        
        # Read documentation mode
        doc_mode_file = self.script_dir / "DOCUMENTATION_MODE.md"
        if doc_mode_file.exists():
            with open(doc_mode_file, 'r') as f:
                content = f.read()
                if "Mode:** QUICK" in content:
                    documentation_mode = "QUICK"
                elif "Mode:** TEMPLATE" in content:
                    documentation_mode = "TEMPLATE"
        
        # Determine project size (simplified)
        codebase_dir = self.script_dir / "codebase"
        project_size = "medium"
        if self.project_name and (codebase_dir / self.project_name).exists():
            # Could add logic to count files/lines here
            project_size = "medium"
        
        # Read template
        with open(template_file, 'r') as f:
            template = f.read()
        
        # Replace placeholders
        from datetime import datetime
        
        replacements = {
            "{{PROJECT_NAME}}": self.project_name or "Not specified",
            "{{PROJECT_PATH}}": self.project_name or "[project-name]",
            "{{ANALYSIS_MODE}}": analysis_mode,
            "{{DOCUMENTATION_MODE}}": documentation_mode,
            "{{ANALYSIS_FOCUS}}": "Existing codebase documentation and analysis" if "DOCUMENTATION_ONLY" in analysis_mode else "Documentation with modernization planning",
            "{{MODERNIZATION_ENABLED}}": "No" if "DOCUMENTATION_ONLY" in analysis_mode else "Yes",
            "{{USER_INTERACTION}}": "None" if documentation_mode == "QUICK" else ("Interactive" if documentation_mode == "GUIDED" else "Template-based"),
            "{{PROJECT_SIZE}}": project_size.capitalize(),
            "{{TOKEN_BUDGET}}": "500,000 tokens (flexible)" if project_size == "medium" else "250,000 tokens (flexible)",
            "{{SETUP_DATE}}": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        
        # Add modernization agents section if needed
        if "DOCUMENTATION_ONLY" in analysis_mode:
            replacements["{{MODERNIZATION_AGENTS}}"] = ""
            replacements["{{TARGET_TECH_STACK_FILE}}"] = ""
        else:
            replacements["{{MODERNIZATION_AGENTS}}"] = """
### Modernization Agents (When Enabled)
- `@modernization-architect` - Create migration roadmap
- `@angular-architect` - Angular-specific migration guidance"""
            replacements["{{TARGET_TECH_STACK_FILE}}"] = "- `TARGET_TECH_STACK.md` - Target technology configuration"
        
        # Add workflow steps based on documentation mode
        if documentation_mode == "QUICK":
            replacements["{{WORKFLOW_STEPS}}"] = """1. Run `@mcp-orchestrator` to coordinate analysis
2. Agents run automatically without interaction
3. Review generated documentation in `output/docs/`"""
        elif documentation_mode == "GUIDED":
            replacements["{{WORKFLOW_STEPS}}"] = """1. Run `@mcp-orchestrator` to coordinate analysis
2. Respond to prompts at key checkpoints:
   - After discovery: Validate technology stack
   - After business logic: Confirm business rules
   - Before diagrams: Specify diagram requirements
   - After generation: Review and refine
3. Review and iterate on documentation"""
        else:  # TEMPLATE
            replacements["{{WORKFLOW_STEPS}}"] = """1. Run `@mcp-orchestrator` to generate templates
2. Review templates in `output/templates/`
3. Fill in domain knowledge and business context
4. Validate completeness with checklist"""
        
        # Add MCP tools section
        replacements["{{MCP_TOOLS}}"] = """- `@serena` - Semantic code analysis (if configured)
- `repomix` - Codebase compression (if installed)
- File system access via MCP
- Memory for cross-agent communication"""
        
        # Add project notes
        if self.project_name:
            replacements["{{PROJECT_NOTES}}"] = f"- Project '{self.project_name}' configured in codebase directory\n- Run repomix before starting analysis"
        else:
            replacements["{{PROJECT_NOTES}}"] = "- No specific project configured yet\n- Place code in codebase/[project-name]/"
        
        # Add next steps
        if documentation_mode == "QUICK":
            replacements["{{NEXT_STEPS}}"] = "1. Run repomix summary\n2. Start with @mcp-orchestrator\n3. Review generated documentation"
        elif documentation_mode == "GUIDED":
            replacements["{{NEXT_STEPS}}"] = "1. Run repomix summary\n2. Start with @mcp-orchestrator\n3. Provide input at checkpoints\n4. Review and refine output"
        else:
            replacements["{{NEXT_STEPS}}"] = "1. Run repomix summary\n2. Generate templates with @mcp-orchestrator\n3. Complete templates with domain knowledge"
        
        # Apply replacements
        for key, value in replacements.items():
            template = template.replace(key, value)
        
        # Write output
        with open(output_file, 'w') as f:
            f.write(template)
        
        print(f"{Colors.GREEN}✓ Generated CLAUDE.md with project configuration{Colors.RESET}")
        print()
    
    def run_mcp_setup(self):
        """Run MCP configuration"""
        print(f"{Colors.MAGENTA}Step 2: Configure MCP Integration{Colors.RESET}")
        print("-" * 40)
        
        # Check for Python script first
        mcp_script_py = self.framework_dir / "scripts" / "setup_mcp.py"
        mcp_script_sh = self.framework_dir / "scripts" / "setup-mcp.sh"
        mcp_script_ps1 = self.framework_dir / "scripts" / "setup-mcp.ps1"
        
        if mcp_script_py.exists():
            subprocess.run([sys.executable, str(mcp_script_py)])
        elif platform.system() == 'Windows' and mcp_script_ps1.exists():
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(mcp_script_ps1)])
        elif mcp_script_sh.exists() and platform.system() != 'Windows':
            subprocess.run(["bash", str(mcp_script_sh)])
        else:
            print(f"{Colors.YELLOW}⚠ MCP setup script not found{Colors.RESET}")
            print(f"{Colors.BLUE}ℹ MCP configuration files have been created{Colors.RESET}")
        
        print()
    
    def show_next_steps(self):
        """Display next steps for the user"""
        print(f"{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.CYAN}║                    Setup Complete!                        ║{Colors.RESET}")
        print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
        print(f"{Colors.GREEN}✓ Framework is ready for use!{Colors.RESET}")
        print()
        
        # Check analysis mode
        analysis_mode_file = self.script_dir / "ANALYSIS_MODE.md"
        analysis_mode = "DOCUMENTATION_ONLY"  # default
        if analysis_mode_file.exists():
            with open(analysis_mode_file, 'r') as f:
                content = f.read()
                # Look for the mode in the "Selected Mode" section
                if "Mode:** DOCUMENTATION_WITH_MODERNIZATION" in content:
                    analysis_mode = "DOCUMENTATION_WITH_MODERNIZATION"
                elif "Mode:** FULL_MODERNIZATION_ASSISTED" in content:
                    analysis_mode = "FULL_MODERNIZATION_ASSISTED"
                elif "Mode:** DOCUMENTATION_ONLY" in content:
                    analysis_mode = "DOCUMENTATION_ONLY"
        
        print(f"{Colors.MAGENTA}Analysis Mode: {analysis_mode}{Colors.RESET}")
        print()
        print(f"{Colors.BLUE}Next Steps:{Colors.RESET}")
        
        if self.project_name:
            print(f"1. Place your codebase in: codebase/{self.project_name}/")
        else:
            print("1. Place your codebase in: codebase/[project-name]/")
        
        print("2. Test MCP integration:")
        if platform.system() == 'Windows':
            print("   python framework/scripts/test_mcp_integration.py")
        else:
            print("   python3 framework/scripts/test_mcp_integration.py")
        
        print("3. Generate Repomix summary (optional but recommended):")
        if self.project_name:
            print(f"   repomix --config .repomix.config.json codebase/{self.project_name}/")
        else:
            print("   repomix --config .repomix.config.json codebase/")
        
        print("4. Start analysis in Claude Code:")
        print("   - Use @serena to activate the project")
        print("   - Use @mcp-orchestrator to begin analysis")
        
        if analysis_mode == "DOCUMENTATION_ONLY":
            print("   - Focus agents: @legacy-code-detective, @business-logic-analyst")
            print("   - Documentation: @documentation-specialist, @diagram-architect")
        elif "MODERNIZATION" in analysis_mode:
            print("   - All agents including: @modernization-architect")
            print("   - TARGET_TECH_STACK.md will guide modernization planning")
        
        print()
        
        print(f"{Colors.YELLOW}Output will be generated in:{Colors.RESET}")
        print("  - Documentation: output/docs/")
        print("  - Diagrams: output/diagrams/")
        print("  - Reports: output/reports/")
        print()
        
        print(f"{Colors.MAGENTA}For detailed instructions, see:{Colors.RESET}")
        print("  - README.md")
        print("  - framework/docs/MCP_USAGE_GUIDE.md")
        print("  - framework/docs/MCP_CONFIGURATION_GUIDE.md")
    
    def run(self):
        """Main setup execution"""
        try:
            self.show_banner()
            
            if not self.check_prerequisites():
                return 1
            
            self.setup_project_structure()
            self.copy_mcp_templates()
            self.configure_codebase_path()
            self.configure_analysis_mode()  # This replaces run_tech_stack_setup
            self.run_mcp_setup()
            self.generate_claude_md()  # Generate CLAUDE.md from template
            self.show_next_steps()
            
            return 0
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Setup cancelled by user{Colors.RESET}")
            return 1
        except Exception as e:
            print(f"\n{Colors.RED}Error during setup: {e}{Colors.RESET}")
            return 1


def main():
    """Main entry point"""
    setup = FrameworkSetup()
    sys.exit(setup.run())


if __name__ == "__main__":
    main()