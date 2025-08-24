#!/usr/bin/env python3
"""
Fix note blocks in class diagrams to use proper single-line syntax
"""

import re
import sys

def fix_note_blocks(content):
    """Convert multi-line note blocks to single-line format"""
    
    # Pattern to match note blocks
    pattern = r'(\s*)note for (\w+)\n((?:.*\n)*?)\s*end note'
    
    def replace_note(match):
        indent = match.group(1)
        class_name = match.group(2)
        note_content = match.group(3)
        
        # Process the note content
        lines = note_content.strip().split('\n')
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Remove leading dashes and colons
                line = re.sub(r'^\s*-\s*', '', line)
                line = re.sub(r'^\s*:\s*', '', line)
                # Clean up annotations
                line = re.sub(r'@(\w+).*', r'@\1', line)
                # Simplify text
                if '@' not in line and '(' not in line:
                    line = line.split(':')[0].strip()
                processed_lines.append(line)
        
        # Join with HTML breaks
        note_text = '<br/>'.join(processed_lines[:4])  # Limit to 4 lines
        
        return f'{indent}note for {class_name} "{note_text}"'
    
    # Replace all note blocks
    fixed_content = re.sub(pattern, replace_note, content, flags=re.MULTILINE)
    
    return fixed_content

if __name__ == "__main__":
    file_path = "output/diagrams/class-diagram-services.mmd"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    fixed_content = fix_note_blocks(content)
    
    with open(file_path, 'w') as f:
        f.write(fixed_content)
    
    print("Fixed all note blocks in class-diagram-services.mmd")