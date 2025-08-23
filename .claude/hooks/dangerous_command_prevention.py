#!/usr/bin/env python3
"""
Dangerous Command Prevention Hook for Claude Code
Blocks potentially dangerous bash commands
"""

import json
import sys
import re
import os
from datetime import datetime
from pathlib import Path


def log_message(message):
    """Log security events to the security log file"""
    log_dir = Path(os.getenv('CLAUDE_PROJECT_DIR', '')) / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'security.log'
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] DANGEROUS_COMMAND_PREVENTION: {message}\n")


def get_dangerous_patterns():
    """Define dangerous command patterns that should be blocked"""
    return [
        # Destructive file operations
        r'rm\s+-rf\s+/',
        r'rm\s+-rf\s+\*',
        r'rm\s+-rf\s+~',
        r'rm\s+-rf\s+\.',
        
        # System modification commands
        r'chmod\s+777',
        r'chmod\s+-R\s+777',
        r'chown\s+-R\s+root',
        
        # Password/authentication manipulation
        r'passwd\s+root',
        r'su\s+-',
        r'sudo\s+su',
        
        # Network and system access
        r'ssh\s+.*@.*\s+(rm|dd|mkfs)',
        r'curl\s+.*\|\s*sh',
        r'wget\s+.*\|\s*sh',
        r'bash\s+<\(curl',
        r'bash\s+<\(wget',
        
        # Disk operations
        r'dd\s+if=.*\s+of=/dev/',
        r'mkfs\.',
        r'fdisk',
        r'parted',
        
        # Process manipulation
        r'kill\s+-9\s+1',
        r'killall\s+-9',
        
        # System service manipulation
        r'systemctl\s+disable',
        r'systemctl\s+stop\s+(ssh|network|firewall)',
        r'service\s+.*\s+stop',
        
        # Cron job manipulation
        r'crontab\s+-r',
        
        # Package management (potentially dangerous)
        r'apt-get\s+remove\s+.*essential',
        r'yum\s+remove\s+.*kernel',
        r'brew\s+uninstall\s+.*bash',
        
        # File system manipulation
        r'mount\s+.*\s+/',
        r'umount\s+/',
        
        # History manipulation
        r'history\s+-c',
        r'unset\s+HISTFILE',
        
        # Binary downloads and execution
        r'curl\s+.*\s+-o\s+/usr/bin/',
        r'wget\s+.*\s+-O\s+/usr/bin/',
        
        # Firewall manipulation
        r'iptables\s+-F',
        r'ufw\s+disable',
        
        # Kernel module manipulation
        r'rmmod',
        r'modprobe\s+-r',
    ]


def get_suspicious_patterns():
    """Define suspicious patterns that should trigger warnings"""
    return [
        r'rm\s+-rf',
        r'sudo\s+',
        r'curl\s+.*\|\s*bash',
        r'wget\s+.*\|\s*bash',
        r'chmod\s+\+x\s+/tmp/',
        r'cp\s+.*\s+/usr/bin/',
        r'mv\s+.*\s+/usr/bin/',
        r'.*>\s*/dev/null\s+2>&1',
        r'nohup\s+.*&',
    ]


def get_critical_directories():
    """Define critical directories that commands should not target"""
    return [
        '/etc/',
        '/usr/bin/',
        '/usr/sbin/',
        '/bin/',
        '/sbin/',
        '/boot/',
        '/System/',
        '/Library/System/',
    ]


def get_security_files():
    """Define security-related files that should be protected"""
    return [
        '/etc/passwd',
        '/etc/shadow',
        '/etc/sudoers',
        '/etc/ssh/sshd_config',
        '/etc/hosts',
        '/etc/resolv.conf',
        '~/.ssh/authorized_keys',
        '~/.ssh/id_rsa',
        '~/.aws/credentials',
    ]


def check_dangerous_patterns(command):
    """Check command against dangerous patterns"""
    dangerous_patterns = get_dangerous_patterns()
    
    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            log_message(f"SECURITY ALERT: Dangerous command blocked - Pattern: {pattern}")
            print(f"SECURITY ALERT: Dangerous command blocked!", file=sys.stderr)
            print(f"Command: {command}", file=sys.stderr)
            print(f"Matched pattern: {pattern}", file=sys.stderr)
            print("This command could cause system damage or security compromise.", file=sys.stderr)
            print("If you need to run this command, please review it carefully and run it manually.", file=sys.stderr)
            return False
    
    return True


def check_suspicious_patterns(command):
    """Check command against suspicious patterns (warnings only)"""
    suspicious_patterns = get_suspicious_patterns()
    
    for pattern in suspicious_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            log_message(f"WARNING: Suspicious command detected - Pattern: {pattern}")
            print(f"WARNING: Potentially risky command detected:", file=sys.stderr)
            print(f"Command: {command}", file=sys.stderr)
            print(f"Matched pattern: {pattern}", file=sys.stderr)
            print("Please review this command carefully.", file=sys.stderr)
            print("Continuing execution...", file=sys.stderr)
            break


def check_critical_directories(command):
    """Check if command targets critical system directories"""
    critical_dirs = get_critical_directories()
    
    for directory in critical_dirs:
        pattern = rf'(rm|mv|cp|chmod|chown).*{re.escape(directory)}'
        if re.search(pattern, command, re.IGNORECASE):
            log_message(f"SECURITY ALERT: Command targets critical system directory: {directory}")
            print(f"SECURITY ALERT: Command targets critical system directory!", file=sys.stderr)
            print(f"Command: {command}", file=sys.stderr)
            print(f"Critical directory: {directory}", file=sys.stderr)
            print("This operation could compromise system stability.", file=sys.stderr)
            return False
    
    return True


def check_security_files(command):
    """Check if command targets security-related files"""
    security_files = get_security_files()
    
    for file_path in security_files:
        # Escape special regex characters in file path
        escaped_path = re.escape(file_path)
        pattern = rf'(rm|mv|cp|chmod|chown|echo.*>|cat.*>).*{escaped_path}'
        if re.search(pattern, command, re.IGNORECASE):
            log_message(f"SECURITY ALERT: Command targets security-sensitive file: {file_path}")
            print(f"SECURITY ALERT: Command targets security-sensitive file!", file=sys.stderr)
            print(f"Command: {command}", file=sys.stderr)
            print(f"Security file: {file_path}", file=sys.stderr)
            print("This operation could compromise system security.", file=sys.stderr)
            return False
    
    return True


def check_command_chaining(command):
    """Check for dangerous command chaining"""
    chaining_pattern = r';\s*(rm|dd|mkfs|fdisk)'
    if re.search(chaining_pattern, command, re.IGNORECASE):
        log_message("SECURITY ALERT: Command chaining with dangerous operations detected")
        print("SECURITY ALERT: Dangerous command chaining detected!", file=sys.stderr)
        print(f"Command: {command}", file=sys.stderr)
        print("Command chaining with destructive operations is not allowed.", file=sys.stderr)
        return False
    
    return True


def check_environment_manipulation(command):
    """Check for potentially dangerous environment variable manipulation"""
    env_pattern = r'(export|unset)\s+(PATH|LD_LIBRARY_PATH|HOME)'
    if re.search(env_pattern, command, re.IGNORECASE):
        log_message("WARNING: Environment variable manipulation detected")
        print("WARNING: Environment variable manipulation detected:", file=sys.stderr)
        print(f"Command: {command}", file=sys.stderr)
        print("Modifying system environment variables can affect security.", file=sys.stderr)


def validate_command(command):
    """Main validation function for bash commands"""
    if not command:
        log_message("No command provided for analysis")
        return True
    
    log_message(f"Analyzing command: {command}")
    
    # Check for dangerous patterns (blocking)
    if not check_dangerous_patterns(command):
        return False
    
    # Check for critical directory access (blocking)
    if not check_critical_directories(command):
        return False
    
    # Check for security file access (blocking)
    if not check_security_files(command):
        return False
    
    # Check for command chaining (blocking)
    if not check_command_chaining(command):
        return False
    
    # Check for suspicious patterns (warnings only)
    check_suspicious_patterns(command)
    
    # Check for environment manipulation (warnings only)
    check_environment_manipulation(command)
    
    log_message(f"Command security check passed: {command}")
    return True


def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Extract command from tool input
        tool_input = input_data.get('tool_input', {})
        command = tool_input.get('command', '')
        
        # Validate the command
        if validate_command(command):
            sys.exit(0)  # Allow command
        else:
            sys.exit(2)  # Block command
    
    except json.JSONDecodeError:
        log_message("Invalid JSON input received")
        sys.exit(1)
    except Exception as e:
        log_message(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()