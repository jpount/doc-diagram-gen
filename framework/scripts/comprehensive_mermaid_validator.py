#!/usr/bin/env python3
"""
Comprehensive Mermaid Diagram Validator and Auto-Fixer
Handles all common Mermaid syntax errors and auto-fixes them
"""

import re
import sys
import os
from typing import Tuple, List, Dict, Optional
from pathlib import Path

class MermaidDiagramError:
    """Represents a Mermaid diagram error"""
    def __init__(self, line_number: int, error_type: str, description: str, severity: str = "error"):
        self.line_number = line_number
        self.error_type = error_type
        self.description = description
        self.severity = severity  # "error", "warning", "info"
    
    def __str__(self):
        return f"Line {self.line_number} [{self.severity.upper()}] {self.error_type}: {self.description}"


class ComprehensiveMermaidValidator:
    """Advanced Mermaid diagram validator with comprehensive error detection"""
    
    VALID_DIAGRAM_TYPES = {
        'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
        'stateDiagram', 'stateDiagram-v2', 'erDiagram', 'journey',
        'gantt', 'pie', 'quadrantChart', 'requirementDiagram',
        'gitGraph', 'mindmap', 'timeline', 'C4Context', 'C4Container',
        'C4Component', 'C4Deployment', 'C4Dynamic', 'sankey'
    }
    
    GRAPH_DIRECTIONS = {'TB', 'TD', 'BT', 'RL', 'LR'}
    
    def __init__(self):
        self.errors: List[MermaidDiagramError] = []
        self.warnings: List[MermaidDiagramError] = []
        
    def validate(self, content: str) -> Tuple[bool, List[MermaidDiagramError]]:
        """
        Comprehensive validation of Mermaid diagram
        Returns: (is_valid, list_of_errors)
        """
        self.errors = []
        self.warnings = []
        lines = content.split('\n')
        
        # Remove leading/trailing empty lines
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        if not lines:
            self.errors.append(MermaidDiagramError(0, "EMPTY_DIAGRAM", "Diagram is empty"))
            return False, self.errors
        
        # Extract non-comment lines for analysis
        non_comment_lines = []
        for i, line in enumerate(lines):
            if not line.strip().startswith('%%'):
                non_comment_lines.append((i + 1, line))
        
        if not non_comment_lines:
            self.errors.append(MermaidDiagramError(0, "ONLY_COMMENTS", "Diagram contains only comments"))
            return False, self.errors
        
        # Detect diagram type
        diagram_type = self._detect_diagram_type(non_comment_lines)
        
        # Type-specific validation
        if diagram_type:
            if diagram_type.startswith('graph') or diagram_type.startswith('flowchart'):
                self._validate_graph(lines, diagram_type)
            elif diagram_type == 'sequenceDiagram':
                self._validate_sequence(lines)
            elif diagram_type == 'classDiagram':
                self._validate_class(lines)
            elif diagram_type.startswith('stateDiagram'):
                self._validate_state(lines)
            elif diagram_type == 'erDiagram':
                self._validate_er(lines)
        else:
            self.errors.append(MermaidDiagramError(
                non_comment_lines[0][0] if non_comment_lines else 1,
                "INVALID_TYPE",
                "No valid diagram type declaration found"
            ))
        
        # Common validations
        self._validate_common(lines)
        
        # Check for duplicate declarations
        self._check_duplicate_declarations(lines)
        
        return len(self.errors) == 0, self.errors + self.warnings
    
    def _detect_diagram_type(self, non_comment_lines: List[Tuple[int, str]]) -> Optional[str]:
        """Detect the diagram type from content"""
        for line_num, line in non_comment_lines:
            line = line.strip()
            for dtype in self.VALID_DIAGRAM_TYPES:
                if line.startswith(dtype):
                    # Handle graph with direction
                    if dtype in ['graph', 'flowchart']:
                        parts = line.split()
                        if len(parts) > 1 and parts[1] in self.GRAPH_DIRECTIONS:
                            return f"{dtype} {parts[1]}"
                    return dtype
        return None
    
    def _check_duplicate_declarations(self, lines: List[str]):
        """Check for duplicate diagram type declarations"""
        type_declarations = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped.startswith('%%'):
                for dtype in self.VALID_DIAGRAM_TYPES:
                    if stripped.startswith(dtype):
                        type_declarations.append((i, stripped))
                        break  # Only count once per line
        
        if len(type_declarations) > 1:
            for i, (line_num, decl) in enumerate(type_declarations[1:], 1):
                self.errors.append(MermaidDiagramError(
                    line_num,
                    "DUPLICATE_DECLARATION",
                    f"Duplicate diagram declaration: '{decl}' (first declaration at line {type_declarations[0][0]})"
                ))
    
    def _validate_graph(self, lines: List[str], diagram_type: str):
        """Validate graph/flowchart specific syntax"""
        has_nodes = False
        has_edges = False
        subgraph_stack = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('%%'):
                continue
                
            # Check for nodes
            if '[' in stripped and ']' in stripped:
                has_nodes = True
                # Check for malformed node syntax
                if re.search(r'\d+\[', stripped):
                    self.warnings.append(MermaidDiagramError(
                        i, "NUMERIC_NODE_ID",
                        "Node ID starts with number - may cause issues"
                    ))
            
            # Check for edges
            if '-->' in stripped or '---' in stripped or '==>' in stripped:
                has_edges = True
                # Check for trailing arrows
                if stripped.endswith('-->') or stripped.endswith('->>'):
                    self.errors.append(MermaidDiagramError(
                        i, "TRAILING_ARROW",
                        "Arrow pointing to nothing"
                    ))
                # Check for malformed arrows
                if '-->-->' in stripped:
                    self.errors.append(MermaidDiagramError(
                        i, "DOUBLE_ARROW",
                        "Double arrow syntax (-->-->) is invalid"
                    ))
            
            # Track subgraphs
            if 'subgraph' in stripped.lower():
                subgraph_stack.append(i)
            elif stripped == 'end':
                if subgraph_stack:
                    subgraph_stack.pop()
                else:
                    self.errors.append(MermaidDiagramError(
                        i, "EXTRA_END",
                        "Extra 'end' statement without matching subgraph"
                    ))
        
        # Check for unclosed subgraphs
        for line_num in subgraph_stack:
            self.errors.append(MermaidDiagramError(
                line_num, "UNCLOSED_SUBGRAPH",
                "Subgraph not closed with 'end'"
            ))
        
        if not has_nodes and not has_edges:
            self.warnings.append(MermaidDiagramError(
                0, "EMPTY_GRAPH",
                "Graph has no nodes or edges defined"
            ))
    
    def _validate_sequence(self, lines: List[str]):
        """Validate sequence diagram specific syntax"""
        has_participants = False
        has_messages = False
        participant_names = set()
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('%%'):
                continue
            
            # Check participants
            if stripped.startswith('participant') or stripped.startswith('actor'):
                has_participants = True
                # Extract participant name
                match = re.match(r'(participant|actor)\s+(.+)', stripped)
                if match:
                    name = match.group(2).strip()
                    # Check for quotes
                    if '"' in name:
                        name = name.strip('"')
                    elif "'" in name:
                        name = name.strip("'")
                    
                    # Check for duplicate participants
                    if name in participant_names:
                        self.warnings.append(MermaidDiagramError(
                            i, "DUPLICATE_PARTICIPANT",
                            f"Participant '{name}' already defined"
                        ))
                    participant_names.add(name)
                    
                    # Check for spaces without quotes
                    if ' ' in name and not (stripped.count('"') >= 2 or stripped.count("'") >= 2):
                        self.errors.append(MermaidDiagramError(
                            i, "UNQUOTED_PARTICIPANT",
                            f"Participant name with spaces needs quotes: '{name}'"
                        ))
            
            # Check for duplicate participant declaration (common error)
            if 'participant "' in stripped and stripped.count('participant') > 1:
                self.errors.append(MermaidDiagramError(
                    i, "MALFORMED_PARTICIPANT",
                    "Multiple 'participant' keywords in one line"
                ))
            
            # Check messages
            if '->>' in stripped or '-->' in stripped or '-->>' in stripped:
                has_messages = True
        
        if not has_participants and not has_messages:
            self.warnings.append(MermaidDiagramError(
                0, "EMPTY_SEQUENCE",
                "Sequence diagram has no participants or messages"
            ))
    
    def _validate_state(self, lines: List[str]):
        """Validate state diagram specific syntax"""
        has_states = False
        has_transitions = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('%%'):
                continue
            
            # Check for graph syntax mixed in (common error)
            if 'graph ' in stripped.lower() and not stripped.startswith('%%'):
                self.errors.append(MermaidDiagramError(
                    i, "MIXED_SYNTAX",
                    "Graph syntax found in state diagram"
                ))
            
            # Check for subgraph (should be 'state' in state diagrams)
            if 'subgraph' in stripped.lower():
                self.errors.append(MermaidDiagramError(
                    i, "WRONG_GROUPING",
                    "Use 'state' instead of 'subgraph' in state diagrams"
                ))
            
            # Check for states
            if 'state ' in stripped or '[*]' in stripped:
                has_states = True
            
            # Check for HTML breaks (problematic in state diagrams)
            if r'\<br/\>' in stripped or r'<br/>' in stripped:
                self.warnings.append(MermaidDiagramError(
                    i, "HTML_IN_STATE",
                    "HTML breaks may not render correctly in state diagrams"
                ))
            
            # Check transitions
            if '-->' in stripped:
                has_transitions = True
        
        if not has_states:
            self.warnings.append(MermaidDiagramError(
                0, "NO_STATES",
                "State diagram has no states defined"
            ))
    
    def _validate_class(self, lines: List[str]):
        """Validate class diagram specific syntax"""
        has_classes = False
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('%%'):
                continue
            
            if 'class ' in stripped:
                has_classes = True
                
            # Check for stereotypes with special characters
            if '<<@' in stripped:
                self.errors.append(MermaidDiagramError(
                    i, "INVALID_STEREOTYPE",
                    "Stereotype cannot contain @ symbol - use <<Entity>> not <<@Entity>>"
                ))
            
            # Check for JPA annotations in fields
            if '@Id' in stripped or '@GeneratedValue' in stripped or '@OneToMany' in stripped:
                self.warnings.append(MermaidDiagramError(
                    i, "JPA_ANNOTATION",
                    "JPA annotations in field definitions may cause parsing errors"
                ))
            
            # Check for relationship syntax
            if '-->' in stripped or '..|>' in stripped or '<|--' in stripped:
                # Check if relationship has proper label syntax
                if '-->' in stripped and ':' not in stripped.split('-->')[1]:
                    # Check if there's text after arrow without colon
                    parts = stripped.split('-->')
                    if len(parts) > 1 and parts[1].strip() and not parts[1].strip().startswith(':'):
                        self.errors.append(MermaidDiagramError(
                            i, "MISSING_COLON",
                            "Relationship label needs colon - use 'A --> B : label' not 'A --> B label'"
                        ))
            
            # Check for method/attribute syntax
            if '::' in stripped or '+' in stripped or '-' in stripped or '#' in stripped:
                # These are valid class diagram elements
                pass
        
        if not has_classes:
            self.warnings.append(MermaidDiagramError(
                0, "NO_CLASSES",
                "Class diagram has no class definitions"
            ))
    
    def _validate_er(self, lines: List[str]):
        """Validate ER diagram specific syntax"""
        has_entities = False
        has_relationships = False
        
        relationship_symbols = ['||--||', '||--o{', '}o--||', '||--|{', '}|--||']
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('%%'):
                continue
            
            # Check for entities (simple word definitions)
            if stripped and not any(sym in stripped for sym in relationship_symbols):
                if not stripped.startswith('erDiagram'):
                    has_entities = True
            
            # Check for relationships
            if any(sym in stripped for sym in relationship_symbols):
                has_relationships = True
        
        if not has_relationships:
            self.warnings.append(MermaidDiagramError(
                0, "NO_RELATIONSHIPS",
                "ER diagram has no relationships defined"
            ))
    
    def _validate_common(self, lines: List[str]):
        """Common validations for all diagram types"""
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('%%'):
                continue
            
            # Check for unclosed quotes
            double_quotes = line.count('"') - line.count('\\"')
            if double_quotes % 2 != 0:
                self.errors.append(MermaidDiagramError(
                    i, "UNCLOSED_QUOTES",
                    "Unclosed double quotes"
                ))
            
            single_quotes = line.count("'") - line.count("\\'")
            # Be careful with contractions
            if single_quotes % 2 != 0 and not re.search(r"\w'\w", line):
                self.warnings.append(MermaidDiagramError(
                    i, "UNCLOSED_QUOTES",
                    "Possibly unclosed single quotes"
                ))
            
            # Check for common typos
            typos = {
                'grpah': 'graph',
                'sequenceDiagam': 'sequenceDiagram',
                'classDiagam': 'classDiagram',
                'stateDiagam': 'stateDiagram',
                'paricipant': 'participant',
                'particpant': 'participant',
            }
            
            for typo, correct in typos.items():
                if typo in line:
                    self.warnings.append(MermaidDiagramError(
                        i, "TYPO",
                        f"Possible typo: '{typo}' should be '{correct}'"
                    ))


class ComprehensiveMermaidFixer:
    """Advanced auto-fixer for Mermaid diagrams"""
    
    def __init__(self):
        self.fixes_applied = []
        
    def fix(self, content: str) -> Tuple[str, List[str]]:
        """
        Apply comprehensive fixes to Mermaid diagram
        Returns: (fixed_content, list_of_fixes)
        """
        self.fixes_applied = []
        lines = content.split('\n')
        
        # Remove duplicate diagram declarations
        lines = self._remove_duplicate_declarations(lines)
        
        # Fix based on detected diagram type
        diagram_type = self._detect_diagram_type(lines)
        
        if diagram_type:
            if diagram_type.startswith('graph') or diagram_type.startswith('flowchart'):
                lines = self._fix_graph(lines)
            elif diagram_type == 'sequenceDiagram':
                lines = self._fix_sequence(lines)
            elif diagram_type.startswith('stateDiagram'):
                lines = self._fix_state(lines)
            elif diagram_type == 'classDiagram':
                lines = self._fix_class(lines)
            elif diagram_type == 'erDiagram':
                lines = self._fix_er(lines)
        else:
            # Try to detect and add diagram type
            lines = self._add_diagram_type(lines)
        
        # Apply common fixes
        lines = self._apply_common_fixes(lines)
        
        return '\n'.join(lines), self.fixes_applied
    
    def _detect_diagram_type(self, lines: List[str]) -> Optional[str]:
        """Detect diagram type from lines"""
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith('%%'):
                for dtype in ComprehensiveMermaidValidator.VALID_DIAGRAM_TYPES:
                    if stripped.startswith(dtype):
                        return dtype
        return None
    
    def _remove_duplicate_declarations(self, lines: List[str]) -> List[str]:
        """Remove duplicate diagram type declarations"""
        fixed_lines = []
        found_declaration = False
        
        for line in lines:
            stripped = line.strip()
            is_declaration = False
            
            if not stripped.startswith('%%'):
                for dtype in ComprehensiveMermaidValidator.VALID_DIAGRAM_TYPES:
                    if stripped.startswith(dtype):
                        is_declaration = True
                        break
            
            if is_declaration:
                if not found_declaration:
                    fixed_lines.append(line)
                    found_declaration = True
                else:
                    self.fixes_applied.append(f"Removed duplicate declaration: '{stripped}'")
            else:
                fixed_lines.append(line)
        
        return fixed_lines
    
    def _add_diagram_type(self, lines: List[str]) -> List[str]:
        """Detect and add missing diagram type"""
        # Analyze content to determine type
        content = '\n'.join(lines)
        
        # Detection patterns
        if '[*]' in content or ('state ' in content.lower() and '-->' in content):
            diagram_type = 'stateDiagram-v2'
        elif 'participant' in content or '->>' in content:
            diagram_type = 'sequenceDiagram'
        elif 'class ' in content and '::' in content:
            diagram_type = 'classDiagram'
        elif any(rel in content for rel in ['||--||', '||--o{', '}o--||']):
            diagram_type = 'erDiagram'
        elif 'subgraph' in content or '-->' in content:
            diagram_type = 'graph TB'
        else:
            diagram_type = 'graph TB'
        
        # Add diagram type at the beginning (after comments)
        fixed_lines = []
        added = False
        
        for line in lines:
            if not added and not line.strip().startswith('%%'):
                fixed_lines.append(diagram_type)
                self.fixes_applied.append(f"Added missing diagram type: {diagram_type}")
                added = True
            fixed_lines.append(line)
        
        if not added:
            fixed_lines.insert(0, diagram_type)
            self.fixes_applied.append(f"Added missing diagram type: {diagram_type}")
        
        return fixed_lines
    
    def _fix_graph(self, lines: List[str]) -> List[str]:
        """Fix graph/flowchart specific issues"""
        fixed_lines = []
        subgraph_count = 0
        end_count = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Fix double arrows
            if '-->-->' in line:
                line = line.replace('-->-->', '-->')
                self.fixes_applied.append("Fixed double arrow (-->-->)")
            
            # Fix trailing arrows
            if stripped.endswith('-->'):
                line = line.rstrip('->').rstrip() + ' --> [TODO]'
                self.fixes_applied.append("Fixed trailing arrow")
            
            # Fix node IDs starting with numbers - more comprehensive
            # Match patterns like: 1[Label], 2A[Label], 123[Label], etc.
            if re.search(r'\b(\d+[A-Za-z]*)\[', line):
                line = re.sub(r'\b(\d+[A-Za-z]*)\[', r'N\1[', line)
                self.fixes_applied.append("Fixed numeric node ID")
            
            # Count subgraphs and ends
            if 'subgraph' in stripped.lower():
                subgraph_count += 1
            elif stripped == 'end':
                end_count += 1
            
            fixed_lines.append(line)
        
        # Balance subgraphs and ends
        if subgraph_count > end_count:
            for _ in range(subgraph_count - end_count):
                fixed_lines.append('end')
                self.fixes_applied.append("Added missing 'end' statement")
        
        return fixed_lines
    
    def _fix_sequence(self, lines: List[str]) -> List[str]:
        """Fix sequence diagram specific issues"""
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Fix malformed participant declarations
            if 'participant "' in line and line.count('participant') > 1:
                # Extract the actual participant name
                match = re.search(r'"([^"]+)"', line)
                if match:
                    name = match.group(1)
                    line = f'    participant "{name}"'
                    self.fixes_applied.append(f"Fixed malformed participant declaration")
            
            # Fix unquoted participant names with spaces
            if stripped.startswith('participant') or stripped.startswith('actor'):
                match = re.match(r'(participant|actor)\s+(.+)', stripped)
                if match:
                    keyword = match.group(1)
                    name = match.group(2).strip()
                    if ' ' in name and not (name.startswith('"') or name.startswith("'")):
                        line = f'    {keyword} "{name}"'
                        self.fixes_applied.append(f"Added quotes to participant name: {name}")
            
            # Fix message arrows with missing spaces
            if '-->' in line or '->>' in line:
                # Add spaces around arrows if missing
                line = re.sub(r'(\w)(-->>?)', r'\1 \2', line)
                line = re.sub(r'(-->>?)(\w)', r'\1 \2', line)
            
            fixed_lines.append(line)
        
        return fixed_lines
    
    def _fix_state(self, lines: List[str]) -> List[str]:
        """Fix state diagram specific issues"""
        fixed_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Remove incompatible graph declarations
            if stripped.startswith('graph '):
                self.fixes_applied.append("Removed incompatible 'graph' declaration from state diagram")
                continue
            
            # Convert subgraph to state
            if 'subgraph' in line:
                line = line.replace('subgraph', 'state')
                self.fixes_applied.append("Converted 'subgraph' to 'state'")
            
            # Fix HTML breaks (optional - can be removed or simplified)
            if r'\<br/\>' in line:
                line = line.replace(r'\<br/\>', ' - ')
                self.fixes_applied.append("Replaced HTML break with dash")
            
            fixed_lines.append(line)
        
        return fixed_lines
    
    def _fix_class(self, lines: List[str]) -> List[str]:
        """Fix class diagram specific issues"""
        fixed_lines = []
        
        for line in lines:
            # Fix stereotypes with @ symbol
            if '<<@' in line:
                line = line.replace('<<@', '<<')
                self.fixes_applied.append("Removed @ from stereotype")
            
            # Remove JPA annotations from fields
            if '@Id' in line or '@GeneratedValue' in line:
                line = re.sub(r'\s*@\w+', '', line)
                self.fixes_applied.append("Removed JPA annotations")
            
            # Fix ER diagram syntax in class diagrams
            if '||--||' in line or '||--o{' in line or '}o--||' in line or 'o--o{' in line:
                # Convert ER syntax to class diagram syntax
                original = line
                # One-to-one
                line = re.sub(r'(\w+)\s*\|\|--\|\|\s*(\w+)\s*(.*)', r'\1 "1" -- "1" \2 : \3', line)
                # One-to-many
                line = re.sub(r'(\w+)\s*\|\|--o\{\s*(\w+)\s*(.*)', r'\1 "1" --o "*" \2 : \3', line)
                # Many-to-one
                line = re.sub(r'(\w+)\s*\}o--\|\|\s*(\w+)\s*(.*)', r'\1 "*" o-- "1" \2 : \3', line)
                # Many-to-many
                line = re.sub(r'(\w+)\s*o--o\{\s*(\w+)\s*(.*)', r'\1 o-- "*" \2 : \3', line)
                
                if line != original:
                    self.fixes_applied.append("Converted ER relationship to class diagram syntax")
            
            # Fix relationship labels without colons
            if '-->' in line and ':' not in line:
                parts = line.split('-->')
                if len(parts) == 2 and parts[1].strip():
                    # Add colon before label
                    line = parts[0] + '--> : ' + parts[1].strip()
                    self.fixes_applied.append("Added colon to relationship label")
            
            fixed_lines.append(line)
        
        return fixed_lines
    
    def _fix_er(self, lines: List[str]) -> List[str]:
        """Fix ER diagram specific issues"""
        # ER diagrams are usually simple, return as-is
        return lines
    
    def _apply_common_fixes(self, lines: List[str]) -> List[str]:
        """Apply common fixes to all diagram types"""
        fixed_lines = []
        
        for line in lines:
            # Fix unclosed quotes
            if not line.strip().startswith('%%'):
                double_quotes = line.count('"') - line.count('\\"')
                if double_quotes % 2 != 0:
                    line += '"'
                    self.fixes_applied.append("Fixed unclosed double quote")
            
            # Fix common typos
            typos = {
                'grpah': 'graph',
                'sequenceDiagam': 'sequenceDiagram',
                'classDiagam': 'classDiagram',
                'stateDiagam': 'stateDiagram',
                'paricipant': 'participant',
                'particpant': 'participant',
            }
            
            for typo, correct in typos.items():
                if typo in line:
                    line = line.replace(typo, correct)
                    self.fixes_applied.append(f"Fixed typo: {typo} -> {correct}")
            
            fixed_lines.append(line)
        
        return fixed_lines


def process_mermaid_in_markdown(content: str) -> Tuple[str, List[str], List[str]]:
    """
    Process all Mermaid blocks in markdown content
    Returns: (fixed_content, errors, fixes)
    """
    all_errors = []
    all_fixes = []
    
    def process_block(match):
        prefix = match.group(1)
        diagram = match.group(2)
        suffix = match.group(3)
        
        # Validate
        validator = ComprehensiveMermaidValidator()
        is_valid, errors = validator.validate(diagram)
        
        if not is_valid:
            # Try to fix
            fixer = ComprehensiveMermaidFixer()
            fixed_diagram, fixes = fixer.fix(diagram)
            
            # Re-validate
            is_valid_after, remaining_errors = validator.validate(fixed_diagram)
            
            for error in remaining_errors:
                all_errors.append(f"Block at position {match.start()}: {error}")
            
            all_fixes.extend(fixes)
            
            return prefix + fixed_diagram + suffix
        
        return match.group(0)
    
    # Process all mermaid blocks
    pattern = r'(```mermaid\n)(.*?)(\n```)'
    fixed_content = re.sub(pattern, process_block, content, flags=re.DOTALL)
    
    return fixed_content, all_errors, all_fixes


def process_file(file_path: str, fix: bool = True, verbose: bool = True) -> bool:
    """
    Process a single file for Mermaid validation and fixing
    Returns: True if file was valid or successfully fixed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if file_path.endswith('.md'):
            # Markdown file with embedded Mermaid
            if '```mermaid' not in content:
                if verbose:
                    print(f"  No Mermaid blocks found in {file_path}")
                return True
            
            fixed_content, errors, fixes = process_mermaid_in_markdown(content)
            
        elif file_path.endswith('.mmd'):
            # Pure Mermaid file
            validator = ComprehensiveMermaidValidator()
            is_valid, errors = validator.validate(content)
            
            if not is_valid and fix:
                fixer = ComprehensiveMermaidFixer()
                fixed_content, fixes = fixer.fix(content)
                
                # Re-validate
                validator = ComprehensiveMermaidValidator()
                is_valid_after, remaining_errors = validator.validate(fixed_content)
                errors = remaining_errors
            else:
                fixed_content = content
                fixes = []
        else:
            if verbose:
                print(f"  Skipping {file_path} - not a Mermaid file")
            return True
        
        # Report results
        if verbose:
            if errors:
                print(f"\n❌ {file_path}")
                for error in errors[:10]:  # Limit to first 10 errors
                    print(f"   {error}")
                if len(errors) > 10:
                    print(f"   ... and {len(errors) - 10} more errors")
            else:
                print(f"✅ {file_path}")
            
            if fixes:
                print(f"   Applied {len(fixes)} fixes:")
                for fix in fixes[:5]:  # Show first 5 fixes
                    print(f"   - {fix}")
                if len(fixes) > 5:
                    print(f"   ... and {len(fixes) - 5} more fixes")
        
        # Write fixed content if requested
        if fix and fixes:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            if verbose:
                print(f"   📝 File updated with fixes")
        
        return len(errors) == 0
        
    except Exception as e:
        if verbose:
            print(f"❗ Error processing {file_path}: {e}")
        return False


def main():
    """Main entry point for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive Mermaid Diagram Validator and Fixer')
    parser.add_argument('path', help='File or directory to process')
    parser.add_argument('--no-fix', action='store_true', help='Validate only, do not fix')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    parser.add_argument('--recursive', action='store_true', help='Process directories recursively')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    fix = not args.no_fix
    verbose = not args.quiet
    
    if path.is_file():
        # Process single file
        success = process_file(str(path), fix=fix, verbose=verbose)
        sys.exit(0 if success else 1)
        
    elif path.is_dir():
        # Process directory
        if verbose:
            print(f"Processing directory: {path}")
            print("=" * 60)
        
        # Find all relevant files
        patterns = ['*.md', '*.mmd'] if args.recursive else ['*.md', '*.mmd']
        files = []
        
        for pattern in patterns:
            if args.recursive:
                files.extend(path.rglob(pattern))
            else:
                files.extend(path.glob(pattern))
        
        if not files:
            print(f"No Mermaid files found in {path}")
            sys.exit(0)
        
        # Process all files
        total = len(files)
        successful = 0
        failed = 0
        
        for file_path in sorted(files):
            if process_file(str(file_path), fix=fix, verbose=verbose):
                successful += 1
            else:
                failed += 1
        
        # Summary
        if verbose:
            print("\n" + "=" * 60)
            print(f"Summary: {successful}/{total} files valid/fixed")
            if failed > 0:
                print(f"         {failed} files still have errors")
        
        sys.exit(0 if failed == 0 else 1)
        
    else:
        print(f"Error: {path} is neither a file nor a directory")
        sys.exit(1)


if __name__ == "__main__":
    main()