# Java Language Knowledge Base

## Detection Patterns
- File extensions: `.java`, `.jsp`, `.jspx`
- Build files: `pom.xml`, `build.gradle`, `build.gradle.kts`
- Config files: `application.properties`, `application.yml`

## Common Frameworks
- Spring Boot / Spring Framework
- Jakarta EE / Java EE
- Hibernate / JPA
- Apache Struts
- JSF (JavaServer Faces)

## Analysis Focus Areas

### Architecture Patterns
- MVC (Model-View-Controller)
- Layered Architecture (Controller, Service, Repository, Entity)
- Microservices with Spring Cloud
- Event-driven with Spring Events or JMS
- CQRS with Axon Framework

### Code Quality Checks
- **God Classes**: Classes > 1000 lines
- **Long Methods**: Methods > 100 lines
- **Cyclomatic Complexity**: Methods with complexity > 10
- **String Concatenation in Loops**: Performance anti-pattern
- **Null Pointer Risks**: Missing null checks
- **Resource Leaks**: Unclosed streams, connections

### Security Vulnerabilities
- SQL Injection (non-parameterized queries)
- Insecure Deserialization
- Weak Random Number Generation
- Hardcoded Credentials
- Log4j vulnerabilities
- XXE (XML External Entity) attacks
- Path Traversal vulnerabilities

### Performance Issues
- N+1 Query Problems (Hibernate/JPA)
- Synchronous blocking I/O
- Missing database indexes
- Connection pool exhaustion
- Memory leaks (static collections, listeners)
- Inefficient collection usage

### Legacy Patterns to Modernize
- **EJB 2.x → Spring/CDI**
- **SOAP → REST/GraphQL**
- **JSP → Modern Frontend (React/Angular)**
- **Servlets → Spring Controllers**
- **JDBC → JPA/Spring Data**
- **Java < 8 → Java 17/21 LTS**

### Best Practices
- Use Optional for nullable returns
- Implement proper equals/hashCode
- Use try-with-resources for AutoCloseable
- Prefer composition over inheritance
- Use dependency injection
- Implement proper logging with SLF4J
- Use builders for complex objects
- Leverage Java Stream API appropriately

### Migration Paths
1. **Java Version Upgrade**:
   - Java 7 → 8: Lambda expressions, Stream API
   - Java 8 → 11: Modules, var keyword
   - Java 11 → 17: Records, sealed classes, pattern matching

2. **Framework Migration**:
   - Struts → Spring MVC
   - EJB → Spring/CDI
   - JAX-WS → JAX-RS/Spring REST

3. **Build Tool Migration**:
   - Ant → Maven/Gradle
   - Maven → Gradle (for larger projects)

## Specific Checks for Agents

### For architect-agent
- Identify architectural layers
- Detect design patterns (Factory, Singleton, Observer)
- Find circular dependencies
- Analyze package structure

### For developer-agent
- Code style violations
- Unused imports and dead code
- Duplicate code detection
- Test coverage analysis

### For analyst-agent
- Business rule extraction from services
- Transaction boundary analysis
- Domain model identification
- Workflow detection in controllers