#!/usr/bin/env python3
"""
Final Mermaid Validator - Production Ready
Combines syntax validation, auto-fixing, and robust parsing
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

class MermaidValidator:
    """Production-ready Mermaid validator"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_and_fix(self, content: str, file_path: Optional[str] = None) -> Tuple[bool, str, List[str]]:
        """
        Validate and auto-fix Mermaid content
        Returns: (is_valid, fixed_content, errors)
        """
        self.errors = []
        self.warnings = []
        
        # Auto-fix common issues
        fixed_content = self._auto_fix(content)
        
        # Validate the fixed content
        is_valid = self._validate(fixed_content, file_path)
        
        return is_valid, fixed_content, self.errors
    
    def _auto_fix(self, content: str) -> str:
        """Auto-fix common Mermaid syntax issues"""
        lines = content.split('\n')
        fixed_lines = []
        diagram_type = None
        
        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith('%%'):
                fixed_lines.append(line)
                continue
            
            # Detect diagram type
            if not diagram_type and line.strip():
                for dt in ['classDiagram', 'sequenceDiagram', 'graph', 'flowchart', 
                          'stateDiagram-v2', 'erDiagram', 'gantt', 'pie']:
                    if line.strip().startswith(dt):
                        diagram_type = dt
                        break
            
            # Apply fixes based on diagram type
            if diagram_type == 'classDiagram':
                line = self._fix_class_diagram_line(line)
            elif diagram_type == 'sequenceDiagram':
                line = self._fix_sequence_diagram_line(line)
            elif diagram_type in ['graph', 'flowchart']:
                line = self._fix_graph_line(line)
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_class_diagram_line(self, line: str) -> str:
        """Fix class diagram specific issues"""
        # Remove @ from stereotypes
        if '<<@' in line:
            line = line.replace('<<@', '<<')
        
        # Fix ER syntax in class diagrams
        if '||--||' in line:
            line = re.sub(r'(\w+)\s*\|\|--\|\|\s*(\w+)', r'\1 "1" -- "1" \2', line)
        elif '||--o{' in line:
            line = re.sub(r'(\w+)\s*\|\|--o\{\s*(\w+)', r'\1 "1" --o "*" \2', line)
        
        # Ensure relationship labels have colons
        if ('-->' in line or '--' in line or '..' in line) and not ':' in line:
            # Check if it looks like it needs a label
            parts = re.split(r'(-->|--|\.\.)', line)
            if len(parts) == 3 and parts[2].strip() and not parts[2].strip().startswith('"'):
                # Has text after arrow that's not a cardinality
                if not re.match(r'^\s*["*\d]+\s+\w+', parts[2]):
                    # Add colon before the label
                    arrow = parts[1]
                    before = parts[0].strip()
                    after = parts[2].strip()
                    # Split after into target and label
                    after_parts = after.split(None, 1)
                    if len(after_parts) == 2:
                        target, label = after_parts
                        line = f"    {before} {arrow} {target} : {label}"
        
        return line
    
    def _fix_sequence_diagram_line(self, line: str) -> str:
        """Fix sequence diagram specific issues"""
        # Fix note content with problematic characters
        if line.strip().startswith('Note'):
            # Remove problematic characters from notes
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    note_content = parts[1]
                    # Clean the content
                    note_content = note_content.replace('"', '')
                    note_content = note_content.replace(':', ' -')
                    line = f"{parts[0]}: {note_content}"
        
        return line
    
    def _fix_graph_line(self, line: str) -> str:
        """Fix graph/flowchart specific issues"""
        # Fix numeric node IDs
        if re.match(r'^\s*\d+\[', line):
            # Prefix with 'node'
            line = re.sub(r'^(\s*)(\d+)(\[)', r'\1node\2\3', line)
        
        # Fix HTML breaks
        line = line.replace('\\<br/\\>', '<br/>')
        
        return line
    
    def _validate(self, content: str, file_path: Optional[str] = None) -> bool:
        """Validate the Mermaid content"""
        lines = content.split('\n')
        
        # Find diagram type
        diagram_type = None
        for line in lines:
            if not line.strip().startswith('%%') and line.strip():
                for dt in ['classDiagram', 'sequenceDiagram', 'graph', 'flowchart',
                          'stateDiagram-v2', 'erDiagram']:
                    if line.strip().startswith(dt):
                        diagram_type = dt
                        break
                break
        
        if not diagram_type:
            self.errors.append("No valid diagram type found")
            return False
        
        # Basic validation checks
        self._check_for_duplicate_declarations(lines)
        self._check_for_syntax_errors(lines, diagram_type)
        
        return len(self.errors) == 0
    
    def _check_for_duplicate_declarations(self, lines: List[str]):
        """Check for duplicate diagram type declarations"""
        diagram_declarations = 0
        for line in lines:
            if not line.strip().startswith('%%'):
                for dt in ['classDiagram', 'sequenceDiagram', 'graph', 'flowchart']:
                    if line.strip().startswith(dt):
                        diagram_declarations += 1
        
        if diagram_declarations > 1:
            self.errors.append("Multiple diagram type declarations found")
    
    def _check_for_syntax_errors(self, lines: List[str], diagram_type: str):
        """Check for common syntax errors"""
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('%%'):
                continue
            
            # Check for @ in stereotypes
            if '<<@' in line:
                self.errors.append(f"Line {i}: Invalid @ symbol in stereotype")
            
            # Check for ER syntax in class diagrams
            if diagram_type == 'classDiagram':
                if '||--||' in line or '||--o{' in line:
                    self.errors.append(f"Line {i}: ER diagram syntax in class diagram")
            
            # Check for numeric node IDs in graphs
            if diagram_type in ['graph', 'flowchart']:
                if re.match(r'^\s*\d+\[', line):
                    self.warnings.append(f"Line {i}: Numeric node ID (may cause issues)")


def validate_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Validate a single Mermaid file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    validator = MermaidValidator()
    is_valid, fixed_content, errors = validator.validate_and_fix(content, str(file_path))
    
    # Write back if fixed
    if fixed_content != content:
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        print(f"  Auto-fixed: {file_path.name}")
    
    return is_valid, errors


def main():
    """Validate and fix all Mermaid files"""
    output_dir = Path("output/diagrams")
    
    if not output_dir.exists():
        print(f"Directory {output_dir} does not exist")
        return 1
    
    files = list(output_dir.glob("*.mmd"))
    
    print("Mermaid Validation and Auto-Fix")
    print("=" * 60)
    
    all_valid = True
    fixed_count = 0
    
    for file_path in sorted(files):
        is_valid, errors = validate_file(file_path)
        
        status = "✅" if is_valid else "❌"
        print(f"{status} {file_path.name}")
        
        if errors:
            all_valid = False
            for error in errors[:3]:
                print(f"   {error}")
    
    print("=" * 60)
    
    if all_valid:
        print("✅ ALL DIAGRAMS ARE VALID!")
        return 0
    else:
        print("❌ Some diagrams have errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())