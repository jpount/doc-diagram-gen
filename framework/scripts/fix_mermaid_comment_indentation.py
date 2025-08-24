#!/usr/bin/env python3
"""
Fix indented comments at the start of Mermaid diagrams
These can cause parsing issues in Mermaid.js
"""

import re
from pathlib import Path
from typing import Tuple, List

def fix_leading_comments(content: str) -> Tuple[str, List[str]]:
    """Remove indentation from leading comment lines before diagram declaration"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    diagram_started = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check if this is a diagram declaration line
        if not diagram_started and stripped and not stripped.startswith('%%'):
            for dt in ['sequenceDiagram', 'classDiagram', 'graph', 'flowchart', 
                      'stateDiagram-v2', 'stateDiagram', 'erDiagram', 'gantt', 
                      'pie', 'journey', 'gitGraph']:
                if stripped.startswith(dt):
                    diagram_started = True
                    break
        
        # If we haven't hit the diagram declaration yet and it's a comment
        if not diagram_started and stripped.startswith('%%'):
            if line != stripped:  # Has indentation
                fixed_lines.append(stripped)
                fixes.append(f"Removed indentation from comment: {stripped[:30]}...")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def fix_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix a single .mmd file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    fixed_content, fixes = fix_leading_comments(content)
    
    if fixes and fixed_content != content:
        with open(file_path, 'w') as f:
            f.write(fixed_content)
        return True, fixes
    return False, []

def main():
    """Fix all Mermaid diagrams with indented comments"""
    output_dir = Path("/Users/jp/work/xxx/doc-diagram-gen/output")
    
    if not output_dir.exists():
        print(f"Directory {output_dir} not found")
        return 1
    
    print("Fixing indented comments in Mermaid diagrams")
    print("=" * 60)
    
    fixed_count = 0
    for mmd_file in sorted(output_dir.rglob("*.mmd")):
        fixed, fixes = fix_file(mmd_file)
        if fixed:
            fixed_count += 1
            print(f"  ✅ {mmd_file.name}")
            for fix in fixes[:2]:  # Show first 2 fixes
                print(f"     - {fix}")
    
    print("\n" + "=" * 60)
    print(f"Fixed {fixed_count} files with indented comments")
    
    if fixed_count > 0:
        print("\n✅ Comments fixed. Now test with:")
        print("  python3 framework/scripts/test_all_mermaid_comprehensive.py")
    else:
        print("\n✅ No indented comments found")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())