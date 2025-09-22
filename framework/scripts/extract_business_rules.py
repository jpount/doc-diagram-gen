#!/usr/bin/env python3
"""
Deterministic Business Rule Extraction from Repomix Summary
Produces consistent results every time for the same input.
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import argparse


class BusinessRuleExtractor:
    """Extract business rules deterministically from Repomix summary"""

    def __init__(self):
        # Define exact patterns for different rule types
        self.patterns = {
            'financial': [
                (r'BigDecimal.*?\.(add|subtract|multiply|divide)\(', 'BigDecimal calculation'),
                (r'(price|fee|tax|total|balance|amount)\s*=.*?[+\-*/]', 'Financial arithmetic'),
                (r'(calculate|compute)(Price|Fee|Tax|Total|Balance|Amount)', 'Financial calculation method'),
            ],
            'state': [
                (r'setStatus\s*\(["\']([^"\']+)["\']', 'Status change'),
                (r'setState\s*\(["\']([^"\']+)["\']', 'State change'),
                (r'(status|state)\s*=\s*["\']([^"\']+)["\']', 'Direct state assignment'),
                (r'order\.(complete|cancel|approve|reject)\(\)', 'Order state transition'),
            ],
            'validation': [
                (r'(validate|verify|check)[A-Z]\w*\s*\(', 'Validation method'),
                (r'if\s*\([^)]*>[^)]*limit[^)]*\)', 'Limit validation'),
                (r'if\s*\([^)]*<[^)]*minimum[^)]*\)', 'Minimum validation'),
                (r'throw\s+new\s+\w*(Invalid|Validation|Business)Exception', 'Validation exception'),
            ],
            'operation': [
                (r'\b(buy|sell|trade)\s*\(', 'Trading operation'),
                (r'(create|update|delete)(Order|Trade|Account|User)\s*\(', 'CRUD operation'),
                (r'(approve|reject|cancel|process)[A-Z]\w*\s*\(', 'Business process operation'),
                (r'(placeOrder|submitOrder|executeOrder)\s*\(', 'Order operation'),
            ]
        }

    def parse_repomix(self, content: str) -> Dict[str, List[str]]:
        """Parse Repomix content into file sections"""
        files = {}
        current_file = None
        current_lines = []

        for line in content.split('\n'):
            # Check for file header
            if line.startswith('## File:') or line.startswith('File:'):
                # Save previous file
                if current_file:
                    files[current_file] = current_lines
                # Start new file
                current_file = line.replace('## File:', '').replace('File:', '').strip()
                current_lines = []
            elif current_file:
                current_lines.append(line)

        # Save last file
        if current_file:
            files[current_file] = current_lines

        return files

    def extract_methods(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract method definitions from code lines"""
        methods = []

        for i, line in enumerate(lines):
            # Look for method signatures (Java-focused for Daytrader)
            method_pattern = r'(public|private|protected)\s+[\w\<\>\[\]]+\s+(\w+)\s*\([^)]*\)'
            match = re.search(method_pattern, line)

            if match:
                method_name = match.group(2)

                # Skip simple getters/setters
                if method_name.startswith('get') or method_name.startswith('set'):
                    if i + 2 < len(lines) and 'return' in lines[i + 1]:
                        continue  # Simple getter
                    if i + 2 < len(lines) and 'this.' in lines[i + 1] and '=' in lines[i + 1]:
                        continue  # Simple setter

                # Get method body (next 20 lines or until next method)
                body_lines = []
                brace_count = 0
                method_started = False

                for j in range(i, min(i + 50, len(lines))):
                    body_lines.append(lines[j])

                    if '{' in lines[j]:
                        brace_count += lines[j].count('{')
                        method_started = True
                    if '}' in lines[j]:
                        brace_count -= lines[j].count('}')

                    if method_started and brace_count == 0:
                        break

                # Extract first 10-15 lines of method body for code snippet
                code_snippet_lines = [line.strip()]
                code_snippet_lines.extend(body_lines[:15] if len(body_lines) > 15 else body_lines)
                code_snippet = '\n'.join(code_snippet_lines)

                methods.append({
                    'name': method_name,
                    'signature': line.strip(),
                    'line_num': i + 1,
                    'body': '\n'.join(body_lines),
                    'code_snippet': code_snippet  # Store snippet for catalog
                })

        return methods

    def apply_patterns(self, method: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply patterns to identify business rules in a method"""
        rules = []

        for rule_type, patterns in self.patterns.items():
            for pattern, description in patterns:
                if re.search(pattern, method['body'], re.IGNORECASE):
                    # Generate deterministic ID based on content
                    rule_id = self.generate_rule_id(method['name'], rule_type, method['line_num'])

                    rules.append({
                        'id': rule_id,
                        'type': rule_type,
                        'description': description,
                        'method': method['name'],
                        'signature': method['signature'],
                        'line': method['line_num'],
                        'pattern_matched': pattern[:50] + '...' if len(pattern) > 50 else pattern,
                        'code_snippet': method.get('code_snippet', '')  # Include code snippet
                    })
                    break  # Only count each method once per category

        return rules

    def generate_rule_id(self, method_name: str, rule_type: str, line_num: int) -> str:
        """Generate deterministic rule ID"""
        # Create hash of method+type+line for consistency
        content = f"{method_name}:{rule_type}:{line_num}"
        hash_val = hashlib.md5(content.encode()).hexdigest()[:6]
        return f"BR-{hash_val}"

    def extract(self, repomix_path: str) -> Dict[str, Any]:
        """Main extraction method"""
        # Read Repomix content
        with open(repomix_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse into files
        files = self.parse_repomix(content)

        all_rules = []
        file_count = 0
        method_count = 0

        # Process each file
        for file_path, lines in files.items():
            # Skip non-Java files for now (can be extended)
            if not file_path.endswith('.java'):
                continue

            file_count += 1
            methods = self.extract_methods(lines)
            method_count += len(methods)

            # Extract rules from each method
            for method in methods:
                method_rules = self.apply_patterns(method)
                for rule in method_rules:
                    rule['file'] = file_path
                    all_rules.append(rule)

        # Sort and assign sequential IDs
        all_rules.sort(key=lambda x: (x['file'], x['line']))
        for i, rule in enumerate(all_rules, 1):
            rule['id'] = f"BR-{i:03d}"

        # Create summary
        summary = {
            'financial': len([r for r in all_rules if r['type'] == 'financial']),
            'state': len([r for r in all_rules if r['type'] == 'state']),
            'validation': len([r for r in all_rules if r['type'] == 'validation']),
            'operation': len([r for r in all_rules if r['type'] == 'operation']),
        }

        return {
            'extraction_timestamp': datetime.now().isoformat(),
            'source_file': repomix_path,
            'files_analyzed': file_count,
            'methods_analyzed': method_count,
            'total_rules_found': len(all_rules),
            'summary': summary,
            'rules': all_rules
        }


def main():
    parser = argparse.ArgumentParser(description='Extract business rules from Repomix summary')
    parser.add_argument('--input', '-i', default='output/reports/repomix-summary.md',
                        help='Path to Repomix summary file')
    parser.add_argument('--output', '-o', default='output/context/business-rules-extracted.json',
                        help='Output JSON file path')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    # Check input file exists
    if not Path(args.input).exists():
        print(f"❌ Error: Input file not found: {args.input}")
        return 1

    # Extract rules
    extractor = BusinessRuleExtractor()
    results = extractor.extract(args.input)

    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print(f"✅ Business Rule Extraction Complete")
    print(f"   Source: {args.input}")
    print(f"   Output: {args.output}")
    print(f"   Files analyzed: {results['files_analyzed']}")
    print(f"   Methods analyzed: {results['methods_analyzed']}")
    print(f"   Total rules found: {results['total_rules_found']}")
    print(f"   - Financial: {results['summary']['financial']}")
    print(f"   - State: {results['summary']['state']}")
    print(f"   - Validation: {results['summary']['validation']}")
    print(f"   - Operation: {results['summary']['operation']}")

    if args.verbose:
        print("\nFirst 5 rules found:")
        for rule in results['rules'][:5]:
            print(f"  {rule['id']}: {rule['method']} ({rule['type']}) - {rule['description']}")

    return 0


if __name__ == '__main__':
    exit(main())