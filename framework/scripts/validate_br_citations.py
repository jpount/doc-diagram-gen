#!/usr/bin/env python3
"""
Validates that BR-XXX, BR-LLM-XXX, and REF-XXX citations are properly used
in documentation and diagrams.
"""
import re
import json
from pathlib import Path
from typing import Set, Dict, List

class BRCitationValidator:
    def __init__(self):
        self.deterministic_rules = set()
        self.llm_rules = set()
        self.ref_citations = set()
        self.all_citations = set()
        self.errors = []
        self.warnings = []

    def load_rules(self):
        """Load the deterministic rules from extraction"""
        rules_file = Path("output/context/business-rules-extracted.json")
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                data = json.load(f)
                for rule in data['rules']:
                    self.deterministic_rules.add(rule['id'])
                    self.all_citations.add(rule['id'])
                print(f"✅ Loaded {len(self.deterministic_rules)} deterministic rules")
        else:
            self.errors.append("❌ business-rules-extracted.json not found")

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
            self.warnings.append("⚠️ codebase-citations.json not found - REF citations not validated")

    def extract_citations_from_file(self, filepath: Path) -> Dict[str, Set[str]]:
        """Extract all BR-XXX, BR-LLM-XXX, and REF-XXX citations from a file"""
        citations = {
            'br': set(),
            'br_llm': set(),
            'ref': set(),
            'all': set()
        }

        if not filepath.exists():
            return citations

        content = filepath.read_text()

        # Find BR-XXX patterns
        br_pattern = re.compile(r'BR-\d{3}')
        br_matches = br_pattern.findall(content)
        citations['br'].update(br_matches)
        citations['all'].update(br_matches)

        # Find BR-LLM-XXX patterns
        br_llm_pattern = re.compile(r'BR-LLM-\d{3}')
        br_llm_matches = br_llm_pattern.findall(content)
        citations['br_llm'].update(br_llm_matches)
        citations['all'].update(br_llm_matches)

        # Find REF-XXX patterns
        ref_pattern = re.compile(r'REF-\d{3}')
        ref_matches = ref_pattern.findall(content)
        citations['ref'].update(ref_matches)
        citations['all'].update(ref_matches)

        return citations

    def validate_documentation(self):
        """Check that documentation files cite business rules and REF-XXX"""
        doc_files = [
            Path("output/docs/business-logic-analysis.md"),
            Path("output/docs/business-rules-catalog.md"),
        ]

        for doc_file in doc_files:
            if doc_file.exists():
                citations = self.extract_citations_from_file(doc_file)

                # Check if deterministic rules are cited
                missing_deterministic = self.deterministic_rules - citations['br']
                if missing_deterministic and len(self.deterministic_rules) > 0:
                    self.warnings.append(
                        f"⚠️ {doc_file.name}: Missing citations for deterministic rules: {sorted(list(missing_deterministic))[:5]}..."
                    )

                print(f"📄 {doc_file.name}:")
                print(f"   - BR-XXX: {len(citations['br'])} citations")
                print(f"   - BR-LLM-XXX: {len(citations['br_llm'])} citations")
                print(f"   - REF-XXX: {len(citations['ref'])} citations")
                print(f"   - Total: {len(citations['all'])} citations")
            else:
                print(f"⏭️ {doc_file.name}: Not yet created")

    def validate_diagrams(self):
        """Check that diagram files include BR-XXX and REF-XXX references"""
        diagram_dir = Path("output/diagrams")

        if not diagram_dir.exists():
            print("⏭️ Diagram directory not yet created")
            return

        mmd_files = list(diagram_dir.glob("*.mmd"))

        for mmd_file in mmd_files:
            citations = self.extract_citations_from_file(mmd_file)

            if len(citations['all']) == 0:
                self.warnings.append(
                    f"⚠️ {mmd_file.name}: No citations found in diagram"
                )
            else:
                print(f"📊 {mmd_file.name}:")
                print(f"   - BR-XXX: {len(citations['br'])} citations")
                print(f"   - BR-LLM-XXX: {len(citations['br_llm'])} citations")
                print(f"   - REF-XXX: {len(citations['ref'])} citations")

    def validate_mapping(self):
        """Ensure all cited rules exist and are documented"""
        # Check all documentation and diagrams
        all_files = []

        # Add docs
        doc_dir = Path("output/docs")
        if doc_dir.exists():
            all_files.extend(doc_dir.glob("*.md"))

        # Add diagrams
        diagram_dir = Path("output/diagrams")
        if diagram_dir.exists():
            all_files.extend(diagram_dir.glob("*.mmd"))

        all_cited_rules = set()
        for filepath in all_files:
            all_cited_rules.update(self.extract_citations_from_file(filepath))

        # Check for citations without definitions
        undefined_rules = all_cited_rules - self.all_citations
        if undefined_rules and all_cited_rules:
            self.errors.append(
                f"❌ Found citations for undefined rules: {undefined_rules}"
            )

    def generate_citation_map(self):
        """Create a mapping file for all BR and REF citations"""
        citation_map = {
            "deterministic_rules": sorted(list(self.deterministic_rules)),
            "llm_rules": sorted(list(self.llm_rules)),
            "ref_citations_count": len(self.ref_citations),
            "total_rules": len(self.deterministic_rules) + len(self.llm_rules),
            "citation_format": {
                "deterministic": "BR-XXX (e.g., BR-001 to BR-039)",
                "llm_discovered": "BR-LLM-XXX (e.g., BR-LLM-001 onwards)",
                "codebase_refs": "REF-XXX (e.g., REF-001 for specific code locations)"
            },
            "usage_examples": {
                "in_documentation": "[BR-004] for buy operation, [REF-042] for code location",
                "in_diagrams": "Process[BR-004: Execute Buy, REF-042]",
                "in_notes": "Note: Implements BR-022 validation at REF-015",
                "cross_reference": "BR-004 (see REF-042 for implementation)"
            }
        }

        output_file = Path("output/context/br-citation-map.json")
        with open(output_file, 'w') as f:
            json.dump(citation_map, f, indent=2)

        print(f"\n💾 Generated citation map: {output_file}")

    def run_validation(self):
        """Run all validation checks"""
        print("\n" + "="*60)
        print("BUSINESS RULE CITATION VALIDATION")
        print("="*60)

        # Load rules and citations
        self.load_rules()
        self.load_ref_citations()

        # Validate documentation
        print("\n📚 Validating Documentation Citations:")
        self.validate_documentation()

        # Validate diagrams
        print("\n📊 Validating Diagram Citations:")
        self.validate_diagrams()

        # Validate mapping
        print("\n🔗 Validating Citation Consistency:")
        self.validate_mapping()

        # Generate citation map
        self.generate_citation_map()

        # Report results
        print("\n" + "-"*60)
        print("VALIDATION RESULTS")
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
            print("\n✅ All BR citations validated successfully!")

        print("\n" + "="*60)
        return len(self.errors) == 0

if __name__ == "__main__":
    validator = BRCitationValidator()
    success = validator.run_validation()
    exit(0 if success else 1)