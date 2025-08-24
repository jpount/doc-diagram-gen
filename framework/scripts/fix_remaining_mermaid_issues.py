#!/usr/bin/env python3
"""
Fix remaining Mermaid syntax issues
Specifically handle sequence diagram notes with complex content
"""

import re
from pathlib import Path

def fix_sequence_diagram_notes(content):
    """Fix notes in sequence diagrams that have problematic characters"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if 'Note' in line and ':' in line:
            # Extract the note parts
            match = re.match(r'(\s*)(Note\s+(?:right|left|over)\s+of\s+\w+):\s*(.*)', line)
            if match:
                indent = match.group(1)
                note_prefix = match.group(2)
                note_content = match.group(3)
                
                # Clean the note content
                # Remove quotes that might cause issues
                note_content = note_content.replace('"', '')
                note_content = note_content.replace(':', ' -')
                
                # Reconstruct the note
                fixed_lines.append(f'{indent}{note_prefix}: {note_content}')
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_class_diagram_relationships(content):
    """Ensure class diagram relationships are properly formatted"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Skip if it's not a relationship line
        if '--' not in line and '..' not in line:
            fixed_lines.append(line)
            continue
            
        # Check if line has cardinality quotes (these are valid)
        if re.match(r'^\s*\w+\s+"[^"]+"\s*(--|\.\.)\w*\s+"[^"]+"\s+\w+', line):
            # This is a valid cardinality pattern, keep it
            fixed_lines.append(line)
        elif '"' in line and ('--' in line or '..' in line):
            # Might have other quote issues
            # Remove any problematic quotes except cardinality
            fixed_line = line
            # Only process if not a valid cardinality pattern
            if not re.search(r'"[\d\*]+"', line):
                fixed_line = line.replace('"', '')
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_file(file_path):
    """Fix a single Mermaid file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Determine diagram type
    first_line = content.strip().split('\n')[0] if content.strip() else ""
    
    if 'sequenceDiagram' in first_line:
        content = fix_sequence_diagram_notes(content)
    elif 'classDiagram' in first_line:
        content = fix_class_diagram_relationships(content)
    
    # Only write if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Fixed: {file_path.name}")
        return True
    return False

def main():
    """Fix all Mermaid files with remaining issues"""
    output_dir = Path("output/diagrams")
    
    # Files with reported issues
    problem_files = [
        "sequence-buy-order.mmd",
        "sequence-sell-order.mmd",
        "class-diagram-entities.mmd"
    ]
    
    print("Fixing remaining Mermaid syntax issues...")
    print("=" * 60)
    
    fixed_count = 0
    for filename in problem_files:
        file_path = output_dir / filename
        if file_path.exists():
            if fix_file(file_path):
                fixed_count += 1
    
    print("=" * 60)
    print(f"Fixed {fixed_count} files")
    
    # Now fix any other files that might have issues
    print("\nChecking all other files...")
    for file_path in output_dir.glob("*.mmd"):
        if file_path.name not in problem_files:
            if fix_file(file_path):
                fixed_count += 1
    
    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == "__main__":
    main()