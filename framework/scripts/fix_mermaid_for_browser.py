#!/usr/bin/env python3
"""
Fix Mermaid diagrams for browser rendering
Addresses issues that cause errors in Mermaid.js 10.6.1
"""

import re
from pathlib import Path

def fix_sequence_diagram_participants(content):
    """Fix participant declarations with complex aliases"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Fix participant declarations with "as" in quotes
        if line.strip().startswith('participant'):
            # Pattern: participant "Alias as Name<br/>Description"
            match = re.match(r'^(\s*)participant\s+"([^"]+)"', line)
            if match:
                indent = match.group(1)
                full_alias = match.group(2)
                
                # If it contains 'as' and '<br/>', simplify it
                if ' as ' in full_alias:
                    # Extract the short name (before 'as')
                    short_name = full_alias.split(' as ')[0]
                    # Create a simplified version
                    fixed_lines.append(f'{indent}participant {short_name}')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_sequence_diagram_notes(content):
    """Fix note formatting issues"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Remove extra spaces after colons in notes
        if 'Note over' in line or 'Note right of' in line or 'Note left of' in line:
            # Remove multiple spaces after colon
            line = re.sub(r':\s+', ': ', line)
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_indentation_in_diagrams(content):
    """Remove unnecessary indentation inside diagrams"""
    lines = content.split('\n')
    
    # Detect diagram type
    diagram_type = None
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('%%'):
            for dt in ['sequenceDiagram', 'classDiagram', 'graph', 'flowchart', 'stateDiagram-v2', 'erDiagram']:
                if stripped.startswith(dt):
                    diagram_type = dt
                    break
            break
    
    if not diagram_type:
        return content
    
    # For sequence diagrams, remove indentation from most lines
    if diagram_type == 'sequenceDiagram':
        fixed_lines = []
        for line in lines:
            stripped = line.strip()
            # Keep comments as-is
            if stripped.startswith('%%') or not stripped:
                fixed_lines.append(line)
            # Remove indentation from diagram content
            else:
                fixed_lines.append(stripped)
        return '\n'.join(fixed_lines)
    
    return content

def fix_graph_subgraph_nesting(content):
    """Fix nested subgraph issues"""
    lines = content.split('\n')
    
    # Count subgraph depth
    subgraph_depth = 0
    fixed_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Track subgraph nesting
        if 'subgraph' in stripped and not stripped.startswith('%%'):
            subgraph_depth += 1
            # Ensure proper indentation for nested subgraphs
            if subgraph_depth > 1:
                fixed_lines.append('    ' * (subgraph_depth - 1) + stripped)
            else:
                fixed_lines.append(stripped)
        elif stripped == 'end':
            subgraph_depth = max(0, subgraph_depth - 1)
            if subgraph_depth > 0:
                fixed_lines.append('    ' * subgraph_depth + stripped)
            else:
                fixed_lines.append(stripped)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_mermaid_file(file_path):
    """Fix a single Mermaid file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Determine diagram type
    diagram_type = None
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('%%'):
            for dt in ['sequenceDiagram', 'classDiagram', 'graph', 'flowchart', 'stateDiagram-v2', 'erDiagram']:
                if stripped.startswith(dt):
                    diagram_type = dt
                    break
            break
    
    if not diagram_type:
        print(f"  ⚠️  {file_path.name}: Could not determine diagram type")
        return False
    
    # Apply fixes based on diagram type
    if diagram_type == 'sequenceDiagram':
        content = fix_sequence_diagram_participants(content)
        content = fix_sequence_diagram_notes(content)
        content = fix_indentation_in_diagrams(content)
    elif diagram_type in ['graph', 'flowchart']:
        content = fix_graph_subgraph_nesting(content)
    
    # Write back if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  ✅ Fixed: {file_path.name}")
        return True
    else:
        print(f"  ✅ No changes needed: {file_path.name}")
        return False

def main():
    """Fix all Mermaid files for browser rendering"""
    output_dir = Path("output/diagrams")
    
    if not output_dir.exists():
        print(f"Directory {output_dir} not found")
        return 1
    
    files = list(output_dir.glob("*.mmd"))
    
    print("Fixing Mermaid diagrams for browser rendering")
    print("=" * 60)
    
    fixed_count = 0
    for file_path in sorted(files):
        if fix_mermaid_file(file_path):
            fixed_count += 1
    
    print("=" * 60)
    print(f"Fixed {fixed_count} files")
    print("\nNow test with:")
    print("  1. python3 framework/scripts/test_mermaid_with_browser.py")
    print("  2. Open framework/document-viewer.html and browse to output/diagrams")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())