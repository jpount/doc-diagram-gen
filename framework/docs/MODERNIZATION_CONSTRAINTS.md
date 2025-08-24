# Modernization Constraints for Agent Analysis

## Project Configuration
- **Analysis Mode**: DOCUMENTATION_ONLY
- **Modernization**: NO

## Agent Constraints

### ALLOWED (Technical Debt & Current Stack Optimization)
✅ **Code Quality Improvements**
- Refactoring god classes and complex methods
- Dead code removal
- Code duplication elimination
- Naming convention improvements

✅ **Security Hardening (Current Stack)**
- Fix security vulnerabilities in existing framework
- Credential externalization
- Input validation improvements
- Authentication/authorization strengthening

✅ **Performance Optimization (Current Stack)**
- Database query optimization
- Caching configuration improvements
- Resource management fixes
- Memory leak resolution

✅ **Documentation & Analysis**
- Architecture documentation
- Code pattern analysis
- Dependency mapping
- Business logic extraction

### NOT ALLOWED (Modernization Recommendations)
❌ **Framework Migrations**
- Java EE → Jakarta EE migration suggestions
- .NET Framework → .NET Core recommendations
- Angular version upgrade paths
- Spring Boot conversion recommendations

❌ **Architectural Modernization**
- Microservices decomposition strategies
- Cloud-native patterns
- Container deployment recommendations
- Technology stack modernization

❌ **Technology Replacement**
- Database technology changes
- Frontend framework replacements
- Build tool modernization
- Infrastructure modernization

## Reminder for All Agents
When providing recommendations, focus ONLY on:
1. **Documenting existing architecture as-is**
2. **Identifying technical debt in current stack**
3. **Suggesting improvements that work within current technology choices**
4. **Security and performance optimizations for existing frameworks**

Do NOT suggest technology migrations, framework upgrades, or architectural modernization unless the project is configured for DOCUMENTATION_WITH_MODERNIZATION or FULL_MODERNIZATION_ASSISTED modes.