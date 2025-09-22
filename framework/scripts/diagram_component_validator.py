#!/usr/bin/env python3
"""
Diagram Component Validator
Validates that all components in Mermaid diagrams exist in the codebase.
This prevents hallucinated architectures by verifying every entity before rendering.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
import subprocess

class DiagramComponentValidator:
    """
    Validates diagram components against actual codebase content
    """

    def __init__(self, repomix_path: str = "output/reports/repomix-summary.md",
                 codebase_path: str = "codebase/"):
        self.repomix_path = Path(repomix_path)
        self.codebase_path = Path(codebase_path)
        self.repomix_content = self._load_repomix()

    def _load_repomix(self) -> str:
        """Load Repomix summary if available"""
        if self.repomix_path.exists():
            with open(self.repomix_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def extract_components_from_diagram(self, diagram_content: str, diagram_type: str = "auto") -> Set[str]:
        """
        Extract all component names from a Mermaid diagram
        """
        components = set()

        # Auto-detect diagram type if not specified
        if diagram_type == "auto":
            diagram_type = self._detect_diagram_type(diagram_content)

        # Extract based on diagram type
        if diagram_type == "classDiagram":
            components.update(self._extract_from_class_diagram(diagram_content))
        elif diagram_type == "sequenceDiagram":
            components.update(self._extract_from_sequence_diagram(diagram_content))
        elif diagram_type == "flowchart" or diagram_type.startswith("graph"):
            components.update(self._extract_from_flowchart(diagram_content))
        elif diagram_type == "C4":
            components.update(self._extract_from_c4_diagram(diagram_content))
        elif diagram_type == "erDiagram":
            components.update(self._extract_from_er_diagram(diagram_content))
        else:
            # Generic extraction for unknown types
            components.update(self._extract_generic_components(diagram_content))

        # Filter out common Mermaid keywords and symbols
        filtered = self._filter_mermaid_keywords(components)
        return filtered

    def _detect_diagram_type(self, content: str) -> str:
        """Detect the type of Mermaid diagram"""
        first_line = content.strip().split('\n')[0].strip()

        if 'classDiagram' in first_line:
            return 'classDiagram'
        elif 'sequenceDiagram' in first_line:
            return 'sequenceDiagram'
        elif 'flowchart' in first_line:
            return 'flowchart'
        elif 'graph' in first_line:
            return 'graph'
        elif 'C4' in first_line:
            return 'C4'
        elif 'erDiagram' in first_line:
            return 'erDiagram'
        elif 'stateDiagram' in first_line:
            return 'stateDiagram'
        return 'unknown'

    def _extract_from_class_diagram(self, content: str) -> Set[str]:
        """Extract class names from class diagrams"""
        components = set()

        # Pattern for class definitions
        class_pattern = r'class\s+(\w+)\s*(?:\{|$)'
        components.update(re.findall(class_pattern, content))

        # Pattern for relationships (A --> B)
        rel_pattern = r'(\w+)\s*(?:--|->|\.\.>|--\*|--o|--\|>)\s*(\w+)'
        for match in re.finditer(rel_pattern, content):
            components.add(match.group(1))
            components.add(match.group(2))

        return components

    def _extract_from_sequence_diagram(self, content: str) -> Set[str]:
        """Extract participants from sequence diagrams"""
        components = set()

        # Pattern for participant declarations
        participant_pattern = r'participant\s+(\w+)(?:\s+as\s+"[^"]+")?'
        components.update(re.findall(participant_pattern, content))

        # Pattern for actor declarations
        actor_pattern = r'actor\s+(\w+)'
        components.update(re.findall(actor_pattern, content))

        # Pattern for messages (A->>B or A-->>B etc)
        message_pattern = r'(\w+)\s*-+>>?\s*(\w+)'
        for match in re.finditer(message_pattern, content):
            components.add(match.group(1))
            components.add(match.group(2))

        return components

    def _extract_from_flowchart(self, content: str) -> Set[str]:
        """Extract node IDs from flowcharts"""
        components = set()

        # Pattern for node definitions: ID[Label] or ID(Label) etc
        node_pattern = r'(\w+)[\[\(\{]([^\]\)\}]+)[\]\)\}]'
        for match in re.finditer(node_pattern, content):
            node_id = match.group(1)
            label = match.group(2)
            # Try to extract meaningful component names from labels
            if not node_id.lower() in ['start', 'end', 'stop', 'a', 'b', 'c']:
                components.add(node_id)
            # Also check if label contains a class/component name
            label_components = re.findall(r'\b[A-Z]\w+(?:Service|Controller|Repository|Manager|Handler|Component)\b', label)
            components.update(label_components)

        return components

    def _extract_from_c4_diagram(self, content: str) -> Set[str]:
        """Extract components from C4 diagrams"""
        components = set()

        # Patterns for C4 elements
        patterns = [
            r'Person\([^,]+,\s*"([^"]+)"',  # Person(id, "name")
            r'System\([^,]+,\s*"([^"]+)"',  # System(id, "name")
            r'Container\([^,]+,\s*"([^"]+)"',  # Container(id, "name")
            r'Component\([^,]+,\s*"([^"]+)"',  # Component(id, "name")
            r'System_Ext\([^,]+,\s*"([^"]+)"',  # External system
            r'Container_Ext\([^,]+,\s*"([^"]+)"',  # External container
        ]

        for pattern in patterns:
            components.update(re.findall(pattern, content))

        # Also extract technology stack mentions
        tech_pattern = r'"[^"]+",\s*"([^"]+)"(?:,\s*"([^"]+)")?'
        for match in re.finditer(tech_pattern, content):
            if match.group(2):  # Technology stack
                tech_components = re.findall(r'\b[A-Z]\w+\b', match.group(2))
                components.update(tech_components)

        return components

    def _extract_from_er_diagram(self, content: str) -> Set[str]:
        """Extract entity names from ER diagrams"""
        components = set()

        # Pattern for entity definitions
        entity_pattern = r'^\s*(\w+)\s*\{'
        components.update(re.findall(entity_pattern, content, re.MULTILINE))

        # Pattern for relationships
        rel_pattern = r'(\w+)\s*\|+[o\*]?--[o\*]?\|+\s*(\w+)'
        for match in re.finditer(rel_pattern, content):
            components.add(match.group(1))
            components.add(match.group(2))

        return components

    def _extract_generic_components(self, content: str) -> Set[str]:
        """Generic extraction for any diagram type"""
        components = set()

        # Look for CamelCase class/component names
        camelcase_pattern = r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b'
        components.update(re.findall(camelcase_pattern, content))

        # Look for common suffixes
        suffix_pattern = r'\b(\w+(?:Service|Controller|Repository|Manager|Component|Handler|Factory|Provider|Gateway|Adapter|Model|Entity|DTO))\b'
        components.update(re.findall(suffix_pattern, content, re.IGNORECASE))

        return components

    def _filter_mermaid_keywords(self, components: Set[str]) -> Set[str]:
        """Filter out Mermaid keywords and common non-component words"""
        keywords = {
            # Mermaid keywords
            'graph', 'subgraph', 'end', 'classDiagram', 'sequenceDiagram',
            'participant', 'actor', 'note', 'loop', 'alt', 'opt', 'par',
            'flowchart', 'TD', 'LR', 'TB', 'BT', 'RL', 'DT',
            'class', 'namespace', 'interface', 'abstract', 'static',
            'erDiagram', 'relationship', 'contains', 'uses',
            # Common non-components
            'Start', 'End', 'Stop', 'Yes', 'No', 'True', 'False',
            'Input', 'Output', 'Process', 'Decision', 'Note',
            # Single letters often used as examples
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'
        }

        return {c for c in components if c not in keywords and len(c) > 1}

    def verify_component(self, component: str) -> Dict:
        """
        Verify if a component exists in the codebase
        Returns verification status and location if found
        """
        result = {
            'component': component,
            'found': False,
            'location': None,
            'search_performed': []
        }

        # Search patterns to try
        patterns = [
            f'class {component}',
            f'interface {component}',
            f'function {component}',
            f'def {component}',
            f'public.*{component}',
            f'struct {component}',
            f'enum {component}',
            f'type {component}',
            f'const {component}',
            f'@Entity.*{component}',
            f'@Table.*{component}',
            f'@Controller.*{component}',
            f'@Service.*{component}',
            f'@Repository.*{component}',
            f'@Component.*{component}'
        ]

        # First try Repomix summary
        if self.repomix_content:
            for pattern in patterns:
                if re.search(pattern, self.repomix_content, re.IGNORECASE):
                    # Try to find line number
                    lines = self.repomix_content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            # Look for file path in surrounding lines
                            file_path = self._extract_file_path(lines, i)
                            result['found'] = True
                            result['location'] = f"{file_path}:{i}" if file_path else f"line {i}"
                            result['search_performed'].append(f"Repomix: {pattern}")
                            return result

        # If not found in Repomix, try raw codebase search
        if self.codebase_path.exists() and not result['found']:
            try:
                for pattern in patterns[:3]:  # Try first 3 patterns in raw codebase
                    cmd = ['grep', '-r', '-n', pattern, str(self.codebase_path)]
                    process = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if process.returncode == 0 and process.stdout:
                        # Parse first match
                        first_match = process.stdout.split('\n')[0]
                        if ':' in first_match:
                            file_info = first_match.split(':')[0]
                            line_num = first_match.split(':')[1] if ':' in first_match else ''
                            result['found'] = True
                            result['location'] = f"{file_info}:{line_num}"
                            result['search_performed'].append(f"Codebase: {pattern}")
                            return result
            except (subprocess.TimeoutExpired, Exception):
                pass

        result['search_performed'].append("All patterns searched")
        return result

    def _extract_file_path(self, lines: List[str], current_line: int) -> str:
        """Try to extract file path from surrounding lines"""
        # Look backwards for file markers
        for i in range(max(0, current_line - 10), current_line):
            line = lines[i]
            # Common file path patterns
            if re.search(r'File:\s*(\S+\.\w+)', line):
                match = re.search(r'File:\s*(\S+\.\w+)', line)
                return match.group(1)
            elif re.search(r'^\s*[/#]+\s*(\S+\.\w+)', line):
                match = re.search(r'^\s*[/#]+\s*(\S+\.\w+)', line)
                return match.group(1)
            elif '.java' in line or '.cs' in line or '.ts' in line or '.py' in line:
                # Extract filename
                match = re.search(r'(\S+\.(?:java|cs|ts|js|py|php|rb|go))', line)
                if match:
                    return match.group(1)
        return None

    def validate_diagram(self, diagram_content: str, diagram_name: str = "diagram") -> Dict:
        """
        Validate all components in a diagram
        Returns comprehensive validation report
        """
        # Extract components
        components = self.extract_components_from_diagram(diagram_content)

        # Check for citation comments
        has_citations = self._check_for_citations(diagram_content)

        # Verify each component
        verification_results = []
        verified_count = 0
        not_found_count = 0

        for component in sorted(components):
            result = self.verify_component(component)
            verification_results.append(result)
            if result['found']:
                verified_count += 1
            else:
                not_found_count += 1

        # Generate validation report
        report = {
            'diagram_name': diagram_name,
            'total_components': len(components),
            'verified': verified_count,
            'not_found': not_found_count,
            'has_citations': has_citations,
            'valid': not_found_count == 0,
            'components': verification_results,
            'summary': self._generate_summary(verification_results, has_citations)
        }

        return report

    def _check_for_citations(self, diagram_content: str) -> bool:
        """
        Check if diagram contains citation comments
        Looking for patterns like:
        %% Component Citations
        %% ComponentName: REF-XXX (file:line)
        """
        lines = diagram_content.split('\n')

        # Look for citation comment patterns
        has_citation_header = any('%% Component Citations' in line or '%% Component Verification' in line for line in lines)
        has_ref_patterns = any(re.search(r'%%.*REF-\d{3}', line) for line in lines)
        has_file_refs = any(re.search(r'%%.*\.(java|cs|ts|js|py|php|rb|go):\d+', line) for line in lines)

        return has_citation_header or has_ref_patterns or has_file_refs

    def _generate_summary(self, results: List[Dict], has_citations: bool = False) -> str:
        """Generate human-readable summary"""
        verified = [r for r in results if r['found']]
        not_found = [r for r in results if not r['found']]

        summary = "## Component Verification Summary\n\n"

        # Citation status
        if has_citations:
            summary += "### ✅ Citation Comments: Present\n\n"
        else:
            summary += "### ⚠️ Citation Comments: Missing\n"
            summary += "Diagrams should include citation comments after the diagram type declaration.\n"
            summary += "See DIAGRAM_VALIDATION_RULES.md for examples.\n\n"

        if verified:
            summary += "### ✅ Verified Components:\n"
            for r in verified:
                summary += f"- `{r['component']}` ({r['location']})\n"
            summary += "\n"

        if not_found:
            summary += "### ❌ Not Found (Excluded from Diagram):\n"
            for r in not_found:
                summary += f"- `{r['component']}` - Not detected in codebase\n"
            summary += "\n"

        if not not_found:
            summary += "**✅ All components verified! Diagram is valid.**\n"
        else:
            summary += f"**⚠️ {len(not_found)} components not found. These should be removed from the diagram.**\n"

        if not has_citations:
            summary += "\n**Recommendation:** Add citation comments to improve traceability.\n"

        return summary

    def validate_file(self, file_path: str) -> List[Dict]:
        """Validate all diagrams in a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        results = []

        # Extract Mermaid diagrams from markdown
        if file_path.endswith('.md'):
            pattern = r'```(?:mermaid|mmd)\s*\n(.*?)\n```'
            diagrams = re.findall(pattern, content, re.DOTALL)
            for i, diagram in enumerate(diagrams, 1):
                result = self.validate_diagram(diagram, f"Diagram {i} in {file_path}")
                results.append(result)

        # For .mmd files, entire content is diagram
        elif file_path.endswith('.mmd'):
            result = self.validate_diagram(content, file_path)
            results.append(result)

        return results


def main():
    """CLI interface for diagram validation"""
    import argparse

    parser = argparse.ArgumentParser(description='Validate Mermaid diagram components against codebase')
    parser.add_argument('path', nargs='?', default='output',
                       help='Path to diagram file or directory (default: output)')
    parser.add_argument('--repomix', default='output/reports/repomix-summary.md',
                       help='Path to Repomix summary')
    parser.add_argument('--codebase', default='codebase/',
                       help='Path to raw codebase')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    parser.add_argument('--strict', action='store_true',
                       help='Exit with error if any components not found')
    parser.add_argument('--verbose', action='store_true',
                       help='Show detailed validation for each component')

    args = parser.parse_args()

    # Initialize validator
    validator = DiagramComponentValidator(args.repomix, args.codebase)

    # Process files
    path = Path(args.path)
    all_results = []
    files_processed = []

    if path.is_file():
        results = validator.validate_file(str(path))
        all_results.extend(results)
        files_processed.append(str(path))
    elif path.is_dir():
        # Find all diagram files in output directory structure
        # Priority locations based on framework structure
        diagram_locations = [
            path / 'diagrams',  # Primary location for .mmd files
            path / 'docs',      # Documentation may contain embedded diagrams
            path              # Root of specified path
        ]

        processed_files = set()  # Avoid processing files twice

        for location in diagram_locations:
            if location.exists():
                # Process .mmd files (standalone diagrams)
                for file_path in location.glob('**/*.mmd'):
                    if str(file_path) not in processed_files:
                        results = validator.validate_file(str(file_path))
                        if results:  # Only add if diagrams were found
                            all_results.extend(results)
                            files_processed.append(str(file_path))
                            processed_files.add(str(file_path))

                # Process .md files (may contain embedded diagrams)
                for file_path in location.glob('**/*.md'):
                    # Skip repomix-summary.md as it's the source data, not diagrams to validate
                    if 'repomix-summary.md' in str(file_path):
                        continue
                    if str(file_path) not in processed_files:
                        results = validator.validate_file(str(file_path))
                        if results:  # Only add if diagrams were found
                            all_results.extend(results)
                            files_processed.append(str(file_path))
                            processed_files.add(str(file_path))

    # Output results
    if not all_results:
        print("No Mermaid diagrams found in the specified path.")
        print(f"Searched in: {path}")
        if path.name == 'output':
            print("Checked: output/diagrams/, output/docs/, and output/")
        exit(0)

    if args.json:
        output = {
            'files_processed': files_processed,
            'total_diagrams': len(all_results),
            'results': all_results
        }
        print(json.dumps(output, indent=2))
    else:
        total_valid = sum(1 for r in all_results if r['valid'])
        total_invalid = sum(1 for r in all_results if not r['valid'])
        total_components = sum(r['total_components'] for r in all_results)
        total_verified = sum(r['verified'] for r in all_results)
        total_not_found = sum(r['not_found'] for r in all_results)

        # Summary header
        print(f"\n{'='*70}")
        print(f"DIAGRAM COMPONENT VALIDATION REPORT")
        print(f"{'='*70}")
        print(f"Files processed: {len(files_processed)}")
        print(f"Diagrams found: {len(all_results)}")
        print(f"Total components: {total_components}")
        print(f"{'='*70}\n")

        # Show results for each diagram
        if args.verbose or total_invalid > 0:
            for result in all_results:
                if not args.verbose and result['valid'] and result.get('has_citations', False):
                    continue  # Skip valid diagrams with citations unless verbose

                print(f"\n{'-'*60}")
                print(f"Diagram: {result['diagram_name']}")
                print(f"Components: {result['total_components']} total, "
                      f"{result['verified']} verified, {result['not_found']} not found")
                print(f"Citations: {'✅ Present' if result.get('has_citations', False) else '⚠️  Missing'}")
                print(f"Status: {'✅ VALID' if result['valid'] else '❌ INVALID'}")

                if args.verbose or not result['valid'] or not result.get('has_citations', False):
                    print("\n" + result['summary'])

        # Overall summary
        print(f"\n{'='*70}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Valid diagrams: {total_valid}/{len(all_results)}")
        if total_invalid > 0:
            print(f"❌ Invalid diagrams: {total_invalid}/{len(all_results)}")
        print(f"\nComponent Statistics:")
        print(f"  • Total components across all diagrams: {total_components}")
        print(f"  • Verified components: {total_verified} ({total_verified*100//total_components if total_components > 0 else 0}%)")
        if total_not_found > 0:
            print(f"  • Unverified components: {total_not_found} ({total_not_found*100//total_components if total_components > 0 else 0}%)")

        if total_invalid > 0:
            print(f"\n⚠️  ACTION REQUIRED: {total_invalid} diagram(s) contain unverified components")
            print("   Run with --verbose to see details of all validations")

    # Exit code
    if args.strict and total_invalid > 0:
        exit(1)
    else:
        exit(0)


if __name__ == '__main__':
    main()