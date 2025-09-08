#!/usr/bin/env python3
"""
Token usage monitoring and optimization tracking for the framework.
Tracks token efficiency from different data sources (Repomix vs raw files).
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse

class TokenMonitor:
    """Monitor and track token usage across different data access strategies"""
    
    # Token estimation constants
    CHARS_PER_TOKEN = 3.5  # Average characters per token
    LINES_PER_TOKEN = 0.75  # Average lines per token
    
    # Cost estimates (in USD per 1K tokens)
    PRICING = {
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3.5-sonnet": {"input": 0.003, "output": 0.015}
    }
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.log_file = self.project_root / "logs" / "token_usage.jsonl"
        self.summary_file = self.project_root / "logs" / "token_summary.json"
        self.model = "claude-3.5-sonnet"  # Default model
        
        # Ensure logs directory exists
        self.log_file.parent.mkdir(exist_ok=True)
    
    def log_usage(self, 
                  agent: str, 
                  operation: str, 
                  input_tokens: int, 
                  output_tokens: int,
                  data_source: str = "unknown",
                  file_path: str = None,
                  optimization_used: bool = False,
                  metadata: Dict = None) -> Dict:
        """Log token usage for an operation"""
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "operation": operation,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "data_source": data_source,
            "file_path": file_path,
            "optimization_used": optimization_used,
            "estimated_cost": self._calculate_cost(input_tokens, output_tokens),
            "model": self.model,
            "metadata": metadata or {}
        }
        
        # Append to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        
        return entry
    
    def estimate_tokens_from_file(self, file_path: str) -> Dict[str, int]:
        """Estimate tokens from file content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            char_count = len(content)
            line_count = content.count('\n')
            
            # Multiple estimation methods
            char_based = int(char_count / self.CHARS_PER_TOKEN)
            line_based = int(line_count / self.LINES_PER_TOKEN)
            
            # Use the more conservative (higher) estimate
            estimated = max(char_based, line_based)
            
            return {
                "estimated_tokens": estimated,
                "char_count": char_count,
                "line_count": line_count,
                "char_based_estimate": char_based,
                "line_based_estimate": line_based
            }
            
        except Exception as e:
            return {
                "estimated_tokens": 0,
                "error": str(e)
            }
    
    def estimate_tokens_from_directory(self, directory: str, patterns: List[str] = None) -> Dict:
        """Estimate total tokens from directory"""
        if patterns is None:
            patterns = ["**/*.java", "**/*.js", "**/*.py", "**/*.ts", "**/*.cs"]
        
        total_tokens = 0
        total_files = 0
        file_breakdown = {}
        
        dir_path = Path(directory)
        
        for pattern in patterns:
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    estimates = self.estimate_tokens_from_file(str(file_path))
                    tokens = estimates.get("estimated_tokens", 0)
                    
                    total_tokens += tokens
                    total_files += 1
                    
                    # Store relative path for cleaner output
                    rel_path = str(file_path.relative_to(dir_path))
                    file_breakdown[rel_path] = {
                        "tokens": tokens,
                        "chars": estimates.get("char_count", 0),
                        "lines": estimates.get("line_count", 0)
                    }
        
        return {
            "total_tokens": total_tokens,
            "total_files": total_files,
            "average_tokens_per_file": int(total_tokens / total_files) if total_files > 0 else 0,
            "file_breakdown": file_breakdown
        }
    
    def compare_strategies(self, codebase_path: str, repomix_path: str = None) -> Dict:
        """Compare token usage between raw codebase and Repomix summary"""
        
        # Estimate raw codebase tokens
        raw_estimate = self.estimate_tokens_from_directory(codebase_path)
        
        # Estimate Repomix tokens if available
        repomix_estimate = {"total_tokens": 0, "available": False}
        
        if repomix_path and os.path.exists(repomix_path):
            repomix_file_estimate = self.estimate_tokens_from_file(repomix_path)
            repomix_estimate = {
                "total_tokens": repomix_file_estimate.get("estimated_tokens", 0),
                "available": True,
                "file_size": repomix_file_estimate.get("char_count", 0),
                "lines": repomix_file_estimate.get("line_count", 0)
            }
        
        # Calculate savings
        if repomix_estimate["available"] and raw_estimate["total_tokens"] > 0:
            token_reduction = raw_estimate["total_tokens"] - repomix_estimate["total_tokens"]
            percentage_reduction = (token_reduction / raw_estimate["total_tokens"]) * 100
        else:
            token_reduction = 0
            percentage_reduction = 0
        
        return {
            "raw_codebase": raw_estimate,
            "repomix_summary": repomix_estimate,
            "optimization": {
                "token_reduction": token_reduction,
                "percentage_reduction": percentage_reduction,
                "cost_savings": self._calculate_cost(token_reduction, 0)
            }
        }
    
    def generate_report(self) -> Dict:
        """Generate comprehensive token usage report"""
        
        # Check if we have any logs
        if not self.log_file.exists():
            return {
                "error": "No token usage logs found",
                "log_file": str(self.log_file)
            }
        
        # Load all log entries
        entries = []
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    entries.append(json.loads(line.strip()))
        except Exception as e:
            return {"error": f"Failed to read logs: {e}"}
        
        if not entries:
            return {"error": "No log entries found"}
        
        # Analyze usage patterns
        total_input = sum(e["input_tokens"] for e in entries)
        total_output = sum(e["output_tokens"] for e in entries)
        total_cost = sum(e.get("estimated_cost", 0) for e in entries)
        
        # Group by data source
        source_breakdown = {}
        for entry in entries:
            source = entry["data_source"]
            if source not in source_breakdown:
                source_breakdown[source] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "operations": 0,
                    "cost": 0
                }
            
            source_breakdown[source]["input_tokens"] += entry["input_tokens"]
            source_breakdown[source]["output_tokens"] += entry["output_tokens"]
            source_breakdown[source]["operations"] += 1
            source_breakdown[source]["cost"] += entry.get("estimated_cost", 0)
        
        # Calculate efficiency metrics
        repomix_usage = source_breakdown.get("repomix", {}).get("input_tokens", 0)
        total_usage = total_input
        repomix_efficiency = (repomix_usage / total_usage * 100) if total_usage > 0 else 0
        
        return {
            "summary": {
                "total_operations": len(entries),
                "total_input_tokens": total_input,
                "total_output_tokens": total_output,
                "total_tokens": total_input + total_output,
                "estimated_total_cost": round(total_cost, 4),
                "repomix_efficiency_percentage": round(repomix_efficiency, 1)
            },
            "by_data_source": source_breakdown,
            "latest_entries": entries[-5:],  # Last 5 entries
            "recommendations": self._generate_recommendations(source_breakdown, repomix_efficiency)
        }
    
    def _generate_recommendations(self, source_breakdown: Dict, repomix_efficiency: float) -> List[str]:
        """Generate optimization recommendations based on usage patterns"""
        recommendations = []
        
        if repomix_efficiency < 80:
            recommendations.append(
                f"LOW REPOMIX USAGE ({repomix_efficiency:.1f}%): Increase Repomix usage to achieve 80%+ token reduction"
            )
        
        raw_tokens = source_breakdown.get("raw", {}).get("input_tokens", 0)
        if raw_tokens > 50000:
            recommendations.append(
                f"HIGH RAW TOKEN USAGE ({raw_tokens:,}): Consider using Repomix compression to reduce costs"
            )
        
        if repomix_efficiency > 90:
            recommendations.append(
                f"EXCELLENT OPTIMIZATION ({repomix_efficiency:.1f}%): Maintaining optimal token efficiency"
            )
        
        return recommendations
    
    def _determine_source(self, file_path: str) -> str:
        """Determine data source from file path"""
        if "repomix" in file_path.lower():
            return "repomix"
        elif "codebase/" in file_path:
            return "raw"
        else:
            return "unknown"
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost in USD"""
        if self.model not in self.PRICING:
            return 0.0
        
        pricing = self.PRICING[self.model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return round(input_cost + output_cost, 4)
    
    def cleanup_old_logs(self, days: int = 7) -> int:
        """Clean up log entries older than specified days"""
        if not self.log_file.exists():
            return 0
        
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        kept_entries = []
        
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    entry = json.loads(line.strip())
                    entry_time = datetime.fromisoformat(entry["timestamp"]).timestamp()
                    if entry_time > cutoff_time:
                        kept_entries.append(entry)
            
            # Rewrite file with kept entries
            with open(self.log_file, "w") as f:
                for entry in kept_entries:
                    f.write(json.dumps(entry) + "\n")
            
            return len(kept_entries)
            
        except Exception as e:
            print(f"Error cleaning logs: {e}")
            return 0

def main():
    """CLI interface for token monitoring"""
    parser = argparse.ArgumentParser(description="Token Usage Monitor")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate usage report')
    
    # Compare command  
    compare_parser = subparsers.add_parser('compare', help='Compare strategies')
    compare_parser.add_argument('--codebase', required=True, help='Path to codebase directory')
    compare_parser.add_argument('--repomix', help='Path to Repomix summary file')
    
    # Estimate command
    estimate_parser = subparsers.add_parser('estimate', help='Estimate tokens')
    estimate_parser.add_argument('path', help='File or directory path')
    estimate_parser.add_argument('--directory', action='store_true', help='Treat path as directory')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean old logs')
    cleanup_parser.add_argument('--days', type=int, default=7, help='Days to keep (default: 7)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    monitor = TokenMonitor()
    
    if args.command == 'report':
        report = monitor.generate_report()
        print(json.dumps(report, indent=2))
    
    elif args.command == 'compare':
        comparison = monitor.compare_strategies(args.codebase, args.repomix)
        print(json.dumps(comparison, indent=2))
    
    elif args.command == 'estimate':
        if args.directory:
            estimates = monitor.estimate_tokens_from_directory(args.path)
        else:
            estimates = monitor.estimate_tokens_from_file(args.path)
        print(json.dumps(estimates, indent=2))
    
    elif args.command == 'cleanup':
        kept = monitor.cleanup_old_logs(args.days)
        print(f"Cleaned logs, kept {kept} recent entries")

if __name__ == "__main__":
    main()