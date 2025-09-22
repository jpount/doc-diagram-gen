#!/usr/bin/env python3
"""
Universal citation validator for all agent types.
Validates REF-XXX citations plus agent-specific citation patterns.
"""
import re
import json
import argparse
from pathlib import Path
from typing import Set, Dict, List

class UniversalCitationValidator:
    def __init__(self, agent_type=None):
        self.agent_type = agent_type
        self.ref_citations = set()
        self.agent_citations = {}
        self.errors = []
        self.warnings = []

        # Define citation patterns for each agent
        self.agent_patterns = {
            'business-logic-analyst': {
                'BR': r'BR-\d{3}',
                'BR-LLM': r'BR-LLM-\d{3}'
            },
            'security-analyst': {
                'SEC': r'SEC-\d{3}',
                'OWASP': r'OWASP-[A-Z]\d{2}',
                'CVE': r'CVE-\d{4}-\d{4,}'
            },
            'performance-analyst': {
                'PERF': r'PERF-\d{3}',
                'OPT': r'OPT-\d{3}'
            },
            'integration-specialist': {
                'INT': r'INT-\d{3}',
                'MSG': r'MSG-\d{3}',
                'EIP': r'EIP-\d{3}'
            },
            'ui-analyst': {
                'UI': r'UI-\d{3}',
                'UX': r'UX-\d{3}'
            },
            'technical-architect': {
                'ARCH': r'ARCH-\d{3}',
                'COMP': r'COMP-\d{3}',
                'TECH': r'TECH-\d{3}'
            },
            'solution-architect': {
                'ARCH': r'ARCH-\d{3}',
                'COMP': r'COMP-\d{3}',
                'TECH': r'TECH-\d{3}'
            }
        }

    def load_ref_citations(self):
        """Load REF-XXX citations from codebase-citations.json"""
        citations_file = Path("output/context/codebase-citations.json")
        if citations_file.exists():
            with open(citations_file, 'r') as f:
                data = json.load(f)
                if 'ref_index' in data:
                    self.ref_citations = set(data['ref_index'].keys())
                    print(f"✅ Loaded {len(self.ref_citations)} REF-XXX citations")
        else:
            self.warnings.append("⚠️ codebase-citations.json not found")

    def load_agent_specific_data(self):
        """Load agent-specific citation data"""
        if self.agent_type == 'business-logic-analyst':
            # Load deterministic business rules
            rules_file = Path("output/context/business-rules-extracted.json")
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    data = json.load(f)
                    br_rules = set()
                    for rule in data.get('rules', []):
                        br_rules.add(rule['id'])
                    self.agent_citations['BR'] = br_rules
                    print(f"✅ Loaded {len(br_rules)} BR-XXX rules")

    def extract_citations_from_file(self, filepath: Path) -> Dict[str, Set[str]]:
        """Extract all citations from a file"""
        citations = {
            'REF': set(),
            'agent_specific': {},
            'all': set()
        }

        if not filepath.exists():
            return citations

        content = filepath.read_text()

        # Extract REF-XXX (universal)
        ref_pattern = re.compile(r'REF-\d{3}')
        ref_matches = ref_pattern.findall(content)
        citations['REF'].update(ref_matches)
        citations['all'].update(ref_matches)

        # Extract agent-specific citations
        if self.agent_type and self.agent_type in self.agent_patterns:
            for citation_type, pattern in self.agent_patterns[self.agent_type].items():
                matches = re.findall(pattern, content)
                if matches:
                    citations['agent_specific'][citation_type] = set(matches)
                    citations['all'].update(matches)

        return citations

    def validate_documentation(self):
        """Check that documentation files have appropriate citations"""
        doc_dir = Path("output/docs")

        if not doc_dir.exists():
            print("⏭️ Documentation directory not yet created")
            return

        # Find agent-specific docs
        doc_patterns = {
            'business-logic': ['business-logic*.md', 'business-rules*.md'],
            'security': ['security*.md', '*vulnerabilities*.md'],
            'performance': ['performance*.md', '*optimization*.md'],
            'integration': ['integration*.md', '*api*.md'],
            'ui': ['ui*.md', '*frontend*.md'],
            'architect': ['*architecture*.md', '*solution*.md']
        }

        for doc_file in doc_dir.glob("*.md"):
            citations = self.extract_citations_from_file(doc_file)

            print(f"\n📄 {doc_file.name}:")
            print(f"   - REF-XXX: {len(citations['REF'])} citations")

            if not citations['REF']:
                self.warnings.append(f"⚠️ {doc_file.name}: No REF-XXX citations found")

            for ctype, cset in citations['agent_specific'].items():
                print(f"   - {ctype}: {len(cset)} citations")

    def validate_diagrams(self):
        """Check that diagram files include appropriate citations"""
        diagram_dir = Path("output/diagrams")

        if not diagram_dir.exists():
            print("\n⏭️ Diagram directory not yet created")
            return

        print("\n📊 Validating Diagram Citations:")

        for mmd_file in diagram_dir.glob("*.mmd"):
            citations = self.extract_citations_from_file(mmd_file)

            # Check for citation comments
            content = mmd_file.read_text()
            has_citation_comment = "%% Component Citations" in content or "%% Citations" in content

            print(f"\n📊 {mmd_file.name}:")

            if not has_citation_comment:
                self.warnings.append(f"⚠️ {mmd_file.name}: Missing citation comment block")

            print(f"   - REF-XXX: {len(citations['REF'])} citations")

            for ctype, cset in citations['agent_specific'].items():
                print(f"   - {ctype}: {len(cset)} citations")

            if len(citations['all']) == 0:
                self.warnings.append(f"⚠️ {mmd_file.name}: No citations found")

    def generate_validation_report(self):
        """Generate a validation report"""
        report = {
            "validation_timestamp": str(Path.cwd()),
            "agent_type": self.agent_type or "universal",
            "ref_citations_available": len(self.ref_citations),
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": []
        }

        if not self.ref_citations:
            report["recommendations"].append(
                "Run: python3 framework/scripts/extract_citations.py"
            )

        if self.agent_type == 'business-logic-analyst' and 'BR' not in self.agent_citations:
            report["recommendations"].append(
                "Run: python3 framework/scripts/extract_business_rules.py"
            )

        output_file = Path("output/context/citation-validation-report.json")
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Validation report saved: {output_file}")

    def run_validation(self):
        """Run complete validation"""
        print("\n" + "="*60)
        print("UNIVERSAL CITATION VALIDATION")
        if self.agent_type:
            print(f"Agent: {self.agent_type}")
        print("="*60)

        # Load universal citations
        self.load_ref_citations()

        # Load agent-specific data
        if self.agent_type:
            self.load_agent_specific_data()

        # Validate documentation
        print("\n📚 Validating Documentation:")
        self.validate_documentation()

        # Validate diagrams
        self.validate_diagrams()

        # Generate report
        self.generate_validation_report()

        # Summary
        print("\n" + "-"*60)
        print("VALIDATION SUMMARY")
        print("-"*60)

        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All citations validated successfully!")

        print("\n" + "="*60)
        return len(self.errors) == 0

def main():
    parser = argparse.ArgumentParser(
        description='Validate citations for agent documentation'
    )
    parser.add_argument(
        '--agent',
        type=str,
        choices=[
            'business-logic-analyst',
            'security-analyst',
            'performance-analyst',
            'integration-specialist',
            'ui-analyst',
            'technical-architect',
            'solution-architect'
        ],
        help='Specify the agent type for specific validation'
    )

    args = parser.parse_args()

    validator = UniversalCitationValidator(agent_type=args.agent)
    success = validator.run_validation()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()