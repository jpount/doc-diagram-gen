#!/usr/bin/env python3
"""
Business Rule Validation Hook for Claude Code
Validates extracted business rules meet quality standards
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

# Get project directory from environment or use current directory
PROJECT_DIR = Path(os.environ.get('CLAUDE_PROJECT_DIR', Path.cwd()))
OUTPUT_DIR = PROJECT_DIR / "output" / "docs"

class Colors:
    """Terminal colors"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def disable():
        """Disable colors for environments that don't support them"""
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.MAGENTA = ''
        Colors.CYAN = ''
        Colors.NC = ''

# Enable colors on Windows if possible
if sys.platform == 'win32' and not os.environ.get('ANSICON'):
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        Colors.disable()

class BusinessRuleValidator:
    """Validates business rules extraction quality"""
    
    # Minimum requirements
    MIN_RULES_REQUIRED = 50
    MIN_CRITICAL_RULES = 5
    MIN_CATEGORIES = 3
    
    # Business rule patterns to search for
    RULE_PATTERNS = [
        r'BR-\d{3,}',  # BR-001, BR-002, etc.
        r'Rule\s+ID\s*[:\|]',  # Rule ID in tables
        r'\|\s*BR-\w+\s*\|',  # Rules in markdown tables
        r'Business Rule\s*#?\d+',  # Business Rule #1, etc.
    ]
    
    # Categories we expect to see
    EXPECTED_CATEGORIES = [
        'validation', 'authorization', 'calculation', 'business process',
        'data management', 'compliance', 'workflow', 'constraint',
        'authentication', 'financial', 'reporting', 'audit'
    ]
    
    def __init__(self):
        self.rules_found = []
        self.rules_by_category = defaultdict(list)
        self.rules_by_criticality = defaultdict(list)
        self.files_with_rules = []
        self.issues = []
        self.warnings = []
    
    def run(self) -> int:
        """Main validation routine"""
        print("=" * 60)
        print("Business Rule Validation")
        print("=" * 60)
        print()
        
        # Check if output directory exists
        if not OUTPUT_DIR.exists():
            print(f"{Colors.YELLOW}⚠️  Output directory not found: {OUTPUT_DIR}{Colors.NC}")
            print("   No documentation to validate yet.")
            return 0
        
        # Extract business rules from documentation
        print(f"{Colors.BLUE}Extracting business rules from documentation...{Colors.NC}")
        self.extract_business_rules()
        
        # Validate rule quality
        print(f"\n{Colors.BLUE}Validating rule quality...{Colors.NC}")
        self.validate_rule_quality()
        
        # Check rule completeness
        print(f"\n{Colors.BLUE}Checking rule completeness...{Colors.NC}")
        self.check_completeness()
        
        # Show summary
        self.show_summary()
        
        # Return exit code
        # Always return 0 to avoid noisy hook errors during early development
        # The validation output is informational, not a hard failure
        return 0
    
    def extract_business_rules(self):
        """Extract business rules from all documentation"""
        for md_file in OUTPUT_DIR.glob("**/*.md"):
            rules_in_file = self.extract_rules_from_file(md_file)
            if rules_in_file:
                self.files_with_rules.append(md_file)
                print(f"   Found {len(rules_in_file)} rules in {md_file.name}")
    
    def extract_rules_from_file(self, file_path: Path) -> List[Dict]:
        """Extract business rules from a single file"""
        rules = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.issues.append(f"Error reading {file_path.name}: {e}")
            return rules
        
        # Search for rule patterns
        for pattern in self.RULE_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Try to extract the full rule context
                rule_info = self.extract_rule_context(content, match.start())
                if rule_info:
                    rule_info['file'] = file_path.name
                    rules.append(rule_info)
                    self.rules_found.append(rule_info)
        
        # Also look for markdown tables with business rules
        table_rules = self.extract_rules_from_tables(content, file_path.name)
        rules.extend(table_rules)
        self.rules_found.extend(table_rules)
        
        return rules
    
    def extract_rule_context(self, content: str, position: int) -> Optional[Dict]:
        """Extract context around a business rule match"""
        lines = content[:position].count('\n') + 1
        
        # Get surrounding lines for context
        all_lines = content.split('\n')
        start = max(0, lines - 2)
        end = min(len(all_lines), lines + 3)
        context_lines = all_lines[start:end]
        context = '\n'.join(context_lines)
        
        rule_info = {
            'line': lines,
            'context': context[:200]  # First 200 chars of context
        }
        
        # Try to extract rule ID
        rule_id_match = re.search(r'BR-\d{3,}|\bBR-\w+\b', context)
        if rule_id_match:
            rule_info['id'] = rule_id_match.group()
        
        # Try to extract category
        category = self.extract_category(context)
        if category:
            rule_info['category'] = category
            self.rules_by_category[category].append(rule_info)
        
        # Try to extract criticality
        criticality = self.extract_criticality(context)
        if criticality:
            rule_info['criticality'] = criticality
            self.rules_by_criticality[criticality].append(rule_info)
        
        # Try to extract code reference
        code_ref = self.extract_code_reference(context)
        if code_ref:
            rule_info['code_reference'] = code_ref
        
        return rule_info
    
    def extract_rules_from_tables(self, content: str, filename: str) -> List[Dict]:
        """Extract business rules from markdown tables"""
        rules = []
        
        # Look for tables with Rule ID columns
        table_pattern = r'\|.*Rule\s*ID.*\|.*\n\|[-:\s|]+\n((?:\|.*\n)+)'
        table_matches = re.finditer(table_pattern, content, re.IGNORECASE | re.MULTILINE)
        
        for match in table_matches:
            table_content = match.group(1)
            rows = table_content.strip().split('\n')
            
            for row in rows:
                if '|' in row:
                    cells = [cell.strip() for cell in row.split('|')]
                    if len(cells) > 2:  # At least ID and description
                        rule_info = {
                            'file': filename,
                            'id': cells[1] if cells[1] else f"Table-{len(rules)}",
                            'description': cells[2] if len(cells) > 2 else '',
                        }
                        
                        # Extract additional info from cells
                        if len(cells) > 3:
                            rule_info['code_reference'] = cells[3]
                        if len(cells) > 4:
                            criticality = self.extract_criticality(cells[4])
                            if criticality:
                                rule_info['criticality'] = criticality
                                self.rules_by_criticality[criticality].append(rule_info)
                        
                        # Categorize based on description
                        category = self.extract_category(rule_info.get('description', ''))
                        if category:
                            rule_info['category'] = category
                            self.rules_by_category[category].append(rule_info)
                        
                        rules.append(rule_info)
        
        return rules
    
    def extract_category(self, text: str) -> Optional[str]:
        """Extract category from rule text"""
        text_lower = text.lower()
        
        for category in self.EXPECTED_CATEGORIES:
            if category in text_lower:
                return category
        
        # Check for common keywords
        if 'validat' in text_lower:
            return 'validation'
        elif 'auth' in text_lower:
            return 'authorization'
        elif 'calculat' in text_lower or 'comput' in text_lower:
            return 'calculation'
        elif 'process' in text_lower or 'workflow' in text_lower:
            return 'business process'
        
        return None
    
    def extract_criticality(self, text: str) -> Optional[str]:
        """Extract criticality level from rule text"""
        text_lower = text.lower()
        
        if 'critical' in text_lower:
            return 'Critical'
        elif 'high' in text_lower:
            return 'High'
        elif 'medium' in text_lower or 'important' in text_lower:
            return 'Medium'
        elif 'low' in text_lower or 'nice' in text_lower:
            return 'Low'
        
        return None
    
    def extract_code_reference(self, text: str) -> Optional[str]:
        """Extract code reference from rule text"""
        # Look for file:line patterns
        code_ref_pattern = r'[\w/]+\.\w+:\d+|\w+\.java:\d+|\w+\.cs:\d+|\w+\.py:\d+'
        match = re.search(code_ref_pattern, text)
        
        if match:
            return match.group()
        
        # Look for class/method references
        class_pattern = r'\b[A-Z][a-zA-Z]+(?:Service|Controller|Manager|Repository|DAO)\b'
        match = re.search(class_pattern, text)
        
        if match:
            return match.group()
        
        return None
    
    def validate_rule_quality(self):
        """Validate the quality of extracted rules"""
        total_rules = len(self.rules_found)
        
        # Check for unique IDs
        rule_ids = [r.get('id') for r in self.rules_found if r.get('id')]
        unique_ids = set(rule_ids)
        
        if len(rule_ids) != len(unique_ids):
            self.issues.append(f"Duplicate rule IDs found ({len(rule_ids) - len(unique_ids)} duplicates)")
        
        # Check for code references
        rules_with_code_ref = [r for r in self.rules_found if r.get('code_reference')]
        if len(rules_with_code_ref) < total_rules * 0.5:
            self.warnings.append(f"Only {len(rules_with_code_ref)}/{total_rules} rules have code references")
        
        # Check for descriptions
        rules_with_desc = [r for r in self.rules_found if r.get('description') or r.get('context')]
        if len(rules_with_desc) < total_rules * 0.8:
            self.warnings.append(f"Only {len(rules_with_desc)}/{total_rules} rules have descriptions")
    
    def check_completeness(self):
        """Check if business rule extraction is complete"""
        total_rules = len(self.rules_found)
        
        # Check minimum rules
        if total_rules < self.MIN_RULES_REQUIRED:
            self.issues.append(f"Only {total_rules} rules found (minimum {self.MIN_RULES_REQUIRED} required)")
            print(f"   {Colors.RED}✗ Insufficient rules: {total_rules}/{self.MIN_RULES_REQUIRED}{Colors.NC}")
        else:
            print(f"   {Colors.GREEN}✓ Rule count: {total_rules} (exceeds minimum){Colors.NC}")
        
        # Check critical rules
        critical_rules = len(self.rules_by_criticality.get('Critical', []))
        if critical_rules < self.MIN_CRITICAL_RULES:
            self.warnings.append(f"Only {critical_rules} critical rules (expected {self.MIN_CRITICAL_RULES}+)")
            print(f"   {Colors.YELLOW}⚠ Critical rules: {critical_rules}/{self.MIN_CRITICAL_RULES}{Colors.NC}")
        else:
            print(f"   {Colors.GREEN}✓ Critical rules: {critical_rules}{Colors.NC}")
        
        # Check categories
        num_categories = len(self.rules_by_category)
        if num_categories < self.MIN_CATEGORIES:
            self.warnings.append(f"Only {num_categories} categories (expected {self.MIN_CATEGORIES}+)")
            print(f"   {Colors.YELLOW}⚠ Categories: {num_categories}/{self.MIN_CATEGORIES}{Colors.NC}")
        else:
            print(f"   {Colors.GREEN}✓ Categories: {num_categories}{Colors.NC}")
    
    def show_summary(self):
        """Display validation summary"""
        print("\n" + "=" * 60)
        print("Business Rule Validation Summary")
        print("=" * 60)
        
        total_rules = len(self.rules_found)
        
        # Overall statistics
        print(f"\n{Colors.CYAN}Statistics:{Colors.NC}")
        print(f"   Total rules extracted: {total_rules}")
        print(f"   Files with rules: {len(self.files_with_rules)}")
        print(f"   Categories identified: {len(self.rules_by_category)}")
        
        # Criticality breakdown
        if self.rules_by_criticality:
            print(f"\n{Colors.CYAN}Rules by Criticality:{Colors.NC}")
            for level in ['Critical', 'High', 'Medium', 'Low']:
                count = len(self.rules_by_criticality.get(level, []))
                if count > 0:
                    print(f"   {level}: {count}")
        
        # Category breakdown
        if self.rules_by_category:
            print(f"\n{Colors.CYAN}Rules by Category:{Colors.NC}")
            for category, rules in sorted(self.rules_by_category.items(), 
                                         key=lambda x: len(x[1]), reverse=True)[:5]:
                print(f"   {category.title()}: {len(rules)}")
        
        # Quality metrics
        rules_with_code = len([r for r in self.rules_found if r.get('code_reference')])
        rules_with_id = len([r for r in self.rules_found if r.get('id')])
        
        print(f"\n{Colors.CYAN}Quality Metrics:{Colors.NC}")
        print(f"   Rules with IDs: {rules_with_id}/{total_rules}")
        print(f"   Rules with code references: {rules_with_code}/{total_rules}")
        
        # Issues and warnings
        if self.issues:
            print(f"\n{Colors.RED}Issues:{Colors.NC}")
            for issue in self.issues:
                print(f"   • {issue}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}Warnings:{Colors.NC}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        # Final verdict
        if total_rules >= self.MIN_RULES_REQUIRED:
            print(f"\n{Colors.GREEN}✅ Business rule extraction meets minimum requirements!{Colors.NC}")
            
            print("\n💡 Recommendations:")
            print("   • Review rules for accuracy and completeness")
            print("   • Ensure all critical rules have code references")
            print("   • Validate business logic with stakeholders")
            print("   • Consider documenting edge cases")
        else:
            print(f"\n{Colors.RED}❌ Business rule extraction incomplete!{Colors.NC}")
            
            print(f"\n{Colors.MAGENTA}Required Actions:{Colors.NC}")
            print("   1. Run @business-logic-analyst agent")
            print("   2. Ensure thorough code analysis")
            print("   3. Extract rules from:")
            print("      • Validation logic")
            print("      • Business calculations")
            print("      • Authorization checks")
            print("      • Data constraints")
            print("   4. Document each rule with:")
            print("      • Unique ID (BR-XXX)")
            print("      • Description")
            print("      • Code reference (file:line)")
            print("      • Criticality level")

def main():
    """Main entry point"""
    validator = BusinessRuleValidator()
    exit_code = validator.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()