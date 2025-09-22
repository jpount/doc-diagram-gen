#!/usr/bin/env python3
"""
Generate Agent Citations File
Creates the citations file for a specific agent by combining REF-XXX and BR-XXX citations
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
import argparse


def extract_used_refs_with_locations(agent_name):
    """Extract REF-XXX citations and track which files use them"""
    ref_usage = {}  # REF-XXX -> list of files using it

    # Check documentation files
    doc_files = [
        'output/docs/business-logic-analysis.md',
        'output/docs/business-rules-catalog.md'
    ]

    for doc_file in doc_files:
        if Path(doc_file).exists():
            with open(doc_file, 'r') as f:
                content = f.read()

            # Find REF citations in brackets
            found_refs = re.findall(r'\[REF-\d{3}\]', content)
            for ref in found_refs:
                ref_id = ref.strip('[]')
                if ref_id not in ref_usage:
                    ref_usage[ref_id] = []
                file_name = Path(doc_file).name
                if file_name not in ref_usage[ref_id]:
                    ref_usage[ref_id].append(file_name)

    # Check diagram files
    diagram_dir = Path('output/diagrams')
    if diagram_dir.exists():
        for diagram_file in diagram_dir.glob('*.mmd'):
            with open(diagram_file, 'r') as f:
                content = f.read()

            # Find REF citations (without brackets in diagrams)
            found_refs = re.findall(r'REF-\d{3}', content)
            for ref_id in found_refs:
                if ref_id not in ref_usage:
                    ref_usage[ref_id] = []
                file_name = diagram_file.name
                if file_name not in ref_usage[ref_id]:
                    ref_usage[ref_id].append(file_name)

    return ref_usage


def extract_br_citations_with_usage(agent_name):
    """Extract BR-XXX citations and track where they're used"""
    br_citations = {}
    br_usage = {}  # BR-XXX -> list of files using it

    # First, extract BR definitions from catalog
    catalog_path = Path('output/docs/business-rules-catalog.md')
    if catalog_path.exists():
        with open(catalog_path, 'r') as f:
            content = f.read()

        # Split content into sections for each BR
        br_sections = re.split(r'(#### BR-\d{3}:)', content)

        # Process pairs of (BR header, BR content)
        for i in range(1, len(br_sections), 2):
            if i + 1 < len(br_sections):
                br_header = br_sections[i]
                br_content = br_sections[i + 1]

                # Extract BR ID and title
                br_match = re.match(r'#### (BR-\d{3}):', br_header)
                if br_match:
                    br_id = br_match.group(1)

                    # Extract title from the content (first line)
                    title_match = re.match(r'\s*([^\n]+)', br_content)
                    br_title = title_match.group(1).strip() if title_match else 'Unknown Rule'

                    # Extract location - look for **Location**: `...`
                    location_pattern = r'\*\*Location\*\*:\s*`([^`]+)`'
                    location_match = re.search(location_pattern, br_content)
                    location = location_match.group(1) if location_match else 'Not specified'

                    # Extract actual code section if available
                    code_pattern = r'\*\*Actual Code\*\*:[^`]*```[^\n]*\n([^`]+)```'
                    code_match = re.search(code_pattern, br_content, re.DOTALL)

                    br_citations[br_id] = {
                        'title': br_title,
                        'type': 'Business Rule',
                        'location': location,
                        'used_in': ['business-rules-catalog.md']  # Always used in catalog
                    }

    # Now check all files for BR usage
    files_to_check = []

    # Add documentation files
    for doc_file in Path('output/docs').glob('*.md'):
        files_to_check.append(doc_file)

    # Add diagram files
    for diagram_file in Path('output/diagrams').glob('*.mmd'):
        files_to_check.append(diagram_file)

    # Check each file for BR references
    for file_path in files_to_check:
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()

            # Find BR references (various formats)
            br_refs = re.findall(r'BR-\d{3}', content)
            for br_id in br_refs:
                if br_id in br_citations:
                    file_name = file_path.name
                    if file_name not in br_citations[br_id]['used_in']:
                        br_citations[br_id]['used_in'].append(file_name)

    return br_citations


def generate_citations_file(agent_name):
    """Generate the complete citations file for an agent"""

    # Load REF-XXX citations from codebase-citations.json
    ref_citations = {}
    citations_path = Path('output/context/codebase-citations.json')
    if citations_path.exists():
        with open(citations_path, 'r') as f:
            citations_data = json.load(f)
        ref_citations = citations_data.get('ref_index', {})
        print(f"✅ Loaded {len(ref_citations)} REF-XXX citations from codebase")
    else:
        print(f"⚠️  No codebase-citations.json found - REF citations unavailable")

    # Extract REF citations with usage tracking
    ref_usage = extract_used_refs_with_locations(agent_name)
    print(f"✅ Found {len(ref_usage)} REF-XXX citations used in documents/diagrams")

    # Extract BR citations with usage tracking
    br_citations = extract_br_citations_with_usage(agent_name)
    print(f"✅ Found {len(br_citations)} BR-XXX business rule citations")

    # Generate the citations file content
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content = f"""# Code Citations Reference - {agent_name}

This document contains all code citations referenced in the {agent_name} documentation.
Each reference ID maps to specific code locations in the codebase.

Generated: {timestamp}
Agent: {agent_name}

---

## Citation Format

Each citation follows this format:
- **REF-XXX** for codebase components (classes, methods, etc.)
- **BR-XXX** for business rules identified during analysis
- Minimal in diagrams: `%% ComponentName: REF-XXX` or `%% BusinessRule: BR-XXX`
- Clean in docs: `ComponentName [REF-XXX]` or `Business Rule [BR-XXX]`

---

## Component Citations (REF-XXX)

"""

    # Add used REF citations with actual usage tracking
    if ref_usage:
        for ref_id in sorted(ref_usage.keys()):
            if ref_id in ref_citations:
                details = ref_citations[ref_id]
                used_in_files = ref_usage[ref_id]
                used_in_str = ', '.join(f'`{f}`' for f in sorted(used_in_files))

                content += f"""### {ref_id}: {details.get('name', 'Unknown')}
- **File**: `{details.get('file_path', 'Unknown')}:{details.get('line', '')}`
- **Type**: {details.get('type', 'Unknown')}
- **Used in**: {used_in_str}

"""
    else:
        content += "*No REF-XXX citations currently in use*\n\n"

    content += """---

## Business Rule Citations (BR-XXX)

"""

    # Add BR citations
    if br_citations:
        for br_id in sorted(br_citations.keys()):
            details = br_citations[br_id]
            content += f"""### {br_id}: {details['title']}
- **Type**: {details['type']}
- **Source Code Location**: `{details['location']}`
- **Used in**: {', '.join(f'`{f}`' for f in sorted(details['used_in']))}

"""
    else:
        content += "*No BR-XXX citations generated yet*\n\n"

    content += """---

## Special References

### External Systems
- **External**: Third-party services not in codebase

### Not Found
- **NOT FOUND**: Components mentioned but not detected in code

---

## Usage Examples

### In Documentation
```markdown
The `TradeDirect` class [REF-002] implements the main trading logic.
This follows business rule BR-004: Order Type Validation.
```

### In Diagrams
```mermaid
sequenceDiagram
    %% Component Citations
    %% TradeDirect: REF-001
    %% TradeConfig: REF-002
    %% Business Rule: BR-004 (Order Status Lifecycle)

    participant TD as TradeDirect
    participant TC as TradeConfig
    Note over TD: Implements BR-004
```

---

*Note: This file contains both REF-XXX citations (from codebase components) and BR-XXX citations (business rules identified during analysis).*
"""

    # Write the citations file
    output_dir = Path('output/citations')
    output_dir.mkdir(parents=True, exist_ok=True)
    citations_file = output_dir / f'{agent_name}-citations.md'

    with open(citations_file, 'w') as f:
        f.write(content)

    print(f"✅ Generated complete citations file: {citations_file}")
    print(f"   - {len(ref_usage)} REF-XXX component citations")
    print(f"   - {len(br_citations)} BR-XXX business rule citations")

    # Show usage statistics
    total_ref_usages = sum(len(files) for files in ref_usage.values())
    total_br_usages = sum(len(details['used_in']) for details in br_citations.values())
    print(f"   - Total REF usage instances: {total_ref_usages}")
    print(f"   - Total BR usage instances: {total_br_usages}")

    return str(citations_file)


def main():
    parser = argparse.ArgumentParser(description='Generate citations file for an agent')
    parser.add_argument(
        'agent_name',
        help='Name of the agent (e.g., business-logic-analyst)'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify citations after generation'
    )

    args = parser.parse_args()

    # Generate citations file
    citations_file = generate_citations_file(args.agent_name)

    # Optionally verify
    if args.verify and Path(citations_file).exists():
        with open(citations_file, 'r') as f:
            content = f.read()

        # Count citations
        ref_count = len(re.findall(r'### REF-\d{3}:', content))
        br_count = len(re.findall(r'### BR-\d{3}:', content))

        print(f"\n✅ Verification Complete:")
        print(f"   - File exists: {citations_file}")
        print(f"   - REF citations: {ref_count}")
        print(f"   - BR citations: {br_count}")
        print(f"   - File size: {Path(citations_file).stat().st_size} bytes")


if __name__ == "__main__":
    main()