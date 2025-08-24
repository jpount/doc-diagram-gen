#!/usr/bin/env python3
"""
Properly fix note blocks in Mermaid class diagrams
Remove all problematic characters and ensure valid syntax
"""

import re
from pathlib import Path

def clean_note_text(text):
    """Clean note text to be Mermaid-safe"""
    # Remove all quotes and problematic characters
    text = text.replace('"', '')
    text = text.replace("'", '')
    text = text.replace('=', ':')
    text = text.replace('{', '(')
    text = text.replace('}', ')')
    text = text.replace(',', '')
    text = text.replace('@', '')
    text = text.replace('(', '')
    text = text.replace(')', '')
    text = text.replace('[', '')
    text = text.replace(']', '')
    text = text.replace('|', '')
    text = text.replace('\\', '/')
    text = text.replace('`', '')
    text = text.replace('~', '-')
    text = text.replace('*', '')
    text = text.replace('&', 'and')
    text = text.replace('%', 'percent')
    text = text.replace('#', 'num')
    text = text.replace('$', '')
    text = text.replace('^', '')
    text = text.replace('!', '')
    text = text.replace('?', '')
    text = text.replace(';', '')
    text = text.replace(':', ' -')
    
    # Clean up whitespace
    text = ' '.join(text.split())
    
    return text

def fix_all_notes_in_file(file_path):
    """Fix all note blocks in a file"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    for line in lines:
        if line.strip().startswith('note for'):
            # Extract the note content
            match = re.match(r'(\s*)note for (\w+)\s+"([^"]*)"', line)
            if match:
                indent = match.group(1)
                class_name = match.group(2)
                note_content = match.group(3)
                
                # Clean the note content
                cleaned = clean_note_text(note_content)
                
                # Simplify to just key information
                parts = cleaned.split('<br/>')
                if parts:
                    # Take first meaningful part only
                    simple_note = parts[0].strip()
                    if len(simple_note) > 50:
                        simple_note = simple_note[:50] + '...'
                    
                    # Write simplified note
                    fixed_lines.append(f'{indent}note for {class_name} "{simple_note}"\n')
                else:
                    # Skip empty notes
                    continue
            else:
                # If the note doesn't match expected format, skip it
                continue
        else:
            fixed_lines.append(line)
    
    # Write back
    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed notes in {file_path}")

def main():
    # Fix both class diagram files
    files = [
        "output/diagrams/class-diagram-services.mmd",
        "output/diagrams/class-diagram-entities.mmd"
    ]
    
    for file_path in files:
        if Path(file_path).exists():
            fix_all_notes_in_file(file_path)

if __name__ == "__main__":
    main()