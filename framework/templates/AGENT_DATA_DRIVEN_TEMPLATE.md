# Agent Data-Driven Template

## CRITICAL: All Content Must Be Data-Driven

This template ensures ALL agent outputs use actual data from analysis, never hardcoded examples.

## Core Principle: Everything From Actual Data

```python
# WRONG: Hardcoded examples
report = """
- Found 55 security vulnerabilities
- OrderService.java has 2500 lines
- Java 1.7 detected
"""

# CORRECT: Data-driven
report = f"""
- Found {actual_findings['security_count']} security vulnerabilities
- {actual_findings['largest_file']['name']} has {actual_findings['largest_file']['lines']} lines
- {actual_findings['language']} {actual_findings['version']} detected
"""
```

## Complete Agent Template with Data-Driven Approach

```python
---
name: data-driven-agent
description: Template for data-driven analysis
tools: Read, Write, Glob, Grep, mcp_serena
---

import json
from pathlib import Path
from datetime import datetime

# Import monitoring utilities
sys.path.insert(0, str(Path(__file__).parent.parent / "framework" / "scripts"))
from token_monitor import track_tokens, get_token_summary
from data_access_utils import get_codebase_data

class DataDrivenAnalyzer:
    """Ensures all analysis is based on actual data"""
    
    def __init__(self):
        self.agent_name = "data-driven-agent"
        self.actual_findings = {}
        self.metrics = {}
        self.issues = []
        
    def analyze(self):
        """Main analysis workflow - all data-driven"""
        
        # Step 1: Get actual data (using proper fallback hierarchy)
        self.gather_actual_data()
        
        # Step 2: Analyze the actual data
        self.perform_analysis()
        
        # Step 3: Generate report from actual findings
        report = self.generate_data_driven_report()
        
        # Step 4: Write with actual metrics
        self.save_with_metrics(report)
        
        return report
    
    def gather_actual_data(self):
        """Gather data using Repomix -> Serena -> Raw hierarchy"""
        
        # Try Repomix first
        repomix_data = get_codebase_data()
        if repomix_data:
            self.extract_from_repomix(repomix_data)
            track_tokens(self.agent_name, len(repomix_data)//4, 0, 
                        "Loading Repomix", "repomix")
            return
        
        # Fallback to targeted searches
        self.search_for_specifics()
    
    def extract_from_repomix(self, content):
        """Extract actual metrics from Repomix content"""
        import re
        
        # Extract actual file counts
        file_matches = re.findall(r'```[^`]*?([^/\n]+\.\w+)', content)
        self.metrics['total_files'] = len(set(file_matches))
        
        # Extract actual line counts
        lines = content.count('\n')
        self.metrics['total_lines'] = lines
        
        # Detect actual technologies
        self.detect_actual_technologies(content)
        
        # Find actual issues
        self.find_actual_issues(content)
    
    def detect_actual_technologies(self, content):
        """Detect technologies from actual content"""
        
        tech_patterns = {
            'java': r'import\s+java\.|public\s+class',
            'python': r'import\s+\w+|from\s+\w+\s+import|def\s+\w+',
            'javascript': r'const\s+\w+|function\s+\w+|require\(',
            'typescript': r'interface\s+\w+|type\s+\w+|:\s*\w+\[\]',
            'csharp': r'using\s+System|namespace\s+\w+|public\s+class'
        }
        
        detected = []
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, content):
                detected.append(tech)
        
        self.actual_findings['technologies'] = detected
        
        # Detect versions from actual files
        self.detect_versions(content)
    
    def detect_versions(self, content):
        """Extract actual version numbers"""
        
        version_patterns = {
            'java': r'<java.version>([^<]+)</java.version>',
            'python': r'python_requires["\']>=([^"\']+)',
            'node': r'"node":\s*"([^"]+)"',
            'spring': r'<spring.version>([^<]+)</spring.version>'
        }
        
        versions = {}
        for tech, pattern in version_patterns.items():
            match = re.search(pattern, content)
            if match:
                versions[tech] = match.group(1)
        
        self.actual_findings['versions'] = versions
    
    def find_actual_issues(self, content):
        """Find actual issues in the code"""
        
        issue_patterns = [
            {
                'pattern': r'class\s+(\w+)[^{]*\{[^}]{2000,}',
                'type': 'god_class',
                'severity': 'critical'
            },
            {
                'pattern': r'catch\s*\([^)]*\)\s*\{\s*\}',
                'type': 'empty_catch',
                'severity': 'high'
            },
            {
                'pattern': r'TODO|FIXME|HACK',
                'type': 'technical_debt',
                'severity': 'medium'
            }
        ]
        
        for issue_def in issue_patterns:
            matches = re.findall(issue_def['pattern'], content)
            for match in matches:
                self.issues.append({
                    'type': issue_def['type'],
                    'severity': issue_def['severity'],
                    'location': match if isinstance(match, str) else match[0],
                    'count': 1
                })
        
        # Aggregate by type
        self.aggregate_issues()
    
    def aggregate_issues(self):
        """Aggregate issues by type and severity"""
        
        by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        by_type = {}
        
        for issue in self.issues:
            by_severity[issue['severity']] += 1
            
            if issue['type'] not in by_type:
                by_type[issue['type']] = 0
            by_type[issue['type']] += 1
        
        self.metrics['issues_by_severity'] = by_severity
        self.metrics['issues_by_type'] = by_type
        self.metrics['total_issues'] = len(self.issues)
    
    def generate_data_driven_report(self):
        """Generate report using only actual data"""
        
        # Get actual token usage
        token_summary = get_token_summary()
        agent_tokens = token_summary.get('by_agent', {}).get(self.agent_name, {})
        
        report = f"""# Data-Driven Analysis Report

## Executive Summary
Generated: {datetime.now().isoformat()}
Agent: {self.agent_name}

### Metrics (Actual Data)
- **Files Analyzed**: {self.metrics.get('total_files', 0)}
- **Total Lines**: {self.metrics.get('total_lines', 0):,}
- **Technologies Detected**: {', '.join(self.actual_findings.get('technologies', ['None detected']))}
- **Total Issues**: {self.metrics.get('total_issues', 0)}

### Issue Distribution (Actual Counts)
- 🔴 Critical: {self.metrics.get('issues_by_severity', {}).get('critical', 0)}
- 🟠 High: {self.metrics.get('issues_by_severity', {}).get('high', 0)}
- 🟡 Medium: {self.metrics.get('issues_by_severity', {}).get('medium', 0)}
- 🟢 Low: {self.metrics.get('issues_by_severity', {}).get('low', 0)}

### Detected Versions
{self.format_versions()}

### Top Issues by Type
{self.format_top_issues()}

### Token Usage (Actual)
- Input Tokens: {agent_tokens.get('input', 0):,}
- Output Tokens: {agent_tokens.get('output', 0):,}
- Total Tokens: {agent_tokens.get('total', 0):,}
- Efficiency Score: {token_summary.get('overall', {}).get('efficiency_score', 0)}%

## Detailed Findings

{self.format_detailed_findings()}

## Data Sources Used
{self.format_data_sources()}
"""
        return report
    
    def format_versions(self):
        """Format detected versions"""
        versions = self.actual_findings.get('versions', {})
        if not versions:
            return "No versions detected"
        
        formatted = []
        for tech, version in versions.items():
            formatted.append(f"- **{tech}**: {version}")
        return '\n'.join(formatted)
    
    def format_top_issues(self):
        """Format top issues by type"""
        by_type = self.metrics.get('issues_by_type', {})
        if not by_type:
            return "No issues detected"
        
        # Sort by count
        sorted_issues = sorted(by_type.items(), key=lambda x: x[1], reverse=True)
        
        formatted = []
        for issue_type, count in sorted_issues[:5]:  # Top 5
            formatted.append(f"- **{issue_type}**: {count} occurrences")
        return '\n'.join(formatted)
    
    def format_detailed_findings(self):
        """Format detailed findings from actual data"""
        if not self.issues:
            return "No detailed findings available"
        
        # Group by severity
        by_severity = {}
        for issue in self.issues[:20]:  # Limit to first 20
            sev = issue['severity']
            if sev not in by_severity:
                by_severity[sev] = []
            by_severity[sev].append(issue)
        
        formatted = []
        severity_order = ['critical', 'high', 'medium', 'low']
        icons = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
        
        for severity in severity_order:
            if severity in by_severity:
                formatted.append(f"### {icons[severity]} {severity.capitalize()} Issues")
                for issue in by_severity[severity][:5]:  # Max 5 per severity
                    formatted.append(f"- **{issue['type']}**: {issue.get('location', 'Multiple locations')}")
        
        return '\n'.join(formatted)
    
    def format_data_sources(self):
        """Show which data sources were used"""
        token_summary = get_token_summary()
        by_source = token_summary.get('by_source', {})
        
        formatted = []
        for source, data in by_source.items():
            percentage = (data['tokens'] / token_summary['overall']['total_tokens'] * 100) if token_summary['overall']['total_tokens'] > 0 else 0
            formatted.append(f"- **{source}**: {data['tokens']:,} tokens ({percentage:.1f}%)")
        
        return '\n'.join(formatted) if formatted else "No data source tracking available"
    
    def save_with_metrics(self, report):
        """Save report and context with actual metrics"""
        
        # Save main report
        Write("output/docs/data-driven-analysis.md", report)
        
        # Save context for next agents
        context = {
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "findings": self.actual_findings,
            "issue_count": len(self.issues),
            "top_issues": self.issues[:10] if self.issues else []
        }
        
        Write(f"output/context/{self.agent_name}-summary.json", 
              json.dumps(context, indent=2))

# Execute analysis
analyzer = DataDrivenAnalyzer()
report = analyzer.analyze()
print(f"✅ Analysis complete with {len(analyzer.issues)} issues found")
```

## Key Patterns for Data-Driven Analysis

### 1. Never Use Hardcoded Values

```python
# ❌ WRONG - Hardcoded
issues = [
    "SQL injection in UserDAO.java",
    "Memory leak in CacheManager",
    "N+1 queries in OrderService"
]

# ✅ CORRECT - Data-driven
issues = []
for finding in actual_analysis['security_issues']:
    issues.append(f"{finding['type']} in {finding['location']}")
```

### 2. Always Extract from Actual Sources

```python
# ❌ WRONG - Assumed metrics
metrics = {
    "files": 1234,
    "lines": 50000,
    "complexity": 12.5
}

# ✅ CORRECT - Calculated from data
metrics = {
    "files": len(Glob("codebase/**/*.java")),
    "lines": sum(len(Read(f).split('\n')) for f in files),
    "complexity": calculate_actual_complexity(files)
}
```

### 3. Use Conditional Formatting

```python
def format_finding(finding):
    """Format based on actual finding data"""
    
    # Only include what actually exists
    parts = []
    
    if 'type' in finding:
        parts.append(f"Type: {finding['type']}")
    
    if 'severity' in finding:
        parts.append(f"Severity: {finding['severity']}")
    
    if 'location' in finding:
        parts.append(f"Location: {finding['location']}")
    
    return " | ".join(parts) if parts else "Unknown finding"
```

### 4. Track Everything

```python
# Track all operations with actual data
operation_log = []

def log_operation(operation, data_size, source):
    """Log every data access"""
    operation_log.append({
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "data_size": data_size,
        "source": source  # repomix, serena, or raw
    })
    
    # Track tokens
    track_tokens(agent_name, data_size//4, 0, operation, source)
```

### 5. Validate Before Reporting

```python
def validate_metrics(metrics):
    """Ensure metrics are from actual data"""
    
    required = ['total_files', 'total_lines', 'issues_found']
    
    for field in required:
        if field not in metrics or metrics[field] == 0:
            print(f"⚠️ Warning: {field} not found or zero")
            metrics[field] = "Not analyzed"
    
    return metrics
```

## Checklist for Data-Driven Compliance

Before completing any agent:

- [ ] All numbers come from actual analysis
- [ ] All file names are detected, not assumed
- [ ] All versions are extracted from files
- [ ] All metrics are calculated, not estimated
- [ ] Token usage is tracked and reported
- [ ] Data sources are documented
- [ ] Context includes only actual findings
- [ ] No placeholder text remains
- [ ] All examples use real detected data
- [ ] Summary statistics match actual counts

## Error Handling for Missing Data

```python
def safe_format(data, key, default="Not detected"):
    """Safely format data that might not exist"""
    
    value = data.get(key, default)
    
    # Never return hardcoded examples
    if value == default:
        return f"{key}: {default}"
    
    # Format actual value
    if isinstance(value, (int, float)):
        return f"{key}: {value:,}"
    elif isinstance(value, list):
        return f"{key}: {len(value)} items"
    else:
        return f"{key}: {value}"
```

This template ensures all agent outputs are completely data-driven, using actual findings rather than hardcoded examples.