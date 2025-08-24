#!/usr/bin/env python3
"""
Mermaid Diagram Auto-Fixer
Automatically fixes common Mermaid diagram errors
"""

import re
from typing import List, Tuple, Optional

class MermaidFixer:
    """Automatically fixes common Mermaid diagram errors"""
    
    def __init__(self):
        self.fixes_applied = []
    
    def fix_diagram(self, diagram: str) -> Tuple[str, List[str]]:
        """
        Fix common Mermaid diagram errors
        Returns: (fixed_diagram, list_of_fixes_applied)
        """
        self.fixes_applied = []
        fixed = diagram
        
        # Fix 1: Ensure proper diagram type declaration
        fixed = self.fix_diagram_type(fixed)
        
        # Fix 2: Fix arrow syntax
        fixed = self.fix_arrow_syntax(fixed)
        
        # Fix 3: Fix node ID issues
        fixed = self.fix_node_ids(fixed)
        
        # Fix 4: Fix quotes and special characters
        fixed = self.fix_quotes(fixed)
        
        # Fix 5: Fix subgraph balance
        fixed = self.fix_subgraph_balance(fixed)
        
        # Fix 6: Fix class diagram syntax
        fixed = self.fix_class_diagram(fixed)
        
        # Fix 7: Fix sequence diagram syntax
        fixed = self.fix_sequence_diagram(fixed)
        
        # Fix 8: Fix state diagram syntax
        fixed = self.fix_state_diagram(fixed)
        
        # Fix 9: Remove trailing arrows
        fixed = self.fix_trailing_arrows(fixed)
        
        # Fix 10: Fix common typos
        fixed = self.fix_common_typos(fixed)
        
        return fixed, self.fixes_applied
    
    def fix_diagram_type(self, diagram: str) -> str:
        """Ensure diagram starts with valid type"""
        lines = diagram.strip().split('\n')
        if not lines:
            return diagram
        
        # Skip comment lines at the beginning
        non_comment_lines = []
        comment_lines = []
        for line in lines:
            if line.strip().startswith('%%'):
                comment_lines.append(line)
            else:
                non_comment_lines.append(line)
        
        if not non_comment_lines:
            return diagram
            
        first_line = non_comment_lines[0].strip() if non_comment_lines else ""
        
        # Common type corrections
        type_corrections = {
            'flowchart': 'graph TB',
            'flow': 'graph TB',
            'sequence': 'sequenceDiagram',
            'class': 'classDiagram',
            'state': 'stateDiagram-v2',
            'er': 'erDiagram',
            'entity': 'erDiagram',
        }
        
        # Check if first non-comment line needs correction
        for wrong, correct in type_corrections.items():
            if first_line.lower().startswith(wrong) and not first_line.startswith(correct):
                non_comment_lines[0] = correct
                self.fixes_applied.append(f"Fixed diagram type: {wrong} -> {correct}")
                return '\n'.join(comment_lines + non_comment_lines)
        
        # If no recognized type, try to infer from content
        valid_types = ['graph', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'gantt', 'pie', 'journey', 'flowchart', 'quadrantChart', 'timeline', 'mindmap']
        if not any(first_line.startswith(dt) for dt in valid_types):
            content_lower = '\n'.join(non_comment_lines).lower()
            
            # Better detection logic
            if 'participant' in content_lower or '->>' in content_lower or 'activate' in content_lower:
                non_comment_lines.insert(0, 'sequenceDiagram')
                self.fixes_applied.append("Added missing sequenceDiagram declaration")
            elif '::' in '\n'.join(non_comment_lines) and 'class ' in content_lower:
                non_comment_lines.insert(0, 'classDiagram')
                self.fixes_applied.append("Added missing classDiagram declaration")
            elif '||--||' in '\n'.join(non_comment_lines) or '||--o{' in '\n'.join(non_comment_lines):
                non_comment_lines.insert(0, 'erDiagram')
                self.fixes_applied.append("Added missing erDiagram declaration")
            elif '[*]' in '\n'.join(non_comment_lines):
                non_comment_lines.insert(0, 'stateDiagram-v2')
                self.fixes_applied.append("Added missing stateDiagram-v2 declaration")
            elif 'subgraph' in content_lower or '-->' in '\n'.join(non_comment_lines):
                non_comment_lines.insert(0, 'graph TB')
                self.fixes_applied.append("Added missing graph TB declaration")
            else:
                non_comment_lines.insert(0, 'graph TB')
                self.fixes_applied.append("Added missing graph TB declaration (default)")
                
            return '\n'.join(comment_lines + non_comment_lines)
        
        return diagram
    
    def fix_arrow_syntax(self, diagram: str) -> str:
        """Fix common arrow syntax errors"""
        fixed = diagram
        
        # Fix multiple arrows (-->-->) to single arrow
        if '-->-->' in fixed:
            fixed = fixed.replace('-->-->', '-->')
            self.fixes_applied.append("Fixed double arrows (-->-->)")
        
        # Fix broken arrows with spaces
        fixed = re.sub(r'--\s+>', '-->', fixed)
        fixed = re.sub(r'--\s+>>', '-->>', fixed)
        
        # Fix arrows with extra dashes
        fixed = re.sub(r'---+>', '-->', fixed)
        fixed = re.sub(r'===+>', '==>', fixed)
        
        if fixed != diagram:
            self.fixes_applied.append("Fixed arrow syntax")
        
        return fixed
    
    def fix_node_ids(self, diagram: str) -> str:
        """Fix node ID issues"""
        lines = diagram.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix node IDs with spaces (not in quotes)
            # Convert: A B[Label] to A_B[Label]
            if '[' in line and not '"' in line and not "'" in line:
                # Find node definitions with spaces
                pattern = r'(\b\w+)\s+(\w+)(\[)'
                if re.search(pattern, line):
                    line = re.sub(pattern, r'\1_\2\3', line)
                    self.fixes_applied.append("Fixed node ID with spaces")
            
            # Fix node IDs starting with numbers
            pattern = r'\b(\d+\w*)\['
            if re.search(pattern, line):
                line = re.sub(pattern, r'N_\1[', line)
                self.fixes_applied.append("Fixed node ID starting with number")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_quotes(self, diagram: str) -> str:
        """Fix quote issues"""
        lines = diagram.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Count quotes
            double_quotes = line.count('"')
            single_quotes = line.count("'")
            
            # Fix unclosed double quotes
            if double_quotes % 2 != 0:
                line += '"'
                self.fixes_applied.append("Fixed unclosed double quote")
            
            # Fix unclosed single quotes (but be careful with contractions)
            if single_quotes % 2 != 0 and not re.search(r"\w'\w", line):
                line += "'"
                self.fixes_applied.append("Fixed unclosed single quote")
            
            # Escape special characters in labels
            if '[' in line and ']' in line:
                # Extract label content
                label_match = re.search(r'\[(.*?)\]', line)
                if label_match:
                    label = label_match.group(1)
                    # Check for unescaped special chars
                    if any(char in label for char in ['#', '&', '<', '>']):
                        fixed_label = label.replace('#', '\\#').replace('&', '\\&').replace('<', '\\<').replace('>', '\\>')
                        line = line.replace(f'[{label}]', f'[{fixed_label}]')
                        self.fixes_applied.append("Escaped special characters in label")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_subgraph_balance(self, diagram: str) -> str:
        """Fix unbalanced subgraph/end statements"""
        lines = diagram.split('\n')
        
        # Count subgraphs and ends
        subgraph_count = 0
        end_count = 0
        
        for line in lines:
            if 'subgraph' in line.lower():
                subgraph_count += 1
            elif re.match(r'^\s*end\s*$', line):
                end_count += 1
        
        # Add missing ends
        if subgraph_count > end_count:
            missing = subgraph_count - end_count
            for _ in range(missing):
                lines.append('end')
            self.fixes_applied.append(f"Added {missing} missing 'end' statement(s)")
        
        # Remove extra ends
        elif end_count > subgraph_count and subgraph_count > 0:
            extra = end_count - subgraph_count
            # Remove from the end
            for i in range(len(lines) - 1, -1, -1):
                if re.match(r'^\s*end\s*$', lines[i]) and extra > 0:
                    lines.pop(i)
                    extra -= 1
            self.fixes_applied.append(f"Removed {end_count - subgraph_count} extra 'end' statement(s)")
        
        return '\n'.join(lines)
    
    def fix_class_diagram(self, diagram: str) -> str:
        """Fix class diagram specific issues"""
        if not diagram.strip().startswith('classDiagram'):
            return diagram
        
        lines = diagram.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix class method syntax
            # Convert: +method() : type to +method() type
            if ':' in line and ('(' in line or '+' in line or '-' in line or '#' in line):
                line = re.sub(r'\s*:\s*', ' ', line)
                self.fixes_applied.append("Fixed class method syntax")
            
            # Fix relationship syntax
            # Ensure spaces around relationship operators
            if '<|--' in line or '--|>' in line or '<|..' in line or '..|>' in line:
                line = re.sub(r'(\w)(<\|--)', r'\1 \2', line)
                line = re.sub(r'(--\|>)(\w)', r'\1 \2', line)
                self.fixes_applied.append("Fixed class relationship spacing")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_sequence_diagram(self, diagram: str) -> str:
        """Fix sequence diagram specific issues"""
        if not 'sequenceDiagram' in diagram:
            return diagram
        
        lines = diagram.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix message syntax
            # Ensure spaces around arrows
            if '->>' in line or '-->' in line or '-->>' in line:
                # Add space before arrow if missing
                line = re.sub(r'(\w)(-->>?)', r'\1 \2', line)
                # Add space after arrow if missing  
                line = re.sub(r'(-->>?)(\w)', r'\1 \2', line)
                
            # Fix participant names with spaces (wrap in quotes)
            if line.strip().startswith('participant'):
                parts = line.split('participant', 1)
                if len(parts) > 1:
                    name = parts[1].strip()
                    if ' ' in name and not (name.startswith('"') or name.startswith("'")):
                        line = f'participant "{name}"'
                        self.fixes_applied.append("Added quotes to participant name with spaces")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_state_diagram(self, diagram: str) -> str:
        """Fix state diagram specific issues"""
        if not 'stateDiagram' in diagram:
            return diagram
        
        fixed = diagram
        
        # Ensure v2 syntax
        if 'stateDiagram' in fixed and not 'stateDiagram-v2' in fixed:
            fixed = fixed.replace('stateDiagram', 'stateDiagram-v2')
            self.fixes_applied.append("Updated to stateDiagram-v2")
        
        # Fix state transitions
        lines = fixed.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Fix [*] syntax for start/end states
            if '[*' in line and not '[*]' in line:
                line = line.replace('[*', '[*]')
                self.fixes_applied.append("Fixed state diagram start/end notation")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_trailing_arrows(self, diagram: str) -> str:
        """Fix arrows pointing to nothing"""
        lines = diagram.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Check for trailing arrows
            stripped = line.strip()
            if stripped.endswith('-->') or stripped.endswith('->>'):
                # Try to fix by adding a placeholder node
                if '-->' in stripped:
                    line = line.replace('-->', '--> [TODO: Add target]')
                elif '->>' in stripped:
                    line = line.replace('->>', '->> TODO: Add target')
                self.fixes_applied.append("Fixed arrow pointing to nothing")
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def fix_common_typos(self, diagram: str) -> str:
        """Fix common typos"""
        fixed = diagram
        
        # Common typos and corrections
        typos = {
            'sequenceDiagam': 'sequenceDiagram',
            'classDiagam': 'classDiagram',
            'stateDiagam': 'stateDiagram',
            'grah ': 'graph ',
            'grpah ': 'graph ',
            'sublgraph': 'subgraph',
            'paricipant': 'participant',
            'particpant': 'participant',
        }
        
        for typo, correct in typos.items():
            if typo in fixed:
                fixed = fixed.replace(typo, correct)
                self.fixes_applied.append(f"Fixed typo: {typo} -> {correct}")
        
        return fixed


def fix_mermaid_in_content(content: str) -> Tuple[str, List[str]]:
    """
    Fix all Mermaid diagrams in markdown content
    Returns: (fixed_content, list_of_all_fixes)
    """
    fixer = MermaidFixer()
    all_fixes = []
    
    # Find all Mermaid code blocks
    pattern = r'(```mermaid\n)(.*?)(\n```)'
    
    def fix_diagram_match(match):
        prefix = match.group(1)
        diagram = match.group(2)
        suffix = match.group(3)
        
        fixed_diagram, fixes = fixer.fix_diagram(diagram)
        all_fixes.extend(fixes)
        
        return prefix + fixed_diagram + suffix
    
    fixed_content = re.sub(pattern, fix_diagram_match, content, flags=re.DOTALL)
    
    return fixed_content, all_fixes


def fix_mermaid_file(file_path: str) -> bool:
    """
    Fix Mermaid diagrams in a file
    Returns: True if fixes were applied
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content, fixes = fix_mermaid_in_content(content)
        
        if fixes:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Fixed {len(fixes)} issue(s) in {file_path}")
            for fix in fixes:
                print(f"  - {fix}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if fix_mermaid_file(file_path):
            print("Fixes applied successfully")
        else:
            print("No fixes needed")
    else:
        print("Usage: python fix_mermaid.py <file_path>")