#!/usr/bin/env python3
"""
Mermaid Diagram Validation Script
Cross-platform validation for Mermaid diagrams in documentation
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class Colors:
    """Terminal colors (cross-platform)"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    
    @staticmethod
    def disable():
        """Disable colors for Windows or when requested"""
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.RESET = ''


class MermaidValidator:
    """Validates Mermaid diagrams for syntax errors"""
    
    # Valid diagram types
    DIAGRAM_TYPES = {
        'graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
        'stateDiagram', 'stateDiagram-v2', 'erDiagram', 'journey',
        'gantt', 'pie', 'quadrantChart', 'requirementDiagram',
        'gitGraph', 'mindmap', 'timeline', 'zenuml', 'sankey'
    }
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path.cwd() / "output" / "docs"
        self.total_files = 0
        self.total_diagrams = 0
        self.valid_diagrams = 0
        self.invalid_diagrams = 0
        self.errors: List[Dict] = []
    
    def validate_all(self) -> bool:
        """Validate all Mermaid diagrams in output directory"""
        print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BLUE}Mermaid Diagram Validation{Colors.RESET}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")
        
        if not self.output_dir.exists():
            print(f"{Colors.YELLOW}⚠ Output directory not found: {self.output_dir}{Colors.RESET}")
            print("  No diagrams to validate yet.")
            return True
        
        # Find all markdown files
        md_files = list(self.output_dir.glob("**/*.md"))
        
        if not md_files:
            print(f"{Colors.YELLOW}ℹ No markdown files found in {self.output_dir}{Colors.RESET}")
            return True
        
        print(f"Found {len(md_files)} markdown file(s) to check\n")
        
        # Process each file
        for md_file in md_files:
            self.validate_file(md_file)
        
        # Show summary
        self.show_summary()
        
        return self.invalid_diagrams == 0
    
    def validate_file(self, file_path: Path):
        """Validate Mermaid diagrams in a single file"""
        self.total_files += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"{Colors.RED}✗ Error reading {file_path.name}: {e}{Colors.RESET}")
            return
        
        # Find all Mermaid code blocks
        pattern = r'```mermaid\n(.*?)\n```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if not matches:
            return
        
        print(f"📄 Validating: {file_path.name}")
        
        for i, diagram in enumerate(matches, 1):
            self.total_diagrams += 1
            errors = self.validate_diagram(diagram)
            
            if errors:
                self.invalid_diagrams += 1
                print(f"   {Colors.RED}✗ Diagram {i}: INVALID{Colors.RESET}")
                for error in errors:
                    print(f"      • {error}")
                self.errors.append({
                    'file': file_path.name,
                    'diagram': i,
                    'errors': errors
                })
            else:
                self.valid_diagrams += 1
                print(f"   {Colors.GREEN}✓ Diagram {i}: Valid{Colors.RESET}")
        
        print()
    
    def validate_diagram(self, diagram: str) -> List[str]:
        """Validate a single Mermaid diagram"""
        errors = []
        lines = diagram.strip().split('\n')
        
        if not lines:
            errors.append("Empty diagram")
            return errors
        
        # Check diagram type
        first_line = lines[0].strip()
        diagram_type = first_line.split()[0] if first_line else ""
        
        if not any(first_line.startswith(dt) for dt in self.DIAGRAM_TYPES):
            errors.append(f"Invalid or missing diagram type: '{diagram_type}'")
            return errors
        
        # Type-specific validation
        if diagram_type in ['graph', 'flowchart']:
            errors.extend(self.validate_flowchart(lines))
        elif diagram_type == 'sequenceDiagram':
            errors.extend(self.validate_sequence(lines))
        elif diagram_type in ['classDiagram']:
            errors.extend(self.validate_class(lines))
        
        # Common validations
        errors.extend(self.validate_common(diagram))
        
        return errors
    
    def validate_flowchart(self, lines: List[str]) -> List[str]:
        """Validate flowchart/graph specific syntax"""
        errors = []
        
        # Check for basic structure
        has_nodes = False
        has_connections = False
        
        for line in lines[1:]:  # Skip diagram type line
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Check for node definitions
            if re.match(r'^[A-Za-z0-9_]+\[', line):
                has_nodes = True
            
            # Check for connections
            if '-->' in line or '---' in line or '-.->':
                has_connections = True
                
                # Check for invalid arrow syntax
                if line.count('-->') > 1:
                    errors.append(f"Multiple arrows on same line: {line[:50]}")
                
                if line.strip().endswith('-->'):
                    errors.append(f"Arrow pointing to nothing: {line[:50]}")
        
        if not has_nodes and not has_connections:
            errors.append("Flowchart has no nodes or connections")
        
        return errors
    
    def validate_sequence(self, lines: List[str]) -> List[str]:
        """Validate sequence diagram specific syntax"""
        errors = []
        
        has_participants = False
        has_messages = False
        
        for line in lines[1:]:  # Skip diagram type line
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            if line.startswith('participant'):
                has_participants = True
            
            if '->>' in line or '-->' in line or '->>' in line or '-->>' in line:
                has_messages = True
        
        if not has_participants:
            errors.append("Sequence diagram missing participant declarations")
        
        if not has_messages:
            errors.append("Sequence diagram has no messages")
        
        return errors
    
    def validate_class(self, lines: List[str]) -> List[str]:
        """Validate class diagram specific syntax"""
        errors = []
        
        has_classes = False
        
        for line in lines[1:]:  # Skip diagram type line
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            if line.startswith('class '):
                has_classes = True
        
        if not has_classes:
            errors.append("Class diagram has no class definitions")
        
        return errors
    
    def validate_common(self, diagram: str) -> List[str]:
        """Common validations for all diagram types"""
        errors = []
        
        # Check for unclosed quotes
        lines = diagram.split('\n')
        for i, line in enumerate(lines, 1):
            quote_count = line.count('"') + line.count("'")
            if quote_count % 2 != 0:
                errors.append(f"Unclosed quotes on line {i}: {line[:50]}")
        
        # Check for subgraph balance
        subgraph_opens = diagram.count('subgraph')
        subgraph_closes = len(re.findall(r'^\s*end\s*$', diagram, re.MULTILINE))
        
        if subgraph_opens > 0 and subgraph_opens != subgraph_closes:
            errors.append(f"Subgraph mismatch: {subgraph_opens} opens, {subgraph_closes} closes")
        
        # Check minimum content
        if len(lines) < 2:
            errors.append("Diagram too short - may be incomplete")
        
        return errors
    
    def show_summary(self):
        """Display validation summary"""
        print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BLUE}Validation Summary{Colors.RESET}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")
        
        print(f"Files scanned: {self.total_files}")
        print(f"Total diagrams: {self.total_diagrams}")
        print(f"{Colors.GREEN}Valid diagrams: {self.valid_diagrams}{Colors.RESET}")
        
        if self.invalid_diagrams > 0:
            print(f"{Colors.RED}Invalid diagrams: {self.invalid_diagrams}{Colors.RESET}\n")
            
            print(f"{Colors.RED}Files with errors:{Colors.RESET}")
            for error in self.errors:
                print(f"  - {error['file']} (Diagram {error['diagram']})")
            
            print(f"\n{Colors.YELLOW}Common fixes:{Colors.RESET}")
            print("  • Ensure diagram starts with valid type (graph, sequenceDiagram, etc.)")
            print("  • Check for unclosed quotes or brackets")
            print("  • Verify arrow syntax (use --> not -->-->)")
            print("  • Balance subgraph/end statements")
            print("  • Test at: https://mermaid.live")
        else:
            print(f"\n{Colors.GREEN}✓ All Mermaid diagrams are valid!{Colors.RESET}")
        
        print()


def main():
    """Main entry point"""
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Validate Mermaid diagrams')
    parser.add_argument('--output-dir', type=str, 
                       help='Output directory to validate (default: output/docs)')
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')
    
    args = parser.parse_args()
    
    # Disable colors if requested or on Windows without ANSI support
    if args.no_color or (sys.platform == 'win32' and not os.environ.get('ANSICON')):
        Colors.disable()
    
    # Set output directory
    output_dir = Path(args.output_dir) if args.output_dir else None
    
    # Run validation
    validator = MermaidValidator(output_dir)
    success = validator.validate_all()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()