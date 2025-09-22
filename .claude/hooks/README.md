# Claude Code Hooks - Streamlined Configuration

## Active Hooks (3 Essential)

### 1. `validate_entities.py` (via framework/scripts/)
**Purpose:** Prevents hallucination in documentation and diagrams
**Trigger:** PostToolUse - after any file operation
**Features:**
- Intelligent text classification (code vs documentation language)
- Validates only actual code references
- Blocks file creation if hallucinations detected
- Provides suggestions for similar entities
- Detailed JSON reporting

### 2. `simple_mermaid_validation.py`
**Purpose:** Validates Mermaid diagram syntax
**Trigger:** PostToolUse - when .mmd or .md files are created/edited
**Features:**
- Checks diagram syntax before writing
- Applies safe formatting fixes
- Validates bracket/brace balance
- Ensures diagrams will render correctly

### 3. `notifications.py`
**Purpose:** User notifications for important events
**Triggers:**
- PreToolUse (ExitPlanMode) - Notifies when approval needed
- Stop - Notifies when task completed
**Features:**
- Desktop notifications
- Customizable messages
- Multiple notification methods

## Removed Hooks (8 Unused)

The following hooks were removed as they were not essential for the core hallucination prevention system:

1. ~~`bash_command_logger.py`~~ - Command logging (not needed)
2. ~~`business_rule_validation.py`~~ - Business rule checking (redundant with entity validation)
3. ~~`dangerous_command_prevention.py`~~ - Command blocking (not relevant)
4. ~~`debug_hook.py`~~ - Debug logging (development only)
5. ~~`documentation_completeness_check.py`~~ - Doc completeness (redundant)
6. ~~`input_detection.py`~~ - Input monitoring (not needed)
7. ~~`session_monitor.py`~~ - Session tracking (not needed)
8. ~~`token_tracking_hook.py`~~ - Token usage tracking (not needed)

## Configuration Location

All hooks are configured in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "ExitPlanMode",
        "hooks": [
          {
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/notifications.py ..."
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "command": "cd $CLAUDE_PROJECT_DIR && python3 framework/scripts/validate_entities.py --block"
          },
          {
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/simple_mermaid_validation.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/notifications.py ..."
          }
        ]
      }
    ]
  }
}
```

## Benefits of Streamlined Configuration

1. **Faster Execution**: Fewer hooks = less overhead
2. **Clearer Purpose**: Each hook has a specific, essential function
3. **Easier Maintenance**: Fewer files to maintain and update
4. **Focused on Core Goal**: Preventing hallucinations in documentation

## Testing Hooks

### Test Entity Validation:
```bash
python3 framework/scripts/validate_entities.py --agent-output output/docs/test.md
```

### Test Mermaid Validation:
```bash
echo '{"file_path": "test.mmd", "content": "graph TD\nA-->B"}' | python3 .claude/hooks/simple_mermaid_validation.py
```

### Test Notifications:
```bash
python3 .claude/hooks/notifications.py "Test message" --title "Test"
```