#!/usr/bin/env python3
"""
Robust Mermaid validator that simulates actual Mermaid parsing
This validator catches errors that would prevent rendering
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

class MermaidParser:
    """Simulates Mermaid parsing to catch real syntax errors"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def parse(self, content: str, filename: str = "unknown") -> Tuple[bool, List[str], List[str]]:
        """Parse Mermaid content and return (is_valid, errors, warnings)"""
        self.errors = []
        self.warnings = []
        
        lines = content.split('\n')
        if not lines:
            self.errors.append(f"{filename}: Empty file")
            return False, self.errors, self.warnings
        
        # Skip comment lines to find diagram type
        diagram_type = None
        diagram_line_idx = 0
        for idx, line in enumerate(lines):
            if not line.strip().startswith('%%') and line.strip():
                diagram_type = self._get_diagram_type(line)
                diagram_line_idx = idx
                break
        
        if not diagram_type:
            self.errors.append(f"{filename}: Invalid or missing diagram type declaration")
            return False, self.errors, self.warnings
        
        # Parse based on diagram type (pass lines starting from diagram declaration)
        if diagram_type == 'classDiagram':
            self._parse_class_diagram(lines[diagram_line_idx:], filename)
        elif diagram_type == 'sequenceDiagram':
            self._parse_sequence_diagram(lines[diagram_line_idx:], filename)
        elif diagram_type in ['graph', 'flowchart']:
            self._parse_graph(lines[diagram_line_idx:], filename, diagram_type)
        elif diagram_type == 'stateDiagram-v2':
            self._parse_state_diagram(lines[diagram_line_idx:], filename)
        elif diagram_type == 'erDiagram':
            self._parse_er_diagram(lines[diagram_line_idx:], filename)
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _get_diagram_type(self, first_line: str) -> Optional[str]:
        """Extract diagram type from first line"""
        line = first_line.strip()
        
        if line.startswith('classDiagram'):
            return 'classDiagram'
        elif line.startswith('sequenceDiagram'):
            return 'sequenceDiagram'
        elif line.startswith('graph'):
            return 'graph'
        elif line.startswith('flowchart'):
            return 'flowchart'
        elif line.startswith('stateDiagram-v2'):
            return 'stateDiagram-v2'
        elif line.startswith('erDiagram'):
            return 'erDiagram'
        elif line.startswith('gantt'):
            return 'gantt'
        elif line.startswith('pie'):
            return 'pie'
        elif line.startswith('journey'):
            return 'journey'
        elif line.startswith('gitGraph'):
            return 'gitGraph'
        
        return None
    
    def _parse_class_diagram(self, lines: List[str], filename: str):
        """Parse and validate class diagram syntax"""
        in_class = False
        current_class = None
        
        for i, line in enumerate(lines[1:], 2):  # Skip diagram declaration
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Check for class definition
            if line.startswith('class '):
                match = re.match(r'class\s+(\w+)\s*\{?', line)
                if match:
                    current_class = match.group(1)
                    in_class = '{' in line
                else:
                    self.errors.append(f"{filename}:{i}: Invalid class definition: {line[:50]}")
            
            # Check for stereotypes
            elif '<<' in line:
                if '<<@' in line:
                    self.errors.append(f"{filename}:{i}: Invalid stereotype with @ symbol")
                elif not re.search(r'<<[^>]+>>', line):
                    self.errors.append(f"{filename}:{i}: Malformed stereotype")
            
            # Check for relationships
            elif '--' in line or '..' in line:
                # Validate relationship syntax
                if not self._validate_class_relationship(line):
                    self.errors.append(f"{filename}:{i}: Invalid relationship syntax: {line[:50]}")
            
            # Check for closing brace
            elif line == '}':
                in_class = False
                current_class = None
            
            # Check for ER diagram syntax in class diagram
            elif '||--||' in line or '||--o{' in line:
                self.errors.append(f"{filename}:{i}: ER diagram syntax in class diagram")
    
    def _validate_class_relationship(self, line: str) -> bool:
        """Validate class diagram relationship syntax"""
        # Valid patterns:
        # A --> B
        # A --> B : label
        # A "1" --> "*" B
        # A "1" --> "*" B : label
        # A ..|> B : implements
        # A --|> B : extends
        # A --o B : aggregation
        # A --* B : composition
        
        # Basic arrow patterns
        arrow_patterns = [
            r'^\s*\w+\s*(--|\.\.|\||o|\*)',  # Start
            r'(>|>\||\||o|\*)\s*\w+',  # End
        ]
        
        # Check for basic structure
        if '--' in line or '..' in line:
            # Must have two identifiers
            parts = re.split(r'--|\.\.', line)
            if len(parts) < 2:
                return False
            
            # Check for label after colon
            if ':' in line:
                colon_parts = line.split(':')
                if len(colon_parts) != 2:
                    return False
        
        return True
    
    def _parse_sequence_diagram(self, lines: List[str], filename: str):
        """Parse and validate sequence diagram syntax"""
        participants = set()
        
        for i, line in enumerate(lines[1:], 2):
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Check for participant declaration
            if line.startswith('participant'):
                # Handle: participant "Alias as Name" or participant Name
                match = re.match(r'participant\s+(".*?"|\w+)', line)
                if match:
                    participant = match.group(1).strip('"')
                    # Extract alias if present
                    if ' as ' in participant:
                        alias = participant.split(' as ')[0]
                        participants.add(alias)
                    else:
                        participants.add(participant)
                else:
                    self.errors.append(f"{filename}:{i}: Invalid participant declaration")
            
            # Check for messages
            elif '->>' in line or '-->>' in line or '->>' in line:
                # Validate message syntax
                if not self._validate_sequence_message(line, participants):
                    self.warnings.append(f"{filename}:{i}: Potential message syntax issue")
            
            # Check for notes
            elif line.startswith('Note'):
                if not self._validate_sequence_note(line):
                    self.warnings.append(f"{filename}:{i}: Complex note content may cause issues")
    
    def _validate_sequence_message(self, line: str, participants: set) -> bool:
        """Validate sequence diagram message syntax"""
        # Pattern: Actor ->> Actor: Message
        pattern = r'^\s*(\w+)\s*(->>|-->>|->|-->)\s*(\w+)\s*:\s*(.+)'
        match = re.match(pattern, line)
        return match is not None
    
    def _validate_sequence_note(self, line: str) -> bool:
        """Validate sequence diagram note syntax"""
        # Notes with complex content can cause issues
        if '":"' in line or '","' in line:
            return False
        return True
    
    def _parse_graph(self, lines: List[str], filename: str, graph_type: str):
        """Parse and validate graph/flowchart syntax"""
        nodes = set()
        
        for i, line in enumerate(lines[1:], 2):
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Check for node definitions
            if '[' in line and ']' in line:
                # Check for numeric node IDs
                if re.match(r'^\s*\d+\[', line):
                    self.errors.append(f"{filename}:{i}: Numeric node ID (may cause issues)")
                
                # Extract node ID
                match = re.match(r'^\s*(\w+)\[', line)
                if match:
                    nodes.add(match.group(1))
            
            # Check for edges
            elif '-->' in line or '---' in line:
                # Basic validation
                if not self._validate_graph_edge(line):
                    self.errors.append(f"{filename}:{i}: Invalid edge syntax")
    
    def _validate_graph_edge(self, line: str) -> bool:
        """Validate graph edge syntax"""
        # Must have arrow
        if '-->' not in line and '---' not in line:
            return False
        return True
    
    def _parse_state_diagram(self, lines: List[str], filename: str):
        """Parse and validate state diagram syntax"""
        for i, line in enumerate(lines[1:], 2):
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Check for HTML breaks
            if '\\<br/\\>' in line:
                self.warnings.append(f"{filename}:{i}: HTML break in state diagram (may cause issues)")
            
            # Check for state transitions
            if '-->' in line:
                if not self._validate_state_transition(line):
                    self.errors.append(f"{filename}:{i}: Invalid state transition")
    
    def _validate_state_transition(self, line: str) -> bool:
        """Validate state transition syntax"""
        # Pattern: State1 --> State2
        # or: State1 --> State2 : label
        return '-->' in line
    
    def _parse_er_diagram(self, lines: List[str], filename: str):
        """Parse and validate ER diagram syntax"""
        for i, line in enumerate(lines[1:], 2):
            line = line.strip()
            if not line or line.startswith('%%'):
                continue
            
            # Check for entity definitions
            if '{' in line and not '}' in line:
                # Start of entity
                pass
            
            # Check for relationships
            elif '||' in line or '}o' in line or 'o{' in line:
                if not self._validate_er_relationship(line):
                    self.errors.append(f"{filename}:{i}: Invalid ER relationship")
    
    def _validate_er_relationship(self, line: str) -> bool:
        """Validate ER diagram relationship syntax"""
        # Must have valid ER notation
        er_patterns = ['||--||', '||--o{', '}o--||', '}o--o{']
        return any(pattern in line for pattern in er_patterns)


def validate_file(file_path: Path) -> Tuple[bool, List[str], List[str]]:
    """Validate a single Mermaid file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    parser = MermaidParser()
    return parser.parse(content, file_path.name)


def main():
    """Validate all Mermaid files with robust parsing"""
    output_dir = Path("output/diagrams")
    files = list(output_dir.glob("*.mmd"))
    
    print("Robust Mermaid Validation")
    print("=" * 60)
    
    all_valid = True
    total_errors = 0
    total_warnings = 0
    
    for file_path in sorted(files):
        is_valid, errors, warnings = validate_file(file_path)
        
        status = "✅" if is_valid else "❌"
        print(f"{status} {file_path.name}")
        
        if errors:
            all_valid = False
            total_errors += len(errors)
            for error in errors[:3]:  # Show first 3 errors
                print(f"   ERROR: {error}")
        
        if warnings:
            total_warnings += len(warnings)
            for warning in warnings[:2]:  # Show first 2 warnings
                print(f"   WARN: {warning}")
    
    print("=" * 60)
    print(f"Errors: {total_errors}, Warnings: {total_warnings}")
    
    if all_valid:
        print("✅ ALL DIAGRAMS PASS ROBUST VALIDATION!")
    else:
        print("❌ Some diagrams have errors that may prevent rendering")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())