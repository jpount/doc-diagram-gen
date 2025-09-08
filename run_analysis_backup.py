#!/usr/bin/env python3
"""
Quick Mode Analysis Runner
Executes agent sequence automatically for hands-off documentation generation
"""

import argparse
import json
import sys
import subprocess
import time
import logging
import os
from pathlib import Path
from typing import List
from datetime import datetime

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class QuickAnalysisRunner:
    """Automated runner for Quick Mode analysis"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_file = self.project_root / "analysis_config.json"
        self.setup_logging()
        self.config = self.load_config()
        
    def setup_logging(self):
        """Setup comprehensive logging"""
        # Create logs directory
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Setup file logging
        log_file = logs_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== Analysis Session Started ===")
        self.logger.info(f"Log file: {log_file}")
        
    def detect_technologies(self) -> dict:
        """Detect technologies from the codebase and Repomix summary"""
        self.logger.info("🔍 Detecting technologies from codebase...")
        
        detected = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "tools": [],
            "confidence_scores": {}
        }
        
        # First scan actual file extensions for definitive evidence
        project_name = self.config.get('project_name', 'unknown')
        codebase_dir = self.project_root / "codebase" / project_name
        
        if codebase_dir.exists():
            self.logger.info(f"📁 Scanning codebase directory: {codebase_dir}")
            file_extensions = {}
            
            for file_path in codebase_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix:
                    ext = file_path.suffix.lower()
                    file_extensions[ext] = file_extensions.get(ext, 0) + 1
            
            # Primary language detection based on actual files
            primary_extensions = {
                ".java": "Java",
                ".js": "JavaScript", 
                ".ts": "TypeScript",
                ".py": "Python",
                ".cs": "C#/.NET",
                ".cpp": "C++",
                ".c": "C",
                ".go": "Go",
                ".rs": "Rust",
                ".rb": "Ruby",
                ".php": "PHP"
            }
            
            for ext, count in file_extensions.items():
                if ext in primary_extensions and count > 0:
                    tech = primary_extensions[ext]
                    detected["languages"].append(tech)
                    detected["confidence_scores"][tech] = 95  # High confidence from file evidence
                    self.logger.info(f"📄 Found {count} {ext} files -> {tech} (95% confidence)")
        
        # Now check Repomix summary for framework/technology patterns (more specific patterns)
        repomix_file = self.project_root / "output" / "reports" / "repomix-summary.md"
        if repomix_file.exists():
            self.logger.info(f"📄 Analyzing Repomix summary: {repomix_file}")
            content = repomix_file.read_text()
            
            # Look for specific import patterns and configuration files - be very strict
            framework_patterns = {
                "J2EE/Jakarta EE": [
                    "javax.ejb", "javax.servlet", "javax.persistence", 
                    "ejb-jar.xml", "@Stateless", "@Entity", "@EJB"
                ],
                "Spring Framework": [
                    "org.springframework", "@Controller", "@Service", 
                    "@Repository", "@Component", "spring-boot-starter"
                ],
                "Hibernate": [
                    "org.hibernate", "hibernate.cfg.xml", "@OneToMany", "@ManyToOne"
                ],
                "JSF": [
                    "javax.faces", "faces-config.xml", "jsf-api"
                ],
                "Angular": [
                    "@angular/core", "angular.json", "import { Component }", "ng serve"
                ],
                "React": [
                    "import React from", "react-dom", "import { useState }", "create-react-app"
                ]
            }
            
            for framework, patterns in framework_patterns.items():
                matches = 0
                found_patterns = []
                
                for pattern in patterns:
                    if pattern in content:
                        matches += 1
                        found_patterns.append(pattern)
                
                if matches > 0:
                    confidence = min(matches * 20, 100)  # 20% per pattern, max 100%
                    detected["frameworks"].append(framework)
                    detected["confidence_scores"][framework] = confidence
                    self.logger.info(f"✅ Detected {framework} (confidence: {confidence}%)")
                    self.logger.info(f"   Found patterns: {', '.join(found_patterns[:3])}")
            
            # Check for specific Java enterprise patterns
            if "Java" in detected["languages"]:
                java_config_patterns = {
                    ".xml": 0, ".properties": 0, ".jsp": 0
                }
                
                for file_path in codebase_dir.rglob("*"):
                    if file_path.is_file() and file_path.suffix.lower() in java_config_patterns:
                        java_config_patterns[file_path.suffix.lower()] += 1
                
                for ext, count in java_config_patterns.items():
                    if count > 0:
                        config_type = {
                            ".xml": "Java XML Configuration",
                            ".properties": "Java Properties",
                            ".jsp": "Java Server Pages"
                        }[ext]
                        detected["tools"].append(config_type)
                        self.logger.info(f"📄 Found {count} {ext} files -> {config_type}")
        
        self.logger.info(f"🎯 Technology Detection Complete:")
        self.logger.info(f"   Languages: {detected['languages']}")
        self.logger.info(f"   Frameworks: {detected['frameworks']}")
        self.logger.info(f"   Tools/Config: {detected['tools']}")
        
        return detected
        
    def load_config(self) -> dict:
        """Load analysis configuration"""
        if not self.config_file.exists():
            print(f"{Colors.RED}❌ analysis_config.json not found. Run setup_simple.py first.{Colors.RESET}")
            sys.exit(1)
            
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def get_agent_sequence(self) -> List[str]:
        """Get agent sequence based on selected document types"""
        agents = []
        doc_types = self.config.get('document_types', [])
        
        # Always start with core agents
        agents.extend(['mcp-orchestrator', 'repomix-analyzer'])
        
        # Add agents based on document types
        if 'architecture' in doc_types:
            agents.append('architect-agent')
            
        if any(dt in doc_types for dt in ['business_rules', 'quality', 'performance', 'security']):
            agents.append('analyst-agent')
            
        # Always end with visualization and documentation
        agents.extend(['diagram-agent', 'doc-writer-agent'])
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(agents))
    
    def check_prerequisites(self) -> bool:
        """Check if prerequisites are met"""
        print(f"{Colors.BOLD}Checking Prerequisites...{Colors.RESET}")
        
        # Check if repomix summary exists
        repomix_file = self.project_root / "output" / "reports" / "repomix-summary.md"
        if not repomix_file.exists():
            print(f"{Colors.YELLOW}⚠️ Repomix summary not found{Colors.RESET}")
            print(f"Run: repomix --config .repomix.config.json codebase/{self.config['project_name']}/")
            return False
            
        # Check if claude command is available
        try:
            result = subprocess.run(['claude', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{Colors.RED}❌ Claude Code CLI not available{Colors.RESET}")
                return False
        except FileNotFoundError:
            print(f"{Colors.RED}❌ Claude Code CLI not installed{Colors.RESET}")
            return False
            
        print(f"{Colors.GREEN}✅ Prerequisites met{Colors.RESET}")
        return True
    
    def check_knowledge_files(self, agent_name: str, detected_tech: dict) -> None:
        """Check and log which knowledge files should be loaded for this agent"""
        self.logger.info(f"🧠 Knowledge loading check for {agent_name}:")
        
        knowledge_dir = self.project_root / "framework" / "knowledge"
        if not knowledge_dir.exists():
            self.logger.warning(f"⚠️ Knowledge directory not found: {knowledge_dir}")
            return
            
        # Check language-specific knowledge
        languages_dir = knowledge_dir / "languages"
        if languages_dir.exists():
            for tech in detected_tech.get("languages", []):
                tech_file = languages_dir / f"{tech.lower().replace('/', '_').replace('#', 'sharp')}.md"
                if tech_file.exists():
                    self.logger.info(f"   ✅ Language knowledge available: {tech} -> {tech_file.name}")
                else:
                    self.logger.info(f"   ❌ Language knowledge missing: {tech}")
        
        # Check framework-specific knowledge  
        frameworks_dir = knowledge_dir / "frameworks"
        if frameworks_dir.exists():
            for tech in detected_tech.get("frameworks", []):
                tech_file = frameworks_dir / f"{tech.lower().replace('/', '_')}.md"
                if tech_file.exists():
                    self.logger.info(f"   ✅ Framework knowledge available: {tech} -> {tech_file.name}")
                else:
                    self.logger.info(f"   ❌ Framework knowledge missing: {tech}")
        
        # Agent-specific knowledge requirements
        agent_knowledge = {
            "architect-agent": ["architecture patterns", "design patterns", "integration patterns"],
            "developer-agent": ["code quality", "technical debt", "anti-patterns"],
            "analyst-agent": ["business rules", "performance", "security"],
            "diagram-agent": ["mermaid", "visualization", "architecture diagrams"]
        }
        
        if agent_name in agent_knowledge:
            self.logger.info(f"   📋 {agent_name} should use: {', '.join(agent_knowledge[agent_name])}")
    
    def create_agent_context_summary(self, agent_name: str, output: str, duration: float, detected_tech: dict, specialization: str = None) -> None:
        """Create a context summary file for inter-agent communication"""
        # Create specialized context filename if needed
        if specialization:
            context_file = self.project_root / "output" / "context" / f"{agent_name}-{specialization}-summary.json"
        else:
            context_file = self.project_root / "output" / "context" / f"{agent_name}-summary.json"
        
        # Extract key findings from agent output
        findings = self.extract_key_findings(agent_name, output)
        
        context_data = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "execution_time": duration,
            "status": "completed",
            "technologies_detected": detected_tech,
            "summary": findings,
            "output_files": self.get_agent_output_files(agent_name),
            "recommendations_for_next": self.get_next_agent_recommendations(agent_name, findings)
        }
        
        with open(context_file, 'w') as f:
            json.dump(context_data, f, indent=2)
        
        self.logger.info(f"💾 Created context file: {context_file}")
    
    def extract_key_findings(self, agent_name: str, output: str) -> dict:
        """Extract key findings from agent output"""
        findings = {
            "key_components": [],
            "technologies": [],
            "patterns": [],
            "issues": [],
            "recommendations": []
        }
        
        if not output:
            return findings
        
        lines = output.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for key patterns in output
            if any(keyword in line.lower() for keyword in ['architecture', 'component', 'service', 'layer']):
                findings["key_components"].append(line[:100])
            elif any(keyword in line.lower() for keyword in ['java', 'ejb', 'spring', 'hibernate']):
                findings["technologies"].append(line[:100])
            elif any(keyword in line.lower() for keyword in ['pattern', 'design', 'mvc', 'dao']):
                findings["patterns"].append(line[:100])
            elif any(keyword in line.lower() for keyword in ['issue', 'problem', 'concern']):
                findings["issues"].append(line[:100])
            elif any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should']):
                findings["recommendations"].append(line[:100])
        
        # Limit to top findings to avoid bloat
        for key in findings:
            findings[key] = findings[key][:5]
        
        return findings
    
    def get_agent_output_files(self, agent_name: str) -> list:
        """Get list of files created by the agent"""
        output_files = []
        
        # Check common output locations
        docs_dir = self.project_root / "output" / "docs"
        diagrams_dir = self.project_root / "output" / "diagrams"
        
        # Look for files that might be from this agent
        agent_keywords = {
            "architect-agent": ["architecture", "system", "component"],
            "analyst-agent": ["business", "rules", "analysis", "performance", "security"],
            "diagram-agent": ["diagram", "mermaid", "visual"],
            "developer-agent": ["code", "quality", "technical", "debt"],
            "doc-writer-agent": ["documentation", "summary", "report"]
        }
        
        keywords = agent_keywords.get(agent_name, [])
        
        for directory in [docs_dir, diagrams_dir]:
            if directory.exists():
                for file_path in directory.glob("*.md"):
                    if any(keyword in file_path.name.lower() for keyword in keywords):
                        output_files.append(str(file_path.relative_to(self.project_root)))
        
        return output_files
    
    def get_next_agent_recommendations(self, agent_name: str, findings: dict) -> dict:
        """Generate recommendations for the next agent based on current findings"""
        recommendations = {}
        
        if agent_name == "architect-agent":
            recommendations = {
                "for_analyst_agent": "Focus on the identified components and analyze their business rules",
                "key_areas": findings.get("key_components", [])[:3],
                "technologies_to_analyze": findings.get("technologies", [])[:3]
            }
        elif agent_name == "analyst-agent":
            recommendations = {
                "for_diagram_agent": "Create diagrams for the identified business processes",
                "business_processes": findings.get("key_components", [])[:3],
                "critical_flows": findings.get("patterns", [])[:3]
            }
        elif agent_name == "diagram-agent":
            recommendations = {
                "for_doc_writer_agent": "Consolidate findings and create comprehensive documentation",
                "diagrams_created": findings.get("key_components", [])[:3]
            }
            
        return recommendations
    
    def run_agent(self, agent_name: str, detected_tech: dict = None) -> bool:
        """Run a single agent with Claude Code CLI"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🤖 STARTING AGENT: {agent_name}")
        self.logger.info(f"{'='*60}")
        
        if detected_tech:
            self.check_knowledge_files(agent_name, detected_tech)
        
        try:
            # Use claude CLI in non-interactive mode
            cmd = [
                'claude',
                '--output-format', 'text',
                '--dangerously-skip-permissions',
                '--print',  # Non-interactive mode
                f'@{agent_name}'
            ]
            
            self.logger.info(f"🚀 Executing command: {' '.join(cmd)}")
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout per agent
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.logger.info(f"✅ {agent_name} completed successfully ({duration:.1f}s)")
                
                # Log output details
                if result.stdout:
                    lines = result.stdout.split('\n')
                    self.logger.info(f"📄 Agent output: {len(lines)} lines, {len(result.stdout)} characters")
                    
                    # Log preview and look for key indicators
                    preview = result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout
                    self.logger.info(f"📖 Output preview:\n{preview}")
                    
                    # Check for knowledge loading indicators in output
                    if "knowledge" in result.stdout.lower():
                        self.logger.info("🧠 Agent output mentions 'knowledge' - likely loaded tech-specific knowledge")
                    if any(tech.lower() in result.stdout.lower() for tech in detected_tech.get("languages", [])):
                        self.logger.info("🎯 Agent output references detected technologies")
                
                # Check for created files and create context summary if missing
                context_file = self.project_root / "output" / "context" / f"{agent_name}-summary.json"
                if context_file.exists():
                    self.logger.info(f"💾 Context file created: {context_file}")
                else:
                    self.logger.warning(f"⚠️ Agent didn't create context file, generating basic summary...")
                    self.create_agent_context_summary(agent_name, result.stdout, duration, detected_tech)
                
                return True
            else:
                self.logger.error(f"❌ {agent_name} failed with return code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"🚫 Error output: {result.stderr[:500]}")
                if result.stdout:
                    self.logger.error(f"📄 Stdout: {result.stdout[:500]}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"⏰ {agent_name} timed out after 30 minutes")
            return False
        except Exception as e:
            self.logger.error(f"💥 {agent_name} exception: {str(e)}")
            return False
    
    def check_agent_completion(self, agent_name: str) -> bool:
        """Check if an agent has already completed successfully"""
        # Check for context file (primary indicator)
        context_file = self.project_root / "output" / "context" / f"{agent_name}-summary.json"
        if context_file.exists():
            try:
                with open(context_file, 'r') as f:
                    context_data = json.load(f)
                if context_data.get("status") == "completed":
                    self.logger.info(f"✅ Agent {agent_name} already completed - skipping")
                    return True
            except (json.JSONDecodeError, KeyError):
                self.logger.warning(f"⚠️ Corrupted context file for {agent_name} - will re-run")
                return False
        
        # Also check for expected output files
        expected_outputs = self.get_expected_output_files(agent_name)
        if expected_outputs and all(Path(f).exists() for f in expected_outputs):
            self.logger.info(f"✅ Agent {agent_name} output files exist - already completed")
            return True
            
        return False
    
    def get_expected_output_files(self, agent_name: str) -> list:
        """Get expected output files for an agent"""
        expected = {
            "mcp-orchestrator": [],  # Creates context only
            "repomix-analyzer": [],  # Creates context only  
            "architect-agent": ["output/docs/system_architecture.md"],
            "analyst-agent": ["output/docs/business_rules_analysis.md"],
            "diagram-agent": ["output/diagrams"],
            "developer-agent": ["output/docs/code_quality_analysis.md"],
            "doc-writer-agent": ["output/docs/final_documentation.md"]
        }
        
        files = expected.get(agent_name, [])
        return [f for f in files if f]  # Return non-empty files
    
    def run_analysis(self, resume: bool = True) -> bool:
        """Run the complete analysis sequence with optional resume capability"""
        self.logger.info(f"🚀 Starting Quick Mode Analysis (resume={resume})")
        self.logger.info(f"Project: {self.config['project_name']}")
        self.logger.info(f"Document Types: {', '.join(self.config['document_types'])}")
        
        print(f"{Colors.BOLD}🚀 Starting Quick Mode Analysis{Colors.RESET}")
        print(f"Project: {self.config['project_name']}")
        print(f"Document Types: {', '.join(self.config['document_types'])}")
        
        if resume:
            print(f"{Colors.CYAN}📋 Resume mode: Will skip completed agents{Colors.RESET}")
        
        if not self.check_prerequisites():
            return False
        
        # Detect technologies first
        detected_tech = self.detect_technologies()
        
        agents = self.get_agent_sequence()
        self.logger.info(f"Agent Sequence: {' → '.join(agents)}")
        print(f"\n{Colors.BOLD}Agent Sequence: {' → '.join(agents)}{Colors.RESET}")
        
        # Check which agents are already completed (if resume mode)
        completed_agents = []
        remaining_agents = []
        failed_agents = []
        
        if resume:
            print(f"\n{Colors.CYAN}🔍 Checking for completed agents...{Colors.RESET}")
            for agent in agents:
                if self.check_agent_completion(agent):
                    completed_agents.append(agent)
                    print(f"   ✅ {agent} - Already completed")
                else:
                    remaining_agents.append(agent)
                    print(f"   ⏳ {agent} - Needs to run")
            
            if completed_agents:
                print(f"\n{Colors.GREEN}📋 Resuming from agent: {remaining_agents[0] if remaining_agents else 'All done!'}{Colors.RESET}")
                self.logger.info(f"Resume: {len(completed_agents)} completed, {len(remaining_agents)} remaining")
        else:
            remaining_agents = agents
            print(f"\n{Colors.YELLOW}🔄 Full restart: Running all agents{Colors.RESET}")
        
        # Execute remaining agents
        for i, agent in enumerate(remaining_agents, 1):
            total_step = agents.index(agent) + 1
            print(f"\n{Colors.BOLD}Step {total_step}/{len(agents)}: {agent}{Colors.RESET}")
            
            if not self.run_agent(agent, detected_tech):
                failed_agents.append(agent)
                self.logger.error(f"❌ Agent {agent} failed, continuing with remaining agents...")
                print(f"{Colors.YELLOW}⚠️ Continuing with remaining agents...{Colors.RESET}")
        
        # Summary
        total_completed = len(completed_agents) + (len(remaining_agents) - len(failed_agents))
        self.logger.info("🏁 Analysis Complete!")
        self.logger.info(f"Results: {total_completed}/{len(agents)} agents succeeded")
        
        print(f"\n{Colors.BOLD}Analysis Complete!{Colors.RESET}")
        
        if completed_agents and resume:
            print(f"{Colors.CYAN}📋 Previously completed: {len(completed_agents)} agents{Colors.RESET}")
        
        if failed_agents:
            self.logger.warning(f"Failed agents: {', '.join(failed_agents)}")
            print(f"{Colors.YELLOW}⚠️ {len(failed_agents)} agents failed: {', '.join(failed_agents)}{Colors.RESET}")
        else:
            self.logger.info("✅ All agents completed successfully")
            print(f"{Colors.GREEN}✅ All agents completed successfully{Colors.RESET}")
        
        print(f"\n{Colors.CYAN}📁 Check results in:{Colors.RESET}")
        print(f"  - Documentation: output/docs/")
        print(f"  - Diagrams: output/diagrams/")
        print(f"  - Context: output/context/")
        print(f"  - Logs: logs/")
        
        return len(failed_agents) == 0

def main():
    parser = argparse.ArgumentParser(description='Run automated codebase analysis')
    parser.add_argument('--mode', choices=['quick', 'guided'], default='quick',
                       help='Analysis mode (quick=automated, guided=interactive)')
    parser.add_argument('--resume', action='store_true', default=True,
                       help='Resume from last completed agent (default: True)')
    parser.add_argument('--restart', action='store_true', 
                       help='Force restart from beginning (overrides --resume)')
    
    args = parser.parse_args()
    
    if args.mode == 'guided':
        print(f"{Colors.YELLOW}Guided mode: Run agents manually in Claude Code{Colors.RESET}")
        print(f"Follow the instructions in CLAUDE.md")
        return
    
    # Determine resume mode
    resume_mode = args.resume and not args.restart
    
    runner = QuickAnalysisRunner()
    success = runner.run_analysis(resume=resume_mode)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()