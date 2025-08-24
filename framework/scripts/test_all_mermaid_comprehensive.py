#!/usr/bin/env python3
"""
Comprehensive test for ALL Mermaid diagrams - both .mmd files and embedded in .md files
Tests them exactly as they would render in a browser with Mermaid.js
"""

import os
import re
import sys
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

def create_comprehensive_test_html(standalone: List[Dict], embedded: List[Dict]) -> str:
    """Create an HTML file that tests all diagrams"""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Comprehensive Mermaid Diagram Test</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; 
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        h2 { 
            color: #666; 
            border-bottom: 2px solid #ddd; 
            padding-bottom: 10px;
            margin-top: 30px;
        }
        .summary {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .test-result { 
            margin: 10px 0; 
            padding: 15px; 
            border-radius: 5px;
            background: white;
            border-left: 4px solid #ddd;
        }
        .success { 
            background: #f0f9ff;
            border-left-color: #4caf50;
        }
        .error { 
            background: #fef2f2;
            border-left-color: #f44336;
        }
        .file-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .path {
            font-size: 0.9em;
            color: #666;
            font-family: monospace;
        }
        .error-details { 
            font-family: 'Courier New', monospace; 
            font-size: 13px; 
            margin-top: 10px;
            padding: 10px;
            background: #fff;
            border: 1px solid #ffcdd2;
            border-radius: 4px;
            color: #c62828;
        }
        .diagram-preview {
            margin-top: 10px;
            padding: 10px;
            background: #fafafa;
            border: 1px solid #ddd;
            border-radius: 4px;
            max-height: 200px;
            overflow: auto;
        }
        pre {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .stats {
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }
        .stat {
            flex: 1;
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        .success-stat { color: #4caf50; }
        .error-stat { color: #f44336; }
        .total-stat { color: #2196f3; }
        
        details {
            margin-top: 10px;
        }
        summary {
            cursor: pointer;
            color: #2196f3;
            font-size: 0.9em;
        }
        summary:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>🔍 Comprehensive Mermaid Diagram Validation</h1>
    
    <div class="summary" id="summary">
        <div class="stats">
            <div class="stat">
                <div class="stat-number total-stat" id="totalCount">0</div>
                <div class="stat-label">Total Diagrams</div>
            </div>
            <div class="stat">
                <div class="stat-number success-stat" id="successCount">0</div>
                <div class="stat-label">✅ Valid</div>
            </div>
            <div class="stat">
                <div class="stat-number error-stat" id="errorCount">0</div>
                <div class="stat-label">❌ Errors</div>
            </div>
        </div>
    </div>
    
    <h2>Standalone Diagrams (.mmd files)</h2>
    <div id="standaloneResults"></div>
    
    <h2>Embedded Diagrams (in .md files)</h2>
    <div id="embeddedResults"></div>
    
    <script>
        // Initialize mermaid with same settings as document-viewer.html
        mermaid.initialize({ 
            startOnLoad: false,
            theme: 'default',
            themeVariables: {
                fontFamily: 'arial, sans-serif'
            },
            flowchart: { 
                useMaxWidth: true, 
                htmlLabels: true,
                curve: 'basis'
            },
            sequence: { useMaxWidth: true },
            gantt: { useMaxWidth: true },
            er: { useMaxWidth: true },
            journey: { useMaxWidth: true },
            gitgraph: { useMaxWidth: true },
            c4: { useMaxWidth: true }
        });
        
        // Standalone diagrams
        const standaloneDiagrams = [
"""
    
    # Add standalone diagrams
    for diagram in standalone:
        content = diagram['content'].replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        html += f"""            {{
                file: '{diagram['file']}',
                path: '{diagram['path']}',
                content: `{content}`
            }},
"""
    
    html += """        ];
        
        // Embedded diagrams
        const embeddedDiagrams = [
"""
    
    # Add embedded diagrams
    for diagram in embedded:
        content = diagram['content'].replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        html += f"""            {{
                file: '{diagram['file']}',
                path: '{diagram['path']}',
                index: {diagram['index']},
                content: `{content}`
            }},
"""
    
    html += """        ];
        
        // Test results
        let totalCount = 0;
        let successCount = 0;
        let errorCount = 0;
        const allErrors = [];
        
        async function testDiagrams() {
            // Test standalone diagrams
            const standaloneDiv = document.getElementById('standaloneResults');
            for (const diagram of standaloneDiagrams) {
                totalCount++;
                const result = await testSingleDiagram(diagram, 'standalone');
                standaloneDiv.appendChild(result);
            }
            
            // Test embedded diagrams
            const embeddedDiv = document.getElementById('embeddedResults');
            for (const diagram of embeddedDiagrams) {
                totalCount++;
                const result = await testSingleDiagram(diagram, 'embedded');
                embeddedDiv.appendChild(result);
            }
            
            // Update summary
            document.getElementById('totalCount').textContent = totalCount;
            document.getElementById('successCount').textContent = successCount;
            document.getElementById('errorCount').textContent = errorCount;
            
            // Log results for command line
            console.log('=== TEST RESULTS ===');
            console.log(`Total: ${totalCount}, Valid: ${successCount}, Errors: ${errorCount}`);
            if (allErrors.length > 0) {
                console.log('\\nErrors found in:');
                allErrors.forEach(err => {
                    console.log(`- ${err.file}: ${err.error}`);
                });
            }
        }
        
        async function testSingleDiagram(diagram, type) {
            const resultDiv = document.createElement('div');
            resultDiv.className = 'test-result';
            
            try {
                // Try to render the diagram
                const diagramId = 'test-' + Math.random().toString(36).substr(2, 9);
                const { svg } = await mermaid.render(diagramId, diagram.content);
                
                // Success
                resultDiv.className += ' success';
                successCount++;
                
                let label = type === 'embedded' 
                    ? `${diagram.file} (Diagram #${diagram.index})` 
                    : diagram.file;
                    
                resultDiv.innerHTML = `
                    <div class="file-name">✅ ${label}</div>
                    <div class="path">Path: ${diagram.path}</div>
                `;
                
            } catch (error) {
                // Error
                resultDiv.className += ' error';
                errorCount++;
                
                let label = type === 'embedded' 
                    ? `${diagram.file} (Diagram #${diagram.index})` 
                    : diagram.file;
                
                allErrors.push({
                    file: label,
                    path: diagram.path,
                    error: error.message || error.toString()
                });
                
                // Get first line of diagram for context
                const firstLines = diagram.content.split('\\n').slice(0, 3).join('\\n');
                
                resultDiv.innerHTML = `
                    <div class="file-name">❌ ${label}</div>
                    <div class="path">Path: ${diagram.path}</div>
                    <div class="error-details">
                        <strong>Error:</strong> ${error.message || error}
                    </div>
                    <details>
                        <summary>View diagram source (first 3 lines)</summary>
                        <div class="diagram-preview">
                            <pre>${firstLines}</pre>
                        </div>
                    </details>
                `;
                
                // Log for debugging
                console.error(`Error in ${label}:`, error.message);
            }
            
            return resultDiv;
        }
        
        // Run tests when page loads
        window.addEventListener('load', testDiagrams);
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
    
    print("Collecting all Mermaid diagrams...")
    standalone, embedded = collect_all_diagrams(output_dir)
    
    print(f"Found {len(standalone)} standalone .mmd files")
    print(f"Found {len(embedded)} embedded diagrams in .md files")
    print(f"Total: {len(standalone) + len(embedded)} diagrams to test")
    
    # Create test HTML
    html_content = create_comprehensive_test_html(standalone, embedded)
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_file = f.name
    
    print(f"\nCreated comprehensive test file: {temp_file}")
    print("\nOpen this file in a browser to see detailed results for ALL diagrams")
    print("Including both standalone .mmd files and embedded diagrams in .md files")
    
    # Try to open automatically
    try:
        import webbrowser
        webbrowser.open(f"file://{temp_file}")
        print("\n✅ Opened in browser automatically")
    except:
        print("\nOpen manually with:")
        if sys.platform == 'darwin':
            print(f"  open {temp_file}")
        elif sys.platform == 'win32':
            print(f"  start {temp_file}")
        else:
            print(f"  xdg-open {temp_file}")
    
    print("\n" + "="*60)
    print("This test shows EXACTLY what will render in document-viewer.html")
    print("Check the browser for:")
    print("  - Summary statistics")
    print("  - Detailed error messages")
    print("  - File paths for each diagram")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())