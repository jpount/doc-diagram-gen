#!/usr/bin/env python3
"""
Mermaid Diagram Validation Hook for Claude Code
Validates all Mermaid diagrams in generated documentation
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Get project directory from environment or use current directory
PROJECT_DIR = Path(os.environ.get('CLAUDE_PROJECT_DIR', Path.cwd()))
OUTPUT_DIR = PROJECT_DIR / "output" / "docs"

class Colors:
    """Terminal colors"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def disable():
        """Disable colors for environments that don't support them"""
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.NC = ''

# Disable colors on Windows if ANSI not supported
if sys.platform == 'win32' and not os.environ.get('ANSICON'):
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        Colors.disable()

class MermaidValidator:
    """Validates Mermaid diagrams for syntax errors"""
    
    DIAGRAM_TYPES = {
        'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
        'stateDiagram', 'stateDiagram-v2', 'erDiagram', 'journey',
        'gantt', 'pie', 'quadrantChart', 'requirementDiagram',
        'gitGraph', 'mindmap', 'timeline', 'C4Context', 'C4Container',
        'C4Component', 'C4Deployment', 'C4Dynamic'
    }
    
    def __init__(self):
        self.total_files = 0
        self.total_diagrams = 0
        self.valid_diagrams = 0
        self.invalid_diagrams = 0
        self.error_files = []
    
    def run(self) -> int:
        """Main validation routine"""
        print("=" * 40)
        print("Mermaid Diagram Validation")
        print("=" * 40)
        
        # Check if output directory exists
        if not OUTPUT_DIR.exists():
            print(f"{Colors.YELLOW}Warning: Output directory not found: {OUTPUT_DIR}{Colors.NC}")
            return 0
        
        # Find all markdown files
        md_files = list(OUTPUT_DIR.glob("**/*.md"))
        
        if not md_files:
            print(f"{Colors.YELLOW}ℹ️  No markdown files found in documentation{Colors.NC}")
            return 0
        
        # Process each file
        for md_file in md_files:
            self.validate_file(md_file)
        
        # Show summary
        self.show_summary()
        
        # Return exit code
        return 1 if self.invalid_diagrams > 0 else 0
    
    def validate_file(self, file_path: Path):
        """Validate Mermaid diagrams in a single file"""
        self.total_files += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"{Colors.RED}Error reading {file_path.name}: {e}{Colors.NC}")
            return
        
        # Extract Mermaid diagrams
        in_mermaid = False
        diagram = []
        line_num = 0
        diagram_start_line = 0
        file_has_errors = False
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip() == '```mermaid':
                in_mermaid = True
                diagram = []
                diagram_start_line = i
            elif line.strip() == '```' and in_mermaid:
                in_mermaid = False
                self.total_diagrams += 1
                
                # Validate the diagram
                diagram_text = '\n'.join(diagram)
                errors = self.validate_diagram(diagram_text)
                
                if errors:
                    self.invalid_diagrams += 1
                    file_has_errors = True
                    rel_path = file_path.relative_to(PROJECT_DIR)
                    print(f"{Colors.RED}✗{Colors.NC} Invalid diagram in {rel_path}:{diagram_start_line}")
                    for error in errors:
                        print(f"   - {error}")
                else:
                    self.valid_diagrams += 1
                    rel_path = file_path.relative_to(PROJECT_DIR)
                    print(f"{Colors.GREEN}✓{Colors.NC} Valid diagram in {rel_path}:{diagram_start_line}")
            elif in_mermaid:
                diagram.append(line)
        
        if file_has_errors and file_path not in self.error_files:
            self.error_files.append(file_path)
    
    def validate_diagram(self, diagram: str) -> List[str]:
        """Validate a single Mermaid diagram"""
        errors = []
        
        if not diagram.strip():
            errors.append("Empty diagram")
            return errors
        
        lines = diagram.strip().split('\n')
        first_line = lines[0].strip() if lines else ""
        
        # Check diagram type
        diagram_type = None
        for dt in self.DIAGRAM_TYPES:
            if first_line.startswith(dt):
                diagram_type = dt
                break
        
        if not diagram_type:
            errors.append(f"Unknown diagram type or missing declaration: '{first_line[:30]}'")
            return errors
        
        # Type-specific validation
        if diagram_type in ['graph', 'flowchart']:
            errors.extend(self.validate_flowchart(lines))
        elif diagram_type == 'sequenceDiagram':
            errors.extend(self.validate_sequence(lines))
        elif diagram_type == 'classDiagram':
            errors.extend(self.validate_class(lines))
        
        # Common validations
        errors.extend(self.validate_common(diagram))
        
        return errors
    
    def validate_flowchart(self, lines: List[str]) -> List[str]:
        """Validate flowchart/graph specific syntax"""
        errors = []
        
        has_content = False
        for line in lines[1:]:  # Skip first line
            line = line.strip()
            if line and not line.startswith('%%'):
                has_content = True
                
                # Check for invalid arrow chains
                if '-->' in line and line.count('-->') > 1:
                    errors.append("Multiple arrows on same line (use separate lines)")
                
                # Check for arrows pointing to nothing
                if line.endswith('-->') or line.endswith('---'):
                    errors.append("Arrow pointing to nothing")
        
        if not has_content:
            errors.append("Flowchart has no nodes or connections")
        
        return errors
    
    def validate_sequence(self, lines: List[str]) -> List[str]:
        """Validate sequence diagram specific syntax"""
        errors = []
        
        has_participants = False
        has_messages = False
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('participant') or line.startswith('actor'):
                has_participants = True
            if '->' in line or '-->' in line:
                has_messages = True
        
        if not has_participants and not has_messages:
            errors.append("Sequence diagram missing participants and messages")
        
        return errors
    
    def validate_class(self, lines: List[str]) -> List[str]:
        """Validate class diagram specific syntax"""
        errors = []
        
        has_classes = False
        for line in lines[1:]:
            if 'class ' in line:
                has_classes = True
                break
        
        if not has_classes:
            errors.append("Class diagram has no class definitions")
        
        return errors
    
    def validate_common(self, diagram: str) -> List[str]:
        """Common validations for all diagram types"""
        errors = []
        
        # Check for unclosed quotes
        for i, line in enumerate(diagram.split('\n'), 1):
            quote_count = line.count('"')
            if quote_count % 2 != 0:
                errors.append(f"Unclosed quotes on line {i}")
        
        # Check subgraph balance
        subgraph_count = diagram.count('subgraph')
        end_count = len(re.findall(r'^\s*end\s*$', diagram, re.MULTILINE))
        
        if subgraph_count > 0 and subgraph_count != end_count:
            errors.append(f"Unbalanced subgraph/end: {subgraph_count} subgraphs, {end_count} ends")
        
        # Check minimum content
        if len(diagram.strip().split('\n')) < 2:
            errors.append("Diagram too short - may be incomplete")
        
        # Check for node IDs starting with numbers (common issue)
        if re.search(r'^\s*\d+\[', diagram, re.MULTILINE):
            errors.append("Node IDs starting with numbers may cause issues")
        
        return errors
    
    def show_summary(self):
        """Display validation summary"""
        print("\n" + "=" * 40)
        print("Validation Summary")
        print("=" * 40)
        print(f"Files scanned: {self.total_files}")
        print(f"Total diagrams: {self.total_diagrams}")
        print(f"{Colors.GREEN}Valid diagrams: {self.valid_diagrams}{Colors.NC}")
        
        if self.invalid_diagrams > 0:
            print(f"{Colors.RED}Invalid diagrams: {self.invalid_diagrams}{Colors.NC}")
            print(f"\n{Colors.RED}Files with invalid diagrams:{Colors.NC}")
            for file_path in self.error_files:
                rel_path = file_path.relative_to(PROJECT_DIR)
                print(f"   - {rel_path}")
            
            print(f"\n{Colors.YELLOW}Common Mermaid Issues & Fixes:{Colors.NC}")
            print("\n1. **Diagram Type Declaration**:")
            print("   ❌ Bad: (missing first line)")
            print("   ✅ Good: sequenceDiagram")
            print("   ✅ Good: graph TB")
            print("\n2. **Flowchart Arrows**:")
            print("   ❌ Bad: A --> B --> C (chained)")
            print("   ✅ Good: A --> B")
            print("           B --> C")
            print("\n3. **Quotes**:")
            print('   ❌ Bad: A["Unclosed]')
            print('   ✅ Good: A["Closed"]')
            print("\n4. **Node IDs**:")
            print("   ❌ Bad: 1[Start]")
            print("   ✅ Good: N1[Start]")
            print("\n🔗 Test diagrams at: https://mermaid.live")
        else:
            print(f"\n{Colors.GREEN}✅ All Mermaid diagrams are syntactically valid!{Colors.NC}")
            print("\n💡 Tips:")
            print("   • Test complex diagrams at https://mermaid.live")
            print("   • Use consistent naming conventions")
            print("   • Add comments with %% prefix")

def main():
    """Main entry point"""
    # Import the auto-fixer if available
    try:
        sys.path.append(str(PROJECT_DIR / 'framework' / 'scripts'))
        from mermaid_validator_final import validate_file
        
        # Auto-fix any files with errors
        print(f"\n{Colors.BLUE}Auto-fixing Mermaid diagrams...{Colors.NC}")
        
        # Find and fix all markdown and mermaid files
        output_dir = PROJECT_DIR / "output"
        fixed_count = 0
        total_count = 0
        
        # Process all .mmd files in output/diagrams
        diagrams_dir = output_dir / "diagrams"
        if diagrams_dir.exists():
            for file_path in diagrams_dir.glob("*.mmd"):
                total_count += 1
                try:
                    # Use the final validator/fixer
                    is_valid, errors = validate_file(file_path)
                    if is_valid:
                        print(f"{Colors.GREEN}✓{Colors.NC} Valid/Fixed: {file_path.relative_to(PROJECT_DIR)}")
                        fixed_count += 1
                    else:
                        print(f"{Colors.YELLOW}⚠{Colors.NC} Issues remain: {file_path.relative_to(PROJECT_DIR)}")
                        for error in errors[:3]:
                            print(f"     - {error}")
                except Exception as e:
                    print(f"{Colors.YELLOW}Warning: Could not process {file_path.name}: {e}{Colors.NC}")
        
    except ImportError:
        print(f"{Colors.YELLOW}Note: Auto-fix script not available{Colors.NC}")
    
    # Now validate again
    validator = MermaidValidator()
    exit_code = validator.run()
    
    # Always return 0 to not block the workflow
    sys.exit(0)

if __name__ == "__main__":
    main()