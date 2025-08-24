# Mermaid Validation Process

## Overview
A streamlined 3-step validation process ensures all Mermaid diagrams work correctly.

## Step 1: Prevention (During Generation)
**File**: `framework/docs/MERMAID_STRICT_RULES.md`
**When**: As agents write diagrams
**Purpose**: Prevent errors from being introduced

Agents follow strict rules to generate valid diagrams:
- Start with diagram type declaration
- Use proper node IDs (alphanumeric, no hyphens)
- Comments at column 1 only
- Proper string escaping
- No tabs, proper spacing

## Step 2: Pre-Write Validation (Automatic Hook)
**File**: `.claude/hooks/simple_mermaid_validation.py`
**When**: Automatically before any file write
**Purpose**: Apply safe fixes to ensure compatibility

Applies browser-compatible fixes:
- Removes trailing whitespace
- Fixes comment indentation
- Ensures proper line endings
- Reduces excessive blank lines
- Fixes common syntax issues

## Step 3: Final Validation (Manual/Post-Generation)
**File**: `framework/scripts/simple_mermaid_validator.py`
**When**: After all generation is complete
**Purpose**: Comprehensive validation of all diagrams

```bash
# Validate all diagrams in output directory
python3 framework/scripts/simple_mermaid_validator.py output/

# Auto-fix any remaining issues
python3 framework/scripts/simple_mermaid_validator.py output/ --fix

# Validate specific file
python3 framework/scripts/simple_mermaid_validator.py output/diagrams/architecture.mmd
```

## File Structure (Simplified)

```
.claude/hooks/
└── simple_mermaid_validation.py  # Pre-write hook (automatic)

framework/
├── docs/
│   └── MERMAID_STRICT_RULES.md   # Prevention rules for agents
└── scripts/
    └── simple_mermaid_validator.py # Final validation tool
```

## Testing Diagrams

Use the browser-based viewer for visual testing:
1. Open `framework/document-viewer.html` in a browser
2. Load your output directory
3. View all diagrams rendered as they would appear in documentation

## Common Issues and Fixes

| Issue | Prevention | Auto-Fix |
|-------|------------|----------|
| Indented comments | Write at column 1 | ✅ Fixed by hook |
| Trailing whitespace | Don't add spaces at line end | ✅ Fixed by hook |
| Missing newline at EOF | Always end with newline | ✅ Fixed by hook |
| Numeric-only node IDs | Use alphanumeric IDs | ❌ Must fix in source |
| Hyphens in node IDs | Use underscores instead | ❌ Must fix in source |

## Quick Commands

```bash
# Check if all diagrams are valid
python3 framework/scripts/simple_mermaid_validator.py output/

# Fix all fixable issues
python3 framework/scripts/simple_mermaid_validator.py output/ --fix

# View in browser
open framework/document-viewer.html
```

## Notes
- The hook runs automatically - no manual intervention needed
- Most issues are fixed automatically
- Remaining issues require manual correction
- Always test in document-viewer.html for final verification