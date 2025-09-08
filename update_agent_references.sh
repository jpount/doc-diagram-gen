#!/bin/bash

echo "=== UPDATING ALL OLD AGENT REFERENCES ==="

# Define old agents and their replacements
declare -A AGENT_MAP
AGENT_MAP["java-architect"]="architect-agent"
AGENT_MAP["angular-architect"]="architect-agent"
AGENT_MAP["dotnet-architect"]="architect-agent"
AGENT_MAP["business-logic-analyst"]="analyst-agent"
AGENT_MAP["performance-analyst"]="analyst-agent"
AGENT_MAP["security-analyst"]="analyst-agent"
AGENT_MAP["modernization-architect"]="analyst-agent"
AGENT_MAP["legacy-code-detective"]="developer-agent"
AGENT_MAP["ui-analysis-specialist"]="architect-agent"
AGENT_MAP["data-model-specialist"]="architect-agent"
AGENT_MAP["domain-boundary-analyst"]="analyst-agent"
AGENT_MAP["api-documentation-specialist"]="doc-writer-agent"
AGENT_MAP["documentation-specialist"]="doc-writer-agent"
AGENT_MAP["executive-summary"]="doc-writer-agent"
AGENT_MAP["diagram-architect"]="diagram-agent"
AGENT_MAP["architecture-selector"]="architect-agent"

# Files to update (excluding archives)
FILES_TO_UPDATE=$(find framework n8n -type f \( -name "*.md" -o -name "*.py" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \) -not -path "*/agents_archive*" 2>/dev/null)

echo "Found $(echo "$FILES_TO_UPDATE" | wc -l) files to check/update"

# Update each file
for file in $FILES_TO_UPDATE; do
    if [[ -f "$file" ]]; then
        updated=false
        for old_agent in "${!AGENT_MAP[@]}"; do
            new_agent="${AGENT_MAP[$old_agent]}"
            
            # Replace @old-agent with @new-agent
            if grep -q "@$old_agent" "$file" 2>/dev/null; then
                sed -i.bak "s/@$old_agent/@$new_agent/g" "$file"
                updated=true
            fi
            
            # Replace "old-agent" with "new-agent" in strings
            if grep -q "\"$old_agent\"" "$file" 2>/dev/null; then
                sed -i.bak "s/\"$old_agent\"/\"$new_agent\"/g" "$file"
                updated=true
            fi
            
            # Replace 'old-agent' with 'new-agent' in strings
            if grep -q "'$old_agent'" "$file" 2>/dev/null; then
                sed -i.bak "s/'$old_agent'/'$new_agent'/g" "$file"
                updated=true
            fi
            
            # Replace old-agent: with new-agent: in YAML
            if grep -q "^[[:space:]]*$old_agent:" "$file" 2>/dev/null; then
                sed -i.bak "s/^\\([[:space:]]*\\)$old_agent:/\\1$new_agent:/" "$file"
                updated=true
            fi
        done
        
        if [[ "$updated" == true ]]; then
            echo "✅ Updated: $file"
            rm -f "$file.bak" 2>/dev/null
        fi
    fi
done

echo ""
echo "=== CHECKING FOR REMAINING OLD REFERENCES ==="
remaining=$(find framework n8n -type f \( -name "*.md" -o -name "*.py" -o -name "*.json" -o -name "*.yaml" \) -not -path "*/agents_archive*" -exec grep -l "java-architect\|angular-architect\|performance-analyst\|security-analyst\|business-logic-analyst\|documentation-specialist\|diagram-architect\|modernization-architect\|legacy-code-detective\|domain-boundary-analyst\|ui-analysis-specialist\|api-documentation-specialist\|executive-summary\|data-model-specialist\|dotnet-architect\|architecture-selector" {} \; 2>/dev/null)

if [[ -n "$remaining" ]]; then
    echo "⚠️  Files with remaining old references:"
    echo "$remaining"
else
    echo "✅ All old agent references updated successfully!"
fi

echo ""
echo "=== UPDATE COMPLETE ==="