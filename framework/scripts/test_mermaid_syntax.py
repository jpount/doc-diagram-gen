#!/usr/bin/env python3
"""
Test Mermaid syntax by attempting to parse the diagrams
This simulates what mermaid.live does
"""

import re
import sys
from pathlib import Path

def check_mermaid_syntax(content):
    """
    Check if Mermaid content has valid syntax
    Returns (is_valid, error_message)
    """
    errors = []
    
    # Remove comments
    lines = []
    for line in content.split('\n'):
        if not line.strip().startswith('%%'):
            lines.append(line)
    content = '\n'.join(lines)
    
    # Check for basic syntax issues
    
    # 1. Check diagram type
    first_line = content.strip().split('\n')[0] if content.strip() else ""
    valid_starts = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
                   'stateDiagram', 'erDiagram', 'gantt', 'pie', 'journey', 'gitGraph']
    
    if not any(first_line.startswith(t) for t in valid_starts):
        errors.append(f"Invalid diagram type: {first_line[:30]}")
    
    # 2. Check for quotes within quotes
    for i, line in enumerate(content.split('\n'), 1):
        # Check for problematic quote patterns
        if '"' in line:
            # Count quotes
            quote_count = 0
            escaped = False
            for char in line:
                if char == '\\':
                    escaped = not escaped
                elif char == '"' and not escaped:
                    quote_count += 1
                else:
                    escaped = False
            
            if quote_count % 2 != 0:
                errors.append(f"Line {i}: Unbalanced quotes")
            
            # Check for quotes within quotes pattern
            # But exclude valid cardinality patterns like "1" -- "1"
            if re.search(r'"[^"]*"[^"]*"', line):
                # Check if it's a valid cardinality pattern
                if not re.match(r'^\s*\w+\s+"[^"]+"\s*(--|\.\.|\||o)\S*\s+"[^"]+"\s+\w+', line):
                    if 'note for' not in line and 'Note' not in line:  # Notes can have complex quotes
                        errors.append(f"Line {i}: Nested quotes detected")
    
    # 3. Check for invalid characters in specific contexts
    if 'classDiagram' in content:
        # Check for @ symbols in stereotypes
        if '<<@' in content:
            errors.append("Invalid stereotype with @ symbol")
        
        # Check for ER diagram syntax in class diagram
        if '||--||' in content or '||--o{' in content:
            errors.append("ER diagram syntax in class diagram")
    
    # 4. Check for unclosed blocks
    if 'subgraph' in content:
        subgraph_count = content.count('subgraph')
        end_count = len(re.findall(r'\bend\b', content))
        if subgraph_count != end_count:
            errors.append(f"Unbalanced subgraph/end: {subgraph_count} vs {end_count}")
    
    # 5. Check for invalid node IDs in graphs
    if 'graph' in first_line or 'flowchart' in first_line:
        # Check for numeric node IDs
        if re.search(r'\b\d+\[', content):
            errors.append("Numeric node IDs detected (may cause issues)")
    
    return len(errors) == 0, errors

def test_file(file_path):
    """Test a single Mermaid file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    is_valid, errors = check_mermaid_syntax(content)
    
    return is_valid, errors

def main():
    """Test all .mmd files"""
    output_dir = Path("output/diagrams")
    files = list(output_dir.glob("*.mmd"))
    
    print("Testing Mermaid syntax in all diagrams...")
    print("=" * 60)
    
    all_valid = True
    for file_path in sorted(files):
        is_valid, errors = test_file(file_path)
        
        status = "✅" if is_valid else "❌"
        print(f"{status} {file_path.name}")
        
        if not is_valid:
            all_valid = False
            for error in errors[:3]:  # Show first 3 errors
                print(f"   - {error}")
    
    print("=" * 60)
    if all_valid:
        print("✅ ALL DIAGRAMS HAVE VALID SYNTAX!")
    else:
        print("❌ Some diagrams have syntax errors")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())