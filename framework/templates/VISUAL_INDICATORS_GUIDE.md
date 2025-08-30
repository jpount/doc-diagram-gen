# Visual Indicators Guide for Architecture Analysis

## Overview
This guide defines standardized visual indicators for all architecture agents to highlight issues, risks, and recommendations clearly.

## Standard Visual Indicators

### Severity Levels
- 🔴 **Critical**: Immediate attention required, blocking issues
- 🟠 **High**: Significant problems, should be addressed soon
- 🟡 **Medium**: Notable issues, plan to address
- 🟢 **Low**: Minor issues, nice to fix
- ⚠️ **Warning**: Potential problems, needs investigation
- ✅ **Good**: Positive finding, best practice followed
- 💡 **Recommendation**: Suggested improvement
- 🚨 **Security**: Security vulnerability or risk
- ⚡ **Performance**: Performance issue or bottleneck
- 🏗️ **Technical Debt**: Code quality or maintenance issue
- 📊 **Metric**: Important measurement or statistic
- 🔄 **Migration**: Modernization or migration consideration
- 🔍 **Investigation**: Requires further analysis

## Usage Examples

### Dependencies and Libraries
```markdown
## Dependencies Analysis

### Critical Issues
- 🔴 **log4j 1.2.17**: Critical security vulnerabilities (CVE-2021-44228)
- 🔴 **commons-collections 3.2.1**: Serialization vulnerability
- 🟠 **Spring Framework 3.2**: End of life, no security updates
- 🟡 **Hibernate 4.2**: Outdated, missing performance improvements

### Recommendations
- 💡 Upgrade to Spring Boot 3.x for better cloud-native support
- 🔄 Migrate from JSF to Angular/React for modern UI
- ⚡ Replace synchronous APIs with reactive programming
```

### Code Quality Issues
```markdown
## Code Quality Analysis

### Critical Problems (Data-Driven Examples)
```python
# Generate from actual detected issues
for issue in actual_analysis['critical_issues']:
    if issue['type'] == 'god_class':
        print(f"- 🔴 **God Classes**: {issue['file']} ({issue['lines']} lines)")
    elif issue['type'] == 'complexity':
        print(f"- 🟠 **Cyclomatic Complexity**: {issue['method']} (complexity: {issue['score']})")
    elif issue['type'] == 'sql_injection':
        print(f"- 🚨 **SQL Injection**: {issue['location']} {issue['detail']}")
    elif issue['type'] == 'n_plus_one':
        print(f"- ⚡ **N+1 Queries**: {issue['method']}")
    elif issue['type'] == 'duplication':
        print(f"- 🏗️ **Code Duplication**: {issue['percentage']}% in {issue['layer']}")
```

### Positive Findings
- ✅ Good test coverage in core modules (78%)
- ✅ Consistent use of dependency injection
- ✅ Well-structured package organization
```

### Architecture Patterns
```markdown
## Architecture Assessment

### Anti-Patterns Detected
- 🔴 **Circular Dependencies**: service ↔ repository packages
- 🟠 **Anemic Domain Model**: Entities with no behavior
- 🟠 **Service Locator**: Hidden dependencies via ServiceLocator.get()
- ⚠️ **Shared Mutable State**: Static collections in Utils classes
- 🏗️ **Big Ball of Mud**: No clear module boundaries

### Migration Risks
- 🔄 **Database Coupling**: Direct JDBC in 47 classes
- 🔄 **Session State**: HTTP session dependency in business logic
- 🔄 **File System**: Hard-coded file paths in configuration
```

## Technology-Specific Indicators

### Java-Specific
```markdown
### Java Issues
- 🔴 **Thread Safety**: Non-synchronized access to shared state
- 🟠 **Memory Leak**: Unclosed resources in try blocks
- 🟡 **Deprecated APIs**: Using Date instead of LocalDateTime
- ⚡ **String Concatenation**: In loops without StringBuilder
- 🚨 **Weak Random**: Using Random for security tokens
```

### .NET-Specific
```markdown
### .NET Issues
- 🔴 **Async Deadlock**: .Result called on async methods
- 🟠 **Disposal**: IDisposable not properly implemented
- 🟡 **Boxing**: Value types boxed in hot paths
- ⚡ **LINQ Performance**: Multiple enumeration of IEnumerable
- 🏗️ **Legacy**: Using Web Forms instead of MVC/Blazor
```

### Angular-Specific
```markdown
### Angular Issues
- 🔴 **Memory Leak**: Unsubscribed observables
- 🟠 **Change Detection**: Using default strategy everywhere
- 🟡 **Bundle Size**: 5MB+ initial bundle
- ⚡ **ExpressionChangedAfterItHasBeenCheckedError**: In 12 components
- 🚨 **XSS Risk**: Using innerHTML without sanitization
```

## Implementation Template for Agents

```python
def format_with_indicators(findings):
    """Format actual findings with appropriate visual indicators"""
    
    severity_icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
        "warning": "⚠️",
        "security": "🚨",
        "performance": "⚡",
        "debt": "🏗️"
    }
    
    formatted_output = []
    
    # Format actual findings from analysis
    for finding in findings:
        # Get appropriate icon based on severity or type
        icon = severity_icons.get(finding.get('severity', '').lower(), "")
        if not icon and 'type' in finding:
            icon = severity_icons.get(finding['type'].lower(), "")
        
        # Build description from actual data
        title = finding.get('title', finding.get('issue', 'Issue'))
        description = finding.get('description', '')
        location = finding.get('location', '')
        
        if location:
            formatted_output.append(f"{icon} **{title}**: {description} at {location}")
        else:
            formatted_output.append(f"{icon} **{title}**: {description}")
    
    return "\n".join(formatted_output)
```

## Markdown Output Structure

```markdown
# Architecture Analysis Report

## 🎯 Executive Summary
```python
# Generate from actual counts
summary = f"""
- 🔴 {counts['critical']} Critical issues requiring immediate attention
- 🟠 {counts['high']} High priority issues
- 🟡 {counts['medium']} Medium priority issues
- ✅ {counts['positive']} Positive findings
"""
```

## 🔴 Critical Issues

### Security Vulnerabilities
- 🚨 **SQL Injection**: Found in 3 locations
- 🚨 **Hardcoded Credentials**: Database password in config
- 🚨 **Weak Encryption**: MD5 used for passwords

### Performance Bottlenecks
- ⚡ **Database**: N+1 queries in main transaction flow
- ⚡ **Memory**: Potential memory leak in cache implementation
- ⚡ **Threading**: Deadlock risk in payment processing

## 🟠 High Priority Issues

### Technical Debt
- 🏗️ **Code Duplication**: 40% duplication in service layer
- 🏗️ **Dead Code**: 2000+ lines of unused code
- 🏗️ **Complex Methods**: 15 methods with complexity > 20

## 💡 Recommendations

### Quick Wins
- ✅ Enable connection pooling (1 day effort)
- ✅ Add database indexes (2 hours effort)
- ✅ Update critical dependencies (1 week effort)

### Strategic Improvements
- 🔄 Migrate to microservices architecture
- 🔄 Implement caching layer
- 🔄 Modernize frontend framework
```

## Best Practices

1. **Use indicators consistently** across all agents
2. **Group by severity** for easy scanning
3. **Provide counts** in executive summary
4. **Mix problems and positives** for balanced view
5. **Include effort estimates** where possible
6. **Link to specific files/lines** for actionability

## Summary Statistics Format

```markdown
## 📊 Analysis Metrics
```python
# Generate from actual metrics
metrics = f"""
- **Files Analyzed**: {actual_metrics['files_analyzed']}
- **Total Lines**: {actual_metrics['total_lines']:,}
- **Issues Found**: 
  - 🔴 Critical: {actual_metrics['issues']['critical']}
  - 🟠 High: {actual_metrics['issues']['high']}
  - 🟡 Medium: {actual_metrics['issues']['medium']}
  - 🟢 Low: {actual_metrics['issues']['low']}
- **Test Coverage**: {actual_metrics['test_coverage']}% {get_coverage_indicator(actual_metrics['test_coverage'])}
- **Technical Debt**: {actual_metrics['debt_estimate']} 🏗️
- **Security Score**: {actual_metrics['security_score']} 🚨
- **Performance Score**: {actual_metrics['performance_score']} ⚡
"""

def get_coverage_indicator(coverage):
    """Return appropriate indicator based on coverage percentage"""
    if coverage >= 80:
        return "✅"
    elif coverage >= 60:
        return "🟡"
    else:
        return "🔴"
```
```

This visual system makes reports more scannable and actionable, helping stakeholders quickly identify what needs attention.