#!/usr/bin/env python3
"""
Test ALL Mermaid diagrams and report specific errors
Uses puppeteer or similar to capture browser console errors
"""

import os
import re
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Tuple

def extract_embedded_diagrams(file_path: Path) -> List[Dict]:
    """Extract all Mermaid diagrams from a markdown file"""
    diagrams = []
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find all ```mermaid blocks
    pattern = r'```mermaid\s*\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for i, diagram_content in enumerate(matches):
        diagrams.append({
            'file': file_path.name,
            'index': i + 1,
            'content': diagram_content.strip()
        })
    
    return diagrams

def collect_all_diagrams(output_dir: Path) -> Tuple[List[Dict], List[Dict]]:
    """Collect all diagrams from both .mmd files and embedded in .md files"""
    standalone_diagrams = []
    embedded_diagrams = []
    
    # Collect standalone .mmd files
    for mmd_file in output_dir.rglob("*.mmd"):
        with open(mmd_file, 'r') as f:
            content = f.read()
        standalone_diagrams.append({
            'file': mmd_file.name,
            'path': str(mmd_file.relative_to(output_dir)),
            'content': content.strip()
        })
    
    # Collect embedded diagrams from .md files
    for md_file in output_dir.rglob("*.md"):
        embedded = extract_embedded_diagrams(md_file)
        for diagram in embedded:
            diagram['path'] = str(md_file.relative_to(output_dir))
            embedded_diagrams.append(diagram)
    
    return standalone_diagrams, embedded_diagrams

def create_test_html_with_error_capture(standalone: List[Dict], embedded: List[Dict]) -> str:
    """Create an HTML file that tests all diagrams and captures errors"""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mermaid Error Diagnostic</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>
    <style>
        body { font-family: arial, sans-serif; padding: 20px; }
        .error { background: #fee; padding: 10px; margin: 10px 0; border-left: 3px solid red; }
        .success { background: #efe; padding: 10px; margin: 10px 0; border-left: 3px solid green; }
        .filename { font-weight: bold; }
        .error-msg { color: red; font-family: monospace; margin-top: 5px; }
        .stats { background: #f0f0f0; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>Mermaid Diagram Error Diagnostic</h1>
    <div id="results"></div>
    
    <script>
        mermaid.initialize({ 
            startOnLoad: false,
            theme: 'default',
            themeVariables: {
                fontFamily: 'arial, sans-serif'
            },
            flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' },
            sequence: { useMaxWidth: true },
            gantt: { useMaxWidth: true },
            er: { useMaxWidth: true }
        });
        
        const allDiagrams = [
"""
    
    # Add all diagrams
    all_diagrams = []
    for diagram in standalone:
        content = diagram['content'].replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        all_diagrams.append({
            'type': 'standalone',
            'file': diagram['file'],
            'path': diagram['path'],
            'content': content
        })
    
    for diagram in embedded:
        content = diagram['content'].replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        all_diagrams.append({
            'type': 'embedded',
            'file': diagram['file'],
            'path': diagram['path'],
            'index': diagram['index'],
            'content': content
        })
    
    for i, d in enumerate(all_diagrams):
        if d['type'] == 'embedded':
            html += f"""            {{
                type: '{d['type']}',
                file: '{d['file']}',
                path: '{d['path']}',
                index: {d['index']},
                content: `{d['content']}`
            }},
"""
        else:
            html += f"""            {{
                type: '{d['type']}',
                file: '{d['file']}',
                path: '{d['path']}',
                content: `{d['content']}`
            }},
"""
    
    html += """        ];
        
        const results = document.getElementById('results');
        let errors = [];
        let successes = 0;
        
        async function testAllDiagrams() {
            for (const diagram of allDiagrams) {
                const resultDiv = document.createElement('div');
                const label = diagram.type === 'embedded' 
                    ? `${diagram.file} (Diagram #${diagram.index})` 
                    : diagram.file;
                
                try {
                    const diagramId = 'test-' + Math.random().toString(36).substr(2, 9);
                    const { svg } = await mermaid.render(diagramId, diagram.content);
                    
                    resultDiv.className = 'success';
                    resultDiv.innerHTML = `<div class="filename">✅ ${label}</div>`;
                    successes++;
                    
                } catch (error) {
                    resultDiv.className = 'error';
                    resultDiv.innerHTML = `
                        <div class="filename">❌ ${label}</div>
                        <div class="error-msg">${error.message || error}</div>
                    `;
                    
                    errors.push({
                        file: label,
                        path: diagram.path,
                        error: error.message || error.toString()
                    });
                }
                
                results.appendChild(resultDiv);
            }
            
            // Add summary
            const summary = document.createElement('div');
            summary.className = 'stats';
            summary.innerHTML = `
                <h2>Summary</h2>
                <p>Total diagrams: ${allDiagrams.length}</p>
                <p>✅ Valid: ${successes}</p>
                <p>❌ Errors: ${errors.length}</p>
            `;
            document.body.insertBefore(summary, results);
            
            // Log errors to console for easy access
            if (errors.length > 0) {
                console.log('ERRORS FOUND:');
                errors.forEach(e => {
                    console.log(`File: ${e.file}`);
                    console.log(`Path: ${e.path}`);
                    console.log(`Error: ${e.error}`);
                    console.log('---');
                });
            } else {
                console.log('ALL DIAGRAMS VALID!');
            }
            
            // Also output as JSON for parsing
            console.log('JSON_RESULTS:', JSON.stringify({
                total: allDiagrams.length,
                valid: successes,
                errors: errors.length,
                errorDetails: errors
            }));
        }
        
        window.addEventListener('load', testAllDiagrams);
    </script>
</body>
</html>"""
    
    return html

def main():
    """Main function"""
    output_dir = Path("/Users/jp/work/xxx/doc-diagram-gen/output")
    
    if not output_dir.exists():
        print(f"Directory {output_dir} not found")
        return 1
    
    print("Running Mermaid Error Diagnostic...")
    print("=" * 60)
    
    standalone, embedded = collect_all_diagrams(output_dir)
    
    print(f"Found {len(standalone)} standalone .mmd files")
    print(f"Found {len(embedded)} embedded diagrams in .md files")
    print(f"Total: {len(standalone) + len(embedded)} diagrams to test")
    
    # Create test HTML
    html_content = create_test_html_with_error_capture(standalone, embedded)
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_file = f.name
    
    print(f"\nCreated diagnostic file: {temp_file}")
    print("\nOpening in browser to capture errors...")
    
    # Try to open automatically
    try:
        import webbrowser
        webbrowser.open(f"file://{temp_file}")
        print("\n✅ Opened in browser")
        print("\nCheck the browser console for detailed error information:")
        print("  1. Open Developer Tools (F12 or Cmd+Option+I)")
        print("  2. Go to Console tab")
        print("  3. Look for 'ERRORS FOUND:' or 'ALL DIAGRAMS VALID!'")
    except:
        print("\nOpen manually with:")
        if sys.platform == 'darwin':
            print(f"  open {temp_file}")
        else:
            print(f"  xdg-open {temp_file}")
    
    print("\n" + "=" * 60)
    print("The diagnostic will show:")
    print("  - Each diagram with ✅ (valid) or ❌ (error)")
    print("  - Specific error messages for failed diagrams")
    print("  - Summary statistics")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())