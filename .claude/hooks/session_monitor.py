#!/usr/bin/env python3
"""
Session Monitor Hook for Claude Code
Monitors Claude's responses for patterns indicating user input is needed
Best used with UserPromptSubmit hook
"""

import sys
import json
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime

class SessionMonitor:
    """Monitor Claude session for interaction patterns"""
    
    def __init__(self):
        self.project_dir = Path(os.getenv('CLAUDE_PROJECT_DIR', Path.cwd()))
        self.state_file = self.project_dir / '.claude' / '.session_state'
        self.notification_script = self.project_dir / '.claude' / 'hooks' / 'notifications.py'
    
    def check_for_input_request(self):
        """
        Check if Claude's recent output suggests waiting for input
        This would need to hook into Claude's output stream
        """
        # Interactive prompt patterns
        interactive_patterns = [
            r"Do you want to proceed\?",
            r"❯\s+\d+\.\s+Yes",  # Claude's interactive prompt format
            r"❯\s+\d+\.\s+No",
            r"Please (choose|select)",
            r"Would you like",
            r"Shall I",
            r"Ready to (continue|proceed)",
            r"Confirm your",
            r"Enter your",
            r"Type 'yes' to confirm"
        ]
        
        try:
            # Try to read recent output from stdin
            input_data = json.load(sys.stdin)
            
            # Get Claude's last response if available
            response = input_data.get('response', '')
            
            # Check for interactive patterns
            for pattern in interactive_patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    return True
                    
        except Exception:
            pass
        
        return False
    
    def send_notification(self, message="Claude is waiting for your response"):
        """Send notification"""
        if self.notification_script.exists():
            subprocess.run([
                sys.executable,
                str(self.notification_script),
                message,
                "--title", "Input Required",
                "--method", "all"
            ], capture_output=True)
    
    def update_state(self, waiting=False):
        """Track session state"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'waiting_for_input': waiting
            }
            self.state_file.parent.mkdir(exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        except Exception:
            pass

def main():
    """Main entry point"""
    monitor = SessionMonitor()
    
    if monitor.check_for_input_request():
        monitor.send_notification()
        monitor.update_state(waiting=True)
    else:
        monitor.update_state(waiting=False)
    
    # Always allow continuation
    sys.exit(0)

if __name__ == "__main__":
    main()