#!/usr/bin/env python3
"""
Input Detection Hook for Claude Code
Detects when Claude might be waiting for user input based on patterns
"""

import sys
import json
import os
import subprocess
from pathlib import Path

def detect_input_prompt(context):
    """
    Detect patterns that suggest Claude is waiting for user input
    """
    # Patterns that indicate Claude is asking for user confirmation
    input_patterns = [
        "do you want to proceed",
        "would you like me to",
        "should i continue",
        "confirm your choice",
        "please select",
        "choose an option",
        "ready to continue",
        "approve this",
        "exitplanmode",  # When exiting plan mode
        "shall i",
        "may i proceed"
    ]
    
    # Check if context suggests waiting for input
    try:
        # Read from stdin if available
        input_data = json.load(sys.stdin)
        
        # Check tool name and context
        tool_name = input_data.get('tool', '').lower()
        
        # ExitPlanMode always requires user input
        if tool_name == 'exitplanmode':
            return True
        
        # Check for patterns in parameters or context
        params_str = json.dumps(input_data.get('parameters', {})).lower()
        
        for pattern in input_patterns:
            if pattern in params_str:
                return True
                
    except Exception:
        pass
    
    return False

def send_notification():
    """Send notification that input is required"""
    notification_script = Path(os.getenv('CLAUDE_PROJECT_DIR', '')) / '.claude' / 'hooks' / 'notifications.py'
    
    if notification_script.exists():
        subprocess.run([
            sys.executable,
            str(notification_script),
            "Claude is waiting for your input",
            "--title", "Action Required",
            "--method", "all"
        ], capture_output=True)

def main():
    """Main entry point"""
    if detect_input_prompt(sys.stdin):
        send_notification()
    
    # Always allow the tool to proceed
    sys.exit(0)

if __name__ == "__main__":
    main()