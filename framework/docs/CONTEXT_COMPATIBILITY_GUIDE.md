# Context Compatibility Guide for Specialist Agents

## Overview
This guide ensures seamless context passing between specialist agents (Java, Angular, .NET architects) and downstream agents that traditionally expect legacy-code-detective output.

## Context Summary Requirements

### All Architecture Agents Must Write Context Summaries

Whether using `@legacy-code-detective` or specialist architects (`@java-architect`, `@angular-architect`, `@dotnet-architect`), each MUST write a standardized context summary.

## Standardized Context File Naming

### Primary Context File (Always Created)
```
output/context/architecture-analysis-summary.json
```

This file should be written by whichever architecture agent runs:
- `legacy-code-detective` (for unknown/complex codebases)
- `java-architect` (for Java codebases)
- `angular-architect` (for Angular codebases)
- `dotnet-architect` (for .NET codebases)

### Agent-Specific Context Files (Additional)
```
output/context/[agent-name]-summary.json
```
Examples:
- `output/context/java-architect-summary.json`
- `output/context/angular-architect-summary.json`
- `output/context/dotnet-architect-summary.json`

## Context Summary Structure (Required Fields)

All architecture agents MUST include these fields in their context summaries:

```json
{
  "agent": "agent-name",
  "timestamp": "ISO-8601 timestamp",
  "token_usage": {
    "input": 12500,
    "output": 3200,
    "total": 15700
  },
  "summary": {
    "key_findings": [],
    "priority_items": [],
    "warnings": [],
    "recommendations_for_next": {
      "business-logic-analyst": [],
      "performance-analyst": [],
      "security-analyst": [],
      "diagram-architect": []
    }
  },
  "data": {
    "technology_stack": {
      "primary_language": "Java 17",
      "frameworks": [],
      "build_system": "Maven",
      "app_server": "Tomcat"
    },
    "critical_files": [],
    "metrics": {
      "total_files": 456,
      "total_lines": 125000
    }
  }
}
```

## Implementation for Specialist Agents

### Java Architect Context Writing
```python
# At the end of java-architect analysis
context_summary = {
    "agent": "java-architect",
    "timestamp": datetime.now().isoformat(),
    "token_usage": get_token_usage(),
    "summary": {
        "key_findings": [
            "Spring Boot 2.5 with Java 11",
            "Heavy use of JPA/Hibernate",
            "15 REST controllers identified"
        ],
        "priority_items": [
            "Critical: Thread-unsafe singleton in PaymentService",
            "High: N+1 queries in OrderRepository"
        ],
        "warnings": [
            "Using deprecated Spring Security methods",
            "Found hardcoded database credentials"
        ],
        "recommendations_for_next": {
            "business-logic-analyst": [
                "Focus on OrderService and PaymentService",
                "Check validation annotations in DTOs"
            ],
            "performance-analyst": [
                "Investigate JPA N+1 queries",
                "Check connection pool configuration"
            ]
        }
    },
    "data": {
        "technology_stack": {
            "primary_language": "Java 11",
            "frameworks": ["Spring Boot 2.5", "Hibernate 5.4"],
            "build_system": "Maven 3.8",
            "app_server": "Embedded Tomcat"
        },
        "critical_files": [
            {"path": "src/main/java/OrderService.java", "reason": "Core business logic"},
            {"path": "pom.xml", "reason": "Dependencies"}
        ],
        "metrics": {
            "total_files": 234,
            "total_lines": 45000,
            "test_coverage": "67%"
        }
    }
}

# Write to BOTH locations for compatibility
Write("output/context/java-architect-summary.json", json.dumps(context_summary, indent=2))
Write("output/context/architecture-analysis-summary.json", json.dumps(context_summary, indent=2))

# Also write main analysis document
Write("output/docs/01-java-architecture-analysis.md", java_analysis_content)
```

## Downstream Agent Context Loading

### Business Logic Analyst (Updated)
```python
def load_previous_context():
    """Load context from any architecture agent"""
    # Try unified context first
    unified_context = Path("output/context/architecture-analysis-summary.json")
    if unified_context.exists():
        with open(unified_context) as f:
            return json.load(f)
    
    # Fallback to legacy-code-detective for backward compatibility
    legacy_context = Path("output/context/legacy-code-detective-summary.json")
    if legacy_context.exists():
        with open(legacy_context) as f:
            return json.load(f)
    
    # Try any specialist agent context
    for agent in ["java-architect", "angular-architect", "dotnet-architect"]:
        context_file = Path(f"output/context/{agent}-summary.json")
        if context_file.exists():
            with open(context_file) as f:
                return json.load(f)
    
    # Fallback to memory
    try:
        return mcp__serena__read_memory("architecture_context")
    except:
        return None
```

## Multiple Specialist Scenario

When multiple specialists run (e.g., Java backend + Angular frontend):

### Merge Context Summaries
```python
def merge_specialist_contexts():
    """Merge contexts from multiple specialists"""
    merged_context = {
        "agent": "architecture-specialists",
        "timestamp": datetime.now().isoformat(),
        "token_usage": {"input": 0, "output": 0, "total": 0},
        "summary": {
            "key_findings": [],
            "priority_items": [],
            "warnings": [],
            "recommendations_for_next": {}
        },
        "data": {
            "technology_stack": {
                "backend": {},
                "frontend": {}
            },
            "critical_files": [],
            "metrics": {}
        }
    }
    
    # Load and merge each specialist's context
    for agent in ["java-architect", "angular-architect"]:
        context_file = Path(f"output/context/{agent}-summary.json")
        if context_file.exists():
            with open(context_file) as f:
                specialist_context = json.load(f)
                
                # Merge findings
                merged_context["summary"]["key_findings"].extend(
                    specialist_context["summary"]["key_findings"]
                )
                merged_context["summary"]["priority_items"].extend(
                    specialist_context["summary"]["priority_items"]
                )
                
                # Merge recommendations
                for next_agent, recs in specialist_context["summary"]["recommendations_for_next"].items():
                    if next_agent not in merged_context["summary"]["recommendations_for_next"]:
                        merged_context["summary"]["recommendations_for_next"][next_agent] = []
                    merged_context["summary"]["recommendations_for_next"][next_agent].extend(recs)
                
                # Add token usage
                merged_context["token_usage"]["total"] += specialist_context["token_usage"]["total"]
    
    # Write merged context
    Write("output/context/architecture-analysis-summary.json", json.dumps(merged_context, indent=2))
```

## Repomix Usage Guidelines

### Priority Order for Code Analysis

1. **Check for Repomix Summary First**
   ```python
   repomix_file = Path("output/reports/repomix-summary.md")
   if repomix_file.exists():
       # Use for initial understanding
       repomix_content = Read(repomix_file)
       # Extract high-level patterns and structure
   ```

2. **Use Repomix for Broad Analysis**
   - Technology detection
   - File structure understanding
   - Dependency overview
   - Initial complexity assessment

3. **Use Raw Files for Specific Details**
   - Exact business rule extraction (need actual code)
   - Line-specific references
   - Detailed implementation patterns
   - Security vulnerability analysis

### Example: Balanced Approach
```python
def analyze_business_logic():
    # Step 1: Use Repomix for overview
    if Path("output/reports/repomix-summary.md").exists():
        repomix = Read("output/reports/repomix-summary.md")
        # Get list of service files from Repomix
        service_files = extract_service_files(repomix)
    else:
        # Fallback to file search
        service_files = Glob("**/*Service.java")
    
    # Step 2: Deep dive into specific files only
    business_rules = []
    for service_file in service_files[:10]:  # Limit to top 10 critical files
        content = Read(service_file)
        rules = extract_business_rules(content)
        business_rules.extend(rules)
    
    return business_rules
```

## Migration Path

### Phase 1: Update Specialist Agents (Immediate)
Add context summary writing to:
- `java-architect`
- `angular-architect`
- `dotnet-architect`

### Phase 2: Update Downstream Agents (Next)
Update context loading in:
- `business-logic-analyst`
- `performance-analyst`
- `security-analyst`
- `diagram-architect`

### Phase 3: Validate Compatibility
Test scenarios:
1. Legacy-code-detective → downstream agents (existing flow)
2. Single specialist → downstream agents
3. Multiple specialists → downstream agents
4. Mixed (specialist + legacy) → downstream agents

## Summary

Key changes needed:
1. **All architecture agents write context summaries** to `output/context/architecture-analysis-summary.json`
2. **Downstream agents check multiple context sources** with graceful fallbacks
3. **Repomix is used for overview**, raw files for details
4. **Multiple specialists merge their contexts** for downstream consumption

This ensures seamless integration regardless of which architecture agents are used.