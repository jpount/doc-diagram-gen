#!/usr/bin/env python3
"""
Universal Mermaid Pre-Write Validation Hook
============================================
This hook automatically validates and fixes ALL Mermaid diagrams
before they are written by ANY agent.

This ensures that all agents (performance-analyst, security-analyst, 
business-logic-analyst, etc.) produce valid Mermaid diagrams.
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Tuple, Optional

# Add framework scripts to path
framework_path = Path(__file__).parent.parent.parent / 'framework' / 'scripts'
sys.path.insert(0, str(framework_path))

try:
    from ultimate_mermaid_validator import UltimateMermaidValidator, ValidationStage
except ImportError:
    print("Warning: Could not import ultimate_mermaid_validator", file=sys.stderr)
    UltimateMermaidValidator = None


class UniversalMermaidHook:
    """
    Universal hook that validates and fixes Mermaid diagrams
    for ALL agents before writing
    """
    
    # Common issues seen across different agents
    COMMON_FIXES = {
        # Performance-analyst specific
        r'\\<br/\\>': '<br/>',  # Fix escaped HTML breaks
        r'<br/\>': '<br/>',  # Ensure proper HTML breaks
        
        # Critical-findings-summary and others
        r'graph LR\s*\n': 'graph LR\n',  # Remove trailing spaces
        r'--+>': '-->',  # Fix multiple dashes in arrows
        r'--\s+>': '-->',  # Fix spaces in arrows
        
        # Security-analyst specific
        r'participant\s+([^"\n]+\s+[^"\n]+)$': r'participant "\1"',  # Quote multi-word participants
        
        # Business-logic-analyst specific
        r'Note\s+over\s+(\w+)\s*:\s{2,}': r'Note over \1: ',  # Fix multiple spaces after colon
        r'Note\s+(right|left)\s+of\s+(\w+)\s*:\s{2,}': r'Note \1 of \2: ',
        
        # All agents - comment indentation
        r'^\s+%%': '%%',  # Comments must start at column 1
        
        # All agents - stereotypes
        r'<<@(\w+)>>': r'<<\1>>',  # Remove @ from stereotypes
    }
    
    def __init__(self):
        self.validator = UltimateMermaidValidator() if UltimateMermaidValidator else None
        self.stats = {
            'files_processed': 0,
            'diagrams_fixed': 0,
            'errors_prevented': 0
        }
    
    def validate_content(self, content: str, filepath: str) -> Tuple[str, bool]:
        """
        Validate and fix content before writing
        
        Args:
            content: The content to validate
            filepath: The intended file path
            
        Returns:
            (fixed_content, had_issues)
        """
        if not content or not filepath:
            return content, False
        
        # Only process files that might contain Mermaid
        if not (filepath.endswith('.md') or filepath.endswith('.mmd')):
            return content, False
        
        self.stats['files_processed'] += 1
        had_issues = False
        
        # Apply common fixes first
        fixed_content = self._apply_common_fixes(content)
        if fixed_content != content:
            had_issues = True
            self.stats['errors_prevented'] += 1
        
        # Then use the validator if available
        if self.validator:
            if filepath.endswith('.md'):
                fixed_content = self._validate_markdown(fixed_content, filepath)
            elif filepath.endswith('.mmd'):
                fixed_content = self._validate_mermaid(fixed_content, filepath)
            
            if fixed_content != content:
                had_issues = True
                self.stats['diagrams_fixed'] += 1
        
        return fixed_content, had_issues
    
    def _apply_common_fixes(self, content: str) -> str:
        """Apply common regex fixes to content"""
        for pattern, replacement in self.COMMON_FIXES.items():
            # Handle multiline patterns
            if pattern.startswith('^'):
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            else:
                content = re.sub(pattern, replacement, content)
        
        # Fix escaped characters in diagrams
        if '```mermaid' in content or '```mmd' in content:
            # Within mermaid blocks, fix common escaping issues
            def fix_mermaid_block(match):
                block = match.group(1)
                # Fix escaped HTML
                block = block.replace('\\<br/\\>', '<br/>')
                block = block.replace('\\<br\\>', '<br/>')
                block = block.replace('\<br/\>', '<br/>')
                # Fix escaped quotes
                block = block.replace('\\"', '"')
                # Fix node IDs with spaces
                block = re.sub(r'(\w+)\s+(\w+)\[', r'\1_\2[', block)
                return f'```mermaid\n{block}\n```'
            
            content = re.sub(r'```(?:mermaid|mmd)\s*\n(.*?)\n```', 
                           fix_mermaid_block, content, flags=re.DOTALL)
        
        return content
    
    def _validate_markdown(self, content: str, filepath: str) -> str:
        """Validate markdown file with embedded Mermaid"""
        pattern = r'```(?:mermaid|mmd)\s*\n(.*?)\n```'
        
        def fix_diagram(match):
            diagram = match.group(1)
            try:
                fixed_diagram, _, _ = self.validator.validate_and_fix(
                    diagram, 
                    os.path.basename(filepath), 
                    ValidationStage.PRE_GENERATION
                )
                return f'```mermaid\n{fixed_diagram}\n```'
            except Exception as e:
                print(f"Warning: Failed to validate diagram: {e}", file=sys.stderr)
                return match.group(0)
        
        return re.sub(pattern, fix_diagram, content, flags=re.DOTALL)
    
    def _validate_mermaid(self, content: str, filepath: str) -> str:
        """Validate pure Mermaid file"""
        try:
            fixed_content, _, _ = self.validator.validate_and_fix(
                content,
                os.path.basename(filepath),
                ValidationStage.PRE_GENERATION
            )
            return fixed_content
        except Exception as e:
            print(f"Warning: Failed to validate Mermaid file: {e}", file=sys.stderr)
            return content
    
    def get_stats(self) -> dict:
        """Get validation statistics"""
        return self.stats.copy()


# Global hook instance
_hook = UniversalMermaidHook()


def pre_write_hook(content: str, filepath: str) -> str:
    """
    Main hook function called before any file write
    
    This function should be called by all agents before writing
    any file that might contain Mermaid diagrams.
    
    Args:
        content: The content to be written
        filepath: The target file path
        
    Returns:
        Fixed content ready to write
    """
    fixed_content, had_issues = _hook.validate_content(content, filepath)
    
    if had_issues:
        print(f"✅ Fixed Mermaid issues in: {os.path.basename(filepath)}")
    
    return fixed_content


def validate_file_content(content: str, filepath: str) -> Tuple[str, bool]:
    """
    Validate content and return both fixed content and validation status
    
    Args:
        content: The content to validate
        filepath: The file path (for context)
        
    Returns:
        (fixed_content, is_valid)
    """
    fixed_content, had_issues = _hook.validate_content(content, filepath)
    return fixed_content, not had_issues


def get_validation_stats() -> dict:
    """Get statistics about validations performed"""
    return _hook.get_stats()


# For command-line testing
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python mermaid_pre_write_validation.py <file_or_content>")
        sys.exit(1)
    
    input_arg = sys.argv[1]
    
    # Check if it's a file or direct content
    if os.path.exists(input_arg):
        # It's a file
        with open(input_arg, 'r', encoding='utf-8') as f:
            content = f.read()
        filepath = input_arg
    else:
        # It's direct content
        content = input_arg
        filepath = "test.md"
    
    # Validate and fix
    fixed_content = pre_write_hook(content, filepath)
    
    # Output result
    print("\n" + "="*60)
    print("FIXED CONTENT:")
    print("="*60)
    print(fixed_content)
    
    # Show stats
    stats = get_validation_stats()
    print("\n" + "="*60)
    print("STATISTICS:")
    print("="*60)
    for key, value in stats.items():
        print(f"{key}: {value}")