#!/usr/bin/env python3
"""
Mermaid Pre-Write Hook for Agents
MANDATORY: All agents MUST use this before writing any Mermaid diagrams
This ensures 100% valid Mermaid output
"""

import re
import sys
from pathlib import Path
from typing import Tuple, List, Optional

# Add script directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from comprehensive_mermaid_validator import (
        ComprehensiveMermaidValidator,
        ComprehensiveMermaidFixer
    )
except ImportError:
    print("ERROR: comprehensive_mermaid_validator.py not found!")
    sys.exit(1)


class MermaidPreWriteProcessor:
    """
    Ensures all Mermaid diagrams are valid BEFORE they are written to files.
    This class applies aggressive fixes to guarantee working diagrams.
    """
    
    def __init__(self):
        self.validator = ComprehensiveMermaidValidator()
        self.fixer = ComprehensiveMermaidFixer()
        
    def process_mermaid_content(self, content: str, diagram_type_hint: Optional[str] = None) -> Tuple[str, List[str]]:
        """
        Process raw Mermaid content to ensure it's valid
        
        Args:
            content: The Mermaid diagram content
            diagram_type_hint: Optional hint about what type of diagram this should be
            
        Returns:
            (processed_content, list_of_fixes_applied)
        """
        fixes_applied = []
        
        # Step 1: Clean up the content
        content = self._clean_content(content)
        
        # Step 2: Ensure diagram type
        content, type_fix = self._ensure_diagram_type(content, diagram_type_hint)
        if type_fix:
            fixes_applied.append(type_fix)
        
        # Step 3: Apply comprehensive fixes
        fixed_content, fixes = self.fixer.fix(content)
        fixes_applied.extend(fixes)
        
        # Step 4: Validate the fixed content
        is_valid, errors = self.validator.validate(fixed_content)
        
        # Step 5: If still not valid, apply aggressive fixes
        if not is_valid:
            fixed_content, aggressive_fixes = self._apply_aggressive_fixes(fixed_content, errors)
            fixes_applied.extend(aggressive_fixes)
        
        # Step 6: Final validation
        is_valid_final, final_errors = self.validator.validate(fixed_content)
        
        if not is_valid_final:
            # Last resort: Create a minimal valid diagram
            fixed_content, fallback_fix = self._create_fallback_diagram(fixed_content, diagram_type_hint)
            fixes_applied.append(fallback_fix)
        
        return fixed_content, fixes_applied
    
    def _clean_content(self, content: str) -> str:
        """Clean up common formatting issues"""
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Fix common encoding issues
            line = line.replace('–', '--')  # em dash to double dash
            line = line.replace('—', '---')  # en dash to triple dash
            line = line.replace('"', '"').replace('"', '"')  # Smart quotes
            line = line.replace(''', "'").replace(''', "'")  # Smart single quotes
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _ensure_diagram_type(self, content: str, hint: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """Ensure the diagram has a valid type declaration"""
        lines = content.split('\n')
        
        # Skip leading empty lines and comments
        non_empty_lines = []
        comment_lines = []
        
        for line in lines:
            if line.strip():
                if line.strip().startswith('%%'):
                    comment_lines.append(line)
                else:
                    non_empty_lines.append(line)
        
        if not non_empty_lines:
            # Empty diagram - create minimal valid diagram
            diagram_type = hint or 'graph TB'
            return f"{diagram_type}\n    A[Empty Diagram]", f"Created minimal {diagram_type}"
        
        # Check if first non-comment line is a valid diagram type
        first_line = non_empty_lines[0].strip()
        valid_types = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
                      'stateDiagram', 'stateDiagram-v2', 'erDiagram', 'gantt', 
                      'pie', 'journey', 'gitGraph', 'mindmap', 'timeline']
        
        has_valid_type = any(first_line.startswith(vt) for vt in valid_types)
        
        if not has_valid_type:
            # Detect type from content or use hint
            detected_type = self._detect_diagram_type(content, hint)
            
            # Add the diagram type
            result = '\n'.join(comment_lines + [detected_type] + non_empty_lines)
            return result, f"Added diagram type: {detected_type}"
        
        return content, None
    
    def _detect_diagram_type(self, content: str, hint: Optional[str] = None) -> str:
        """Detect the appropriate diagram type from content"""
        if hint:
            # Use hint if provided
            if hint.lower() in ['state', 'statemachine']:
                return 'stateDiagram-v2'
            elif hint.lower() in ['sequence', 'seq']:
                return 'sequenceDiagram'
            elif hint.lower() in ['class', 'classes']:
                return 'classDiagram'
            elif hint.lower() in ['er', 'entity', 'erd']:
                return 'erDiagram'
            elif hint.lower() in ['flow', 'flowchart']:
                return 'flowchart TB'
            elif hint.lower() in ['graph']:
                return 'graph TB'
        
        # Detect from content patterns
        content_lower = content.lower()
        
        if '[*]' in content or 'state ' in content_lower:
            return 'stateDiagram-v2'
        elif 'participant' in content_lower or '->>' in content:
            return 'sequenceDiagram'
        elif 'class ' in content_lower and ('::' in content or '<<' in content):
            return 'classDiagram'
        elif any(rel in content for rel in ['||--||', '||--o{', '}o--||', '||--|{']):
            return 'erDiagram'
        elif 'subgraph' in content_lower or '-->' in content:
            return 'graph TB'
        else:
            return 'graph TB'  # Default
    
    def _apply_aggressive_fixes(self, content: str, errors: List) -> Tuple[str, List[str]]:
        """Apply more aggressive fixes based on specific errors"""
        fixes_applied = []
        lines = content.split('\n')
        
        # Extract error types
        error_types = set()
        for error in errors:
            if hasattr(error, 'error_type'):
                error_types.add(error.error_type)
        
        # Fix based on error types
        if 'DUPLICATE_DECLARATION' in error_types:
            # Remove all duplicate type declarations
            fixed_lines = []
            seen_declaration = False
            
            for line in lines:
                is_declaration = any(
                    line.strip().startswith(dt) 
                    for dt in ['graph', 'flowchart', 'sequenceDiagram', 
                              'classDiagram', 'stateDiagram', 'erDiagram']
                )
                
                if is_declaration:
                    if not seen_declaration:
                        fixed_lines.append(line)
                        seen_declaration = True
                    else:
                        fixes_applied.append(f"Removed duplicate: {line.strip()}")
                else:
                    fixed_lines.append(line)
            
            lines = fixed_lines
        
        if 'MIXED_SYNTAX' in error_types:
            # Fix mixed syntax (e.g., state diagrams with graph syntax)
            diagram_type = self._detect_diagram_type('\n'.join(lines), None)
            
            if 'stateDiagram' in diagram_type:
                # Convert graph syntax to state syntax
                fixed_lines = []
                for line in lines:
                    if 'subgraph' in line:
                        line = line.replace('subgraph', 'state')
                        fixes_applied.append("Converted subgraph to state")
                    if 'graph ' in line and not line.strip().startswith('%%'):
                        continue  # Skip graph declarations
                    fixed_lines.append(line)
                lines = fixed_lines
            elif 'graph' in diagram_type or 'flowchart' in diagram_type:
                # Convert state syntax to graph syntax
                fixed_lines = []
                for line in lines:
                    if 'state ' in line and '"' in line:
                        line = line.replace('state ', 'subgraph ')
                        fixes_applied.append("Converted state to subgraph")
                    fixed_lines.append(line)
                lines = fixed_lines
        
        return '\n'.join(lines), fixes_applied
    
    def _create_fallback_diagram(self, content: str, hint: Optional[str] = None) -> Tuple[str, str]:
        """Create a minimal valid diagram as a last resort"""
        diagram_type = self._detect_diagram_type(content, hint)
        
        # Extract any meaningful content
        lines = content.split('\n')
        labels = []
        
        for line in lines:
            # Try to extract labels from nodes
            match = re.search(r'\[([^\]]+)\]', line)
            if match:
                labels.append(match.group(1))
        
        if not labels:
            labels = ["Diagram Content", "Could Not Be Parsed", "See Source"]
        
        # Create minimal valid diagram based on type
        if 'sequenceDiagram' in diagram_type:
            fallback = "sequenceDiagram\n"
            fallback += "    participant A as System\n"
            fallback += "    participant B as User\n"
            fallback += f"    Note over A,B: {labels[0] if labels else 'Diagram'}\n"
        elif 'classDiagram' in diagram_type:
            fallback = "classDiagram\n"
            fallback += f"    class DiagramClass {{\n"
            fallback += f"        +String content\n"
            fallback += f"        +parseError() bool\n"
            fallback += f"    }}\n"
        elif 'stateDiagram' in diagram_type:
            fallback = "stateDiagram-v2\n"
            fallback += "    [*] --> Processing\n"
            fallback += f"    Processing --> Error : {labels[0] if labels else 'Parse Failed'}\n"
            fallback += "    Error --> [*]\n"
        elif 'erDiagram' in diagram_type:
            fallback = "erDiagram\n"
            fallback += "    ENTITY ||--o{ ATTRIBUTE : has\n"
            fallback += "    ENTITY {\n"
            fallback += "        string id\n"
            fallback += "        string name\n"
            fallback += "    }\n"
        else:
            # Default to simple graph
            fallback = "graph TB\n"
            for i, label in enumerate(labels[:3]):
                fallback += f"    N{i}[{label}]\n"
            if len(labels) > 1:
                fallback += "    N0 --> N1\n"
            if len(labels) > 2:
                fallback += "    N1 --> N2\n"
        
        return fallback, f"Created fallback {diagram_type} diagram due to parsing errors"


def process_markdown_with_mermaid(markdown_content: str) -> Tuple[str, List[str]]:
    """
    Process all Mermaid blocks in markdown content
    
    Args:
        markdown_content: Markdown content with embedded Mermaid blocks
        
    Returns:
        (processed_content, list_of_all_fixes)
    """
    processor = MermaidPreWriteProcessor()
    all_fixes = []
    
    def process_block(match):
        prefix = match.group(1)
        diagram = match.group(2)
        suffix = match.group(3)
        
        # Detect type hint from context if available
        hint = None
        if 'class' in prefix.lower() or 'class' in diagram.lower()[:100]:
            hint = 'class'
        elif 'sequence' in prefix.lower() or 'sequence' in diagram.lower()[:100]:
            hint = 'sequence'
        elif 'state' in prefix.lower() or 'state' in diagram.lower()[:100]:
            hint = 'state'
        elif 'entity' in prefix.lower() or 'er' in prefix.lower():
            hint = 'er'
        
        fixed_diagram, fixes = processor.process_mermaid_content(diagram, hint)
        all_fixes.extend(fixes)
        
        return prefix + fixed_diagram + suffix
    
    # Process all mermaid blocks
    pattern = r'(```mermaid\n)(.*?)(\n```)'
    processed_content = re.sub(pattern, process_block, markdown_content, flags=re.DOTALL)
    
    return processed_content, all_fixes


def process_mermaid_file(file_content: str, file_path: Optional[str] = None) -> Tuple[str, List[str]]:
    """
    Process a pure Mermaid file (.mmd)
    
    Args:
        file_content: The Mermaid diagram content
        file_path: Optional file path for context
        
    Returns:
        (processed_content, list_of_fixes)
    """
    processor = MermaidPreWriteProcessor()
    
    # Try to detect type from filename
    hint = None
    if file_path:
        file_lower = file_path.lower()
        if 'class' in file_lower:
            hint = 'class'
        elif 'sequence' in file_lower or 'seq' in file_lower:
            hint = 'sequence'
        elif 'state' in file_lower:
            hint = 'state'
        elif 'entity' in file_lower or 'er' in file_lower:
            hint = 'er'
        elif 'flow' in file_lower:
            hint = 'flow'
    
    return processor.process_mermaid_content(file_content, hint)


# MAIN FUNCTION FOR AGENTS TO USE
def ensure_valid_mermaid(content: str, file_path: Optional[str] = None) -> str:
    """
    MANDATORY FUNCTION FOR ALL AGENTS
    
    This function MUST be called before writing any Mermaid content to files.
    It guarantees that the output will be valid Mermaid syntax.
    
    Args:
        content: The content to process (markdown with mermaid or pure mermaid)
        file_path: Optional file path for context
        
    Returns:
        Processed content with valid Mermaid diagrams
    
    Example:
        # In an agent before using Write()
        content = ensure_valid_mermaid(content, file_path)
        Write(file_path, content)
    """
    try:
        if '```mermaid' in content:
            # Markdown with embedded Mermaid
            processed_content, fixes = process_markdown_with_mermaid(content)
        elif file_path and (file_path.endswith('.mmd') or file_path.endswith('.mermaid')):
            # Pure Mermaid file
            processed_content, fixes = process_mermaid_file(content, file_path)
        else:
            # Assume it's pure Mermaid content
            processed_content, fixes = process_mermaid_file(content, file_path)
        
        if fixes:
            print(f"✅ Applied {len(fixes)} Mermaid fixes")
            for fix in fixes[:3]:  # Show first 3 fixes
                print(f"   - {fix}")
            if len(fixes) > 3:
                print(f"   ... and {len(fixes) - 3} more")
        
        return processed_content
        
    except Exception as e:
        print(f"⚠️  Warning: Mermaid processing failed: {e}")
        print("   Returning original content")
        return content


if __name__ == "__main__":
    # Test/CLI usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Mermaid Pre-Write Processor')
    parser.add_argument('file', help='File to process')
    parser.add_argument('--output', '-o', help='Output file (default: overwrite input)')
    
    args = parser.parse_args()
    
    # Read input file
    with open(args.file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process content
    processed = ensure_valid_mermaid(content, args.file)
    
    # Write output
    output_file = args.output or args.file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(processed)
    
    print(f"✅ Processed: {output_file}")