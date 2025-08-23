#!/usr/bin/env python3
"""
Bash Command Logger Hook for Claude Code
Logs all bash commands with descriptions to the logs directory
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path


def log_bash_command():
    """Log bash command and description to log file"""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Extract command and description from tool input
        tool_input = input_data.get('tool_input', {})
        command = tool_input.get('command', '')
        description = tool_input.get('description', 'No description')
        
        # Get project directory
        project_dir = Path(os.getenv('CLAUDE_PROJECT_DIR', Path.cwd()))
        
        # Create logs directory if it doesn't exist
        log_dir = project_dir / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Log file path
        log_file = log_dir / 'bash-command-log.txt'
        
        # Format log entry with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {command} - {description}\n"
        
        # Append to log file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Exit successfully to allow command to proceed
        sys.exit(0)
        
    except json.JSONDecodeError:
        # If JSON parsing fails, log error but don't block command
        try:
            error_log = log_dir / 'bash-command-log-errors.txt'
            with open(error_log, 'a') as f:
                f.write(f"[{datetime.now()}] JSON decode error\n")
        except:
            pass
        sys.exit(0)
        
    except Exception as e:
        # Log any other errors but don't block command
        try:
            error_log = log_dir / 'bash-command-log-errors.txt'
            with open(error_log, 'a') as f:
                f.write(f"[{datetime.now()}] Error: {e}\n")
        except:
            pass
        sys.exit(0)


if __name__ == "__main__":
    log_bash_command()