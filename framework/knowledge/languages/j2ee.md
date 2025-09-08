# J2EE/Jakarta EE Knowledge Base

## Detection Patterns
- File extensions: `.java`, `.jsp`, `.jspx`, `.tag`, `.tld`
- Deployment descriptors: `web.xml`, `application.xml`, `ejb-jar.xml`, `weblogic.xml`, `jboss-web.xml`
- EAR/WAR structure: `META-INF/`, `WEB-INF/`, `.ear`, `.war`, `.jar`
- Server configs: `server.xml`, `context.xml`, `persistence.xml`

## Common Application Servers
- WebSphere (IBM)
- WebLogic (Oracle)
- JBoss/WildFly (Red Hat)
- GlassFish
- Apache Tomcat (Servlet container)
- Apache TomEE

## J2EE Components & Patterns

### Web Tier
- **Servlets**: HTTP request handling
- **JSP (JavaServer Pages)**: Dynamic web pages
- **JSF (JavaServer Faces)**: Component-based UI
- **JSTL**: JSP Standard Tag Library
- **Struts/Struts2**: MVC framework
- **Filters & Listeners**: Request/response processing

### Business Tier
- **EJB (Enterprise JavaBeans)**:
  - Session Beans (Stateless/Stateful)
  - Message-Driven Beans (MDB)
  - Entity Beans (deprecated, use JPA)
- **JMS (Java Message Service)**: Async messaging
- **JTA (Java Transaction API)**: Distributed transactions
- **JNDI (Java Naming and Directory Interface)**: Resource lookup

### Data Tier
- **JPA (Java Persistence API)**: ORM standard
- **JDBC**: Database connectivity
- **Connection Pooling**: DataSource management
- **DAO Pattern**: Data Access Objects

## Analysis Focus Areas

### Architecture Patterns
- **Multi-tier Architecture**: Presentation, Business, Data tiers
- **MVC Pattern**: Model-View-Controller separation
- **Service Layer Pattern**: Business logic encapsulation
- **Front Controller**: Centralized request handling
- **Business Delegate**: Decoupling presentation from business tier
- **Session Facade**: Simplified business interface

### Security Vulnerabilities
- **Container-Managed Security**: Role-based access control
- **Form-Based Authentication**: Login form vulnerabilities
- **Session Management**: Session fixation, hijacking
- **SQL Injection**: PreparedStatement usage
- **XSS in JSP**: Output encoding issues
- **XML External Entity (XXE)**: XML parser configuration
- **Insecure Deserialization**: Java serialization risks
- **LDAP Injection**: Directory service queries

### Performance Issues
- **EJB Pool Exhaustion**: Insufficient bean instances
- **Database Connection Leaks**: Unclosed connections
- **Session State Size**: Large HTTP session objects
- **N+1 Query Problem**: Lazy loading issues
- **Remote EJB Calls**: Network latency
- **JSP Compilation**: First-time access delays
- **Memory Leaks**: Static references, ThreadLocal
- **Transaction Scope**: Overly broad transactions

### Legacy Patterns to Modernize
- **EJB 2.x → EJB 3.x/CDI**: Annotation-based configuration
- **Entity Beans → JPA**: Modern ORM
- **XDoclet → Annotations**: Metadata in code
- **Struts 1 → Spring MVC/JSF**: Modern web frameworks
- **Stateful Session Beans → REST + Client State**: Stateless services
- **SOAP Web Services → REST APIs**: Lightweight services
- **JSP Scriptlets → JSTL/EL**: Clean view layer
- **web.xml → Annotations**: Servlet 3.0+ configuration

### J2EE-Specific Anti-patterns
- **Service Locator Anti-pattern**: Use dependency injection
- **Anemic Domain Model**: Business logic in wrong layer
- **God Session Bean**: Oversized business components
- **Chatty Remote Interfaces**: Too many remote calls
- **Data Transfer Object Explosion**: Too many DTOs
- **Transaction Script**: Procedural instead of OO

### Best Practices
- Use connection pooling for database access
- Implement proper transaction boundaries
- Leverage container-managed security
- Use JPA for persistence layer
- Implement caching strategically
- Follow J2EE design patterns
- Use dependency injection (CDI)
- Implement proper logging (SLF4J)
- Handle exceptions at appropriate layers
- Use asynchronous processing for long tasks

## Migration Strategies

### J2EE to Jakarta EE
1. **Namespace Migration**:
   - `javax.*` → `jakarta.*`
   - Update all imports
   - Update XML schemas

2. **Application Server Migration**:
   - WebSphere → Open Liberty
   - WebLogic → WildFly
   - Update server-specific configurations

3. **EJB Modernization**:
   - EJB 2.x → EJB 3.x with annotations
   - Remove home/remote interfaces
   - Use CDI for dependency injection

### J2EE to Spring
1. **EJB → Spring Beans**
2. **JTA → Spring Transactions**
3. **JMS → Spring JMS/Spring Integration**
4. **JSF → Spring MVC/Thymeleaf**

### J2EE to Microservices
1. **Identify bounded contexts**
2. **Extract services from EARs**
3. **Replace remote EJBs with REST**
4. **Implement service discovery**
5. **Add API gateway**

## Specific Checks for Agents

### For architect-agent
- Identify EAR/WAR structure
- Map EJB dependencies
- Detect integration points (JMS, Web Services)
- Analyze deployment descriptors
- Find JNDI lookups

### For developer-agent
- Check for deprecated APIs
- Find synchronization issues
- Detect resource leaks
- Analyze transaction boundaries
- Check exception handling

### For analyst-agent
- Extract business logic from EJBs
- Map JMS message flows
- Identify transaction scopes
- Document security constraints
- Analyze batch jobs

## Common J2EE Configuration Files

### web.xml patterns
```xml
<!-- Security constraints -->
<security-constraint>
<security-role>
<filter>
<servlet>
<session-config>
```

### persistence.xml patterns
```xml
<persistence-unit>
<jta-data-source>
<properties>
```

### ejb-jar.xml patterns
```xml
<enterprise-beans>
<session>
<message-driven>
<assembly-descriptor>
```

## Technology Stack Combinations
- **Classic J2EE**: Servlets + JSP + EJB + JPA
- **Struts Stack**: Struts + Spring + Hibernate
- **JSF Stack**: JSF + EJB + JPA
- **Modern Jakarta EE**: CDI + JAX-RS + JPA + JSON-B