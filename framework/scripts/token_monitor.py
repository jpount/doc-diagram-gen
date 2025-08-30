#!/usr/bin/env python3
"""
Token Usage Monitor for Codebase Analysis Framework
Tracks token consumption across agents and provides optimization insights
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import re

@dataclass
class TokenUsage:
    """Token usage data structure"""
    agent: str
    timestamp: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    phase: str = ""
    cost_estimate: float = 0.0
    efficiency_score: float = 0.0
    data_source: str = ""  # repomix, serena, or raw

class TokenMonitor:
    """
    Monitors and tracks token usage across all agents
    """
    
    # Token pricing (as of 2024 - adjust as needed)
    PRICING = {
        "claude-3-opus": {"input": 0.015, "output": 0.075},  # per 1K tokens
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03}
    }
    
    # Token budgets by project size and agent
    BUDGETS = {
        "small": {  # <10K lines
            "legacy-code-detective": 30000,
            "business-logic-analyst": 25000,
            "performance-analyst": 20000,
            "security-analyst": 20000,
            "diagram-architect": 15000,
            "documentation-specialist": 30000,
            "modernization-architect": 35000,
            "total": 175000
        },
        "medium": {  # 10K-100K lines
            "legacy-code-detective": 50000,
            "business-logic-analyst": 40000,
            "performance-analyst": 35000,
            "security-analyst": 35000,
            "diagram-architect": 25000,
            "documentation-specialist": 50000,
            "modernization-architect": 50000,
            "total": 285000
        },
        "large": {  # 100K+ lines
            "legacy-code-detective": 75000,
            "business-logic-analyst": 60000,
            "performance-analyst": 50000,
            "security-analyst": 50000,
            "diagram-architect": 35000,
            "documentation-specialist": 75000,
            "modernization-architect": 75000,
            "total": 420000
        }
    }
    
    def __init__(self, project_size: str = "medium", model: str = "claude-3-sonnet"):
        self.project_size = project_size
        self.model = model
        self.log_file = Path("output/reports/token-usage-log.json")
        self.summary_file = Path("output/reports/token-usage-summary.json")
        self.usage_history: List[TokenUsage] = []
        self.current_agent: Optional[str] = None
        self.session_start = datetime.now().isoformat()
        
        # Create output directory if needed
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing history
        self._load_history()
    
    def _load_history(self):
        """Load existing token usage history"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    for entry in data:
                        self.usage_history.append(TokenUsage(**entry))
            except:
                pass
    
    def track_usage(self, agent: str, input_tokens: int, output_tokens: int,
                   phase: str = "", data_source: str = "") -> TokenUsage:
        """
        Track token usage for an agent
        
        Args:
            agent: Name of the agent
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            phase: Optional phase description
            data_source: Source of data (repomix, serena, raw)
        
        Returns:
            TokenUsage object with calculated metrics
        """
        total = input_tokens + output_tokens
        
        # Calculate cost
        cost = self._calculate_cost(input_tokens, output_tokens)
        
        # Calculate efficiency score
        efficiency = self._calculate_efficiency(data_source, total)
        
        usage = TokenUsage(
            agent=agent,
            timestamp=datetime.now().isoformat(),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total,
            phase=phase,
            cost_estimate=cost,
            efficiency_score=efficiency,
            data_source=data_source
        )
        
        self.usage_history.append(usage)
        self._save_usage(usage)
        
        # Check budget
        self._check_budget(agent, total)
        
        return usage
    
    def get_ccusage(self) -> Optional[Dict[str, int]]:
        """
        Try to get token usage from ccusage command if available
        
        Returns:
            Dict with token counts or None if not available
        """
        try:
            # Try to run ccusage command
            result = subprocess.run(
                ["ccusage"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse output (format may vary)
                output = result.stdout
                
                # Common patterns for token usage output
                patterns = [
                    r"Input:\s*(\d+)",
                    r"Output:\s*(\d+)",
                    r"Total:\s*(\d+)",
                    r"Tokens used:\s*(\d+)",
                    r"(\d+)\s*input.*?(\d+)\s*output"
                ]
                
                tokens = {}
                for pattern in patterns:
                    matches = re.findall(pattern, output, re.IGNORECASE)
                    if matches:
                        if len(matches[0]) == 2:  # input/output pair
                            tokens["input"] = int(matches[0][0])
                            tokens["output"] = int(matches[0][1])
                        elif "input" in pattern.lower():
                            tokens["input"] = int(matches[0])
                        elif "output" in pattern.lower():
                            tokens["output"] = int(matches[0])
                        elif "total" in pattern.lower():
                            tokens["total"] = int(matches[0])
                
                return tokens if tokens else None
                
        except (subprocess.SubprocessError, FileNotFoundError):
            return None
    
    def estimate_from_text(self, text: str) -> int:
        """
        Estimate token count from text
        
        Rule of thumb: ~1 token per 4 characters or ~0.75 tokens per word
        """
        # Method 1: Character-based (more accurate for code)
        char_estimate = len(text) / 4
        
        # Method 2: Word-based (more accurate for documentation)
        word_estimate = len(text.split()) * 0.75
        
        # Use average for balance
        return int((char_estimate + word_estimate) / 2)
    
    def track_file_read(self, file_path: str, content: str, agent: str) -> TokenUsage:
        """
        Track tokens from reading a file
        """
        tokens = self.estimate_from_text(content)
        source = self._determine_source(file_path)
        
        return self.track_usage(
            agent=agent,
            input_tokens=tokens,
            output_tokens=0,
            phase=f"Reading {file_path}",
            data_source=source
        )
    
    def _determine_source(self, file_path: str) -> str:
        """Determine data source from file path"""
        if "repomix" in file_path.lower():
            return "repomix"
        elif "codebase/" in file_path:
            return "raw"
        else:
            return "serena"
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost in USD"""
        if self.model not in self.PRICING:
            return 0.0
        
        pricing = self.PRICING[self.model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return round(input_cost + output_cost, 4)
    
    def _calculate_efficiency(self, data_source: str, total_tokens: int) -> float:
        """
        Calculate efficiency score based on data source
        
        Repomix: 100% efficient (best)
        Serena: 60% efficient (good)
        Raw: 20% efficient (poor)
        """
        efficiency_map = {
            "repomix": 1.0,
            "serena": 0.6,
            "raw": 0.2,
            "": 0.5  # Unknown
        }
        
        return efficiency_map.get(data_source.lower(), 0.5)
    
    def _check_budget(self, agent: str, tokens_used: int):
        """Check if agent is within budget"""
        if agent not in self.BUDGETS[self.project_size]:
            return
        
        budget = self.BUDGETS[self.project_size][agent]
        
        # Calculate total used by this agent
        agent_total = sum(
            u.total_tokens for u in self.usage_history 
            if u.agent == agent
        )
        
        if agent_total > budget:
            print(f"⚠️ WARNING: {agent} exceeded token budget!")
            print(f"   Used: {agent_total:,} / Budget: {budget:,}")
            print(f"   Overage: {agent_total - budget:,} tokens")
        elif agent_total > budget * 0.8:
            print(f"⚠️ CAUTION: {agent} at {(agent_total/budget*100):.0f}% of budget")
    
    def _save_usage(self, usage: TokenUsage):
        """Save usage to log file"""
        # Convert history to dictionaries
        history_data = [asdict(u) for u in self.usage_history]
        
        with open(self.log_file, 'w') as f:
            json.dump(history_data, f, indent=2)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive usage summary
        """
        if not self.usage_history:
            return {"message": "No usage data available"}
        
        # Overall stats
        total_input = sum(u.input_tokens for u in self.usage_history)
        total_output = sum(u.output_tokens for u in self.usage_history)
        total_all = sum(u.total_tokens for u in self.usage_history)
        total_cost = sum(u.cost_estimate for u in self.usage_history)
        
        # By agent
        by_agent = {}
        for usage in self.usage_history:
            if usage.agent not in by_agent:
                by_agent[usage.agent] = {
                    "input": 0, "output": 0, "total": 0, 
                    "cost": 0.0, "calls": 0
                }
            by_agent[usage.agent]["input"] += usage.input_tokens
            by_agent[usage.agent]["output"] += usage.output_tokens
            by_agent[usage.agent]["total"] += usage.total_tokens
            by_agent[usage.agent]["cost"] += usage.cost_estimate
            by_agent[usage.agent]["calls"] += 1
        
        # By data source
        by_source = {}
        for usage in self.usage_history:
            source = usage.data_source or "unknown"
            if source not in by_source:
                by_source[source] = {"tokens": 0, "calls": 0}
            by_source[source]["tokens"] += usage.total_tokens
            by_source[source]["calls"] += 1
        
        # Calculate efficiency
        weighted_efficiency = sum(
            u.total_tokens * u.efficiency_score for u in self.usage_history
        ) / total_all if total_all > 0 else 0
        
        # Budget status
        budget_total = self.BUDGETS[self.project_size]["total"]
        budget_used_pct = (total_all / budget_total * 100) if budget_total > 0 else 0
        
        summary = {
            "session_start": self.session_start,
            "project_size": self.project_size,
            "model": self.model,
            "overall": {
                "total_tokens": total_all,
                "input_tokens": total_input,
                "output_tokens": total_output,
                "total_cost_usd": round(total_cost, 2),
                "efficiency_score": round(weighted_efficiency * 100, 1),
                "budget_used": f"{budget_used_pct:.1f}%",
                "budget_remaining": max(0, budget_total - total_all)
            },
            "by_agent": by_agent,
            "by_source": by_source,
            "top_consumers": self._get_top_consumers(by_agent, 5),
            "recommendations": self._get_recommendations(by_source, weighted_efficiency)
        }
        
        # Save summary
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def _get_top_consumers(self, by_agent: Dict, limit: int = 5) -> List[Dict]:
        """Get top token consuming agents"""
        sorted_agents = sorted(
            by_agent.items(), 
            key=lambda x: x[1]["total"], 
            reverse=True
        )[:limit]
        
        return [
            {
                "agent": agent,
                "tokens": data["total"],
                "percentage": f"{(data['total'] / sum(a[1]['total'] for a in by_agent.items()) * 100):.1f}%"
            }
            for agent, data in sorted_agents
        ]
    
    def _get_recommendations(self, by_source: Dict, efficiency: float) -> List[str]:
        """Generate recommendations based on usage patterns"""
        recommendations = []
        
        # Check efficiency
        if efficiency < 0.5:
            recommendations.append("🔴 Critical: Poor token efficiency - ensure Repomix is generated")
        elif efficiency < 0.7:
            recommendations.append("🟡 Warning: Suboptimal efficiency - check Repomix completeness")
        else:
            recommendations.append("✅ Good: Efficient token usage")
        
        # Check data sources
        if "raw" in by_source and by_source["raw"]["tokens"] > 0:
            raw_pct = by_source["raw"]["tokens"] / sum(s["tokens"] for s in by_source.values()) * 100
            if raw_pct > 20:
                recommendations.append(f"⚠️ {raw_pct:.0f}% raw codebase access - regenerate Repomix")
        
        # Check if Repomix is being used
        if "repomix" not in by_source or by_source["repomix"]["tokens"] == 0:
            recommendations.append("🚨 Not using Repomix - generate with: repomix --config .repomix.config.json")
        
        return recommendations
    
    def display_summary(self):
        """Display formatted summary to console"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("📊 TOKEN USAGE SUMMARY")
        print("="*60)
        
        overall = summary["overall"]
        print(f"\n🎯 Overall Statistics:")
        print(f"  Total Tokens: {overall['total_tokens']:,}")
        print(f"  Input/Output: {overall['input_tokens']:,} / {overall['output_tokens']:,}")
        print(f"  Estimated Cost: ${overall['total_cost_usd']:.2f}")
        print(f"  Efficiency Score: {overall['efficiency_score']}%")
        print(f"  Budget Used: {overall['budget_used']}")
        print(f"  Remaining: {overall['budget_remaining']:,} tokens")
        
        print(f"\n👥 Top Token Consumers:")
        for consumer in summary["top_consumers"]:
            print(f"  {consumer['agent']}: {consumer['tokens']:,} ({consumer['percentage']})")
        
        print(f"\n📍 By Data Source:")
        for source, data in summary["by_source"].items():
            print(f"  {source}: {data['tokens']:,} tokens ({data['calls']} calls)")
        
        print(f"\n💡 Recommendations:")
        for rec in summary["recommendations"]:
            print(f"  {rec}")
        
        print("\n" + "="*60)


# Convenience functions for agents to use
_monitor = None

def init_monitor(project_size: str = "medium", model: str = "claude-3-sonnet"):
    """Initialize the token monitor"""
    global _monitor
    _monitor = TokenMonitor(project_size, model)
    return _monitor

def track_tokens(agent: str, input_tokens: int, output_tokens: int, 
                phase: str = "", data_source: str = ""):
    """Track token usage for current operation"""
    global _monitor
    if not _monitor:
        _monitor = TokenMonitor()
    return _monitor.track_usage(agent, input_tokens, output_tokens, phase, data_source)

def estimate_tokens(text: str) -> int:
    """Estimate token count from text"""
    global _monitor
    if not _monitor:
        _monitor = TokenMonitor()
    return _monitor.estimate_from_text(text)

def check_ccusage(agent: str = "current"):
    """Check and track tokens from ccusage if available"""
    global _monitor
    if not _monitor:
        _monitor = TokenMonitor()
    
    usage = _monitor.get_ccusage()
    if usage:
        return _monitor.track_usage(
            agent=agent,
            input_tokens=usage.get("input", 0),
            output_tokens=usage.get("output", 0),
            phase="ccusage_check"
        )
    return None

def get_token_summary():
    """Get current token usage summary"""
    global _monitor
    if not _monitor:
        _monitor = TokenMonitor()
    return _monitor.get_summary()

def display_token_report():
    """Display formatted token usage report"""
    global _monitor
    if not _monitor:
        _monitor = TokenMonitor()
    _monitor.display_summary()


if __name__ == "__main__":
    import sys
    
    # Command line interface
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "init":
            size = sys.argv[2] if len(sys.argv) > 2 else "medium"
            model = sys.argv[3] if len(sys.argv) > 3 else "claude-3-sonnet"
            monitor = init_monitor(size, model)
            print(f"✅ Token monitor initialized for {size} project with {model}")
        
        elif command == "report":
            display_token_report()
        
        elif command == "check":
            usage = check_ccusage()
            if usage:
                print(f"✅ Tracked {usage.total_tokens} tokens from ccusage")
            else:
                print("❌ ccusage not available")
        
        elif command == "test":
            # Test tracking
            monitor = init_monitor("medium", "claude-3-sonnet")
            
            # Simulate some usage
            track_tokens("test-agent", 1000, 500, "testing", "repomix")
            track_tokens("test-agent", 2000, 1000, "analyzing", "serena")
            track_tokens("test-agent", 5000, 2000, "raw access", "raw")
            
            display_token_report()
        
        else:
            print("Usage: python token_monitor.py [init|report|check|test] [project_size] [model]")
    else:
        print("Token Monitor - Track token usage across agents")
        print("Usage: python token_monitor.py [init|report|check|test]")
        print()
        print("Commands:")
        print("  init [size] [model]  - Initialize monitor")
        print("  report               - Display usage report")
        print("  check                - Check ccusage if available")
        print("  test                 - Run test simulation")