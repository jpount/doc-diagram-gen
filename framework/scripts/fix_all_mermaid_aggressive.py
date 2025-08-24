#!/usr/bin/env python3
"""
Aggressive Mermaid fixer - fixes ALL common issues that break rendering in browsers
"""

import re
from pathlib import Path
from typing import List, Tuple

def fix_mermaid_content(content: str, file_name: str = "") -> Tuple[str, List[str]]:
    """Fix all common Mermaid rendering issues"""
    fixes_applied = []
    original = content
    
    # Detect diagram type
    diagram_type = None
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('%%'):
            for dt in ['sequenceDiagram', 'classDiagram', 'graph', 'flowchart', 
                      'stateDiagram-v2', 'stateDiagram', 'erDiagram', 'gantt', 
                      'pie', 'journey', 'gitGraph']:
                if stripped.startswith(dt):
                    diagram_type = dt
                    break
            break
    
    if not diagram_type:
        return content, ["Could not determine diagram type"]
    
    # Apply fixes based on diagram type
    if diagram_type == 'sequenceDiagram':
        content, seq_fixes = fix_sequence_diagram(content)
        fixes_applied.extend(seq_fixes)
    elif diagram_type == 'classDiagram':
        content, class_fixes = fix_class_diagram(content)
        fixes_applied.extend(class_fixes)
    elif diagram_type in ['graph', 'flowchart']:
        content, graph_fixes = fix_graph_diagram(content)
        fixes_applied.extend(graph_fixes)
    elif diagram_type.startswith('stateDiagram'):
        content, state_fixes = fix_state_diagram(content)
        fixes_applied.extend(state_fixes)
    elif diagram_type == 'erDiagram':
        content, er_fixes = fix_er_diagram(content)
        fixes_applied.extend(er_fixes)
    
    # Common fixes for all diagram types
    content, common_fixes = apply_common_fixes(content)
    fixes_applied.extend(common_fixes)
    
    return content, fixes_applied

def fix_sequence_diagram(content: str) -> Tuple[str, List[str]]:
    """Fix sequence diagram specific issues"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        
        # Remove indentation (except for comments)
        if not line.strip().startswith('%%'):
            line = line.strip()
            if line != original_line.strip():
                fixes.append("Removed indentation")
        
        # Fix participant declarations with complex aliases
        if line.startswith('participant'):
            # Pattern: participant "Name as Description<br/>Details"
            match = re.match(r'^participant\s+"([^"]+)"', line)
            if match:
                full_text = match.group(1)
                if ' as ' in full_text:
                    # Extract just the name part
                    name = full_text.split(' as ')[0]
                    line = f'participant {name}'
                    fixes.append(f"Simplified participant: {name}")
        
        # Fix notes with extra spaces after colon
        if 'Note ' in line:
            original = line
            line = re.sub(r':\s+', ': ', line)
            if line != original:
                fixes.append("Fixed note spacing")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def fix_class_diagram(content: str) -> Tuple[str, List[str]]:
    """Fix class diagram specific issues"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        
        # Remove @ from stereotypes
        if '<<@' in line:
            line = line.replace('<<@', '<<')
            fixes.append("Removed @ from stereotype")
        
        # Fix ER diagram syntax in class diagrams
        if '||--||' in line:
            line = re.sub(r'(\w+)\s*\|\|--\|\|\s*(\w+)', r'\1 "1" -- "1" \2', line)
            fixes.append("Fixed ER syntax to class syntax")
        elif '||--o{' in line:
            line = re.sub(r'(\w+)\s*\|\|--o\{\s*(\w+)', r'\1 "1" --o "*" \2', line)
            fixes.append("Fixed ER syntax to class syntax")
        
        # Ensure relationship labels have colons
        if ('-->' in line or '--' in line or '..' in line) and ':' not in line:
            # Check if it has a label that needs a colon
            parts = re.split(r'(-->|--|\.\.)', line)
            if len(parts) == 3:
                before = parts[0].strip()
                arrow = parts[1]
                after = parts[2].strip()
                
                # Check if 'after' has both target and label
                after_parts = after.split(None, 1)
                if len(after_parts) == 2 and not after_parts[1].startswith('"'):
                    target, label = after_parts
                    line = f"    {before} {arrow} {target} : {label}"
                    fixes.append("Added colon to relationship label")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def fix_graph_diagram(content: str) -> Tuple[str, List[str]]:
    """Fix graph/flowchart specific issues"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    subgraph_count = 0
    
    for line in lines:
        original_line = line
        
        # Fix numeric node IDs
        if re.match(r'^\s*\d+\[', line):
            line = re.sub(r'^(\s*)(\d+)(\[)', r'\1node\2\3', line)
            fixes.append("Fixed numeric node ID")
        
        # Fix HTML breaks
        if '\\<br/\\>' in line:
            line = line.replace('\\<br/\\>', '<br/>')
            fixes.append("Fixed HTML break syntax")
        
        # Track and fix subgraph nesting
        if 'subgraph' in line and not line.strip().startswith('%%'):
            subgraph_count += 1
        elif line.strip() == 'end':
            subgraph_count = max(0, subgraph_count - 1)
        
        fixed_lines.append(line)
    
    # Check for unbalanced subgraphs
    if subgraph_count != 0:
        fixes.append(f"Warning: Unbalanced subgraphs (count: {subgraph_count})")
    
    return '\n'.join(fixed_lines), fixes

def fix_state_diagram(content: str) -> Tuple[str, List[str]]:
    """Fix state diagram specific issues"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    # First line might be stateDiagram without -v2
    if lines and lines[0].strip() == 'stateDiagram':
        lines[0] = 'stateDiagram-v2'
        fixes.append("Updated to stateDiagram-v2")
    
    for line in lines:
        # Fix HTML breaks in state diagrams
        if '<br/>' in line and not line.strip().startswith('%%'):
            line = line.replace('<br/>', '\\n')
            fixes.append("Replaced <br/> with \\n in state diagram")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def fix_er_diagram(content: str) -> Tuple[str, List[str]]:
    """Fix ER diagram specific issues"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Ensure proper ER relationship syntax
        if '||' in line or '}o' in line or 'o{' in line:
            # Check if it's a valid ER relationship
            if not any(pattern in line for pattern in ['||--||', '||--o{', '}o--||', '}o--o{']):
                # Try to fix it
                line = re.sub(r'(\w+)\s+(\|\||\}o|o\{)', r'\1 ||--||', line)
                fixes.append("Fixed ER relationship syntax")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def apply_common_fixes(content: str) -> Tuple[str, List[str]]:
    """Apply fixes common to all diagram types"""
    fixes = []
    
    # Remove trailing whitespace
    lines = content.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]
    if lines != cleaned_lines:
        content = '\n'.join(cleaned_lines)
        fixes.append("Removed trailing whitespace")
    
    # Ensure file ends with newline
    if not content.endswith('\n'):
        content += '\n'
        fixes.append("Added final newline")
    
    # Remove multiple consecutive blank lines
    original = content
    content = re.sub(r'\n\n\n+', '\n\n', content)
    if content != original:
        fixes.append("Removed excessive blank lines")
    
    return content, fixes

def fix_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix a single file"""
    if file_path.suffix == '.mmd':
        # Standalone Mermaid file
        with open(file_path, 'r') as f:
            content = f.read()
        
        fixed_content, fixes = fix_mermaid_content(content, file_path.name)
        
        if fixes and fixed_content != content:
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            return True, fixes
        return False, []
    
    elif file_path.suffix == '.md':
        # Markdown file with embedded diagrams
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find and fix all mermaid blocks
        def fix_mermaid_block(match):
            diagram_content = match.group(1)
            fixed_content, _ = fix_mermaid_content(diagram_content, f"{file_path.name} (embedded)")
            return f'```mermaid\n{fixed_content}\n```'
        
        original = content
        content = re.sub(r'```mermaid\s*\n(.*?)\n```', fix_mermaid_block, content, flags=re.DOTALL)
        
        if content != original:
            with open(file_path, 'w') as f:
                f.write(content)
            return True, ["Fixed embedded diagrams"]
        return False, []
    
    return False, []

def main():
    """Fix all Mermaid diagrams aggressively"""
    output_dir = Path("/Users/jp/work/xxx/doc-diagram-gen/output")
    
    if not output_dir.exists():
        print(f"Directory {output_dir} not found")
        return 1
    
    print("Aggressive Mermaid Fix - Fixing ALL diagrams")
    print("=" * 60)
    
    # Fix standalone .mmd files
    print("\n📄 Fixing standalone .mmd files:")
    mmd_count = 0
    for mmd_file in sorted(output_dir.rglob("*.mmd")):
        fixed, fixes = fix_file(mmd_file)
        if fixed:
            mmd_count += 1
            print(f"  ✅ {mmd_file.name}")
            for fix in fixes[:3]:  # Show first 3 fixes
                print(f"     - {fix}")
        else:
            print(f"  ✅ {mmd_file.name} (no changes needed)")
    
    # Fix embedded diagrams in .md files
    print("\n📝 Fixing embedded diagrams in .md files:")
    md_count = 0
    for md_file in sorted(output_dir.rglob("*.md")):
        # Check if file has mermaid blocks
        with open(md_file, 'r') as f:
            if '```mermaid' in f.read():
                fixed, fixes = fix_file(md_file)
                if fixed:
                    md_count += 1
                    print(f"  ✅ {md_file.name}")
                    for fix in fixes:
                        print(f"     - {fix}")
                else:
                    print(f"  ✅ {md_file.name} (no changes needed)")
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Fixed {mmd_count} .mmd files")
    print(f"  Fixed {md_count} .md files with embedded diagrams")
    print("\n✅ All diagrams have been processed")
    print("\nNow test with:")
    print("  python3 framework/scripts/test_all_mermaid_comprehensive.py")
    print("\nOr open framework/document-viewer.html to verify")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())