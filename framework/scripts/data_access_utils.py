#!/usr/bin/env python3
"""
Data Access Utilities - Enforced Fallback Hierarchy
Ensures all agents follow: Repomix -> Serena -> Raw Codebase
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

class DataAccessManager:
    """
    Manages data access with enforced fallback hierarchy.
    Priority: 1. Repomix, 2. Serena MCP, 3. Raw Codebase
    """
    
    def __init__(self):
        self.repomix_paths = [
            "output/reports/repomix-summary.md",
            "output/reports/repomix-analysis.md", 
            "codebase/repomix-output.md",
            "docs/repomix-summary.md"
        ]
        self.access_log = []
        self._serena_activated = False
        
    def get_codebase_data(self, 
                          pattern: Optional[str] = None,
                          file_path: Optional[str] = None,
                          search_term: Optional[str] = None) -> Any:
        """
        Universal data access with enforced fallback hierarchy.
        
        Args:
            pattern: File pattern to search (e.g., "*.java")
            file_path: Specific file path to read
            search_term: Term to search for in codebase
            
        Returns:
            Data from the highest priority source available
        """
        
        # Try Repomix first
        result = self._try_repomix(pattern, file_path, search_term)
        if result is not None:
            self._log_access("repomix", pattern or file_path or search_term)
            return result
            
        # Fallback to Serena
        result = self._try_serena(pattern, file_path, search_term)
        if result is not None:
            self._log_access("serena", pattern or file_path or search_term)
            return result
            
        # Last resort: raw codebase
        print("⚠️ WARNING: Falling back to raw codebase access (high token usage)")
        print("💡 Recommendation: Generate Repomix summary first:")
        print("   repomix --config .repomix.config.json codebase/")
        
        result = self._try_raw_codebase(pattern, file_path, search_term)
        self._log_access("raw_codebase", pattern or file_path or search_term)
        
        # Alert if too many raw accesses
        self._check_raw_access_threshold()
        
        return result
    
    def _try_repomix(self, pattern: Optional[str], 
                     file_path: Optional[str], 
                     search_term: Optional[str]) -> Optional[Any]:
        """Try to get data from Repomix summary"""
        
        for repomix_path in self.repomix_paths:
            if Path(repomix_path).exists():
                print(f"✅ Using Repomix: {repomix_path}")
                
                with open(repomix_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Handle different query types
                if search_term:
                    if search_term.lower() in content.lower():
                        return self._extract_context(content, search_term)
                        
                if file_path:
                    extracted = self._extract_file_from_repomix(content, file_path)
                    if extracted:
                        return extracted
                        
                if pattern:
                    matches = self._extract_pattern_from_repomix(content, pattern)
                    if matches:
                        return matches
                        
                # Return full content if no specific query
                if not any([search_term, file_path, pattern]):
                    return content
                    
        return None
    
    def _try_serena(self, pattern: Optional[str],
                    file_path: Optional[str],
                    search_term: Optional[str]) -> Optional[Any]:
        """Try to get data using Serena MCP"""
        
        try:
            print("⚠️ Repomix not sufficient, trying Serena MCP...")
            
            # Mock Serena calls - replace with actual MCP calls in Claude
            # In actual use, these would be:
            # mcp__serena__activate_project("codebase")
            # mcp__serena__search_for_pattern(search_term)
            # etc.
            
            if not self._serena_activated:
                # Activate Serena (mock)
                print("Activating Serena MCP...")
                self._serena_activated = True
                
            if search_term:
                # Mock search
                print(f"Serena: Searching for '{search_term}'")
                return None  # Would return actual results
                
            if file_path:
                # Mock file lookup
                print(f"Serena: Looking up '{file_path}'")
                return None
                
            if pattern:
                # Mock pattern search
                print(f"Serena: Pattern search '{pattern}'")
                return None
                
        except Exception as e:
            print(f"❌ Serena not available: {e}")
            
        return None
    
    def _try_raw_codebase(self, pattern: Optional[str],
                          file_path: Optional[str], 
                          search_term: Optional[str]) -> Any:
        """Last resort: access raw codebase"""
        
        if file_path:
            full_path = Path("codebase") / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
            
        if pattern:
            # Use glob for pattern matching
            from glob import glob
            files = glob(f"codebase/**/{pattern}", recursive=True)
            return files
            
        if search_term:
            # Basic grep-like search
            results = []
            for file_path in Path("codebase").rglob("*"):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if search_term.lower() in content.lower():
                                results.append(str(file_path))
                    except:
                        pass
            return results
            
        return None
    
    def _extract_context(self, content: str, search_term: str, 
                        context_lines: int = 50) -> str:
        """Extract relevant context around search term"""
        
        lines = content.split('\n')
        relevant_lines = []
        
        for i, line in enumerate(lines):
            if search_term.lower() in line.lower():
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                relevant_lines.extend(lines[start:end])
                relevant_lines.append("---")
                
        return '\n'.join(relevant_lines)
    
    def _extract_file_from_repomix(self, content: str, file_path: str) -> Optional[str]:
        """Extract specific file content from Repomix summary"""
        
        # Repomix typically includes files in markdown code blocks
        # Pattern 1: With file path in code block header
        pattern1 = f"```[^`]*{re.escape(file_path)}.*?\n(.*?)```"
        match = re.search(pattern1, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
            
        # Pattern 2: File path mentioned before code block
        pattern2 = f"{re.escape(file_path)}.*?```.*?\n(.*?)```"
        match = re.search(pattern2, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)
            
        return None
    
    def _extract_pattern_from_repomix(self, content: str, pattern: str) -> List[str]:
        """Extract pattern matches from Repomix content"""
        
        matches = []
        
        # Convert file pattern to regex
        if '*' in pattern:
            regex_pattern = pattern.replace('*', '.*').replace('.', r'\.')
        else:
            regex_pattern = pattern
            
        # Find all matches
        found = re.findall(f".*{regex_pattern}.*", content, re.IGNORECASE | re.MULTILINE)
        matches.extend(found[:100])  # Limit to first 100 matches
        
        return matches if matches else None
    
    def _log_access(self, level: str, query: str):
        """Log data access for monitoring"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "fallback_level": level,
            "query": str(query)
        }
        
        self.access_log.append(log_entry)
        
        # Also write to file for persistence
        log_file = Path("output/reports/data-access-log.json")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        all_logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                all_logs = json.load(f)
                
        all_logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(all_logs, f, indent=2)
    
    def _check_raw_access_threshold(self):
        """Alert if too many raw codebase accesses"""
        
        raw_count = sum(1 for log in self.access_log if log['fallback_level'] == 'raw_codebase')
        
        if raw_count > 10:
            print(f"🚨 ALERT: {raw_count} raw codebase accesses detected!")
            print("   This is inefficient. Please generate Repomix summary:")
            print("   repomix --config .repomix.config.json codebase/")
    
    def get_access_statistics(self) -> Dict[str, Any]:
        """Get statistics about data access patterns"""
        
        total = len(self.access_log)
        if total == 0:
            return {"message": "No data accesses logged"}
            
        by_level = {}
        for log in self.access_log:
            level = log['fallback_level']
            by_level[level] = by_level.get(level, 0) + 1
            
        stats = {
            "total_accesses": total,
            "by_level": by_level,
            "percentages": {
                level: f"{(count*100/total):.1f}%"
                for level, count in by_level.items()
            },
            "efficiency_score": self._calculate_efficiency_score(by_level, total)
        }
        
        return stats
    
    def _calculate_efficiency_score(self, by_level: Dict[str, int], total: int) -> str:
        """Calculate efficiency score based on access patterns"""
        
        if total == 0:
            return "N/A"
            
        # Weight: Repomix=100, Serena=60, Raw=0
        weighted_sum = (
            by_level.get('repomix', 0) * 100 +
            by_level.get('serena', 0) * 60 +
            by_level.get('raw_codebase', 0) * 0
        )
        
        score = weighted_sum / total
        
        if score >= 80:
            return f"Excellent ({score:.0f}/100)"
        elif score >= 60:
            return f"Good ({score:.0f}/100)"
        elif score >= 40:
            return f"Fair ({score:.0f}/100)"
        else:
            return f"Poor ({score:.0f}/100) - Generate Repomix!"


# Convenience functions for direct use
_manager = DataAccessManager()

def get_codebase_data(pattern=None, file_path=None, search_term=None):
    """Get codebase data with enforced fallback hierarchy"""
    return _manager.get_codebase_data(pattern, file_path, search_term)

def get_access_stats():
    """Get data access statistics"""
    return _manager.get_access_statistics()

def check_repomix_available():
    """Check if Repomix summary is available"""
    for path in _manager.repomix_paths:
        if Path(path).exists():
            return True
    return False


if __name__ == "__main__":
    # Test the utility
    print("Data Access Utility Test")
    print("-" * 40)
    
    # Check Repomix availability
    if check_repomix_available():
        print("✅ Repomix summary available")
    else:
        print("❌ Repomix summary not found")
        print("   Run: repomix --config .repomix.config.json codebase/")
    
    # Test data access
    print("\nTesting data access hierarchy...")
    data = get_codebase_data(search_term="springframework")
    if data:
        print(f"Found data: {len(str(data))} characters")
    
    # Show statistics
    print("\nAccess Statistics:")
    stats = get_access_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k}: {v}")
        else:
            print(f"  {key}: {value}")