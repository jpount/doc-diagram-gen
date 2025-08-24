#!/usr/bin/env python3
"""
Test script for documentation configuration system.
Validates the documentation-config.json file and shows what will be generated.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

def load_config(config_path: Path) -> Dict:
    """Load the documentation configuration file"""
    if not config_path.exists():
        print(f"{Colors.RED}Error: Configuration file not found at {config_path}{Colors.RESET}")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Error: Invalid JSON in configuration file: {e}{Colors.RESET}")
        sys.exit(1)

def check_modernization_mode() -> bool:
    """Check if modernization mode is enabled"""
    analysis_mode_file = Path(__file__).parent.parent.parent / "ANALYSIS_MODE.md"
    
    if not analysis_mode_file.exists():
        return False
    
    with open(analysis_mode_file, 'r') as f:
        content = f.read()
        return "MODERNIZATION" in content

def get_enabled_documents(config: Dict, modernization_enabled: bool) -> Dict[str, List[str]]:
    """Get lists of enabled and disabled documents"""
    enabled = []
    disabled = []
    
    # Check default documents
    for doc_name, doc_info in config['documentation']['default_documents'].items():
        if doc_info['enabled']:
            enabled.append(f"{doc_name} ({doc_info['category']})")
        else:
            disabled.append(f"{doc_name} ({doc_info['category']})")
    
    # Check optional documents
    for doc_name, doc_info in config['documentation']['optional_documents'].items():
        if doc_info['enabled']:
            enabled.append(f"{doc_name} ({doc_info['category']})")
        else:
            disabled.append(f"{doc_name} ({doc_info['category']})")
    
    # Check modernization documents (only if modernization is enabled)
    if modernization_enabled:
        for doc_name, doc_info in config['documentation']['modernization_documents'].items():
            if doc_name != 'description':
                if doc_info.get('enabled', False):
                    enabled.append(f"{doc_name} ({doc_info['category']})")
                else:
                    disabled.append(f"{doc_name} ({doc_info['category']})")
    
    return {'enabled': enabled, 'disabled': disabled}

def display_configuration(config: Dict):
    """Display the current configuration"""
    print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.CYAN}║        Documentation Configuration Test Results           ║{Colors.RESET}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
    
    # Check modernization mode
    modernization_enabled = check_modernization_mode()
    mode_text = "Enabled" if modernization_enabled else "Disabled"
    mode_color = Colors.GREEN if modernization_enabled else Colors.YELLOW
    print(f"\n{Colors.MAGENTA}Modernization Mode:{Colors.RESET} {mode_color}{mode_text}{Colors.RESET}")
    
    # Get enabled/disabled documents
    doc_status = get_enabled_documents(config, modernization_enabled)
    
    # Display enabled documents
    print(f"\n{Colors.GREEN}Documents to be Generated ({len(doc_status['enabled'])}):{Colors.RESET}")
    if doc_status['enabled']:
        for doc in sorted(doc_status['enabled']):
            print(f"  ✓ {doc}")
    else:
        print(f"  {Colors.YELLOW}No documents enabled!{Colors.RESET}")
    
    # Display disabled documents
    print(f"\n{Colors.YELLOW}Documents NOT Generated ({len(doc_status['disabled'])}):{Colors.RESET}")
    if doc_status['disabled']:
        for doc in sorted(doc_status['disabled']):
            print(f"  ✗ {doc}")
    else:
        print(f"  {Colors.GREEN}All documents enabled!{Colors.RESET}")
    
    # Display generation settings
    settings = config['documentation']['generation_settings']
    print(f"\n{Colors.BLUE}Generation Settings:{Colors.RESET}")
    print(f"  Output Directory: {settings['output_directory']}")
    print(f"  File Format: {settings['file_format']}")
    print(f"  Include TOC: {settings['include_table_of_contents']}")
    print(f"  Include Metadata: {settings['include_metadata']}")
    print(f"  Include Timestamps: {settings['include_timestamps']}")
    print(f"  Max File Size: {settings['max_file_size_mb']} MB")
    print(f"  Generate Index: {settings['generate_index']}")
    
    # Category summary
    print(f"\n{Colors.MAGENTA}Category Summary:{Colors.RESET}")
    categories = config['documentation']['categories']
    for cat_name, cat_info in categories.items():
        status = "✓" if cat_info.get('default_enabled', False) else "✗"
        print(f"  {status} {cat_name}: {cat_info['description']}")

def test_agent_integration():
    """Test if the documentation-specialist agent can read the config"""
    print(f"\n{Colors.CYAN}Testing Agent Integration:{Colors.RESET}")
    
    agent_file = Path(__file__).parent.parent.parent / ".claude" / "agents" / "documentation-specialist.md"
    
    if not agent_file.exists():
        print(f"  {Colors.RED}✗ documentation-specialist agent not found{Colors.RESET}")
        return False
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Check if agent references the config file
    if "documentation-config.json" in content:
        print(f"  {Colors.GREEN}✓ Agent is configured to use documentation-config.json{Colors.RESET}")
        
        # Check for configuration loading logic
        if "Load documentation configuration" in content:
            print(f"  {Colors.GREEN}✓ Agent includes configuration loading logic{Colors.RESET}")
        else:
            print(f"  {Colors.YELLOW}⚠ Agent may need configuration loading code{Colors.RESET}")
        
        return True
    else:
        print(f"  {Colors.RED}✗ Agent does not reference documentation-config.json{Colors.RESET}")
        return False

def simulate_generation():
    """Simulate what the documentation-specialist would generate"""
    config_path = Path(__file__).parent.parent / "configs" / "documentation-config.json"
    config = load_config(config_path)
    modernization_enabled = check_modernization_mode()
    
    print(f"\n{Colors.CYAN}Simulating Documentation Generation:{Colors.RESET}")
    print(f"\n{Colors.BLUE}The documentation-specialist agent would generate:{Colors.RESET}")
    
    count = 0
    
    # Process default documents
    for doc_name, doc_info in config['documentation']['default_documents'].items():
        if doc_info['enabled']:
            count += 1
            print(f"  {count}. {doc_name}")
            print(f"     Category: {doc_info['category']}")
            print(f"     Priority: {doc_info['priority']}")
    
    # Process optional documents
    for doc_name, doc_info in config['documentation']['optional_documents'].items():
        if doc_info['enabled']:
            count += 1
            print(f"  {count}. {doc_name}")
            print(f"     Category: {doc_info['category']}")
            print(f"     Priority: {doc_info['priority']}")
    
    # Process modernization documents
    if modernization_enabled:
        for doc_name, doc_info in config['documentation']['modernization_documents'].items():
            if doc_name != 'description' and doc_info.get('enabled', False):
                count += 1
                print(f"  {count}. {doc_name}")
                print(f"     Category: {doc_info['category']}")
                print(f"     Priority: {doc_info['priority']}")
                print(f"     {Colors.BLUE}(Modernization document){Colors.RESET}")
    
    print(f"\n{Colors.GREEN}Total documents to generate: {count}{Colors.RESET}")
    
    if count == 0:
        print(f"{Colors.RED}⚠ Warning: No documents are enabled for generation!{Colors.RESET}")
        print(f"{Colors.YELLOW}Run the setup wizard to configure document selection.{Colors.RESET}")

def main():
    """Main test function"""
    print(f"{Colors.CYAN}Documentation Configuration Test{Colors.RESET}")
    print("=" * 60)
    
    # Load configuration
    config_path = Path(__file__).parent.parent / "configs" / "documentation-config.json"
    config = load_config(config_path)
    
    # Display current configuration
    display_configuration(config)
    
    # Test agent integration
    test_agent_integration()
    
    # Simulate generation
    simulate_generation()
    
    print(f"\n{Colors.GREEN}✓ Configuration test complete{Colors.RESET}")
    print(f"\n{Colors.BLUE}To modify the configuration, either:{Colors.RESET}")
    print(f"  1. Run the setup wizard: python setup.py")
    print(f"  2. Edit directly: framework/configs/documentation-config.json")

if __name__ == "__main__":
    main()