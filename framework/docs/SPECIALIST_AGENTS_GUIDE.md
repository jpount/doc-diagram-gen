# Specialist Architecture Agents Guide

## Overview

The framework now includes specialized architecture agents that provide deep, technology-specific analysis. These agents offer superior results compared to the generic `legacy-code-detective` when analyzing codebases with specific technologies.

## Available Specialist Agents

### Technology-Specific Architects

| Agent | Specialization | Best For |
|-------|---------------|----------|
| `@java-architect` | Java/J2EE, Spring, EJB, Servlets | Legacy and modern Java applications |
| `@dotnet-architect` | C#, ASP.NET, .NET Framework/Core | Windows and .NET applications |
| `@angular-architect` | AngularJS through Angular 17+ | Angular SPAs and enterprise apps |
| `@architecture-selector` | Multi-technology detection | Choosing the right specialists |

### Generic Fallback
| Agent | Use When |
|-------|----------|
| `@legacy-code-detective` | Unknown technologies or 5+ different technologies |

## How to Use Specialist Agents

### Option 1: Automatic Selection (Recommended)

1. **Run the architecture selector first:**
   ```
   @architecture-selector
   ```
   This analyzes your codebase and recommends which specialists to use.

2. **Review the selection report:**
   Check `output/docs/00-agent-selection-report.md` for recommendations

3. **Run the recommended specialists:**
   ```
   @java-architect      # If Java was detected
   @angular-architect   # If Angular was detected
   ```

### Option 2: Manual Selection

If you know your technology stack, run the appropriate specialist directly:

#### For Java Applications:
```
@java-architect
@business-logic-analyst
@performance-analyst
@security-analyst
```

#### For .NET Applications:
```
@dotnet-architect
@business-logic-analyst
@performance-analyst
@security-analyst
```

#### For Angular Applications:
```
@angular-architect
@performance-analyst
@security-analyst
```

#### For Full-Stack Applications:
```
# Run backend and frontend specialists
@java-architect       # or @dotnet-architect
@angular-architect
@business-logic-analyst
@performance-analyst
@security-analyst
```

## Benefits of Using Specialists

### Java Architect Benefits:
- Detects Java-specific anti-patterns (god classes, string concatenation in loops)
- Analyzes Maven/Gradle dependencies for vulnerabilities
- Identifies Spring/EJB/Servlet patterns
- Provides Java version migration paths
- Checks for Java-specific security issues (serialization, weak random)

### .NET Architect Benefits:
- Analyzes .NET Framework vs .NET Core/5+ differences
- Detects async/await anti-patterns
- Checks Entity Framework performance issues
- Identifies WCF to gRPC migration opportunities
- Analyzes NuGet vulnerabilities

### Angular Architect Benefits:
- Detects RxJS memory leaks
- Analyzes change detection strategies
- Identifies AngularJS to Angular migration paths
- Checks for XSS vulnerabilities in templates
- Analyzes bundle sizes and lazy loading

## Execution Strategies

### For Simple Codebases (Single Technology)
```
1. @[technology]-architect
2. @business-logic-analyst
3. @performance-analyst
4. @security-analyst
5. @diagram-architect
```

### For Complex Codebases (Multiple Technologies)
```
1. @architecture-selector    # First, to identify technologies
2. @[backend]-architect      # Run specialists in parallel
3. @[frontend]-architect     
4. @business-logic-analyst   # Then cross-cutting agents
5. @performance-analyst
6. @security-analyst
7. @modernization-architect
```

### For Unknown/Legacy Codebases
```
1. @architecture-selector     # Identify what we're dealing with
2. @legacy-code-detective     # General discovery
3. @[specific]-architect      # Technology-specific deep dives
4. [Continue with standard agents]
```

## Output Files

Each specialist generates a comprehensive analysis document:

| Agent | Output File |
|-------|------------|
| `@java-architect` | `output/docs/01-java-architecture-analysis.md` |
| `@dotnet-architect` | `output/docs/01-dotnet-architecture-analysis.md` |
| `@angular-architect` | `output/docs/01-angular-architecture-analysis.md` |
| `@architecture-selector` | `output/docs/00-agent-selection-report.md` |

## When to Use Which Approach

### Use Specialists When:
- You have a codebase primarily in one technology (>70%)
- You need deep, technology-specific insights
- You want framework-specific migration recommendations
- You need to identify language-specific anti-patterns

### Use Generic Agent When:
- Technology stack is completely unknown
- Codebase has 5+ different technologies equally distributed
- You need a quick, high-level overview
- Codebase is very old with obsolete technologies

### Use Multiple Specialists When:
- You have a clear multi-tier architecture
- Backend and frontend use different technologies
- You have microservices in different languages
- You need comprehensive analysis of each tier

## Example Workflows

### Example 1: Legacy Java EE Application
```
@java-architect           # Deep Java/J2EE analysis
@business-logic-analyst   # Extract business rules from EJBs
@performance-analyst      # Find N+1 queries, connection leaks
@security-analyst         # Check for Java-specific vulnerabilities
@modernization-architect  # Plan Spring Boot migration
```

### Example 2: Full-Stack .NET + Angular App
```
@architecture-selector    # Confirm it's .NET + Angular
@dotnet-architect        # Analyze ASP.NET backend
@angular-architect       # Analyze Angular frontend
@business-logic-analyst  # Extract rules from both tiers
@performance-analyst     # End-to-end performance
@diagram-architect       # Create architecture diagrams
```

### Example 3: Unknown Legacy System
```
@architecture-selector    # Discover what technologies exist
# Review report, then run recommended agents
@legacy-code-detective   # If many technologies found
# OR
@[specific]-architect    # If 1-3 main technologies found
```

## Tips for Best Results

1. **Always run `@architecture-selector` first** if you're unsure about the technology stack

2. **Run specialists in parallel** when possible (backend and frontend architects can run simultaneously)

3. **Save tokens** by running only the specialists you need - don't run Java architect on a pure .NET codebase

4. **Check the selection report** before running specialists to understand what will be analyzed

5. **Specialists work best** with their target technology - they provide 2-3x more insights than generic agents

## Adding New Specialists

If you need a specialist for another technology (Python, Go, PHP, etc.), you can:
1. Copy an existing specialist agent as a template
2. Modify it for your technology's patterns and frameworks
3. Save it in `.claude/agents/[technology]-architect.md`
4. Update the `architecture-selector` to detect and recommend it

## Summary

Specialist agents provide superior, technology-specific analysis compared to generic agents. Use them when:
- You know your technology stack
- You need deep, framework-specific insights  
- You want technology-specific recommendations
- You need to identify language-specific issues

The combination of `@architecture-selector` + appropriate specialists will give you the most comprehensive and accurate documentation of your codebase.