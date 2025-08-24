#!/usr/bin/env python3
"""
Comprehensive Mermaid Validation and Auto-Fix Script
This validates and fixes Mermaid diagrams BEFORE they are written to files
"""

import re
import sys
import os
from pathlib import Path
from typing import Tuple, List, Optional

# Import the comprehensive validator
sys.path.append(str(Path(__file__).parent))
try:
    from comprehensive_mermaid_validator import (
        ComprehensiveMermaidValidator,
        ComprehensiveMermaidFixer,
        process_mermaid_in_markdown
    )
except ImportError:
    # Fall back to original implementation if comprehensive validator not available
    pass

class MermaidValidator:
    """Validates Mermaid diagrams and reports errors"""
    
    VALID_DIAGRAM_TYPES = {
        'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
        'stateDiagram', 'stateDiagram-v2', 'erDiagram', 'journey',
        'gantt', 'pie', 'quadrantChart', 'requirementDiagram',
        'gitGraph', 'mindmap', 'timeline', 'sankey', 'C4Context'
    }
    
    def validate(self, content: str) -> Tuple[bool, List[str]]:
        """
        Validate Mermaid diagram content
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        lines = content.strip().split('\n')
        
        # Skip comments
        non_comment_lines = [l for l in lines if not l.strip().startswith('%%')]
        
        if not non_comment_lines:
            errors.append("Empty diagram (only comments)")
            return False, errors
        
        # Check diagram type
        first_line = non_comment_lines[0].strip()
        diagram_type = first_line.split()[0] if first_line else ""
        
        if not any(first_line.startswith(dt) for dt in self.VALID_DIAGRAM_TYPES):
            errors.append(f"Invalid or missing diagram type: '{diagram_type}'")
        
        # Type-specific validation
        if diagram_type == 'stateDiagram-v2' or diagram_type == 'stateDiagram':
            # Should not have graph syntax
            if 'graph ' in content or 'subgraph' in content.lower():
                errors.append("State diagram contains graph/flowchart syntax - incompatible!")
        
        elif diagram_type in ['graph', 'flowchart']:
            # Should not have state diagram syntax
            if '[*]' in content or 'stateDiagram' in content:
                errors.append("Graph/flowchart contains state diagram syntax - incompatible!")
        
        elif diagram_type == 'sequenceDiagram':
            # Check for participant declarations
            if 'participant' not in content and '->>' not in content:
                errors.append("Sequence diagram missing participants or messages")
        
        elif diagram_type == 'classDiagram':
            # Check for class definitions
            if 'class ' not in content:
                errors.append("Class diagram missing class definitions")
        
        elif diagram_type == 'erDiagram':
            # Check for entity relationships
            if not any(rel in content for rel in ['||--||', '||--o{', '}o--||', '||--|{']):
                errors.append("ER diagram missing relationship definitions")
        
        # Common validation
        errors.extend(self._validate_common(content))
        
        return len(errors) == 0, errors
    
    def _validate_common(self, content: str) -> List[str]:
        """Common validations for all diagram types"""
        errors = []
        
        # Check for unbalanced subgraphs (only in graph/flowchart)
        if 'graph' in content or 'flowchart' in content:
            subgraph_count = content.count('subgraph')
            end_count = len(re.findall(r'\bend\b', content))
            if subgraph_count != end_count:
                errors.append(f"Unbalanced subgraph/end: {subgraph_count} subgraphs, {end_count} ends")
        
        # Check for unclosed quotes
        for i, line in enumerate(content.split('\n'), 1):
            if line.strip().startswith('%%'):
                continue
            quotes = line.count('"') - line.count('\\"')
            if quotes % 2 != 0:
                errors.append(f"Line {i}: Unclosed quotes")
        
        # Check for trailing arrows
        for i, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()
            if stripped.endswith('-->') or stripped.endswith('->>'):
                errors.append(f"Line {i}: Arrow pointing to nothing")
        
        return errors


class MermaidAutoFixer:
    """Automatically fixes common Mermaid diagram errors"""
    
    def fix(self, content: str) -> Tuple[str, List[str]]:
        """
        Fix Mermaid diagram content
        Returns: (fixed_content, list_of_fixes_applied)
        """
        fixes = []
        fixed = content
        
        # Detect what type of diagram this should be
        diagram_type = self._detect_diagram_type(fixed)
        
        # Fix mixed syntax issues
        fixed, type_fixes = self._fix_mixed_syntax(fixed, diagram_type)
        fixes.extend(type_fixes)
        
        # Add diagram type if missing
        fixed, type_fix = self._ensure_diagram_type(fixed, diagram_type)
        if type_fix:
            fixes.append(type_fix)
        
        # Fix common issues
        fixed, common_fixes = self._fix_common_issues(fixed, diagram_type)
        fixes.extend(common_fixes)
        
        return fixed, fixes
    
    def _detect_diagram_type(self, content: str) -> str:
        """Detect the intended diagram type from content"""
        
        # Remove comments for analysis
        lines = [l for l in content.split('\n') if not l.strip().startswith('%%')]
        clean_content = '\n'.join(lines)
        
        # Check for explicit type declaration
        if lines and lines[0].strip():
            first_line = lines[0].strip()
            for dtype in ['stateDiagram-v2', 'stateDiagram', 'sequenceDiagram', 
                         'classDiagram', 'erDiagram', 'graph', 'flowchart']:
                if first_line.startswith(dtype):
                    return dtype.split()[0]
        
        # Detect from content patterns
        if '[*]' in clean_content or '-->' in clean_content and 'state' in clean_content.lower():
            return 'stateDiagram-v2'
        elif 'participant' in clean_content or '->>' in clean_content:
            return 'sequenceDiagram'
        elif '::' in clean_content and 'class ' in clean_content:
            return 'classDiagram'
        elif any(rel in clean_content for rel in ['||--||', '||--o{', '}o--||']):
            return 'erDiagram'
        elif 'subgraph' in clean_content or '-->' in clean_content:
            return 'graph TB'
        else:
            return 'graph TB'
    
    def _fix_mixed_syntax(self, content: str, diagram_type: str) -> Tuple[str, List[str]]:
        """Fix mixed diagram syntax issues"""
        fixes = []
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip comments
            if line.strip().startswith('%%'):
                fixed_lines.append(line)
                continue
            
            # Fix state diagram with graph syntax
            if diagram_type.startswith('stateDiagram'):
                if line.strip().startswith('graph '):
                    fixes.append("Removed incompatible 'graph' declaration from state diagram")
                    continue  # Skip this line
                if 'subgraph' in line:
                    # Convert subgraph to state
                    line = line.replace('subgraph', 'state')
                    fixes.append("Converted 'subgraph' to 'state' in state diagram")
                if '<br/>' in line:
                    # State diagrams don't support HTML breaks
                    line = line.replace('<br/>', ' ')
                    fixes.append("Removed HTML breaks from state diagram")
            
            # Fix graph with state syntax
            elif diagram_type.startswith('graph'):
                if line.strip().startswith('stateDiagram'):
                    fixes.append("Removed incompatible 'stateDiagram' from graph")
                    continue
                if '[*]' in line:
                    # Convert state notation to node
                    line = line.replace('[*]', 'Start')
                    fixes.append("Converted state notation to graph node")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines), fixes
    
    def _ensure_diagram_type(self, content: str, diagram_type: str) -> Tuple[str, Optional[str]]:
        """Ensure diagram has correct type declaration"""
        lines = content.split('\n')
        
        # Separate comments and content
        comment_lines = []
        content_lines = []
        
        for line in lines:
            if line.strip().startswith('%%'):
                comment_lines.append(line)
            else:
                # Skip duplicate diagram declarations
                if line.strip() and not any(line.strip().startswith(dt) for dt in 
                                           ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
                                            'stateDiagram', 'erDiagram', 'gantt', 'pie']):
                    content_lines.append(line)
                elif not content_lines:  # Keep first diagram declaration only
                    content_lines.append(line)
        
        # Check if type is present
        has_type = False
        if content_lines:
            first_content = content_lines[0].strip()
            if first_content and any(first_content.startswith(dt) for dt in 
                                    ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
                                     'stateDiagram', 'erDiagram', 'gantt', 'pie']):
                has_type = True
        
        if not has_type:
            # Add the diagram type
            result = '\n'.join(comment_lines + [diagram_type] + content_lines)
            return result, f"Added missing diagram type: {diagram_type}"
        
        # Remove duplicate declarations
        seen_declaration = False
        clean_lines = comment_lines.copy()
        for line in content_lines:
            if any(line.strip().startswith(dt) for dt in ['graph', 'flowchart', 'sequenceDiagram', 
                                                          'classDiagram', 'stateDiagram', 'erDiagram']):
                if not seen_declaration:
                    clean_lines.append(line)
                    seen_declaration = True
            else:
                clean_lines.append(line)
        
        return '\n'.join(clean_lines), None
    
    def _fix_common_issues(self, content: str, diagram_type: str) -> Tuple[str, List[str]]:
        """Fix common diagram issues"""
        fixes = []
        fixed = content
        
        # Fix arrows
        if '--->' in fixed:
            fixed = fixed.replace('--->', '-->')
            fixes.append("Fixed arrow syntax (---> to -->)")
        
        if '-->-->' in fixed:
            fixed = fixed.replace('-->-->', '-->')
            fixes.append("Fixed double arrow")
        
        # Fix trailing arrows
        lines = fixed.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines):
            if line.strip().endswith('-->') or line.strip().endswith('->>'):
                line = line.rstrip('->')
                fixes.append(f"Removed trailing arrow on line {i+1}")
            fixed_lines.append(line)
        fixed = '\n'.join(fixed_lines)
        
        # Fix unbalanced subgraphs (only for graph/flowchart)
        if diagram_type.startswith('graph') or diagram_type.startswith('flowchart'):
            subgraph_count = fixed.count('subgraph')
            end_count = len(re.findall(r'\bend\b', fixed))
            
            if subgraph_count > end_count:
                # Add missing ends
                missing = subgraph_count - end_count
                fixed += '\nend' * missing
                fixes.append(f"Added {missing} missing 'end' statements")
            elif end_count > subgraph_count:
                # Remove extra ends
                extra = end_count - subgraph_count
                for _ in range(extra):
                    fixed = re.sub(r'\bend\s*$', '', fixed, count=1)
                fixes.append(f"Removed {extra} extra 'end' statements")
        
        # Fix sequence diagram participant names
        if diagram_type == 'sequenceDiagram':
            lines = fixed.split('\n')
            fixed_lines = []
            for line in lines:
                if line.strip().startswith('participant'):
                    # Extract name and quote if needed
                    match = re.match(r'participant\s+(.+)', line.strip())
                    if match:
                        name = match.group(1).strip()
                        if ' ' in name and not (name.startswith('"') or name.startswith("'")):
                            line = f'    participant "{name}"'
                            fixes.append(f"Added quotes to participant: {name}")
                fixed_lines.append(line)
            fixed = '\n'.join(fixed_lines)
        
        return fixed, fixes


def validate_and_fix_mermaid(content: str) -> Tuple[str, bool, List[str], List[str]]:
    """
    Main function to validate and fix Mermaid content
    Returns: (fixed_content, is_valid, errors, fixes)
    """
    validator = MermaidValidator()
    fixer = MermaidAutoFixer()
    
    # First validate
    is_valid, errors = validator.validate(content)
    
    if not is_valid:
        # Try to fix
        fixed_content, fixes = fixer.fix(content)
        
        # Re-validate
        is_valid_after, remaining_errors = validator.validate(fixed_content)
        
        return fixed_content, is_valid_after, remaining_errors, fixes
    
    return content, True, [], []


def validate_markdown_with_mermaid(markdown_content: str) -> Tuple[str, List[str], List[str]]:
    """
    Validate and fix all Mermaid blocks in markdown content
    Returns: (fixed_content, all_errors, all_fixes)
    """
    all_errors = []
    all_fixes = []
    
    def process_mermaid_block(match):
        prefix = match.group(1)
        diagram = match.group(2)
        suffix = match.group(3)
        
        fixed_diagram, is_valid, errors, fixes = validate_and_fix_mermaid(diagram)
        
        if errors:
            all_errors.extend(errors)
        if fixes:
            all_fixes.extend(fixes)
        
        return prefix + fixed_diagram + suffix
    
    # Process all mermaid blocks
    pattern = r'(```mermaid\n)(.*?)(\n```)'
    fixed_content = re.sub(pattern, process_mermaid_block, markdown_content, flags=re.DOTALL)
    
    return fixed_content, all_errors, all_fixes


# For use in agents
def ensure_valid_mermaid_before_write(content: str, file_path: str = None) -> str:
    """
    Ensure content has valid Mermaid diagrams before writing
    This should be called by agents BEFORE using Write()
    """
    try:
        # Try to use the comprehensive validator if available
        if '```mermaid' in content:
            # Markdown file with embedded diagrams
            fixed_content, errors, fixes = process_mermaid_in_markdown(content)
            
            if fixes:
                print(f"Applied {len(fixes)} Mermaid fixes:")
                for fix in fixes[:5]:
                    print(f"  - {fix}")
            
            if errors:
                print(f"Warning: {len(errors)} Mermaid errors remain:")
                for error in errors[:5]:
                    print(f"  - {error}")
            
            return fixed_content
        
        elif file_path and file_path.endswith('.mmd'):
            # Pure Mermaid file
            validator = ComprehensiveMermaidValidator()
            is_valid, errors = validator.validate(content)
            
            if not is_valid:
                fixer = ComprehensiveMermaidFixer()
                fixed_content, fixes = fixer.fix(content)
                
                if fixes:
                    print(f"Applied {len(fixes)} Mermaid fixes:")
                    for fix in fixes[:5]:
                        print(f"  - {fix}")
                
                # Re-validate
                is_valid_after, remaining_errors = validator.validate(fixed_content)
                
                if remaining_errors:
                    print(f"Warning: {len(remaining_errors)} Mermaid errors remain:")
                    for error in remaining_errors[:5]:
                        print(f"  - {error}")
                
                return fixed_content
            
            return content
            
    except (NameError, AttributeError):
        # Fall back to original implementation
        if '```mermaid' in content:
            # Markdown file with embedded diagrams
            fixed_content, errors, fixes = validate_markdown_with_mermaid(content)
            
            if fixes:
                print(f"Applied {len(fixes)} Mermaid fixes:")
                for fix in fixes[:5]:
                    print(f"  - {fix}")
            
            if errors:
                print(f"Warning: {len(errors)} Mermaid errors remain:")
                for error in errors[:5]:
                    print(f"  - {error}")
            
            return fixed_content
        
        elif file_path and file_path.endswith('.mmd'):
            # Pure Mermaid file
            fixed_content, is_valid, errors, fixes = validate_and_fix_mermaid(content)
            
            if fixes:
                print(f"Applied {len(fixes)} Mermaid fixes:")
                for fix in fixes[:5]:
                    print(f"  - {fix}")
            
            if errors:
                print(f"Warning: {len(errors)} Mermaid errors remain:")
                for error in errors[:5]:
                    print(f"  - {error}")
            
            return fixed_content
    
    return content


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        fixed_content = ensure_valid_mermaid_before_write(content, file_path)
        
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        
        print(f"Validated and fixed: {file_path}")
    else:
        print("Usage: python validate_and_fix_mermaid.py <file>")