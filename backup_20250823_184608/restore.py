#!/usr/bin/env python3
"""
Restore Script for Framework Backup
Restores the framework to the backed-up state
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def restore_framework(backup_dir: Path, project_dir: Path, component: str = "all"):
    """Restore framework from backup"""
    
    print(f"{Colors.BLUE}Framework Restore Utility{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 50}{Colors.RESET}\n")
    
    # Verify backup exists
    if not backup_dir.exists():
        print(f"{Colors.RED}Error: Backup directory not found: {backup_dir}{Colors.RESET}")
        return False
    
    print(f"Backup source: {backup_dir}")
    print(f"Restore target: {project_dir}\n")
    
    # Components to restore
    components = {
        "framework": {
            "source": backup_dir / "framework",
            "target": project_dir / "framework",
            "description": "Framework scripts and templates"
        },
        "claude": {
            "source": backup_dir / ".claude",
            "target": project_dir / ".claude",
            "description": "Claude agents and hooks"
        },
        "config": {
            "files": [
                (".mcp.json", "MCP configuration"),
                ("setup.py", "Python setup script"),
                ("setup.sh", "Shell setup script"),
                ("setup.ps1", "PowerShell setup script"),
                ("README.md", "Main documentation"),
                ("STRUCTURE.md", "Structure documentation")
            ],
            "description": "Configuration files"
        }
    }
    
    # Restore based on component selection
    if component == "all":
        to_restore = components.keys()
    else:
        to_restore = [component] if component in components else []
    
    if not to_restore:
        print(f"{Colors.RED}Invalid component: {component}{Colors.RESET}")
        print("Valid components: all, framework, claude, config")
        return False
    
    # Perform restoration
    for comp in to_restore:
        print(f"\n{Colors.YELLOW}Restoring {comp}...{Colors.RESET}")
        
        if comp in ["framework", "claude"]:
            source = components[comp]["source"]
            target = components[comp]["target"]
            
            if source.exists():
                # Backup current version
                if target.exists():
                    backup_name = f"{target.name}_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    backup_path = target.parent / backup_name
                    shutil.move(str(target), str(backup_path))
                    print(f"  Backed up current to: {backup_name}")
                
                # Copy from backup
                shutil.copytree(str(source), str(target))
                print(f"  {Colors.GREEN}✓ Restored {components[comp]['description']}{Colors.RESET}")
            else:
                print(f"  {Colors.YELLOW}⚠ Source not found: {source}{Colors.RESET}")
        
        elif comp == "config":
            for filename, description in components[comp]["files"]:
                source_file = backup_dir / filename
                target_file = project_dir / filename
                
                if source_file.exists():
                    # Backup current version
                    if target_file.exists():
                        backup_name = f"{filename}.before_restore"
                        shutil.copy2(str(target_file), str(target_file.parent / backup_name))
                    
                    # Copy from backup
                    shutil.copy2(str(source_file), str(target_file))
                    print(f"  {Colors.GREEN}✓ Restored {description}{Colors.RESET}")
                else:
                    print(f"  {Colors.YELLOW}⚠ File not found: {filename}{Colors.RESET}")
    
    print(f"\n{Colors.GREEN}Restoration complete!{Colors.RESET}")
    return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Restore framework from backup")
    parser.add_argument(
        "--component",
        choices=["all", "framework", "claude", "config"],
        default="all",
        help="Component to restore (default: all)"
    )
    parser.add_argument(
        "--backup-dir",
        default="backup_20250823_184608",
        help="Backup directory name"
    )
    
    args = parser.parse_args()
    
    # Determine paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    backup_dir = script_dir  # Script is in backup directory
    
    # Confirm restoration
    print(f"{Colors.YELLOW}This will restore {args.component} from backup.{Colors.RESET}")
    print(f"{Colors.YELLOW}Current files will be backed up with '_before_restore' suffix.{Colors.RESET}")
    response = input("\nProceed with restoration? (y/n): ")
    
    if response.lower() != 'y':
        print("Restoration cancelled.")
        return
    
    # Perform restoration
    success = restore_framework(backup_dir, project_dir, args.component)
    
    if success:
        print(f"\n{Colors.BLUE}Next steps:{Colors.RESET}")
        print("1. Verify restored files")
        print("2. Restart Claude Code if configuration changed")
        print("3. Test framework functionality")

if __name__ == "__main__":
    main()