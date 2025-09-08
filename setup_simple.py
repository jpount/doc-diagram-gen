#!/usr/bin/env python3
"""
Simplified Setup Script for Documentation Framework
Focus on document types rather than agent selection
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List
import platform
import subprocess

# Color codes for terminal output
class Colors:
    """Terminal colors that work cross-platform"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class SimplifiedSetup:
    """Simplified setup focused on documentation needs"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent.resolve()
        self.framework_dir = self.script_dir / "framework"
        self.output_dir = self.script_dir / "output"
        self.codebase_dir = self.script_dir / "codebase"
        self.config = {
            "mode": "quick",
            "project_name": None,
            "document_types": [],
            "detected_tech": []
        }
    
    def run(self):
        """Main setup flow"""
        self.show_banner()
        
        # Step 1: Choose mode
        self.select_mode()
        
        # Step 2: Configure project
        self.configure_project()
        
        # Step 3: Select documentation types
        self.select_documentation()
        
        # Step 4: Detect tech stack
        self.detect_tech_stack()
        
        # Step 5: Create configuration
        self.create_configuration()
        
        # Step 6: Show next steps
        self.show_next_steps()
    
    def show_banner(self):
        """Display welcome banner"""
        os.system('cls' if platform.system() == 'Windows' else 'clear')
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.CYAN}     Documentation Framework - Simplified Setup{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        print()
        print(f"{Colors.BLUE}Generate comprehensive documentation for your codebase{Colors.RESET}")
        print(f"{Colors.BLUE}in just a few simple steps.{Colors.RESET}")
        print()
    
    def select_mode(self):
        """Select documentation mode"""
        print(f"{Colors.BOLD}Step 1: Choose Documentation Mode{Colors.RESET}")
        print()
        print("1. Quick Docs - Automated, no interaction (1-2 hours)")
        print("2. Guided Docs - Interactive with review points (3-4 hours)")
        print()
        
        while True:
            choice = input(f"Select mode [1-2]: ").strip()
            if choice == "1":
                self.config["mode"] = "quick"
                print(f"{Colors.GREEN}✓ Quick mode selected{Colors.RESET}")
                break
            elif choice == "2":
                self.config["mode"] = "guided"
                print(f"{Colors.GREEN}✓ Guided mode selected{Colors.RESET}")
                break
            else:
                print(f"{Colors.RED}Invalid choice. Please enter 1 or 2.{Colors.RESET}")
        print()
    
    def configure_project(self):
        """Configure project settings"""
        print(f"{Colors.BOLD}Step 2: Configure Project{Colors.RESET}")
        print()
        
        # Get project name
        default_name = "my-project"
        project_name = input(f"Project name [{default_name}]: ").strip() or default_name
        self.config["project_name"] = project_name
        
        # Create project directory
        project_dir = self.codebase_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"{Colors.GREEN}✓ Project configured: {project_name}{Colors.RESET}")
        print(f"{Colors.BLUE}  Place your code in: {project_dir}{Colors.RESET}")
        print()
    
    def select_documentation(self):
        """Select documentation types needed"""
        print(f"{Colors.BOLD}Step 3: Select Documentation Types{Colors.RESET}")
        print()
        
        doc_types = {
            "1": {"id": "architecture", "name": "Architecture Documentation", "essential": True},
            "2": {"id": "business_rules", "name": "Business Rules & Domain Logic", "essential": False},
            "3": {"id": "security", "name": "Security Assessment", "essential": False},
            "4": {"id": "performance", "name": "Performance Analysis", "essential": False},
            "5": {"id": "api", "name": "API Documentation", "essential": False},
            "6": {"id": "quality", "name": "Code Quality & Technical Debt", "essential": True},
            "7": {"id": "migration", "name": "Migration/Modernization Plan", "essential": False},
            "8": {"id": "ui_analysis", "name": "UI/UX Analysis", "essential": False},
            "9": {"id": "developer_guide", "name": "Developer/Troubleshooting Guide", "essential": False},
            "10": {"id": "executive_summary", "name": "Executive Summary", "essential": False},
            "11": {"id": "deployment", "name": "Deployment & Operations Guide", "essential": False},
            "12": {"id": "database", "name": "Database Schema & Data Model", "essential": False}
        }
        
        print("Available documentation types:")
        for key, doc in doc_types.items():
            essential = " (recommended)" if doc["essential"] else ""
            print(f"  {key}. {doc['name']}{essential}")
        
        print()
        print("Select documentation types:")
        print("  - Enter numbers separated by commas (e.g., 1,3,5)")
        print("  - Enter 'all' for comprehensive documentation")
        print("  - Enter 'essential' for recommended set only")
        print()
        
        while True:
            choice = input("Your selection: ").strip().lower()
            
            if choice == "all":
                self.config["document_types"] = [doc["id"] for doc in doc_types.values()]
                print(f"{Colors.GREEN}✓ All documentation types selected{Colors.RESET}")
                break
            elif choice == "essential":
                self.config["document_types"] = [
                    doc["id"] for doc in doc_types.values() if doc["essential"]
                ]
                print(f"{Colors.GREEN}✓ Essential documentation types selected{Colors.RESET}")
                break
            else:
                try:
                    selections = [s.strip() for s in choice.split(",")]
                    selected_docs = []
                    for sel in selections:
                        if sel in doc_types:
                            selected_docs.append(doc_types[sel]["id"])
                    
                    if selected_docs:
                        self.config["document_types"] = selected_docs
                        print(f"{Colors.GREEN}✓ {len(selected_docs)} documentation types selected{Colors.RESET}")
                        break
                    else:
                        print(f"{Colors.RED}No valid selections. Please try again.{Colors.RESET}")
                except:
                    print(f"{Colors.RED}Invalid input. Please try again.{Colors.RESET}")
        
        print()
    
    def detect_tech_stack(self):
        """Inform user about technology detection process"""
        print(f"{Colors.BOLD}Step 4: Technology Stack{Colors.RESET}")
        print()
        
        print(f"{Colors.BLUE}🎯 Technology Detection Process:{Colors.RESET}")
        print(f"  • Technology stack will be automatically detected during analysis")
        print(f"  • {Colors.CYAN}@mcp-orchestrator{Colors.RESET} coordinates the detection")
        print(f"  • {Colors.CYAN}@repomix-analyzer{Colors.RESET} analyzes your actual codebase and identifies technologies") 
        print(f"  • Agents automatically load appropriate knowledge based on detected technologies")
        print()
        
        print(f"{Colors.GREEN}✓ Technology detection will happen when you run the analysis{Colors.RESET}")
        print(f"{Colors.BLUE}  No technology guessing during setup - detection uses actual code analysis{Colors.RESET}")
        
        # Set config to indicate auto-detection
        self.config["detected_tech"] = ["Will be auto-detected during analysis"]
        print()
    
    def _show_detection_results(self, detected):
        """Display the auto-detection results"""
        print(f"{Colors.GREEN}🎯 Auto-Detection Results:{Colors.RESET}")
        print()
        
        has_findings = False
        for tech_type, techs in detected.items():
            if isinstance(techs, list) and techs:
                has_findings = True
                print(f"{Colors.CYAN}{tech_type.title()}:{Colors.RESET}")
                for tech in techs:
                    confidence = detected.get("confidence", {}).get(tech, 0)
                    confidence_text = "High" if confidence > 20 else "Medium" if confidence > 10 else "Low"
                    print(f"  • {tech} ({confidence_text} confidence)")
                print()
        
        if not has_findings:
            print(f"{Colors.YELLOW}No specific technologies detected.{Colors.RESET}")
            print()
    
    def _confirm_technologies(self, detected):
        """Ask user to confirm/modify detected technologies"""
        print(f"{Colors.BOLD}Confirm Technology Stack:{Colors.RESET}")
        print("1. Use detected technologies")
        print("2. Modify detected technologies") 
        print("3. Manual selection (ignore detection)")
        print()
        
        while True:
            choice = input("Your choice [1-3]: ").strip()
            
            if choice == "1":
                # Use as-is
                self.config["detected_tech"] = self._flatten_detected_tech(detected)
                print(f"{Colors.GREEN}✓ Using auto-detected technologies{Colors.RESET}")
                break
            elif choice == "2":
                # Let user modify
                self._modify_detected_tech(detected)
                break
            elif choice == "3":
                # Manual selection
                self._manual_tech_selection()
                break
            else:
                print(f"{Colors.RED}Invalid choice. Please enter 1, 2, or 3.{Colors.RESET}")
        
        print()
    
    def _modify_detected_tech(self, detected):
        """Allow user to modify detected technologies"""
        print(f"{Colors.YELLOW}Modify Detected Technologies:{Colors.RESET}")
        print("You can add or remove technologies from the detected list.")
        print()
        
        # Get flat list of detected techs
        current_techs = self._flatten_detected_tech(detected)
        
        print("Current technologies:")
        for i, tech in enumerate(current_techs, 1):
            print(f"  {i}. {tech}")
        print()
        
        # Common technologies to add
        common_techs = [
            "Java", "Spring", "Spring Boot", "J2EE/Jakarta EE",
            "JavaScript", "TypeScript", "Node.js", "React", "Angular", "Vue",
            "Python", "Django", "Flask", "FastAPI",
            "C#/.NET", ".NET Core", "ASP.NET",
            "PostgreSQL", "MySQL", "MongoDB", "Redis",
            "Docker", "Kubernetes", "AWS", "Azure"
        ]
        
        print("Add technologies (enter numbers separated by commas, or type technology names):")
        for i, tech in enumerate(common_techs, 1):
            if tech not in current_techs:
                print(f"  {i}. {tech}")
        print()
        
        additions = input("Add technologies (or press Enter to skip): ").strip()
        if additions:
            # Parse additions
            for addition in additions.split(","):
                addition = addition.strip()
                if addition.isdigit():
                    idx = int(addition) - 1
                    if 0 <= idx < len([t for t in common_techs if t not in current_techs]):
                        available = [t for t in common_techs if t not in current_techs]
                        current_techs.append(available[idx])
                else:
                    current_techs.append(addition)
        
        # Remove technologies
        print(f"\nRemove technologies (enter numbers to remove, or press Enter to skip):")
        for i, tech in enumerate(current_techs, 1):
            print(f"  {i}. {tech}")
        
        removals = input("Remove technologies: ").strip()
        if removals:
            indices_to_remove = []
            for removal in removals.split(","):
                if removal.strip().isdigit():
                    indices_to_remove.append(int(removal.strip()) - 1)
            
            # Remove in reverse order to maintain indices
            for idx in sorted(indices_to_remove, reverse=True):
                if 0 <= idx < len(current_techs):
                    current_techs.pop(idx)
        
        self.config["detected_tech"] = current_techs
        print(f"{Colors.GREEN}✓ Technology stack updated{Colors.RESET}")
    
    def _manual_tech_selection(self):
        """Manual technology selection when auto-detection isn't available"""
        print(f"{Colors.BOLD}Manual Technology Selection:{Colors.RESET}")
        print("Select the technologies used in your project:")
        print()
        
        tech_categories = {
            "Languages": ["Java", "JavaScript", "TypeScript", "Python", "C#/.NET"],
            "Frameworks": ["Spring", "Spring Boot", "J2EE", "Angular", "React", "Django", "Flask", "ASP.NET"],
            "Databases": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Oracle"],
            "Tools": ["Docker", "Kubernetes", "AWS", "Azure"]
        }
        
        selected = []
        
        for category, techs in tech_categories.items():
            print(f"{Colors.CYAN}{category}:{Colors.RESET}")
            for i, tech in enumerate(techs, 1):
                print(f"  {i}. {tech}")
            
            selections = input(f"Select {category.lower()} (numbers separated by commas, or press Enter to skip): ").strip()
            if selections:
                for sel in selections.split(","):
                    try:
                        idx = int(sel.strip()) - 1
                        if 0 <= idx < len(techs):
                            selected.append(techs[idx])
                    except ValueError:
                        pass
            print()
        
        if not selected:
            selected = ["Generic (no specific technologies)"]
        
        self.config["detected_tech"] = selected
        print(f"{Colors.GREEN}✓ Technology stack configured{Colors.RESET}")
        print()
    
    def _flatten_detected_tech(self, detected):
        """Convert detected tech dict to flat list"""
        flat_list = []
        for tech_type, techs in detected.items():
            if isinstance(techs, list) and tech_type != "confidence":
                flat_list.extend(techs)
        return flat_list
    
    def create_configuration(self):
        """Create configuration files"""
        print(f"{Colors.BOLD}Step 5: Creating Configuration{Colors.RESET}")
        print()
        
        # Create output directories
        dirs_to_create = [
            self.output_dir / "docs",
            self.output_dir / "diagrams",
            self.output_dir / "context",
            self.output_dir / "reports"
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        config_file = self.script_dir / "analysis_config.json"
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"{Colors.GREEN}✓ Configuration saved to analysis_config.json{Colors.RESET}")
        
        # Create MCP configuration
        self.create_mcp_config()
        
        # Create Repomix configuration
        self.create_repomix_config()
        
        # Create simplified CLAUDE.md
        claude_md = self.create_claude_md()
        claude_file = self.script_dir / "CLAUDE.md"
        with open(claude_file, 'w') as f:
            f.write(claude_md)
        
        print(f"{Colors.GREEN}✓ Created CLAUDE.md for agents{Colors.RESET}")
        print()
    
    def create_claude_md(self) -> str:
        """Create CLAUDE.md from template with proper substitutions"""
        
        # Load the template
        template_file = self.script_dir / "framework" / "templates" / "CLAUDE.template.md"
        if not template_file.exists():
            # Fallback to simple generation if template missing
            return self._create_simple_claude_md()
        
        with open(template_file, 'r') as f:
            template = f.read()
        
        # Get required agents
        agents = self.get_required_agents()
        
        # Technology stack formatting
        if self.config['detected_tech'] and self.config['detected_tech'] != ["Generic (no specific technologies)"]:
            tech_stack = "\n".join(f"- **{tech}** - Agents will load knowledge from framework/knowledge/" 
                                  for tech in self.config['detected_tech'])
            tech_stack += f"\n\n### Knowledge Loading\n"
            tech_stack += f"Agents automatically load technology-specific knowledge:\n"
            tech_stack += f"- Language patterns from `framework/knowledge/languages/`\n"
            tech_stack += f"- Framework patterns from `framework/knowledge/frameworks/`\n"
            tech_stack += f"- Generic fallback if specific knowledge unavailable"
        else:
            tech_stack = "- **Generic Analysis** - No specific technologies detected\n- Agents will use generic patterns and analysis"
        
        # Workflow steps based on mode
        if self.config['mode'] == 'quick':
            workflow_steps = f"""1. Run agents in sequence (automated)
2. No checkpoints - fully automated
3. Check output/docs/ when complete

### Agent Sequence:
```bash
{chr(10).join(f'@{agent}' for agent in agents)}
```"""
        else:
            workflow_steps = f"""1. Run agents with checkpoints for review
2. Respond to prompts at key checkpoints:
   - After architecture: Review system structure  
   - After analysis: Review findings
   - After diagrams: Verify visualizations
   - Final review: Approve documentation

### Agent Sequence with Checkpoints:
```bash
{chr(10).join(f'@{agent}' for agent in agents)}
```"""
        
        # Documentation types
        doc_types = "\n".join(f"- **{doc_type.replace('_', ' ').title()}**" 
                             for doc_type in self.config['document_types'])
        
        # Perform substitutions
        replacements = {
            "{{PROJECT_NAME}}": self.config['project_name'],
            "{{ANALYSIS_MODE}}": "DOCUMENTATION_ONLY",
            "{{DOCUMENTATION_MODE}}": self.config['mode'].upper(),
            "{{PROJECT_PATH}}": self.config['project_name'],
            "{{ANALYSIS_FOCUS}}": "Selected documentation types",
            "{{MODERNIZATION_ENABLED}}": "Yes" if "migration" in self.config['document_types'] else "No", 
            "{{USER_INTERACTION}}": "Interactive" if self.config['mode'] == 'guided' else "Automated",
            "{{REPOMIX_STATUS}}": "✅ ENABLED (80% token reduction)",
            # REMOVED: Serena status (not working)
            "{{MODERNIZATION_CONSTRAINTS}}": "",
            "{{TECHNOLOGY_STACK}}": tech_stack,
            "{{MODERNIZATION_AGENTS}}": "",
            "{{WORKFLOW_STEPS}}": workflow_steps,
            "{{MCP_TOOLS}}": "- `repomix` - Codebase compression (✅ ENABLED - PRIMARY)\n- File system access via MCP\n- Memory for cross-agent communication",
            "{{PROJECT_SIZE}}": "Medium",
            "{{TOKEN_BUDGET}}": "50,000 tokens (with Repomix)",
            "{{TARGET_TECH_STACK_FILE}}": f"- Technology Stack: {', '.join(self.config['detected_tech'])}"
        }
        
        # Apply all replacements
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        # Add selected documentation types
        result += f"\n\n## Selected Documentation Types\n{doc_types}\n"
        
        return result
    
    def _create_simple_claude_md(self) -> str:
        """Fallback simple CLAUDE.md creation"""
        agents = self.get_required_agents()
        
        return f"""# Simplified Documentation Framework Configuration

## Project: {self.config['project_name']}
## Mode: {self.config['mode'].title()}

## Technology Stack
{chr(10).join(f'- {tech}' for tech in self.config['detected_tech'])}

## Quick Start

### 1. Generate Repomix Summary (REQUIRED)
```bash
repomix --config .repomix.config.json codebase/{self.config['project_name']}/
```

### 2. Run Analysis
```bash
{chr(10).join(f'@{agent}' for agent in agents)}
```

## Selected Documentation Types
{chr(10).join(f'- {doc_type.replace("_", " ").title()}' for doc_type in self.config['document_types'])}
"""
    
    def get_required_agents(self) -> List[str]:
        """Get required agents based on selected documentation"""
        # Load agent configuration
        agent_config_file = self.framework_dir / "agents" / "core_agents.json"
        with open(agent_config_file, 'r') as f:
            agent_config = json.load(f)
        
        agents = set()
        
        # Add agents based on document types
        for doc_type in self.config["document_types"]:
            if doc_type in agent_config["document_types"]:
                agents.update(agent_config["document_types"][doc_type]["agents"])
        
        # Ensure proper order
        agent_order = ["architect-agent", "developer-agent", "analyst-agent", "diagram-agent", "doc-writer-agent"]
        return [a for a in agent_order if a in agents]
    
    def show_next_steps(self):
        """Show next steps to the user"""
        print(f"{Colors.BOLD}Setup Complete!{Colors.RESET}")
        print()
        print(f"{Colors.CYAN}Next Steps:{Colors.RESET}")
        print()
        print(f"1. Copy your code to: {Colors.YELLOW}codebase/{self.config['project_name']}/{Colors.RESET}")
        print()
        print(f"2. Generate Repomix summary:{Colors.YELLOW}")
        print(f"   repomix --config .repomix.config.json codebase/{self.config['project_name']}/{Colors.RESET}")
        print()
        
        if self.config["mode"] == "quick":
            print(f"3. For automated analysis, choose one:{Colors.YELLOW}")
            print(f"   Option A: Automated terminal session:")
            print(f"   python3 run_analysis.py --mode quick{Colors.RESET}")
            print()
            print(f"   Option B: Use n8n workflow for full automation")
        else:
            print(f"3. Start Claude Code and run agents interactively")
            print(f"   Follow the checkpoints in CLAUDE.md")
        
        print()
        print(f"{Colors.GREEN}Happy documenting!{Colors.RESET}")
    
    def create_mcp_config(self):
        """Create .mcp.json configuration file"""
        mcp_template_file = self.framework_dir / "mcp-configs" / "mcp.template.json"
        if mcp_template_file.exists():
            # Copy template to project root
            mcp_config_file = self.script_dir / ".mcp.json"
            shutil.copy2(mcp_template_file, mcp_config_file)
            print(f"{Colors.GREEN}✓ Created .mcp.json from template{Colors.RESET}")
        else:
            # Create basic MCP config
            basic_mcp = {
                "mcpServers": {
                    "filesystem": {
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-filesystem", "${PWD}"],
                        "env": {}
                    },
                    "memory": {
                        "command": "npx", 
                        "args": ["-y", "@modelcontextprotocol/server-memory"],
                        "env": {}
                    }
                }
            }
            mcp_config_file = self.script_dir / ".mcp.json"
            with open(mcp_config_file, 'w') as f:
                json.dump(basic_mcp, f, indent=2)
            print(f"{Colors.GREEN}✓ Created basic .mcp.json{Colors.RESET}")
    
    def create_repomix_config(self):
        """Create .repomix.config.json configuration file"""
        repomix_template_file = self.framework_dir / "mcp-configs" / ".repomix.config.json"
        if repomix_template_file.exists():
            # Copy template to project root
            repomix_config_file = self.script_dir / ".repomix.config.json"
            
            # Read template and update output path for project
            with open(repomix_template_file, 'r') as f:
                repomix_config = json.load(f)
            
            # Update output path to project-specific location
            repomix_config["output"]["filePath"] = f"output/reports/repomix-summary.md"
            
            with open(repomix_config_file, 'w') as f:
                json.dump(repomix_config, f, indent=2)
                
            print(f"{Colors.GREEN}✓ Created .repomix.config.json{Colors.RESET}")
        else:
            # Create basic repomix config
            basic_repomix = {
                "output": {
                    "filePath": f"output/reports/repomix-summary.md",
                    "style": "markdown",
                    "headerText": "# Codebase Summary\\nGenerated by Repomix for AI-optimized analysis",
                    "removeComments": False,
                    "removeEmptyLines": False,
                    "showLineNumbers": False,
                    "copyToClipboard": False
                },
                "include": ["**/*.java", "**/*.js", "**/*.ts", "**/*.py", "**/*.cs"],
                "ignore": {"useGitignore": True, "useDefaultPatterns": True}
            }
            repomix_config_file = self.script_dir / ".repomix.config.json"
            with open(repomix_config_file, 'w') as f:
                json.dump(basic_repomix, f, indent=2)
            print(f"{Colors.GREEN}✓ Created basic .repomix.config.json{Colors.RESET}")

if __name__ == "__main__":
    setup = SimplifiedSetup()
    setup.run()