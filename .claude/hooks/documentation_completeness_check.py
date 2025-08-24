#!/usr/bin/env python3
"""
Documentation Completeness Check Hook for Claude Code
Ensures all required documentation files are generated
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional

# Get project directory from environment or use current directory
PROJECT_DIR = Path(os.environ.get('CLAUDE_PROJECT_DIR', Path.cwd()))
OUTPUT_DIR = PROJECT_DIR / "output" / "docs"

class Colors:
    """Terminal colors"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def disable():
        """Disable colors for environments that don't support them"""
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.MAGENTA = ''
        Colors.NC = ''

# Enable colors on Windows if possible
if sys.platform == 'win32' and not os.environ.get('ANSICON'):
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        Colors.disable()

class DocumentationChecker:
    """Checks documentation completeness"""
    
    # Required documentation files
    REQUIRED_DOCS = [
        {
            'file': '00-executive-summary.md',
            'description': 'Executive Summary',
            'min_size': 500,  # Minimum file size in bytes
            'required_sections': ['Overview', 'Key Findings', 'Recommendations']
        },
        {
            'file': '01-archaeological-analysis.md',
            'description': 'Legacy Code Archaeological Analysis',
            'min_size': 1000,
            'required_sections': ['Technology Stack', 'Dependencies', 'Technical Debt']
        },
        {
            'file': '02-business-logic-analysis.md',
            'description': 'Business Logic Analysis and Domain Modeling',
            'min_size': 2000,
            'required_sections': ['Business Rules', 'Domain Model']
        },
        {
            'file': '03-visual-architecture-documentation.md',
            'description': 'Visual Architecture Documentation',
            'min_size': 1000,
            'required_sections': ['Architecture', 'Diagrams']
        },
        {
            'file': '04-comprehensive-performance-analysis.md',
            'description': 'Performance Analysis',
            'min_size': 1000,
            'required_sections': ['Performance', 'Bottlenecks', 'Optimization']
        },
        {
            'file': '05-comprehensive-security-analysis.md',
            'description': 'Security Analysis',
            'min_size': 1000,
            'required_sections': ['Security', 'Vulnerabilities', 'Recommendations']
        },
        {
            'file': '06-modernization-strategy.md',
            'description': 'Modernization Strategy',
            'min_size': 1500,
            'required_sections': ['Strategy', 'Roadmap', 'Risks']
        }
    ]
    
    # Optional but recommended files
    OPTIONAL_DOCS = [
        '07-technical-architecture-specification.md',
        '08-api-documentation-specifications.md',
        '09-database-schema-documentation.md',
        '10-comprehensive-business-rules-extraction.md',
        '11-complete-sequence-diagrams.md',
        '12-migration-procedures-and-runbooks.md',
        '13-operational-procedures-and-troubleshooting.md',
        '14-developer-onboarding-documentation.md'
    ]
    
    def __init__(self):
        self.missing_files = []
        self.incomplete_files = []
        self.complete_files = []
        self.optional_found = []
        self.warnings = []
    
    def run(self) -> int:
        """Main checking routine"""
        print("=" * 60)
        print("Documentation Completeness Check")
        print("=" * 60)
        print()
        
        # Check if output directory exists
        if not OUTPUT_DIR.exists():
            print(f"{Colors.YELLOW}⚠️  Output directory not found: {OUTPUT_DIR}{Colors.NC}")
            print("   Documentation has not been generated yet.")
            print("   Run analysis agents to generate documentation.")
            return 0
        
        # Check required documentation
        print(f"{Colors.BLUE}Checking required documentation...{Colors.NC}")
        self.check_required_docs()
        
        # Check optional documentation
        print(f"\n{Colors.BLUE}Checking optional documentation...{Colors.NC}")
        self.check_optional_docs()
        
        # Check for business rules
        print(f"\n{Colors.BLUE}Checking business rules extraction...{Colors.NC}")
        self.check_business_rules()
        
        # Check for diagrams
        print(f"\n{Colors.BLUE}Checking diagram generation...{Colors.NC}")
        self.check_diagrams()
        
        # Show summary
        self.show_summary()
        
        # Return exit code
        # Always return 0 to avoid noisy hook errors during early development
        # The validation output is informational, not a hard failure
        return 0
    
    def check_required_docs(self):
        """Check for required documentation files"""
        for doc_info in self.REQUIRED_DOCS:
            file_path = OUTPUT_DIR / doc_info['file']
            
            if not file_path.exists():
                self.missing_files.append(doc_info)
                print(f"   {Colors.RED}✗ Missing: {doc_info['file']}{Colors.NC}")
            else:
                # Check file size
                file_size = file_path.stat().st_size
                if file_size < doc_info['min_size']:
                    self.incomplete_files.append({
                        'file': doc_info['file'],
                        'reason': f'Too small ({file_size} bytes < {doc_info["min_size"]} bytes)'
                    })
                    print(f"   {Colors.YELLOW}⚠ Incomplete: {doc_info['file']} (too small){Colors.NC}")
                else:
                    # Check for required sections
                    missing_sections = self.check_sections(file_path, doc_info['required_sections'])
                    if missing_sections:
                        self.incomplete_files.append({
                            'file': doc_info['file'],
                            'reason': f'Missing sections: {", ".join(missing_sections)}'
                        })
                        print(f"   {Colors.YELLOW}⚠ Incomplete: {doc_info['file']} (missing sections){Colors.NC}")
                    else:
                        self.complete_files.append(doc_info['file'])
                        print(f"   {Colors.GREEN}✓ Complete: {doc_info['file']}{Colors.NC}")
    
    def check_optional_docs(self):
        """Check for optional documentation files"""
        for doc_file in self.OPTIONAL_DOCS:
            file_path = OUTPUT_DIR / doc_file
            
            if file_path.exists():
                self.optional_found.append(doc_file)
                print(f"   {Colors.GREEN}✓ Found: {doc_file}{Colors.NC}")
            else:
                print(f"   {Colors.BLUE}ℹ Optional: {doc_file}{Colors.NC}")
    
    def check_sections(self, file_path: Path, required_sections: List[str]) -> List[str]:
        """Check if file contains required sections"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
        except Exception:
            return required_sections
        
        missing = []
        for section in required_sections:
            if section.lower() not in content:
                missing.append(section)
        
        return missing
    
    def check_business_rules(self):
        """Check for business rules extraction"""
        business_rules_found = 0
        
        # Check all documentation for business rules
        for md_file in OUTPUT_DIR.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Count business rules (look for BR- patterns or rule tables)
                import re
                br_patterns = len(re.findall(r'BR-\d+|Rule ID.*\|', content))
                business_rules_found += br_patterns
            except Exception:
                pass
        
        if business_rules_found == 0:
            self.warnings.append("No business rules found (expected 50+)")
            print(f"   {Colors.RED}✗ No business rules extracted{Colors.NC}")
        elif business_rules_found < 50:
            self.warnings.append(f"Only {business_rules_found} business rules found (expected 50+)")
            print(f"   {Colors.YELLOW}⚠ Only {business_rules_found} rules found (expected 50+){Colors.NC}")
        else:
            print(f"   {Colors.GREEN}✓ {business_rules_found} business rules extracted{Colors.NC}")
    
    def check_diagrams(self):
        """Check for diagram generation"""
        diagram_count = 0
        diagram_dir = PROJECT_DIR / "output" / "diagrams"
        
        # Check in documentation files
        for md_file in OUTPUT_DIR.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    diagram_count += content.count('```mermaid')
            except Exception:
                pass
        
        # Check diagram directory
        if diagram_dir.exists():
            diagram_files = list(diagram_dir.glob("*.mermaid")) + list(diagram_dir.glob("*.md"))
            diagram_count += len(diagram_files)
        
        if diagram_count == 0:
            self.warnings.append("No diagrams found")
            print(f"   {Colors.RED}✗ No diagrams generated{Colors.NC}")
        elif diagram_count < 5:
            self.warnings.append(f"Only {diagram_count} diagrams found (expected more)")
            print(f"   {Colors.YELLOW}⚠ Only {diagram_count} diagrams found{Colors.NC}")
        else:
            print(f"   {Colors.GREEN}✓ {diagram_count} diagrams generated{Colors.NC}")
    
    def show_summary(self):
        """Display check summary"""
        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)
        
        # Status overview
        total_required = len(self.REQUIRED_DOCS)
        complete = len(self.complete_files)
        incomplete = len(self.incomplete_files)
        missing = len(self.missing_files)
        
        print(f"\nRequired Documentation: {complete}/{total_required} complete")
        print(f"   {Colors.GREEN}✓ Complete: {complete}{Colors.NC}")
        print(f"   {Colors.YELLOW}⚠ Incomplete: {incomplete}{Colors.NC}")
        print(f"   {Colors.RED}✗ Missing: {missing}{Colors.NC}")
        
        if self.optional_found:
            print(f"\nOptional Documentation: {len(self.optional_found)} found")
        
        # Details on issues
        if self.missing_files:
            print(f"\n{Colors.RED}Missing Required Files:{Colors.NC}")
            for doc in self.missing_files:
                print(f"   • {doc['file']}: {doc['description']}")
                print(f"     Agent needed: {self.get_agent_for_doc(doc['file'])}")
        
        if self.incomplete_files:
            print(f"\n{Colors.YELLOW}Incomplete Files:{Colors.NC}")
            for doc in self.incomplete_files:
                print(f"   • {doc['file']}: {doc['reason']}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}Warnings:{Colors.NC}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        # Recommendations
        if self.missing_files or self.incomplete_files:
            print(f"\n{Colors.MAGENTA}Recommendations:{Colors.NC}")
            print("1. Run missing analysis agents:")
            
            agents_needed = set()
            for doc in self.missing_files:
                agent = self.get_agent_for_doc(doc['file'])
                if agent:
                    agents_needed.add(agent)
            
            for agent in agents_needed:
                print(f"   @{agent}")
            
            print("\n2. Ensure agents complete their analysis")
            print("3. Check for errors in agent execution")
        else:
            print(f"\n{Colors.GREEN}✅ Documentation is complete!{Colors.NC}")
            print("\nNext steps:")
            print("   1. Review generated documentation in output/docs/")
            print("   2. Validate diagrams with mermaid_diagram_validation.py")
            print("   3. Check business rules completeness")
    
    def get_agent_for_doc(self, filename: str) -> str:
        """Get the agent responsible for generating a document"""
        agent_map = {
            '00-executive-summary': 'documentation-specialist',
            '01-archaeological-analysis': 'legacy-code-detective',
            '02-business-logic-analysis': 'business-logic-analyst',
            '03-visual-architecture': 'diagram-architect',
            '04-comprehensive-performance': 'performance-analyst',
            '05-comprehensive-security': 'security-analyst',
            '06-modernization-strategy': 'modernization-architect'
        }
        
        for key, agent in agent_map.items():
            if filename.startswith(key):
                return agent
        
        return 'documentation-specialist'

def main():
    """Main entry point"""
    checker = DocumentationChecker()
    exit_code = checker.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()