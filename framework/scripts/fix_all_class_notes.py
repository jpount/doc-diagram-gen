#!/usr/bin/env python3
"""
Fix all note blocks in class diagrams to use proper single-line syntax
"""

import re
import sys
from pathlib import Path

def fix_note_blocks(content):
    """Convert multi-line note blocks to single-line format"""
    
    # Pattern to match note blocks with end note
    pattern = r'(\s*)note for (\w+)\n((?:.*\n)*?)\s*end note'
    
    def replace_note(match):
        indent = match.group(1)
        class_name = match.group(2)
        note_content = match.group(3)
        
        # Process the note content
        lines = []
        for line in note_content.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('//'):
                # Clean up special characters and limit length
                line = line.replace('"', "'")
                line = line.replace('\\', '/')
                line = line[:100]  # Limit line length
                lines.append(line)
        
        # Take first 3 non-empty lines
        lines = [l for l in lines if l][:3]
        
        if not lines:
            return ''  # Remove empty notes
        
        # Join with HTML breaks
        note_text = '<br/>'.join(lines)
        
        return f'{indent}note for {class_name} "{note_text}"'
    
    # Replace all note blocks
    fixed_content = re.sub(pattern, replace_note, content, flags=re.MULTILINE)
    
    return fixed_content

def main():
    # Fix both class diagram files
    files = [
        "output/diagrams/class-diagram-services.mmd",
        "output/diagrams/class-diagram-entities.mmd"
    ]
    
    for file_path in files:
        if Path(file_path).exists():
            print(f"Processing {file_path}...")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            fixed_content = fix_note_blocks(content)
            
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            
            print(f"  Fixed note blocks in {file_path}")

if __name__ == "__main__":
    main()