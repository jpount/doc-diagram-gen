#!/usr/bin/env python3
"""
Repomix Parser - Extracts code components from repomix-summary.md
Pure Python implementation for parsing the compressed codebase representation.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class CodeComponent:
    """Represents a code component found in the codebase"""
    name: str
    type: str  # class, interface, method, config, enum, annotation
    file_path: str
    repomix_line: int
    original_line: Optional[int] = None
    signature: Optional[str] = None
    parent_class: Optional[str] = None
    snippet: Optional[str] = None


class RepomixParser:
    """Parser for repomix-summary.md files"""

    def __init__(self, repomix_path: str = "output/reports/repomix-summary.md"):
        self.repomix_path = Path(repomix_path)
        self.content: List[str] = []
        self.file_boundaries: Dict[str, Tuple[int, int]] = {}
        self.components: Dict[str, List[CodeComponent]] = {
            'classes': [],
            'interfaces': [],
            'methods': [],
            'enums': [],
            'configs': [],
            'annotations': [],
            'api_endpoints': []
        }

    def load(self) -> bool:
        """Load the repomix file into memory"""
        if not self.repomix_path.exists():
            print(f"❌ Repomix file not found: {self.repomix_path}")
            return False

        with open(self.repomix_path, 'r', encoding='utf-8') as f:
            self.content = f.readlines()

        print(f"✅ Loaded {len(self.content)} lines from {self.repomix_path}")
        self._identify_file_boundaries()
        return True

    def _identify_file_boundaries(self):
        """Identify where each file starts and ends in the repomix summary"""
        current_file = None
        start_line = 0

        for i, line in enumerate(self.content):
            if line.startswith("## File: "):
                if current_file:
                    # Save previous file boundary
                    self.file_boundaries[current_file] = (start_line, i - 1)

                # Start new file
                current_file = line[9:].strip()  # Remove "## File: "
                start_line = i

        # Save last file
        if current_file:
            self.file_boundaries[current_file] = (start_line, len(self.content) - 1)

        print(f"📁 Found {len(self.file_boundaries)} files in repomix summary")

    def extract_all_components(self) -> Dict:
        """Extract all code components from the repomix file"""
        for file_path, (start, end) in self.file_boundaries.items():
            self._extract_from_file(file_path, start, end)

        # Summary
        total = sum(len(v) for v in self.components.values())
        print(f"\n📊 Extraction Summary:")
        print(f"  - Classes: {len(self.components['classes'])}")
        print(f"  - Interfaces: {len(self.components['interfaces'])}")
        print(f"  - Methods: {len(self.components['methods'])}")
        print(f"  - Enums: {len(self.components['enums'])}")
        print(f"  - Configs: {len(self.components['configs'])}")
        print(f"  - API Endpoints: {len(self.components['api_endpoints'])}")
        print(f"  - Total: {total} components")

        return self.components

    def _extract_from_file(self, file_path: str, start: int, end: int):
        """Extract components from a specific file section"""

        # Skip non-code files
        if not self._is_code_file(file_path):
            return

        # Track current class for method association
        current_class = None
        in_code_block = False
        relative_line = 0

        for i in range(start, min(end + 1, len(self.content))):
            line = self.content[i]

            # Track code blocks
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                relative_line = 0
                continue

            if in_code_block:
                relative_line += 1

                # Java/C#/JSP/JSF patterns
                if file_path.endswith(('.java', '.cs')):
                    self._extract_java_components(line, file_path, i, relative_line, current_class)

                    # Track current class
                    class_match = re.match(r'\s*(public\s+)?(class|interface)\s+(\w+)', line)
                    if class_match:
                        current_class = class_match.group(3)

                # JSP/JSF patterns
                elif file_path.endswith(('.jsp', '.jsf', '.xhtml')):
                    self._extract_jsp_jsf_components(line, file_path, i, relative_line)
                    # Also try Java patterns since JSP can contain Java code
                    self._extract_java_components(line, file_path, i, relative_line, current_class)

                # Python patterns
                elif file_path.endswith('.py'):
                    self._extract_python_components(line, file_path, i, relative_line, current_class)

                    # Track current class
                    class_match = re.match(r'\s*class\s+(\w+)', line)
                    if class_match:
                        current_class = class_match.group(1)

                # JavaScript/TypeScript patterns
                elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                    self._extract_javascript_components(line, file_path, i, relative_line)

                # Configuration files
                elif file_path.endswith(('.properties', '.yml', '.yaml', '.xml')):
                    self._extract_config_values(line, file_path, i, relative_line)

    def _is_code_file(self, file_path: str) -> bool:
        """Check if file is a code file we should parse"""
        code_extensions = (
            '.java', '.jsp', '.jsf', '.xhtml',  # Java and Java web files
            '.cs', '.aspx', '.ascx',  # .NET files
            '.py', '.js', '.ts', '.jsx', '.tsx',
            '.go', '.rb', '.php', '.swift', '.kt', '.scala', '.rs',
            '.cpp', '.c', '.h', '.hpp'
        )
        return file_path.endswith(code_extensions)

    def _extract_java_components(self, line: str, file_path: str, repomix_line: int,
                                 relative_line: int, current_class: Optional[str]):
        """Extract Java/C# specific components"""

        # Classes and Interfaces
        class_match = re.match(r'\s*(public\s+|private\s+|protected\s+)?(abstract\s+)?(class|interface|enum)\s+(\w+)', line)
        if class_match:
            component_type = class_match.group(3)
            name = class_match.group(4)

            if component_type == 'enum':
                target = 'enums'
            elif component_type == 'interface':
                target = 'interfaces'
            else:
                target = 'classes'

            self.components[target].append(CodeComponent(
                name=name,
                type=component_type,
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature=line.strip(),
                snippet=line.strip()
            ))

        # Methods
        method_match = re.match(r'\s*(public\s+|private\s+|protected\s+)?(static\s+)?(\w+[\[\]<>,\s]*)\s+(\w+)\s*\([^)]*\)', line)
        if method_match and not re.match(r'\s*(if|while|for|switch)\s*\(', line):
            return_type = method_match.group(3)
            method_name = method_match.group(4)

            # Skip constructors and common keywords
            if method_name not in ['if', 'while', 'for', 'switch', 'catch']:
                self.components['methods'].append(CodeComponent(
                    name=method_name,
                    type='method',
                    file_path=file_path,
                    repomix_line=repomix_line + 1,
                    original_line=relative_line,
                    signature=line.strip(),
                    parent_class=current_class,
                    snippet=line.strip()
                ))

        # Annotations (potential API endpoints)
        annotation_match = re.match(r'\s*@(\w+)(\([^)]*\))?', line)
        if annotation_match:
            annotation = annotation_match.group(1)
            if annotation in ['RequestMapping', 'GetMapping', 'PostMapping', 'PutMapping',
                            'DeleteMapping', 'Path', 'Route']:
                self.components['api_endpoints'].append(CodeComponent(
                    name=annotation,
                    type='api_endpoint',
                    file_path=file_path,
                    repomix_line=repomix_line + 1,
                    original_line=relative_line,
                    signature=line.strip(),
                    parent_class=current_class,
                    snippet=line.strip()
                ))

    def _extract_python_components(self, line: str, file_path: str, repomix_line: int,
                                  relative_line: int, current_class: Optional[str]):
        """Extract Python specific components"""

        # Classes
        class_match = re.match(r'\s*class\s+(\w+)', line)
        if class_match:
            self.components['classes'].append(CodeComponent(
                name=class_match.group(1),
                type='class',
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature=line.strip(),
                snippet=line.strip()
            ))

        # Functions/Methods
        func_match = re.match(r'\s*def\s+(\w+)\s*\([^)]*\)', line)
        if func_match:
            self.components['methods'].append(CodeComponent(
                name=func_match.group(1),
                type='method' if current_class else 'function',
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature=line.strip(),
                parent_class=current_class,
                snippet=line.strip()
            ))

        # Decorators (potential API endpoints)
        decorator_match = re.match(r'\s*@(\w+\.)?(\w+)(\([^)]*\))?', line)
        if decorator_match:
            decorator = decorator_match.group(2)
            if decorator in ['route', 'get', 'post', 'put', 'delete', 'api', 'endpoint']:
                self.components['api_endpoints'].append(CodeComponent(
                    name=decorator,
                    type='api_endpoint',
                    file_path=file_path,
                    repomix_line=repomix_line + 1,
                    original_line=relative_line,
                    signature=line.strip(),
                    parent_class=current_class,
                    snippet=line.strip()
                ))

    def _extract_jsp_jsf_components(self, line: str, file_path: str, repomix_line: int,
                                    relative_line: int):
        """Extract JSP/JSF specific components and validations"""

        # JSP useBean declarations (very common in JSP files)
        usebean_match = re.search(r'<jsp:useBean\s+id="(\w+)".*type="([^"]+)"', line)
        if usebean_match:
            bean_name = usebean_match.group(1)
            bean_type = usebean_match.group(2)
            # Extract just the class name from full path
            class_name = bean_type.split('.')[-1] if '.' in bean_type else bean_type

            self.components['classes'].append(CodeComponent(
                name=bean_name,
                type='jsp_bean',
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature=f"jsp:useBean {bean_name} of type {class_name}",
                snippet=line.strip()
            ))

        # JSP imports
        import_match = re.search(r'<%@\s*page.*import="([^"]+)"', line)
        if import_match:
            imports = import_match.group(1)
            # Track as configuration/import
            self.components['configs'].append(CodeComponent(
                name='jsp_import',
                type='import',
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature=f"JSP imports: {imports}",
                snippet=line.strip()
            ))

        # JSP Scriptlets with Java code
        scriptlet_match = re.search(r'<%[^@%].*%>', line)
        if scriptlet_match:
            # Mark as containing business logic
            self.components['methods'].append(CodeComponent(
                name='jsp_scriptlet',
                type='scriptlet',
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature='JSP Scriptlet',
                snippet=line.strip()[:100]  # Limit snippet length
            ))

        # JSF Managed Beans
        bean_match = re.search(r'#\{(\w+)\.(\w+)', line)
        if bean_match:
            bean_name = bean_match.group(1)
            method_name = bean_match.group(2)

            # Add as method reference
            self.components['methods'].append(CodeComponent(
                name=method_name,
                type='jsf_binding',
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature=line.strip(),
                parent_class=bean_name,
                snippet=line.strip()
            ))

        # JSF Validators
        validator_match = re.search(r'<f:validate(\w+)', line)
        if validator_match:
            self.components['configs'].append(CodeComponent(
                name=f"JSF_{validator_match.group(1)}",
                type='jsf_validator',
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature=line.strip(),
                snippet=line.strip()
            ))

        # JSTL conditions (business logic)
        jstl_match = re.search(r'<c:(?:if|when|forEach|choose)', line)
        if jstl_match:
            self.components['configs'].append(CodeComponent(
                name=f"JSTL_{jstl_match.group(0)[3:]}",
                type='jstl_logic',
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature=line.strip(),
                snippet=line.strip()
            ))

    def _extract_javascript_components(self, line: str, file_path: str, repomix_line: int,
                                      relative_line: int):
        """Extract JavaScript/TypeScript components"""

        # Classes
        class_match = re.match(r'\s*(export\s+)?(class|interface)\s+(\w+)', line)
        if class_match:
            component_type = class_match.group(2)
            name = class_match.group(3)

            target = 'interfaces' if component_type == 'interface' else 'classes'
            self.components[target].append(CodeComponent(
                name=name,
                type=component_type,
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature=line.strip(),
                snippet=line.strip()
            ))

        # Functions
        func_match = re.match(r'\s*(export\s+)?(async\s+)?(function\s+)?(\w+)\s*[=:]\s*(async\s+)?(\([^)]*\)|function)', line)
        if func_match and func_match.group(4) not in ['if', 'while', 'for', 'switch']:
            self.components['methods'].append(CodeComponent(
                name=func_match.group(4),
                type='function',
                file_path=file_path,
                repomix_line=repomix_line + 1,
                original_line=relative_line,
                signature=line.strip(),
                snippet=line.strip()
            ))

    def _extract_config_values(self, line: str, file_path: str, repomix_line: int,
                              relative_line: int):
        """Extract configuration values"""

        # Properties files
        if file_path.endswith('.properties'):
            config_match = re.match(r'([^#=\s]+)\s*=\s*(.+)', line)
            if config_match:
                self.components['configs'].append(CodeComponent(
                    name=config_match.group(1),
                    type='property',
                    file_path=file_path,
                    repomix_line=repomix_line + 1,
                    original_line=relative_line,
                    signature=line.strip(),
                    snippet=config_match.group(2).strip()
                ))

        # YAML files
        elif file_path.endswith(('.yml', '.yaml')):
            config_match = re.match(r'\s*([^:#]+):\s*(.+)', line)
            if config_match and not line.strip().startswith('#'):
                self.components['configs'].append(CodeComponent(
                    name=config_match.group(1).strip(),
                    type='yaml_config',
                    file_path=file_path,
                    repomix_line=repomix_line + 1,
                    original_line=relative_line,
                    signature=line.strip(),
                    snippet=config_match.group(2).strip()
                ))

    def export_to_json(self, output_path: str = "output/context/codebase-citations.json"):
        """Export extracted components to JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert dataclasses to dicts
        export_data = {}
        for key, components in self.components.items():
            export_data[key] = [asdict(c) for c in components]

        # Add metadata (will be updated by caller if needed)
        export_data["metadata"] = {}

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

        print(f"✅ Exported citations to {output_file}")
        return export_data


if __name__ == "__main__":
    # Test the parser
    parser = RepomixParser()
    if parser.load():
        parser.extract_all_components()
        parser.export_to_json()