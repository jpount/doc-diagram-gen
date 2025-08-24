#!/usr/bin/env python3
"""
Aggressively fix ALL spaces after colons in Note statements
"""

import re
from pathlib import Path
from typing import Tuple, List

def fix_note_spacing_aggressive(content: str) -> Tuple[str, List[str]]:
    """Remove ALL extra spaces after colons in Note statements"""
    fixes = []
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        
        # Fix any Note statement with spaces after colon
        if line.strip().startswith('Note '):
            # Find the colon and remove ALL spaces after it (leaving just one)
            if ':' in line:
                # Split at the colon
                parts = line.split(':', 1)
                if len(parts) == 2:
                    # Remove ALL leading spaces from the text part
                    text_part = parts[1].lstrip()
                    # Reconstruct with single space
                    if text_part:  # Only add space if there's text
                        line = parts[0] + ': ' + text_part
                    else:
                        line = parts[0] + ':'
                    
                    if line != original_line:
                        fixes.append(f"Fixed: {line[:60]}...")
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines), fixes

def fix_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix a single file"""
    if file_path.suffix == '.mmd':
        with open(file_path, 'r') as f:
            content = f.read()
        
        fixed_content, fixes = fix_note_spacing_aggressive(content)
        
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
        all_fixes = []
        
        def fix_mermaid_block(match):
            nonlocal changed, all_fixes
            diagram_content = match.group(1)
            fixed_content, fixes = fix_note_spacing_aggressive(diagram_content)
            if fixes:
                changed = True
                all_fixes.extend(fixes)
            return f'```mermaid\n{fixed_content}\n```'
        
        content = re.sub(r'```mermaid\s*\n(.*?)\n```', fix_mermaid_block, content, flags=re.DOTALL)
        
        if changed:
            with open(file_path, 'w') as f:
                f.write(content)
            return True, all_fixes
        return False, []
    
    return False, []

def main():
    """Fix ALL Note spacing issues aggressively"""
    output_dir = Path("/Users/jp/work/xxx/doc-diagram-gen/output")
    
    if not output_dir.exists():
        print(f"Directory {output_dir} not found")
        return 1
    
    print("AGGRESSIVE Fix for ALL Note spacing issues")
    print("=" * 60)
    
    # Count all Notes with issues first
    total_issues = 0
    for mmd_file in output_dir.rglob("*.mmd"):
        with open(mmd_file, 'r') as f:
            for line in f:
                if line.strip().startswith('Note ') and ': ' in line:
                    # Check if there are multiple spaces after colon
                    if re.search(r':\s{2,}', line):
                        total_issues += 1
    
    print(f"Found {total_issues} Note statements with spacing issues")
    print()
    
    # Fix standalone .mmd files
    print("📄 Fixing standalone .mmd files:")
    mmd_count = 0
    
    for mmd_file in sorted(output_dir.rglob("*.mmd")):
        fixed, fixes = fix_file(mmd_file)
        if fixed:
            mmd_count += 1
            print(f"  ✅ {mmd_file.name} - Fixed {len(fixes)} lines")
    
    # Fix embedded diagrams in .md files
    print("\n📝 Fixing embedded diagrams in .md files:")
    md_count = 0
    for md_file in sorted(output_dir.rglob("*.md")):
        with open(md_file, 'r') as f:
            if '```mermaid' in f.read():
                fixed, fixes = fix_file(md_file)
                if fixed:
                    md_count += 1
                    print(f"  ✅ {md_file.name} - Fixed {len(fixes)} lines")
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Fixed {mmd_count} .mmd files")
    print(f"  Fixed {md_count} .md files with embedded diagrams")
    
    # Re-count issues
    remaining_issues = 0
    for mmd_file in output_dir.rglob("*.mmd"):
        with open(mmd_file, 'r') as f:
            for line in f:
                if line.strip().startswith('Note ') and ': ' in line:
                    if re.search(r':\s{2,}', line):
                        remaining_issues += 1
                        print(f"STILL HAS ISSUE: {mmd_file.name}: {line.strip()[:60]}")
    
    if remaining_issues == 0:
        print("\n✅ ALL Note spacing issues fixed!")
    else:
        print(f"\n⚠️  {remaining_issues} issues remain")
    
    print("\nNow test with:")
    print("  python3 framework/scripts/test_all_mermaid_comprehensive.py")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())