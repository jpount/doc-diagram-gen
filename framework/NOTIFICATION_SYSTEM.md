# Generic Notification System

## Overview
Created a unified notification system that provides cross-platform voice and popup notifications for Claude Code hooks. The notification message is specified directly in the hook configuration within settings.local.json.

## Features

### Cross-Platform Support
- **macOS**: Native notifications via osascript + say command for voice
- **Windows**: Toast notifications via PowerShell + Speech Synthesis for voice
- **Linux**: notify-send for popups + espeak/festival for voice
- **Fallback**: Terminal output when GUI/voice unavailable

### Notification Methods
- **Voice**: Text-to-speech announcement
- **Popup**: Desktop/toast notification
- **Terminal**: Console output (fallback)
- **All**: Try all available methods

## Implementation

### Core Script: `notifications.py`
Location: `.claude/hooks/notifications.py`

**Usage:**
```bash
python3 notifications.py "message" [options]

Options:
  --title TITLE        Notification title (default: "Claude Code")
  --method METHOD      Notification method: voice, popup, terminal, all (default: all)
```

**Features:**
- Accepts message as command-line argument
- Falls back to environment variable `NOTIFICATION_MESSAGE`
- Logs all notifications to `logs/notifications.log`
- Graceful error handling
- Cross-platform compatibility

## Hook Configuration

### In settings.local.json

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/notifications.py 'Task completed successfully!' --title 'Claude Code' --method all"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/notifications.py 'Claude Code is waiting for your input' --title 'User Input Required' --method all"
          }
        ]
      }
    ]
  }
}
```

## Supported Hook Events

### Currently Configured:
1. **Stop Hook**: Notifies when a task is completed
   - Message: "Task completed successfully!"
   - Title: "Claude Code"

2. **UserPromptSubmit Hook**: Notifies when user input is needed
   - Message: "Claude Code is waiting for your input"
   - Title: "User Input Required"

### Can Be Added:
- **PreToolUse**: Before tool execution
- **PostToolUse**: After tool execution
- **PostWrite**: After file writes
- **Error**: On errors
- **Start**: When Claude Code starts

## Notification Log

All notifications are logged to: `logs/notifications.log`

Format:
```
[YYYY-MM-DD HH:MM:SS] [METHOD] Message
```

Example:
```
[2025-08-23 18:02:31] [TERMINAL] Test notification
[2025-08-23 18:02:37] [POPUP] Test Alert: Test popup and voice
[2025-08-23 18:02:39] [VOICE] Test popup and voice
```

## Testing

### Test Commands:
```bash
# Test terminal output
python3 .claude/hooks/notifications.py "Test message" --method terminal

# Test popup notification
python3 .claude/hooks/notifications.py "Test popup" --method popup

# Test voice announcement
python3 .claude/hooks/notifications.py "Test voice" --method voice

# Test all methods
python3 .claude/hooks/notifications.py "Test all" --method all

# Custom title
python3 .claude/hooks/notifications.py "Custom test" --title "My App"
```

## Customization

### Adding New Hook Notifications

To add notifications for other events, edit `settings.local.json`:

```json
"PreToolUse": [
  {
    "matcher": "SpecificTool",
    "hooks": [
      {
        "type": "command",
        "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/notifications.py 'Starting tool execution' --title 'Tool Alert'"
      }
    ]
  }
]
```

### Customizing Messages

Simply change the message text in the command:
- Keep messages concise for voice clarity
- Use single quotes to handle spaces in messages
- Escape special characters if needed

### Changing Default Behavior

Edit the `--method` parameter:
- `voice` - Voice only
- `popup` - Visual notification only
- `terminal` - Console output only
- `all` - Try all available methods

## Platform-Specific Requirements

### macOS
- No additional requirements (uses built-in tools)

### Windows
- PowerShell (included in Windows)
- Windows 10+ for toast notifications

### Linux
- `notify-send` for desktop notifications (usually pre-installed)
- `espeak` or `festival` for voice (optional)

Install on Ubuntu/Debian:
```bash
sudo apt-get install libnotify-bin espeak
```

## Benefits Over Previous Implementation

1. **Single Script**: One notifications.py handles all notification needs
2. **Hook Configuration**: Messages defined in settings.local.json
3. **No Code Changes**: Different messages for different hooks without editing Python
4. **Flexible**: Easy to add new notification points
5. **Cross-Platform**: Works on all major operating systems
6. **Logged**: All notifications tracked in logs directory
7. **Maintainable**: Single point of maintenance

## Summary

The generic notification system provides:
- ✅ Cross-platform voice and popup notifications
- ✅ Messages configured in hook definitions
- ✅ Multiple notification methods with fallback
- ✅ Comprehensive logging
- ✅ Easy customization via settings.local.json
- ✅ No need for separate hook scripts per notification type