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

# Import the centralized document-to-agent mapping
sys.path.append(str(Path(__file__).parent))
from n8n.services.n8n_config_reader import N8nConfigReader

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
            
            # Look for specific import patterns and configuration files - VERY strict with word boundaries
            import re
            
            framework_patterns = {
                "J2EE/Jakarta EE": [
                    r"javax\.ejb\b", r"javax\.servlet\b", r"javax\.persistence\b", 
                    r"ejb-jar\.xml", r"@Stateless\b", r"@Entity\b", r"@EJB\b"
                ],
                "Spring Framework": [
                    r"org\.springframework\b", r"@Controller\b", r"@Service\b", 
                    r"@Repository\b", r"@Component\b", r"spring-boot-starter"
                ],
                "Hibernate": [
                    r"org\.hibernate\b", r"hibernate\.cfg\.xml", r"@OneToMany\b", r"@ManyToOne\b"
                ],
                "JSF": [
                    r"javax\.faces\b", r"faces-config\.xml", r"jsf-api\b"
                ],
                # REMOVED: Angular and React patterns - too prone to false positives in legacy Java
            }
            
            for framework, regex_patterns in framework_patterns.items():
                matches = 0
                found_patterns = []
                
                for pattern in regex_patterns:
                    # Use regex search with word boundaries for precision
                    if re.search(pattern, content):
                        matches += 1
                        # Store clean pattern name for display
                        clean_pattern = pattern.replace(r'\b', '').replace(r'\.', '.')
                        found_patterns.append(clean_pattern)
                
                if matches > 0:
                    confidence = min(matches * 25, 100)  # 25% per pattern, max 100%
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
    
    def get_agent_execution_plan(self, detected_tech: dict = None) -> List[dict]:
        """Get detailed agent execution plan with specializations using centralized mapping"""
        self.logger.info("🎯 Creating multi-context execution plan...")
        
        execution_plan = []
        doc_types = self.config.get('document_types', [])
        
        # Use centralized config reader for consistent mapping
        config_reader = N8nConfigReader(self.project_root)
        document_to_agents = config_reader.DOCUMENT_TO_AGENTS
        
        # Always start with required discovery agents
        for agent in config_reader.REQUIRED_DISCOVERY_AGENTS:
            execution_plan.append({
                "agent": agent,
                "specialization": None, 
                "focus": self._get_agent_focus_description(agent),
                "context_key": agent,
                "knowledge_focus": None
            })
        
        # Use provided detected tech or detect if not provided
        if detected_tech is None:
            detected_tech = self.detect_technologies()
            
        primary_languages = detected_tech.get("languages", [])
        frameworks = detected_tech.get("frameworks", [])
        
        self.logger.info(f"📚 Detected technologies: Languages={primary_languages}, Frameworks={frameworks}")
        
        # Generate agent plan based on document selections using centralized mapping
        agent_counts = {}  # Track how many times each agent is needed
        specializations = {}  # Track specializations for each agent
        
        # Count agents needed from document selections
        for doc_type in doc_types:
            if doc_type in document_to_agents:
                required_agents = document_to_agents[doc_type]
                for agent in required_agents:
                    agent_counts[agent] = agent_counts.get(agent, 0) + 1
                    if agent not in specializations:
                        specializations[agent] = []
                    specializations[agent].append(doc_type)
                self.logger.info(f"   📋 {doc_type} -> {required_agents}")
            else:
                self.logger.warning(f"   ⚠️ Unknown document type: {doc_type}")
        
        # Generate execution plan based on agent requirements
        for agent, count in agent_counts.items():
            if agent in ['mcp-orchestrator', 'repomix-analyzer']:
                continue  # Already added above
                
            agent_specializations = specializations[agent]
            
            if agent == "architect-agent":
                # For architect, create technology-specific instances
                tech_instances = 0
                for tech in primary_languages[:2]:  # Top 2 languages
                    if tech_instances >= count:
                        break
                    tech_key = tech.lower().replace('/', '_').replace('#', 'sharp').replace(' ', '_')
                    execution_plan.append({
                        "agent": agent,
                        "specialization": tech_key,
                        "focus": f"{tech} architecture analysis for: {', '.join(agent_specializations)}",
                        "context_key": f"architect-{tech_key}",
                        "knowledge_focus": tech
                    })
                    tech_instances += 1
                    self.logger.info(f"   📐 {agent} ({tech_key}): {', '.join(agent_specializations)}")
                    
                # Add framework-specific instances if needed
                for framework in frameworks[:1]:
                    if tech_instances >= count or framework in primary_languages:
                        break
                    fw_key = framework.lower().replace('/', '_').replace(' ', '_')
                    execution_plan.append({
                        "agent": agent,
                        "specialization": fw_key,
                        "focus": f"{framework} architecture analysis for: {', '.join(agent_specializations)}",
                        "context_key": f"architect-{fw_key}",
                        "knowledge_focus": framework
                    })
                    tech_instances += 1
                    self.logger.info(f"   📐 {agent} ({fw_key}): {', '.join(agent_specializations)}")
                    
            elif agent == "analyst-agent":
                # For analyst, create specialization-specific instances
                for i, doc_type in enumerate(agent_specializations):
                    if i >= count:
                        break
                    specialization = doc_type.replace('_', '')  # business_rules -> business
                    execution_plan.append({
                        "agent": agent,
                        "specialization": specialization,
                        "focus": self._get_analysis_focus(doc_type),
                        "context_key": f"analyst-{specialization}",
                        "knowledge_focus": f"{doc_type}_analysis"
                    })
                    self.logger.info(f"   🔍 {agent} ({specialization}): {doc_type}")
                    
            elif agent == "developer-agent":
                # For developer, create specialization-specific instances
                for i, doc_type in enumerate(agent_specializations):
                    if i >= count:
                        break
                    specialization = doc_type.replace('_', '')  # developer_guide -> developerguide
                    execution_plan.append({
                        "agent": agent,
                        "specialization": specialization,
                        "focus": self._get_developer_focus(doc_type),
                        "context_key": f"developer-{specialization}",
                        "knowledge_focus": f"{doc_type}_analysis"
                    })
                    self.logger.info(f"   👨‍💻 {agent} ({specialization}): {doc_type}")
        
        # Always end with required final agents
        existing_agents = [step["agent"] for step in execution_plan if step["specialization"] is None]
        for agent in config_reader.REQUIRED_FINAL_AGENTS:
            if agent not in existing_agents:  # Avoid duplicates with non-specialized versions
                execution_plan.append({
                    "agent": agent,
                    "specialization": None,
                    "focus": self._get_agent_focus_description(agent),
                    "context_key": agent,
                    "knowledge_focus": "synthesis" if agent == "diagram-agent" else "documentation"
                })
        
        self.logger.info(f"📋 Execution plan created: {len(execution_plan)} specialized agent runs")
        return execution_plan
    
    def _get_agent_focus_description(self, agent: str) -> str:
        """Get focus description for an agent"""
        focus_map = {
            "mcp-orchestrator": "MCP setup and coordination",
            "repomix-analyzer": "Codebase analysis and technology detection", 
            "diagram-agent": "Comprehensive diagram generation from all contexts",
            "doc-writer-agent": "Final documentation synthesis from all contexts"
        }
        return focus_map.get(agent, f"{agent} analysis")
    
    def _get_analysis_focus(self, doc_type: str) -> str:
        """Get analysis focus description for document type"""
        focus_map = {
            "business_rules": "Business rules and domain logic extraction",
            "performance": "Performance bottlenecks and optimization analysis",
            "security": "Security vulnerabilities and compliance analysis", 
            "ui_analysis": "UI/UX architecture and component analysis",
            "migration": "Legacy modernization and migration analysis"
        }
        return focus_map.get(doc_type, f"{doc_type} analysis")
    
    def _get_developer_focus(self, doc_type: str) -> str:
        """Get developer focus description for document type"""
        focus_map = {
            "quality": "Code quality and technical debt analysis",
            "developer_guide": "Development setup and coding standards analysis",
            "deployment": "Deployment procedures and infrastructure analysis"
        }
        return focus_map.get(doc_type, f"{doc_type} development analysis")
    
    def get_agent_sequence(self, detected_tech: dict = None) -> List[str]:
        """Get simple agent sequence for backward compatibility"""
        plan = self.get_agent_execution_plan(detected_tech)
        return [f"{step['agent']}" + (f"-{step['specialization']}" if step['specialization'] else "") 
                for step in plan]
    
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
    
    def check_knowledge_files(self, agent_name: str, detected_tech: dict, specialization: str = None) -> None:
        """Check and log which knowledge files should be loaded for this agent"""
        display_name = f"{agent_name}" + (f" ({specialization})" if specialization else "")
        self.logger.info(f"🧠 Knowledge loading check for {display_name}:")
        
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
                # Try frameworks directory first
                tech_file = frameworks_dir / f"{tech.lower().replace('/', '_').replace(' ', '_')}.md"
                if tech_file.exists():
                    self.logger.info(f"   ✅ Framework knowledge available: {tech} -> {tech_file.name}")
                else:
                    # Fallback: Check if it's actually in languages directory (e.g., J2EE)
                    lang_tech_file = languages_dir / f"{tech.lower().replace('/', '_').replace(' ', '_')}.md"
                    if lang_tech_file.exists():
                        self.logger.info(f"   ✅ Framework knowledge available: {tech} -> {lang_tech_file.name} (in languages)")
                    else:
                        self.logger.info(f"   ❌ Framework knowledge missing: {tech}")
        
        # Specialization-specific knowledge requirements
        if specialization:
            spec_knowledge = {
                "java": ["Java enterprise patterns", "J2EE/Jakarta EE", "Spring Framework", "Maven/Gradle builds", "JVM optimization"],
                "j2ee_jakarta_ee": ["J2EE/Jakarta EE patterns", "Enterprise architecture", "EJB patterns", "JPA/Hibernate", "Application server deployment"],
                "angular": ["Angular architecture", "TypeScript patterns", "Component design", "RxJS patterns", "Angular CLI"],
                "businessrules": ["Business rule extraction", "Domain modeling", "Process analysis", "Workflow patterns", "Decision trees"],
                "performance": [
                    "Performance profiling", "JVM performance tuning", "Database query optimization",
                    "Memory leak detection", "CPU bottleneck analysis", "Network latency analysis",
                    "Caching strategies", "Load testing patterns", "Scalability assessment"
                ],
                "security": [
                    "OWASP Top 10", "Authentication/authorization patterns", "SQL injection prevention",
                    "XSS protection", "CSRF prevention", "Cryptography patterns", "Secure coding practices",
                    "Vulnerability assessment", "Compliance frameworks (SOX, HIPAA, GDPR)", "Security logging"
                ],
                "quality": ["Code quality metrics", "Technical debt analysis", "Refactoring patterns", "Code review checklist", "Testing strategies"],
                "ui": ["UI/UX patterns", "Frontend architecture", "Component analysis", "JSF/JSP patterns", "Responsive design", "Accessibility"],
                "migration": ["Legacy system analysis", "Migration strategies", "Risk assessment", "Modernization patterns", "Technology transition"],
                "architecture": ["System architecture patterns", "Integration patterns", "Data architecture", "Security architecture", "Performance architecture"],
                "developerguide": ["Development workflows", "Build processes", "Testing frameworks", "Debugging techniques", "IDE configuration"],
                "deployment": ["Deployment patterns", "Infrastructure as code", "Container orchestration", "CI/CD pipelines", "Environment management"]
            }
            
            if specialization in spec_knowledge:
                self.logger.info(f"   🎯 Specialized knowledge for {specialization}: {', '.join(spec_knowledge[specialization])}")
        
        # Agent-specific knowledge requirements (expandable base knowledge)
        agent_knowledge = {
            "architect-agent": [
                "architecture patterns", "design patterns", "integration patterns", 
                "microservices architecture", "API design", "system decomposition",
                "scalability patterns", "data architecture", "enterprise architecture"
            ],
            "developer-agent": [
                "code quality", "technical debt", "anti-patterns", "refactoring techniques",
                "SOLID principles", "clean code practices", "testing strategies",
                "dependency management", "build optimization", "code review guidelines"
            ],
            "analyst-agent": [
                "business rules", "performance analysis", "security assessment",
                "vulnerability scanning", "compliance frameworks", "risk assessment",
                "performance profiling", "bottleneck identification", "optimization strategies",
                "business process modeling", "domain analysis", "data flow analysis"
            ],
            "diagram-agent": [
                "mermaid syntax", "visualization best practices", "architecture diagrams",
                "sequence diagrams", "data flow diagrams", "entity relationship diagrams",
                "network diagrams", "deployment diagrams", "component diagrams"
            ],
            "doc-writer-agent": [
                "technical writing", "documentation standards", "API documentation",
                "user guides", "architecture documentation", "troubleshooting guides",
                "executive summaries", "migration guides", "compliance documentation"
            ]
        }
        
        if agent_name in agent_knowledge:
            self.logger.info(f"   📋 {agent_name} base knowledge: {', '.join(agent_knowledge[agent_name])}")
    
    def create_agent_context_summary(self, agent_name: str, output: str, duration: float, detected_tech: dict, specialization: str = None, context_key: str = None) -> None:
        """Create a context summary file for inter-agent communication"""
        # Use provided context_key or create one
        if context_key:
            context_file = self.project_root / "output" / "context" / f"{context_key}-summary.json"
        elif specialization:
            context_file = self.project_root / "output" / "context" / f"{agent_name}-{specialization}-summary.json"
        else:
            context_file = self.project_root / "output" / "context" / f"{agent_name}-summary.json"
        
        # Extract key findings from agent output
        findings = self.extract_key_findings(agent_name, output)
        
        context_data = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "specialization": specialization,
            "context_key": context_key or (f"{agent_name}-{specialization}" if specialization else agent_name),
            "execution_time": duration,
            "status": "completed",
            "technologies_detected": detected_tech,
            "summary": findings,
            "output_files": self.get_agent_output_files(agent_name),
            "recommendations_for_next": self.get_next_agent_recommendations(agent_name, findings, specialization)
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
    
    def get_next_agent_recommendations(self, agent_name: str, findings: dict, specialization: str = None) -> dict:
        """Generate recommendations for the next agent based on current findings"""
        recommendations = {}
        
        # Create specialized recommendations based on agent and specialization
        if agent_name == "architect-agent":
            if specialization:
                recommendations = {
                    f"for_other_agents": f"Reference {specialization} architecture findings when analyzing related components",
                    "specialization_focus": specialization,
                    "key_architectural_components": findings.get("key_components", [])[:3],
                    "technology_specific_patterns": findings.get("patterns", [])[:3]
                }
            else:
                recommendations = {
                    "for_analyst_agent": "Focus on the identified components and analyze their business rules",
                    "key_areas": findings.get("key_components", [])[:3],
                    "technologies_to_analyze": findings.get("technologies", [])[:3]
                }
                
        elif agent_name == "analyst-agent":
            if specialization:
                recommendations = {
                    f"for_diagram_agent": f"Create diagrams highlighting {specialization} analysis findings",
                    "analysis_focus": specialization,
                    "critical_findings": findings.get("key_components", [])[:3],
                    "specialized_insights": findings.get("recommendations", [])[:3]
                }
            else:
                recommendations = {
                    "for_diagram_agent": "Create diagrams for the identified business processes",
                    "business_processes": findings.get("key_components", [])[:3],
                    "critical_flows": findings.get("patterns", [])[:3]
                }
                
        elif agent_name == "developer-agent":
            recommendations = {
                "for_doc_writer_agent": f"Include {specialization} quality findings in final documentation",
                "quality_focus": specialization,
                "key_issues": findings.get("issues", [])[:3],
                "improvement_recommendations": findings.get("recommendations", [])[:3]
            }
            
        elif agent_name == "diagram-agent":
            recommendations = {
                "for_doc_writer_agent": "Consolidate all specialized findings and create comprehensive documentation",
                "diagrams_created": findings.get("key_components", [])[:3],
                "contexts_to_synthesize": "all specialized contexts"
            }
            
        return recommendations
    
    def run_data_integrity_check(self, agent_name: str) -> None:
        """Run data integrity validation after agent execution"""
        try:
            # Import and run the existing data integrity validator
            import subprocess
            result = subprocess.run(
                ['python3', 'framework/scripts/data_integrity_validator.py'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check for violations in output
            if "violations" in result.stderr.lower() and "0 invalid" not in result.stderr:
                self.logger.warning(f"🚨 DATA INTEGRITY VIOLATIONS detected after {agent_name}")
                # Log a sample of violations
                lines = result.stderr.split('\n')
                violation_lines = [line for line in lines if "❌" in line or "Found:" in line][:5]
                for violation_line in violation_lines:
                    self.logger.warning(f"   {violation_line}")
                self.logger.warning(f"   Full report: python3 framework/scripts/data_integrity_validator.py")
            else:
                self.logger.info(f"✅ No data integrity violations detected for {agent_name}")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Could not run data integrity check: {e}")
    
    def run_diagram_validation(self) -> None:
        """Run diagram validation and auto-fix after diagram-agent execution"""
        try:
            self.logger.info("🔧 Running diagram validation and auto-fix...")
            
            # Run validator with auto-fix
            result = subprocess.run(
                ['python3', 'framework/scripts/simple_mermaid_validator.py', '--fix'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse results
            if "invalid" in result.stderr and "0 invalid" not in result.stderr:
                self.logger.warning(f"🚨 BROKEN DIAGRAMS detected and fixed")
                # Log summary
                lines = result.stderr.split('\n')
                summary_line = [line for line in lines if "Summary:" in line]
                if summary_line:
                    self.logger.warning(f"   {summary_line[0]}")
            else:
                self.logger.info("✅ All diagrams valid - no fixes needed")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Could not run diagram validation: {e}")
    
    def run_agent(self, execution_step: dict, detected_tech: dict = None) -> bool:
        """Run a single agent with specialized context using Claude Code CLI"""
        agent_name = execution_step["agent"]
        specialization = execution_step.get("specialization")
        focus = execution_step.get("focus", "General analysis")
        knowledge_focus = execution_step.get("knowledge_focus")
        context_key = execution_step.get("context_key", agent_name)
        
        # Create display name for logging
        display_name = f"{agent_name}"
        if specialization:
            display_name += f" ({specialization})"
            
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🤖 STARTING SPECIALIZED AGENT: {display_name}")
        self.logger.info(f"🎯 Focus: {focus}")
        if knowledge_focus:
            self.logger.info(f"🧠 Knowledge Focus: {knowledge_focus}")
        self.logger.info(f"📝 Context Key: {context_key}")
        self.logger.info(f"{'='*60}")
        
        if detected_tech:
            self.check_knowledge_files(agent_name, detected_tech, specialization)
        
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
                context_file = self.project_root / "output" / "context" / f"{context_key}-summary.json"
                if context_file.exists():
                    self.logger.info(f"💾 Context file created: {context_file}")
                else:
                    self.logger.warning(f"⚠️ Agent didn't create specialized context file, generating basic summary...")
                    self.create_agent_context_summary(agent_name, result.stdout, duration, detected_tech, specialization, context_key)
                
                # Run data integrity validation after agent completes
                self.run_data_integrity_check(agent_name)
                
                # Run diagram validation if this is diagram-agent
                if agent_name == "diagram-agent":
                    self.run_diagram_validation()
                
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
    
    def check_step_completion(self, execution_step: dict) -> bool:
        """Check if a specialized agent execution step has already completed successfully"""
        agent_name = execution_step["agent"]
        context_key = execution_step.get("context_key", agent_name)
        specialization = execution_step.get("specialization")
        
        # Check for specialized context file (primary indicator)
        context_file = self.project_root / "output" / "context" / f"{context_key}-summary.json"
        if context_file.exists():
            try:
                with open(context_file, 'r') as f:
                    context_data = json.load(f)
                
                # Check for completion indicators - be flexible about format
                status = context_data.get("status")
                has_timestamp = context_data.get("timestamp")
                has_agent = context_data.get("agent") == agent_name
                
                # Consider completed if:
                # 1. Explicit status = "completed", OR
                # 2. Has timestamp + correct agent (implies successful execution)
                is_completed = (status == "completed") or (has_timestamp and has_agent)
                
                if is_completed:
                    display_name = f"{agent_name}" + (f" ({specialization})" if specialization else "")
                    self.logger.info(f"✅ {display_name} already completed - skipping")
                    return True
                else:
                    display_name = f"{agent_name}" + (f" ({specialization})" if specialization else "")
                    self.logger.warning(f"⚠️ {display_name} context exists but incomplete - will re-run")
                    return False
                    
            except (json.JSONDecodeError, KeyError) as e:
                display_name = f"{agent_name}" + (f" ({specialization})" if specialization else "")
                self.logger.warning(f"⚠️ Corrupted context file for {display_name} - will re-run")
                return False
        
        # Also check for expected output files (be very careful here to avoid false positives)
        expected_outputs = self.get_expected_output_files(execution_step)
        if expected_outputs and all(Path(f).exists() for f in expected_outputs):
            display_name = f"{agent_name}" + (f" ({specialization})" if specialization else "")
            self.logger.info(f"✅ {display_name} output files exist - already completed")
            return True
            
        return False
    
    def get_expected_output_files(self, execution_step: dict) -> list:
        """Get expected output files for a specialized execution step"""
        agent_name = execution_step["agent"]
        specialization = execution_step.get("specialization")
        
        # Be very conservative about expected outputs to avoid false completion detection
        # Only check for files that are DEFINITIVE indicators of completion
        expected = {
            "mcp-orchestrator": [],  # Context-only completion
            "repomix-analyzer": [],  # Context-only completion
            "architect-agent": [],   # Context-only completion
            "analyst-agent": [],     # Context-only completion
            "diagram-agent": [],     # Context-only completion - too many false positives from old files
            "developer-agent": [],   # Context-only completion
            "doc-writer-agent": []   # Context-only completion
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
        
        # Detect technologies first (separate from execution plan)
        detected_tech = self.detect_technologies()
        
        # Get detailed execution plan with already-detected technologies
        execution_plan = self.get_agent_execution_plan(detected_tech)
        
        # Display execution plan
        print(f"\n{Colors.BOLD}📋 Multi-Context Execution Plan:{Colors.RESET}")
        for i, step in enumerate(execution_plan, 1):
            display_name = f"{step['agent']}"
            if step['specialization']:
                display_name += f" ({step['specialization']})"
            print(f"  {i}. {display_name} - {step['focus']}")
        
        self.logger.info(f"📋 Execution plan: {len(execution_plan)} specialized steps")
        
        # Check which steps are already completed (if resume mode)
        completed_steps = []
        remaining_steps = []
        failed_steps = []
        
        if resume:
            print(f"\n{Colors.CYAN}🔍 Checking for completed specialized steps...{Colors.RESET}")
            for step in execution_plan:
                if self.check_step_completion(step):
                    completed_steps.append(step)
                    display_name = f"{step['agent']}" + (f" ({step['specialization']})" if step['specialization'] else "")
                    print(f"   ✅ {display_name} - Already completed")
                else:
                    remaining_steps.append(step)
                    display_name = f"{step['agent']}" + (f" ({step['specialization']})" if step['specialization'] else "")
                    print(f"   ⏳ {display_name} - Needs to run")
            
            if completed_steps:
                next_step = remaining_steps[0] if remaining_steps else None
                if next_step:
                    next_display = f"{next_step['agent']}" + (f" ({next_step['specialization']})" if next_step['specialization'] else "")
                    print(f"\n{Colors.GREEN}📋 Resuming from step: {next_display}{Colors.RESET}")
                else:
                    print(f"\n{Colors.GREEN}📋 All steps completed!{Colors.RESET}")
                self.logger.info(f"Resume: {len(completed_steps)} completed, {len(remaining_steps)} remaining")
        else:
            remaining_steps = execution_plan
            print(f"\n{Colors.YELLOW}🔄 Full restart: Running all {len(execution_plan)} steps{Colors.RESET}")
        
        # Execute remaining steps
        for i, step in enumerate(remaining_steps, 1):
            total_step = execution_plan.index(step) + 1
            display_name = f"{step['agent']}" + (f" ({step['specialization']})" if step['specialization'] else "")
            print(f"\n{Colors.BOLD}Step {total_step}/{len(execution_plan)}: {display_name}{Colors.RESET}")
            print(f"{Colors.BLUE}Focus: {step['focus']}{Colors.RESET}")
            
            if not self.run_agent(step, detected_tech):
                failed_steps.append(step)
                self.logger.error(f"❌ Specialized step {step['context_key']} failed, continuing...")
                print(f"{Colors.YELLOW}⚠️ Continuing with remaining steps...{Colors.RESET}")
        
        # Summary
        total_completed = len(completed_steps) + (len(remaining_steps) - len(failed_steps))
        self.logger.info("🏁 Multi-Context Analysis Complete!")
        self.logger.info(f"Results: {total_completed}/{len(execution_plan)} specialized steps succeeded")
        
        print(f"\n{Colors.BOLD}Multi-Context Analysis Complete!{Colors.RESET}")
        
        if completed_steps and resume:
            print(f"{Colors.CYAN}📋 Previously completed: {len(completed_steps)} specialized steps{Colors.RESET}")
        
        if failed_steps:
            failed_names = [f"{s['agent']}" + (f" ({s['specialization']})" if s['specialization'] else "") for s in failed_steps]
            self.logger.warning(f"Failed steps: {', '.join(failed_names)}")
            print(f"{Colors.YELLOW}⚠️ {len(failed_steps)} specialized steps failed: {', '.join(failed_names)}{Colors.RESET}")
        else:
            self.logger.info("✅ All specialized steps completed successfully")
            print(f"{Colors.GREEN}✅ All specialized steps completed successfully{Colors.RESET}")
        
        # Show context summary
        self.show_context_summary()
        
        print(f"\n{Colors.CYAN}📁 Check results in:{Colors.RESET}")
        print(f"  - Documentation: output/docs/")
        print(f"  - Diagrams: output/diagrams/")
        print(f"  - Context: output/context/ ({len(execution_plan)} specialized contexts)")
        print(f"  - Logs: logs/")
        
        return len(failed_steps) == 0
    
    def show_context_summary(self) -> None:
        """Show summary of all created contexts"""
        context_dir = self.project_root / "output" / "context"
        context_files = list(context_dir.glob("*-summary.json"))
        
        if context_files:
            print(f"\n{Colors.CYAN}🗂️ Specialized Contexts Created:{Colors.RESET}")
            for context_file in sorted(context_files):
                try:
                    with open(context_file, 'r') as f:
                        context_data = json.load(f)
                    
                    agent = context_data.get("agent", "unknown")
                    specialization = context_data.get("specialization")
                    status = context_data.get("status", "unknown")
                    
                    display_name = agent + (f" ({specialization})" if specialization else "")
                    status_icon = "✅" if status == "completed" else "❌"
                    
                    print(f"   {status_icon} {display_name} -> {context_file.name}")
                    
                except (json.JSONDecodeError, FileNotFoundError):
                    print(f"   ⚠️ {context_file.name} - Corrupted or unreadable")
        
        self.logger.info(f"📊 Context summary: {len(context_files)} specialized context files created")

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