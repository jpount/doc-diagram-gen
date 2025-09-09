#!/usr/bin/env python3
"""
Data Integrity Validator
Scans generated documentation for fabricated data violations
Enforces the framework rule: NEVER use fabricated metrics, dates, or specific values
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class DataIntegrityValidator:
    """Validates that agents only use actual data from the codebase"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.violations = []
        
        # Patterns for fabricated data
        self.violation_patterns = {
            "specific_dates": [
                r'\b\d{4}-\d{2}-\d{2}\b',  # 2025-01-09 format
                r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
                r'\b\d{1,2}/(0?[1-9]|1[0-2])/\d{4}\b'  # MM/DD/YYYY
            ],
            "specific_percentages": [
                r'\b\d+\.\d+%\b',  # 40.5%
                r'\b\d+-\d+%\b'    # 40-60%
            ],
            "specific_dollar_amounts": [
                r'\$\d+(?:,\d{3})*(?:\.\d{2})?\b',  # $1,000.00
                r'\b\d+(?:,\d{3})*\s*dollars?\b'    # 1000 dollars
            ],
            "specific_timings": [
                r'\b\d+(?:\.\d+)?\s*(?:ms|milliseconds?|seconds?|minutes?)\b',  # 200ms, 1.5 seconds
                r'\b\d+-\d+\s*(?:ms|milliseconds?|seconds?|minutes?)\b'        # 200-500ms
            ],
            "specific_counts": [
                r'\b\d{3,}\s*(?:users?|files?|lines?|classes?|methods?)\b',  # 1000 users
                r'\bexactly\s+\d+\b',   # exactly 50
                r'\bprecisely\s+\d+\b'  # precisely 100
            ],
            "specific_sizes": [
                r'\b\d+(?:\.\d+)?\s*(?:KB|MB|GB|TB)\b',  # 500KB, 1.5MB
                r'\b\d+-\d+\s*(?:KB|MB|GB|TB)\b'        # 200-500KB
            ]
        }
        
        # Approved generic terms to suggest instead
        self.approved_alternatives = {
            "specific_percentages": ["high", "low", "significant", "substantial", "moderate", "minimal"],
            "specific_timings": ["fast", "slow", "extended", "brief", "rapid", "prolonged"],
            "specific_counts": ["many", "few", "numerous", "several", "multiple", "extensive"],
            "specific_sizes": ["large", "small", "compact", "substantial", "minimal"],
            "specific_dates": ["recent", "current", "latest", "historical", "ongoing"]
        }
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for data integrity violations"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return [{"error": f"Could not read {file_path}: {e}"}]
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for category, patterns in self.violation_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        violations.append({
                            "file": str(file_path.relative_to(self.project_root)),
                            "line": line_num,
                            "category": category,
                            "violation": match.group(0),
                            "context": line.strip(),
                            "suggestion": self.get_suggestion(category, match.group(0))
                        })
        
        return violations
    
    def get_suggestion(self, category: str, violation: str) -> str:
        """Get suggested replacement for violation"""
        alternatives = self.approved_alternatives.get(category, ["generic description"])
        
        # Context-sensitive suggestions
        if category == "specific_percentages":
            if "%" in violation and any(word in violation.lower() for word in ["reduction", "decrease"]):
                return "significant reduction"
            elif "%" in violation and any(word in violation.lower() for word in ["increase", "growth"]):
                return "substantial increase"
            else:
                return "high percentage"
                
        elif category == "specific_timings":
            if any(unit in violation.lower() for unit in ["ms", "milliseconds"]):
                return "brief processing time"
            elif any(unit in violation.lower() for unit in ["seconds", "minutes"]):
                return "extended processing time"
            else:
                return "moderate duration"
                
        elif category == "specific_dates":
            return "recent analysis"
            
        elif category == "specific_dollar_amounts":
            return "substantial amount"
            
        elif category == "specific_counts":
            if int(''.join(filter(str.isdigit, violation))) > 1000:
                return "numerous"
            else:
                return "several"
                
        elif category == "specific_sizes":
            return "substantial size"
            
        return alternatives[0]
    
    def scan_all_output(self) -> Dict:
        """Scan all output files for violations"""
        results = {
            "total_files": 0,
            "files_with_violations": 0,
            "total_violations": 0,
            "violations_by_category": {},
            "detailed_violations": []
        }
        
        # Scan output directories
        output_dirs = [
            self.project_root / "output" / "docs",
            self.project_root / "output" / "reports",
            self.project_root / "output" / "context"
        ]
        
        for output_dir in output_dirs:
            if output_dir.exists():
                for file_path in output_dir.rglob("*.md"):
                    results["total_files"] += 1
                    
                    file_violations = self.scan_file(file_path)
                    if file_violations:
                        results["files_with_violations"] += 1
                        results["total_violations"] += len(file_violations)
                        results["detailed_violations"].extend(file_violations)
                        
                        # Count by category
                        for violation in file_violations:
                            category = violation.get("category", "unknown")
                            results["violations_by_category"][category] = results["violations_by_category"].get(category, 0) + 1
        
        return results
    
    def generate_report(self, results: Dict) -> None:
        """Generate a comprehensive violation report"""
        print("🚨 DATA INTEGRITY VALIDATION REPORT")
        print("=" * 50)
        
        print(f"📊 Summary:")
        print(f"  - Files scanned: {results['total_files']}")
        print(f"  - Files with violations: {results['files_with_violations']}")
        print(f"  - Total violations: {results['total_violations']}")
        
        if results["total_violations"] == 0:
            print("\n✅ NO VIOLATIONS FOUND - Data integrity maintained!")
            return
        
        print(f"\n🚨 VIOLATIONS BY CATEGORY:")
        for category, count in results["violations_by_category"].items():
            print(f"  - {category.replace('_', ' ').title()}: {count}")
        
        print(f"\n📋 DETAILED VIOLATIONS:")
        
        for violation in results["detailed_violations"][:20]:  # Show first 20
            print(f"\n❌ {violation['file']}:{violation['line']}")
            print(f"   Category: {violation['category']}")
            print(f"   Found: '{violation['violation']}'")
            print(f"   Context: {violation['context'][:80]}...")
            print(f"   ✅ Suggest: '{violation['suggestion']}'")
        
        if len(results["detailed_violations"]) > 20:
            print(f"\n... and {len(results['detailed_violations']) - 20} more violations")
        
        print(f"\n🔧 REMEDIATION REQUIRED:")
        print(f"  1. Replace specific values with generic terms")
        print(f"  2. Use only actual data from codebase/context files")
        print(f"  3. Avoid fabricated metrics, dates, or amounts")
        print(f"  4. Update agent templates to prevent future violations")

def main():
    """Run data integrity validation"""
    validator = DataIntegrityValidator()
    results = validator.scan_all_output()
    validator.generate_report(results)
    
    # Return appropriate exit code
    return 1 if results["total_violations"] > 0 else 0

if __name__ == "__main__":
    sys.exit(main())