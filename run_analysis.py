#!/usr/bin/env python3
"""
Simple run_analysis function for hands-off execution
Matches the agents specified in CLAUDE.md
"""

import subprocess
import sys
from pathlib import Path

def run_analysis(agents):
    """
    Run the specified agents in sequence using Claude Code
    
    Args:
        agents: List of agent names to execute in order
    """
    
    print(f"🤖 Running analysis with agents: {agents}")
    
    project_root = Path(__file__).parent
    failed_agents = []
    completed_agents = []
    
    for i, agent in enumerate(agents, 1):
        print(f"\n[{i}/{len(agents)}] Running @{agent}...")
        
        try:
            # Execute agent using Claude Code CLI
            result = subprocess.run([
                'claude',
                '--output-format', 'text', 
                '--dangerously-skip-permissions',
                '--print',  # Non-interactive mode
                f'@{agent}'
            ], 
            cwd=str(project_root),
            check=True,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
            )
            
            print(f"✅ {agent} completed successfully")
            completed_agents.append(agent)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {agent} failed with exit code {e.returncode}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            failed_agents.append(agent)
            
        except subprocess.TimeoutExpired:
            print(f"❌ {agent} timed out after 30 minutes")
            failed_agents.append(agent)
            
        except Exception as e:
            print(f"❌ {agent} failed with error: {e}")
            failed_agents.append(agent)
    
    # Summary
    print(f"\n📊 Analysis Summary:")
    print(f"✅ Completed: {len(completed_agents)}")
    print(f"❌ Failed: {len(failed_agents)}")
    
    if completed_agents:
        print(f"\nSuccessful agents: {', '.join(completed_agents)}")
    
    if failed_agents:
        print(f"\nFailed agents: {', '.join(failed_agents)}")
        
    # Return success if at least one agent completed
    return len(completed_agents) > 0

if __name__ == "__main__":
    import json
    
    # Try to read agents from analysis_config.json (created by setup.py)
    config_file = Path(__file__).parent / "analysis_config.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                configured_agents = config.get("selected_agents", [])
            print(f"📋 Using agents from analysis_config.json: {configured_agents}")
            default_agents = configured_agents
        except Exception as e:
            print(f"⚠️  Error reading analysis_config.json: {e}")
            print("🔄 Using fallback default agents")
            default_agents = ['solution-architect', 'technical-architect', 'business-logic-analyst']
    else:
        print(f"⚠️  analysis_config.json not found, using fallback agents")
        default_agents = ['solution-architect', 'technical-architect', 'business-logic-analyst']
    
    # Use command line args if provided, otherwise use config or defaults
    if len(sys.argv) > 1:
        agents = sys.argv[1:]
        print(f"🎯 Using command line agents: {agents}")
    else:
        agents = default_agents
        
    success = run_analysis(agents)
    sys.exit(0 if success else 1)