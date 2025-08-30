#!/bin/bash
# Validate all Mermaid diagrams in the project
# This script should be run after any agent creates or modifies diagrams

echo "🔍 Validating all Mermaid diagrams..."
echo "====================================="

# Run validation
python3 framework/scripts/simple_mermaid_validator.py output/diagrams

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All diagrams are valid and ready for document-viewer.html!"
    echo "🌐 Open framework/document-viewer.html to view them"
else
    echo ""
    echo "❌ Some diagrams have validation errors!"
    echo "🔧 Run the following to see details:"
    echo "    python3 framework/scripts/simple_mermaid_validator.py output/diagrams --json"
    exit 1
fi