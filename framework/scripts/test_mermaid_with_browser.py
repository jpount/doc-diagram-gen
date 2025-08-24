#!/usr/bin/env python3
"""
Test Mermaid diagrams by actually rendering them in a browser
This mimics what document-viewer.html does
"""

import os
import sys
import json
import time
import tempfile
from pathlib import Path
from typing import List, Tuple

def create_test_html(diagram_files: List[Path]) -> str:
    """Create an HTML file that tests all diagrams"""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mermaid Diagram Test</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .test-result { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .diagram-container { margin: 20px 0; padding: 10px; border: 1px solid #ddd; }
        .error-details { font-family: monospace; font-size: 12px; margin-top: 10px; }
        pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Mermaid Diagram Validation</h1>
    <div id="results"></div>
    
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
        
        // Diagram content to test
        const diagrams = [
"""
    
    # Add each diagram file
    for file_path in diagram_files:
        with open(file_path, 'r') as f:
            content = f.read()
            # Escape for JavaScript
            content = content.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
            html += f"            {{\n"
            html += f"                name: '{file_path.name}',\n"
            html += f"                content: `{content}`\n"
            html += f"            }},\n"
    
    html += """        ];
        
        // Test results
        const results = [];
        let successCount = 0;
        let errorCount = 0;
        
        async function testDiagrams() {
            const resultsDiv = document.getElementById('results');
            
            for (const diagram of diagrams) {
                const resultDiv = document.createElement('div');
                resultDiv.className = 'test-result';
                
                try {
                    // Try to render the diagram
                    const diagramId = 'test-' + Math.random().toString(36).substr(2, 9);
                    const { svg } = await mermaid.render(diagramId, diagram.content);
                    
                    // Success
                    resultDiv.className += ' success';
                    resultDiv.innerHTML = `✅ <strong>${diagram.name}</strong> - Valid`;
                    successCount++;
                    results.push({name: diagram.name, status: 'success'});
                } catch (error) {
                    // Error
                    resultDiv.className += ' error';
                    resultDiv.innerHTML = `
                        ❌ <strong>${diagram.name}</strong> - Invalid
                        <div class="error-details">
                            Error: ${error.message || error}
                        </div>
                    `;
                    errorCount++;
                    results.push({
                        name: diagram.name, 
                        status: 'error', 
                        error: error.message || error.toString()
                    });
                    
                    // Log for debugging
                    console.error(`Error in ${diagram.name}:`, error);
                    console.log('Diagram content:', diagram.content.substring(0, 200));
                }
                
                resultsDiv.appendChild(resultDiv);
            }
            
            // Summary
            const summaryDiv = document.createElement('div');
            summaryDiv.style.marginTop = '20px';
            summaryDiv.style.padding = '15px';
            summaryDiv.style.background = successCount === diagrams.length ? '#d4edda' : '#f8d7da';
            summaryDiv.style.borderRadius = '5px';
            summaryDiv.innerHTML = `
                <h2>Summary</h2>
                <p>Total: ${diagrams.length} diagrams</p>
                <p>✅ Valid: ${successCount}</p>
                <p>❌ Invalid: ${errorCount}</p>
            `;
            resultsDiv.insertBefore(summaryDiv, resultsDiv.firstChild);
            
            // Save results to console for Python to read
            console.log('TEST_RESULTS:' + JSON.stringify(results));
        }
        
        // Run tests when page loads
        window.addEventListener('load', testDiagrams);
    </script>
</body>
</html>"""
    
    return html

def test_diagrams_in_browser(diagram_dir: Path) -> List[dict]:
    """Test diagrams by opening them in a browser"""
    
    # Get all .mmd files
    diagram_files = list(diagram_dir.glob("*.mmd"))
    
    if not diagram_files:
        print("No .mmd files found")
        return []
    
    print(f"Testing {len(diagram_files)} diagrams with actual Mermaid.js...")
    
    # Create test HTML
    html_content = create_test_html(diagram_files)
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_file = f.name
    
    print(f"Created test file: {temp_file}")
    print("Open this file in a browser to see the test results")
    print("\nOr use this command to open in default browser:")
    
    if sys.platform == 'darwin':  # macOS
        print(f"  open {temp_file}")
    elif sys.platform == 'win32':  # Windows
        print(f"  start {temp_file}")
    else:  # Linux
        print(f"  xdg-open {temp_file}")
    
    print("\nThe test will show:")
    print("- ✅ for diagrams that render successfully")
    print("- ❌ for diagrams with errors (with error details)")
    
    # Try to open automatically
    try:
        import webbrowser
        webbrowser.open(f"file://{temp_file}")
        print("\nOpened in browser automatically")
    except:
        pass
    
    return []

def main():
    """Main function"""
    output_dir = Path("output/diagrams")
    
    if not output_dir.exists():
        print(f"Directory {output_dir} not found")
        return 1
    
    test_diagrams_in_browser(output_dir)
    
    print("\n" + "="*60)
    print("Check the browser window for detailed results")
    print("This shows EXACTLY what errors you'll see in document-viewer.html")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())