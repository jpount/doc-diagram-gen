#!/usr/bin/env python3
"""
Fix all Note spacing issues in Mermaid diagrams
Specifically handles extra spaces after colons in Note statements
"""

import re
from pathlib import Path
from typing import Tuple, List

def fix_note_spacing(content: str) -> Tuple[str, List[str]]:
    """Fix all Note statement spacing issues"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        
        # Fix "Note over" statements with extra spaces after colon
        if 'Note over' in line and ':' in line:
            # Pattern to match "Note over X, Y:  <spaces>  text"
            line = re.sub(r'(Note\s+over\s+[^:]+):\s+', r'\1: ', line)
            if line != original_line:
                fixes.append(f"Fixed note spacing: {line.strip()[:50]}...")
        
        # Fix "Note right of" and "Note left of" with extra spaces
        elif 'Note right of' in line and ':' in line:
            line = re.sub(r'(Note\s+right\s+of\s+[^:]+):\s+', r'\1: ', line)
            if line != original_line:
                fixes.append(f"Fixed note spacing: {line.strip()[:50]}...")
        
        elif 'Note left of' in line and ':' in line:
            line = re.sub(r'(Note\s+left\s+of\s+[^:]+):\s+', r'\1: ', line)
            if line != original_line:
                fixes.append(f"Fixed note spacing: {line.strip()[:50]}...")
                
        # Also handle Note statements that might not have been caught
        elif line.strip().startswith('Note ') and ':' in line:
            # General pattern for any Note statement
            line = re.sub(r':\s{2,}', ': ', line)
            if line != original_line:
                fixes.append(f"Fixed note spacing: {line.strip()[:50]}...")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def fix_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix a single file"""
    if file_path.suffix == '.mmd':
        with open(file_path, 'r') as f:
            content = f.read()
        
        fixed_content, fixes = fix_note_spacing(content)
        
        if fixes and fixed_content != content:
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            return True, fixes
        return False, []
    
    elif file_path.suffix == '.md':
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Find and fix all mermaid blocks
        changed = False
        def fix_mermaid_block(match):
            nonlocal changed
            diagram_content = match.group(1)
            fixed_content, fixes = fix_note_spacing(diagram_content)
            if fixes:
                changed = True
            return f'```mermaid\n{fixed_content}\n```'
        
        original = content
        content = re.sub(r'```mermaid\s*\n(.*?)\n```', fix_mermaid_block, content, flags=re.DOTALL)
        
        if changed:
            with open(file_path, 'w') as f:
                f.write(content)
            return True, ["Fixed note spacing in embedded diagrams"]
        return False, []
    
    return False, []

def main():
    """Fix Note spacing in all Mermaid diagrams"""
    output_dir = Path("/Users/jp/work/xxx/doc-diagram-gen/output")
    
    if not output_dir.exists():
        print(f"Directory {output_dir} not found")
        return 1
    
    print("Fixing Note spacing issues in Mermaid diagrams")
    print("=" * 60)
    
    # Fix standalone .mmd files
    print("\n📄 Fixing standalone .mmd files:")
    mmd_count = 0
    mmd_files_with_issues = []
    
    for mmd_file in sorted(output_dir.rglob("*.mmd")):
        fixed, fixes = fix_file(mmd_file)
        if fixed:
            mmd_count += 1
            mmd_files_with_issues.append(mmd_file.name)
            print(f"  ✅ {mmd_file.name}")
            for fix in fixes[:2]:  # Show first 2 fixes
                print(f"     - {fix}")
    
    # Fix embedded diagrams in .md files
    print("\n📝 Fixing embedded diagrams in .md files:")
    md_count = 0
    for md_file in sorted(output_dir.rglob("*.md")):
        with open(md_file, 'r') as f:
            if '```mermaid' in f.read():
                fixed, fixes = fix_file(md_file)
                if fixed:
                    md_count += 1
                    print(f"  ✅ {md_file.name}")
                    for fix in fixes:
                        print(f"     - {fix}")
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Fixed {mmd_count} .mmd files")
    print(f"  Fixed {md_count} .md files with embedded diagrams")
    
    if mmd_count > 0:
        print(f"\nFiles that had Note spacing issues:")
        for file in mmd_files_with_issues:
            print(f"  - {file}")
    
    print("\n✅ Note spacing fixed. Now test with:")
    print("  python3 framework/scripts/test_all_mermaid_comprehensive.py")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())