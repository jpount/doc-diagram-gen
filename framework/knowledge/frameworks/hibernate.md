# Hibernate Knowledge Base

## Detection Patterns
- Configuration files: `hibernate.cfg.xml`, `persistence.xml`
- Annotations: `@Entity`, `@Table`, `@Id`, `@GeneratedValue`, `@OneToMany`, `@ManyToOne`, `@JoinColumn`
- Imports: `org.hibernate.*`, `javax.persistence.*`, `jakarta.persistence.*`
- Property files: `hibernate.properties`

## Architecture Patterns
- **ORM Pattern**: Object-Relational Mapping
- **Session Factory**: Central configuration and session management
- **Session Per Request**: Web application session management
- **DAO Pattern**: Data Access Objects with Hibernate
- **Repository Pattern**: Modern data access abstraction

## Common Components
- **SessionFactory**: Thread-safe factory for Session instances
- **Session**: Single-threaded, short-lived object representing conversation between app and database
- **Transaction**: Database transaction management
- **Query/Criteria**: Query interfaces for data retrieval
- **HQL**: Hibernate Query Language

## Performance Considerations
- **N+1 Query Problem**: Common performance issue with lazy loading
- **First/Second Level Caching**: Hibernate caching strategies
- **Batch Processing**: Bulk operations for large datasets
- **Connection Pooling**: Database connection management
- **Lazy vs Eager Loading**: Fetch strategies

## Security Considerations
- **HQL Injection**: Parameterized queries to prevent injection attacks
- **Entity Access Control**: Securing entity-level operations
- **Connection Security**: Database connection encryption

## Common Anti-Patterns
- **God Entity**: Overly complex entity classes
- **Chatty Interface**: Too many database calls
- **Premature Optimization**: Over-caching or complex mappings
- **Session-in-View**: Keeping session open in presentation layer