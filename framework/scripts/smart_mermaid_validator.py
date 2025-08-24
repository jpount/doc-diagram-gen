#!/usr/bin/env python3
"""
Smart Mermaid Validator with Error-Based Fixing
Validates Mermaid diagrams and applies intelligent fixes based on error messages
"""

import os
import re
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class MermaidValidator:
    """Smart validator that learns from error messages to fix diagrams"""
    
    def __init__(self):
        self.error_patterns = {
            # Pattern: (error regex, fix function)
            r"Expecting 'SQE'.*got 'PS'": self.fix_unquoted_parentheses,
            r"Expecting.*COLON": self.fix_missing_colon,
            r"Expecting 'TAGSTART'": self.fix_node_label_quotes,
            r"Parse error.*got 'PS'": self.fix_special_characters,
            r"expecting 'TEXT'": self.fix_text_formatting,
            r"Invalid syntax": self.fix_syntax_issues,
            r"Duplicate id": self.fix_duplicate_ids,
            r"no viable alternative": self.fix_diagram_type,
        }
    
    def extract_diagrams(self, content: str, file_path: str) -> List[Dict]:
        """Extract all Mermaid diagrams from content"""
        diagrams = []
        
        if file_path.endswith('.mmd'):
            diagrams.append({
                'content': content,
                'line_start': 1,
                'type': 'standalone'
            })
        else:
            # Extract from markdown code blocks
            pattern = r'```(?:mermaid|mmd)\s*\n(.*?)\n```'
            for match in re.finditer(pattern, content, re.DOTALL):
                diagram_content = match.group(1)
                line_start = content[:match.start()].count('\n') + 1
                diagrams.append({
                    'content': diagram_content,
                    'line_start': line_start,
                    'type': 'embedded'
                })
        
        return diagrams
    
    def apply_basic_fixes(self, content: str) -> str:
        """Apply safe, universal fixes"""
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            line = line.rstrip()
            
            # Fix indented comments (must start at column 1)
            if line.strip().startswith('%%'):
                line = line.strip()
            
            fixed_lines.append(line)
        
        content = '\n'.join(fixed_lines)
        
        # Fix excessive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure file ends with newline
        if content and not content.endswith('\n'):
            content += '\n'
        
        return content
    
    def fix_unquoted_parentheses(self, content: str, error_line: int = None) -> str:
        """Fix unquoted parentheses in node labels"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if line.strip().startswith('%%') or not line.strip():
                continue
            
            # Pattern for node definitions with labels containing parentheses
            # Match: nodeId[label with (parens)]
            pattern = r'(\w+)\[([^\]]*\([^\]]*\))\]'
            
            def quote_if_needed(match):
                node_id = match.group(1)
                label = match.group(2)
                # If label contains parens and isn't quoted, quote it
                if '(' in label and not (label.startswith('"') and label.endswith('"')):
                    return f'{node_id}["{label}"]'
                return match.group(0)
            
            lines[i] = re.sub(pattern, quote_if_needed, line)
            
            # Also fix method calls in labels
            # Pattern: something[getMethod()]
            pattern2 = r'(\w+)\[(\w+\(\)[^\]]*)\]'
            lines[i] = re.sub(pattern2, r'\1["\2"]', lines[i])
        
        return '\n'.join(lines)
    
    def fix_missing_colon(self, content: str, error_line: int = None) -> str:
        """Fix missing colons in relationship labels"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if line.strip().startswith('%%') or not line.strip():
                continue
            
            # Fix class diagram relationships missing colon
            # Pattern: A --> B label  (should be A --> B : label)
            pattern = r'(\w+\s*(?:-->|<--|<\|--|--\||--o|o--|\|--)\s*\w+)\s+([^:\s][^:\n]+)$'
            lines[i] = re.sub(pattern, r'\1 : \2', line)
            
            # Fix ER diagram relationships
            # Pattern: ENTITY1 ||--o{ ENTITY2 relationship
            pattern2 = r'(\w+\s*\|\|--[o\|]\{\s*\w+)\s+([^:\s][^:\n]+)$'
            lines[i] = re.sub(pattern2, r'\1 : \2', line)
        
        return '\n'.join(lines)
    
    def fix_node_label_quotes(self, content: str, error_line: int = None) -> str:
        """Fix node labels that need quotes"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if line.strip().startswith('%%') or not line.strip():
                continue
            
            # Find node definitions with problematic characters
            # Pattern: nodeId[label with: special chars]
            pattern = r'(\w+)\[([^\]]*[:\(\)\{\}\[\]<>@#$%^&*+=|\\\/][^\]]*)\]'
            
            def quote_label(match):
                node_id = match.group(1)
                label = match.group(2)
                # If not already quoted
                if not (label.startswith('"') and label.endswith('"')):
                    # Escape any quotes in the label
                    label = label.replace('"', '\\"')
                    return f'{node_id}["{label}"]'
                return match.group(0)
            
            lines[i] = re.sub(pattern, quote_label, line)
        
        return '\n'.join(lines)
    
    def fix_special_characters(self, content: str, error_line: int = None) -> str:
        """Fix special characters in labels and text"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if line.strip().startswith('%%') or not line.strip():
                continue
            
            # Fix HTML entities and special chars
            # Replace < and > with escaped versions in labels
            if '[' in line and ']' in line:
                # Extract label content
                pattern = r'\[([^\]]+)\]'
                
                def fix_label(match):
                    label = match.group(1)
                    if not (label.startswith('"') and label.endswith('"')):
                        # Check if label needs quoting
                        if any(char in label for char in ['<', '>', '(', ')', ':', ';', '@', '#', '$', '%', '^', '&', '*']):
                            label = label.replace('"', '\\"')
                            return f'["{label}"]'
                    return match.group(0)
                
                lines[i] = re.sub(pattern, fix_label, line)
            
            # Fix Note spacing
            lines[i] = re.sub(r'(Note\s+(?:over|right of|left of)\s+[^:]+:)\s{2,}', r'\1 ', line)
        
        return '\n'.join(lines)
    
    def fix_text_formatting(self, content: str, error_line: int = None) -> str:
        """Fix text formatting issues"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Remove @ symbols from stereotypes
            lines[i] = re.sub(r'<<@(\w+)>>', r'<<\1>>', line)
            
            # Fix multiple spaces after colons
            lines[i] = re.sub(r':\s{2,}', ': ', line)
            
            # Fix spaces around arrows (should be consistent)
            lines[i] = re.sub(r'\s*-->\s*', ' --> ', line)
            lines[i] = re.sub(r'\s*<--\s*', ' <-- ', line)
            lines[i] = re.sub(r'\s*--\s*', ' -- ', line)
        
        return '\n'.join(lines)
    
    def fix_syntax_issues(self, content: str, error_line: int = None) -> str:
        """Fix general syntax issues"""
        lines = content.split('\n')
        
        # Check for stateDiagram vs stateDiagram-v2
        for i, line in enumerate(lines):
            if line.strip() == 'stateDiagram':
                lines[i] = 'stateDiagram-v2'
        
        # Ensure subgraphs have matching end statements
        subgraph_count = 0
        end_count = 0
        for line in lines:
            if line.strip().startswith('subgraph'):
                subgraph_count += 1
            elif line.strip() == 'end':
                end_count += 1
        
        # Add missing end statements
        if subgraph_count > end_count:
            for _ in range(subgraph_count - end_count):
                lines.append('end')
        
        return '\n'.join(lines)
    
    def fix_duplicate_ids(self, content: str, error_line: int = None) -> str:
        """Fix duplicate node IDs"""
        lines = content.split('\n')
        seen_ids = set()
        
        for i, line in enumerate(lines):
            # Find node definitions
            pattern = r'^(\s*)(\w+)(\[.*?\])?'
            match = re.match(pattern, line)
            
            if match:
                indent = match.group(1)
                node_id = match.group(2)
                label = match.group(3) or ''
                
                if node_id in seen_ids and node_id not in ['end', 'else', 'participant', 'Note']:
                    # Rename duplicate
                    new_id = f"{node_id}_{i}"
                    lines[i] = f"{indent}{new_id}{label}"
                else:
                    seen_ids.add(node_id)
        
        return '\n'.join(lines)
    
    def fix_diagram_type(self, content: str, error_line: int = None) -> str:
        """Fix diagram type declaration"""
        lines = content.split('\n')
        
        # Ensure first non-comment line is a valid diagram type
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('%%'):
                # Check if it's a valid diagram type
                valid_types = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
                              'stateDiagram-v2', 'erDiagram', 'journey', 'gantt', 
                              'pie', 'gitGraph', 'mindmap', 'timeline', 'quadrantChart',
                              'sankey', 'block-beta', 'C4Context', 'C4Container']
                
                first_word = line.strip().split()[0] if line.strip() else ''
                if first_word not in valid_types:
                    # Try to infer diagram type from content
                    if 'participant' in content:
                        lines.insert(i, 'sequenceDiagram')
                    elif 'class' in content:
                        lines.insert(i, 'classDiagram')
                    elif '-->' in content or '--' in content:
                        lines.insert(i, 'graph TD')
                break
        
        return '\n'.join(lines)
    
    def validate_with_mermaid_cli(self, diagram_content: str) -> Tuple[bool, str]:
        """Validate using Mermaid CLI and get detailed error"""
        try:
            # Check for mmdc
            result = subprocess.run(['which', 'mmdc'], capture_output=True, text=True)
            if result.returncode != 0:
                mmdc_cmd = ['npx', '@mermaid-js/mermaid-cli']
            else:
                mmdc_cmd = ['mmdc']
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as tmp_input:
                tmp_input.write(diagram_content)
                tmp_input_path = tmp_input.name
            
            tmp_output_path = tmp_input_path.replace('.mmd', '.svg')
            
            try:
                cmd = mmdc_cmd + ['-i', tmp_input_path, '-o', tmp_output_path, '-t', 'default']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                os.unlink(tmp_input_path)
                if os.path.exists(tmp_output_path):
                    os.unlink(tmp_output_path)
                
                if result.returncode == 0:
                    return True, "Valid"
                else:
                    error_msg = result.stderr or result.stdout or "Unknown error"
                    return False, error_msg
                    
            except subprocess.TimeoutExpired:
                os.unlink(tmp_input_path)
                if os.path.exists(tmp_output_path):
                    os.unlink(tmp_output_path)
                return False, "Timeout: Diagram took too long to render"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def fix_based_on_error(self, content: str, error_msg: str) -> str:
        """Apply fixes based on specific error message"""
        fixed_content = content
        
        # Try each error pattern
        for pattern, fix_func in self.error_patterns.items():
            if re.search(pattern, error_msg, re.IGNORECASE):
                # Extract line number if available
                line_match = re.search(r'line (\d+)', error_msg)
                error_line = int(line_match.group(1)) if line_match else None
                
                # Apply the fix
                fixed_content = fix_func(fixed_content, error_line)
        
        return fixed_content
    
    def validate_and_fix(self, content: str, max_iterations: int = 5) -> Tuple[str, bool, List[str]]:
        """Validate and iteratively fix content"""
        fixed_content = self.apply_basic_fixes(content)
        errors = []
        
        for iteration in range(max_iterations):
            is_valid, error_msg = self.validate_with_mermaid_cli(fixed_content)
            
            if is_valid:
                return fixed_content, True, errors
            
            errors.append(f"Iteration {iteration + 1}: {error_msg}")
            
            # Try to fix based on error
            new_content = self.fix_based_on_error(fixed_content, error_msg)
            
            # If no change was made, try more aggressive fixes
            if new_content == fixed_content:
                new_content = self.fix_unquoted_parentheses(new_content)
                new_content = self.fix_missing_colon(new_content)
                new_content = self.fix_node_label_quotes(new_content)
                new_content = self.fix_special_characters(new_content)
            
            # Check if we made any progress
            if new_content == fixed_content:
                # No more fixes to try
                break
            
            fixed_content = new_content
        
        return fixed_content, False, errors

def validate_file(file_path: str, validator: MermaidValidator, auto_fix: bool = False) -> Dict:
    """Validate and optionally fix a file"""
    results = {
        'file': file_path,
        'valid': True,
        'fixed': False,
        'errors': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        results['valid'] = False
        results['errors'].append(f"Could not read file: {str(e)}")
        return results
    
    # Extract diagrams
    diagrams = validator.extract_diagrams(content, file_path)
    
    if not diagrams and file_path.endswith('.mmd'):
        results['errors'].append("Empty Mermaid diagram file")
        return results
    
    # For .mmd files, validate and fix the entire content
    if file_path.endswith('.mmd'):
        fixed_content, is_valid, errors = validator.validate_and_fix(content)
        
        if not is_valid:
            results['valid'] = False
            results['errors'].extend(errors)
        
        if auto_fix and fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            results['fixed'] = True
    
    # For .md files, validate and fix each diagram block
    elif diagrams:
        all_valid = True
        new_content = content
        
        for diagram in diagrams:
            diagram_content = diagram['content']
            fixed_diagram, is_valid, errors = validator.validate_and_fix(diagram_content)
            
            if not is_valid:
                all_valid = False
                results['errors'].extend([f"Diagram at line {diagram['line_start']}: {e}" for e in errors])
            
            if auto_fix and fixed_diagram != diagram_content:
                # Replace in content
                old_block = f'```mermaid\n{diagram_content}\n```'
                new_block = f'```mermaid\n{fixed_diagram}\n```'
                new_content = new_content.replace(old_block, new_block)
                
                old_block = f'```mmd\n{diagram_content}\n```'
                new_block = f'```mmd\n{fixed_diagram}\n```'
                new_content = new_content.replace(old_block, new_block)
        
        results['valid'] = all_valid
        
        if auto_fix and new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            results['fixed'] = True
    
    return results

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Mermaid validator with error-based fixing')
    parser.add_argument('path', nargs='?', default='output', help='Path to file or directory')
    parser.add_argument('--fix', action='store_true', help='Automatically fix errors')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    validator = MermaidValidator()
    path = Path(args.path)
    files_to_validate = []
    
    if path.is_file():
        if path.suffix in ['.md', '.mmd']:
            files_to_validate.append(path)
    elif path.is_dir():
        files_to_validate.extend(path.glob('**/*.md'))
        files_to_validate.extend(path.glob('**/*.mmd'))
    else:
        print(f"Error: {path} is not a valid file or directory")
        return 1
    
    if not files_to_validate:
        print("No .md or .mmd files found")
        return 0
    
    all_results = []
    total_valid = 0
    total_invalid = 0
    total_fixed = 0
    
    for file_path in files_to_validate:
        result = validate_file(str(file_path), validator, auto_fix=args.fix)
        all_results.append(result)
        
        if result['valid']:
            total_valid += 1
            status = "✅"
        else:
            total_invalid += 1
            status = "❌"
        
        if result['fixed']:
            total_fixed += 1
            status += " 🔧"
        
        if not args.json:
            print(f"{status} {file_path}")
            if not result['valid']:
                for error in result['errors'][:3]:  # Show first 3 errors
                    print(f"   - {error[:100]}...")
    
    if args.json:
        print(json.dumps({
            'summary': {
                'total_files': len(files_to_validate),
                'valid': total_valid,
                'invalid': total_invalid,
                'fixed': total_fixed
            },
            'files': all_results
        }, indent=2))
    else:
        print(f"\nSummary: {total_valid} valid, {total_invalid} invalid, {total_fixed} fixed")
    
    return 0 if total_invalid == 0 else 1

if __name__ == '__main__':
    exit(main())