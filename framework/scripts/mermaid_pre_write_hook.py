#!/usr/bin/env python3
"""
Mermaid Pre-Write Hook
Validates and fixes Mermaid content BEFORE writing to files
This ensures no broken diagrams are ever written
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_mermaid_validator import MermaidValidator

def ensure_valid_mermaid(content: str, file_path: str = None) -> str:
    """
    Ensures Mermaid content is valid before writing
    
    Args:
        content: The Mermaid diagram content or markdown with diagrams
        file_path: Optional file path for context (helps determine if .md or .mmd)
    
    Returns:
        Fixed and validated content
    
    Raises:
        ValueError: If content cannot be fixed after maximum attempts
    """
    validator = MermaidValidator()
    
    # Apply basic fixes first
    content = validator.apply_basic_fixes(content)
    
    # Determine if this is standalone Mermaid or embedded
    is_mermaid_file = file_path and file_path.endswith('.mmd')
    
    if is_mermaid_file or (not file_path and not '```' in content):
        # Standalone Mermaid diagram
        fixed_content, is_valid, errors = validator.validate_and_fix(content)
        
        if not is_valid:
            error_msg = f"Cannot fix Mermaid diagram"
            if file_path:
                error_msg += f" for {file_path}"
            error_msg += f": {'; '.join(errors[:3])}"
            raise ValueError(error_msg)
        
        return fixed_content
    else:
        # Markdown with embedded diagrams
        diagrams = validator.extract_diagrams(content, file_path or 'content.md')
        
        if not diagrams:
            # No Mermaid content, return as-is
            return content
        
        # Fix each diagram
        fixed_content = content
        for diagram in diagrams:
            original = diagram['content']
            fixed, is_valid, errors = validator.validate_and_fix(original)
            
            if not is_valid:
                error_msg = f"Cannot fix Mermaid diagram at line {diagram['line_start']}"
                if file_path:
                    error_msg += f" in {file_path}"
                error_msg += f": {'; '.join(errors[:3])}"
                raise ValueError(error_msg)
            
            # Replace in content if changed
            if fixed != original:
                # Replace all occurrences of this exact diagram
                old_block = f'```mermaid\n{original}\n```'
                new_block = f'```mermaid\n{fixed}\n```'
                fixed_content = fixed_content.replace(old_block, new_block)
                
                old_block = f'```mmd\n{original}\n```'
                new_block = f'```mmd\n{fixed}\n```'
                fixed_content = fixed_content.replace(old_block, new_block)
        
        return fixed_content

def validate_mermaid_file(file_path: str) -> bool:
    """
    Validates a Mermaid file and returns True if valid or fixable
    
    Args:
        file_path: Path to the file to validate
    
    Returns:
        True if file is valid or was successfully fixed
        False if file has unfixable errors
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fixed_content = ensure_valid_mermaid(content, file_path)
        
        # Write back if changed
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"Fixed: {file_path}")
        
        return True
    except ValueError as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error with {file_path}: {e}")
        return False

def main():
    """Main function for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: mermaid_pre_write_hook.py <file_or_content>")
        print("  If argument is a file path, validates and fixes the file")
        print("  Otherwise, validates the content and outputs fixed version")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    # Check if it's a file
    if os.path.isfile(arg):
        success = validate_mermaid_file(arg)
        sys.exit(0 if success else 1)
    else:
        # Treat as content
        try:
            fixed = ensure_valid_mermaid(arg)
            print(fixed)
            sys.exit(0)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()