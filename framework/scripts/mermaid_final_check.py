#!/usr/bin/env python3
"""
Mermaid Final Check and Fix
Final validation pass for all Mermaid diagrams in the project
Run this after all generation is complete to ensure everything works
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smart_mermaid_validator import MermaidValidator, validate_file

def check_mmdc_available() -> bool:
    """Check if Mermaid CLI is available"""
    try:
        result = subprocess.run(['which', 'mmdc'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
        
        # Try npx
        result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def final_check_and_fix(directory: str = 'output', auto_fix: bool = True) -> Dict:
    """
    Perform final check and fix on all Mermaid diagrams
    
    Args:
        directory: Directory to check (default: output)
        auto_fix: Whether to automatically fix issues (default: True)
    
    Returns:
        Dictionary with results summary
    """
    validator = MermaidValidator()
    results = {
        'total_files': 0,
        'valid_files': 0,
        'fixed_files': 0,
        'failed_files': 0,
        'files': []
    }
    
    # Check if mmdc is available
    if not check_mmdc_available():
        print("⚠️  Warning: Mermaid CLI (mmdc) not found. Install with:")
        print("   npm install -g @mermaid-js/mermaid-cli")
        print("   Falling back to basic validation only.\n")
    
    # Find all files with Mermaid content
    path = Path(directory)
    files_to_check = []
    
    if path.is_dir():
        files_to_check.extend(path.glob('**/*.md'))
        files_to_check.extend(path.glob('**/*.mmd'))
    elif path.is_file() and path.suffix in ['.md', '.mmd']:
        files_to_check.append(path)
    else:
        print(f"Error: {directory} is not a valid directory or file")
        return results
    
    if not files_to_check:
        print("No .md or .mmd files found")
        return results
    
    print(f"🔍 Checking {len(files_to_check)} files for Mermaid diagrams...\n")
    
    # Process each file
    for file_path in sorted(files_to_check):
        results['total_files'] += 1
        file_result = validate_file(str(file_path), validator, auto_fix=auto_fix)
        
        # Display result
        if file_result['valid']:
            if file_result['fixed']:
                print(f"✅ 🔧 {file_path.relative_to(Path.cwd()) if file_path.is_absolute() else file_path}")
                results['fixed_files'] += 1
            else:
                print(f"✅    {file_path.relative_to(Path.cwd()) if file_path.is_absolute() else file_path}")
            results['valid_files'] += 1
        else:
            print(f"❌    {file_path.relative_to(Path.cwd()) if file_path.is_absolute() else file_path}")
            for error in file_result['errors'][:2]:  # Show first 2 errors
                print(f"      └─ {error[:80]}...")
            results['failed_files'] += 1
        
        # Store detailed result
        results['files'].append({
            'path': str(file_path),
            'valid': file_result['valid'],
            'fixed': file_result.get('fixed', False),
            'errors': file_result.get('errors', [])
        })
    
    # Print summary
    print("\n" + "="*60)
    print("📊 FINAL CHECK SUMMARY")
    print("="*60)
    print(f"Total files checked:  {results['total_files']}")
    print(f"Valid files:         {results['valid_files']} ✅")
    print(f"Fixed files:         {results['fixed_files']} 🔧")
    print(f"Failed files:        {results['failed_files']} ❌")
    
    if results['failed_files'] > 0:
        print("\n⚠️  Some files still have errors. Review the errors above.")
        print("   You may need to manually fix complex issues.")
    else:
        print("\n🎉 All Mermaid diagrams are valid!")
    
    # Save detailed report
    report_path = Path(directory) / 'mermaid_final_check_report.json'
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    # Test with browser if all valid
    if results['failed_files'] == 0:
        print("\n💡 TIP: Test diagrams visually by opening:")
        print(f"   framework/document-viewer.html")
        print(f"   Then load the '{directory}' directory")
    
    return results

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Final check and fix for all Mermaid diagrams',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Check and fix all diagrams in output/
  %(prog)s --no-fix          # Check only, don't fix
  %(prog)s docs/             # Check diagrams in docs/ directory
  %(prog)s output/diagrams/  # Check specific subdirectory
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        default='output',
        help='Directory to check (default: output)'
    )
    
    parser.add_argument(
        '--no-fix',
        action='store_true',
        help="Don't automatically fix issues, only report them"
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON only'
    )
    
    args = parser.parse_args()
    
    # Run final check
    results = final_check_and_fix(
        directory=args.directory,
        auto_fix=not args.no_fix
    )
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    # Exit with error code if there are failures
    sys.exit(1 if results['failed_files'] > 0 else 0)

if __name__ == '__main__':
    main()