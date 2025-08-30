#!/usr/bin/env python3
"""
Dynamic Analysis Limits Calculator

Calculates optimal file analysis limits based on:
- Available MCP tools (Repomix, Serena, Sourcegraph, AST)
- Project size and complexity
- User overrides
- Token budget constraints

Usage in agents:
    from framework.scripts.dynamic_limits import get_analysis_limits
    limits = get_analysis_limits(agent_name="java-architect")
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess

class DynamicLimitsCalculator:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "framework/configs/analysis-limits-config.json"
        self.config = self._load_config()
        self.project_root = Path.cwd()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load the analysis limits configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Config file not found: {self.config_path}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Fallback default configuration"""
        return {
            "analysis_limits": {
                "default_limits": {
                    "critical_files_max": 20,
                    "total_files_scan": 100,
                    "token_budget": 200000
                }
            }
        }
    
    def detect_available_mcps(self) -> Dict[str, bool]:
        """Detect which MCP tools are available"""
        mcps = {
            "repomix": False,
            "serena": False, 
            "sourcegraph": False,
            "ast": False
        }
        
        # Check Repomix
        if (self.project_root / "output" / "reports" / "repomix-summary.md").exists():
            mcps["repomix"] = True
        elif subprocess.run(["which", "repomix"], capture_output=True).returncode == 0:
            mcps["repomix"] = True
            
        # Check Serena (via MCP - look for .mcp.json or similar indicators)
        if (self.project_root / ".mcp.json").exists():
            mcps["serena"] = True
            
        # Check Sourcegraph
        if subprocess.run(["which", "src"], capture_output=True).returncode == 0:
            mcps["sourcegraph"] = True
            
        return mcps
    
    def determine_project_size(self) -> str:
        """Determine project size category"""
        try:
            # Try to get from Repomix summary first
            repomix_path = self.project_root / "output" / "reports" / "repomix-summary.md"
            if repomix_path.exists():
                with open(repomix_path, 'r') as f:
                    content = f.read()
                    if "Total lines:" in content:
                        lines_match = content.split("Total lines:")[1].split()[0].replace(',', '')
                        total_lines = int(lines_match)
                        return self._categorize_by_lines(total_lines)
            
            # Fallback: count files in codebase
            codebase_patterns = ["**/*.java", "**/*.py", "**/*.js", "**/*.ts", "**/*.cs"]
            total_files = 0
            
            for pattern in codebase_patterns:
                files = list(self.project_root.glob(pattern))
                total_files += len(files)
            
            # Estimate lines from file count
            estimated_lines = total_files * 150
            return self._categorize_by_lines(estimated_lines)
            
        except Exception as e:
            print(f"⚠️ Could not determine project size: {e}")
            return "medium"  # Safe default
    
    def _categorize_by_lines(self, lines: int) -> str:
        """Categorize project by line count"""
        if lines < 10000:
            return "small"
        elif lines < 100000:
            return "medium" 
        elif lines < 1000000:
            return "large"
        else:
            return "enterprise"
    
    def get_mcp_strategy_key(self, mcps: Dict[str, bool]) -> str:
        """Determine which MCP strategy to use"""
        if mcps["repomix"] and mcps["serena"] and mcps["sourcegraph"]:
            return "all_mcps"
        elif mcps["repomix"] and mcps["serena"]:
            return "repomix_plus_serena"
        elif mcps["repomix"]:
            return "repomix_only"
        elif mcps["serena"]:
            return "serena_only"
        else:
            return "default_limits"
    
    def load_user_overrides(self) -> Dict[str, Any]:
        """Load user overrides from file or environment variables"""
        overrides = {}
        
        # Check for override file
        override_file = self.project_root / "ANALYSIS_LIMITS_OVERRIDE.json"
        if override_file.exists():
            try:
                with open(override_file, 'r') as f:
                    file_overrides = json.load(f)
                    overrides.update(file_overrides)
                    print(f"✅ Loaded user overrides from {override_file}")
            except Exception as e:
                print(f"⚠️ Could not load override file: {e}")
        
        # Check environment variables
        env_overrides = {}
        if os.getenv("ANALYSIS_MAX_CRITICAL_FILES"):
            env_overrides["critical_files_max"] = int(os.getenv("ANALYSIS_MAX_CRITICAL_FILES"))
        if os.getenv("ANALYSIS_TOKEN_BUDGET"):
            env_overrides["token_budget"] = int(os.getenv("ANALYSIS_TOKEN_BUDGET"))
        if os.getenv("ANALYSIS_FORCE_DEEP_SCAN"):
            env_overrides["force_deep_scan"] = os.getenv("ANALYSIS_FORCE_DEEP_SCAN").lower() == "true"
        
        if env_overrides:
            print(f"✅ Loaded environment overrides: {list(env_overrides.keys())}")
            overrides.update(env_overrides)
        
        return overrides
    
    def calculate_limits(self, agent_name: str = "generic") -> Dict[str, Any]:
        """Calculate final analysis limits"""
        config = self.config["analysis_limits"]
        
        # Step 1: Detect available MCPs
        mcps = self.detect_available_mcps()
        mcp_strategy = self.get_mcp_strategy_key(mcps)
        
        # Step 2: Determine project size
        project_size = self.determine_project_size()
        
        # Step 3: Get base limits
        if mcp_strategy in config.get("mcp_optimized_limits", {}):
            base_limits = config["mcp_optimized_limits"][mcp_strategy].copy()
        else:
            base_limits = config["default_limits"].copy()
        
        # Step 4: Apply project size multiplier
        multiplier = config["project_size_multipliers"][project_size]["multiplier"]
        base_limits["critical_files_max"] = int(base_limits["critical_files_max"] * multiplier)
        base_limits["total_files_scan"] = int(base_limits["total_files_scan"] * multiplier)
        
        # Step 5: Apply agent-specific adjustments
        if agent_name in config.get("agent_specific_overrides", {}):
            agent_config = config["agent_specific_overrides"][agent_name]
            # Could apply complexity factors here based on detected frameworks
            
        # Step 6: Apply user overrides
        user_overrides = self.load_user_overrides()
        base_limits.update(user_overrides)
        
        # Step 7: Apply safety caps
        safety_caps = config["limit_calculation"]["safety_caps"]
        base_limits["critical_files_max"] = min(
            base_limits["critical_files_max"], 
            safety_caps["max_critical_files_absolute"]
        )
        base_limits["token_budget"] = min(
            base_limits["token_budget"],
            safety_caps["max_token_budget_absolute"]
        )
        
        # Add metadata
        result = {
            "limits": base_limits,
            "metadata": {
                "mcps_available": mcps,
                "mcp_strategy": mcp_strategy,
                "project_size": project_size,
                "multiplier_applied": multiplier,
                "agent_name": agent_name,
                "user_overrides_applied": list(user_overrides.keys()),
                "calculation_timestamp": __import__('datetime').datetime.now().isoformat()
            }
        }
        
        # Log the calculation
        self._log_calculation(result)
        
        return result
    
    def _log_calculation(self, result: Dict[str, Any]):
        """Log the limit calculation for user awareness"""
        limits = result["limits"]
        meta = result["metadata"]
        
        print("\n" + "="*60)
        print("🎯 DYNAMIC ANALYSIS LIMITS CALCULATED")
        print("="*60)
        print(f"📊 Project Size: {meta['project_size']} (multiplier: {meta['multiplier_applied']}x)")
        print(f"🔧 MCPs Available: {', '.join([k for k, v in meta['mcps_available'].items() if v]) or 'None'}")
        print(f"⚡ Strategy: {meta['mcp_strategy']}")
        print(f"👤 Agent: {meta['agent_name']}")
        
        if meta['user_overrides_applied']:
            print(f"🔄 User Overrides: {', '.join(meta['user_overrides_applied'])}")
        
        print(f"\n📈 FINAL LIMITS:")
        print(f"  • Critical files: {limits['critical_files_max']}")
        print(f"  • Total files scan: {limits.get('total_files_scan', 'N/A')}")
        print(f"  • Token budget: {limits['token_budget']:,}")
        
        if limits['token_budget'] > 100000:
            print(f"  ⚠️ Warning: High token budget - consider enabling more MCPs")
        
        token_savings = meta.get('token_savings_percent', 0)
        if token_savings > 0:
            print(f"  ✅ Token savings: ~{token_savings}%")
        
        print("="*60 + "\n")

def get_analysis_limits(agent_name: str = "generic", config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Public function for agents to get their analysis limits
    
    Args:
        agent_name: Name of the requesting agent (java-architect, dotnet-architect, etc.)
        config_path: Optional path to config file
    
    Returns:
        Dictionary containing limits and metadata
    """
    calculator = DynamicLimitsCalculator(config_path)
    return calculator.calculate_limits(agent_name)

def create_override_template():
    """Create a template override file for users"""
    template = {
        "_description": "User overrides for analysis limits",
        "_usage": "Modify values below to override default analysis limits",
        "critical_files_max": None,
        "total_files_scan": None, 
        "token_budget": None,
        "force_deep_scan": False,
        "_examples": {
            "small_project": {"critical_files_max": 10, "token_budget": 25000},
            "large_project": {"critical_files_max": 150, "token_budget": 75000},
            "enterprise": {"critical_files_max": 300, "token_budget": 40000}
        }
    }
    
    with open("ANALYSIS_LIMITS_OVERRIDE.json", 'w') as f:
        json.dump(template, f, indent=2)
    
    print("✅ Created ANALYSIS_LIMITS_OVERRIDE.json template")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create-template":
        create_override_template()
    else:
        # Demo calculation
        limits = get_analysis_limits("java-architect")
        print(f"\nCalculated limits: {limits['limits']}")