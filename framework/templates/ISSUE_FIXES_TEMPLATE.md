# Issue Fixes and Code Examples Template

## Overview

All architecture, performance, and security agents MUST provide specific fixes and code examples for any issues and technical debt they identify. This template provides the structure for presenting actionable solutions.

## Issue Documentation Format

### Standard Issue Structure

For each issue identified, agents MUST provide:

```markdown
### 🔴 [Issue Name] - [Severity Level]

**Issue Description**: Clear description of the problem
**Impact**: What this issue affects (performance, security, maintainability)
**Risk Level**: Low/Medium/High/Critical
**Effort to Fix**: Low/Medium/High/Very High

#### Current Code (Problematic)
```[language]
// Show actual problematic code from analysis
[current problematic code]
```

#### Recommended Fix
```[language]
// Show improved version with explanations
[fixed code with improvements]
```

#### Why This Fix Works
- Explanation point 1
- Explanation point 2
- Key improvement benefits

#### Implementation Steps
1. Step 1 description
2. Step 2 description
3. Step 3 description

#### Additional Resources
- Links to best practices
- Documentation references
- Framework-specific guides
```

## Common Fix Categories

### Java Architecture Fixes

#### 1. Legacy EJB to Modern Spring
```java
// ❌ Problematic: Legacy EJB pattern
@Stateless
@LocalBean
public class TradeServiceEJB implements TradeServiceLocal {
    @PersistenceContext
    private EntityManager entityManager;
    
    @Resource
    private SessionContext sessionContext;
    
    public Trade createTrade(TradeRequest request) {
        // Complex EJB-specific transaction management
        if (sessionContext.getRollbackOnly()) {
            throw new EJBException("Transaction marked for rollback");
        }
        // Business logic mixed with infrastructure
        return processTradeEJB(request);
    }
}

// ✅ Improved: Modern Spring Boot service
@Service
@Transactional
public class TradeService {
    
    private final TradeRepository tradeRepository;
    private final TradeValidator tradeValidator;
    private final NotificationService notificationService;
    
    public TradeService(TradeRepository tradeRepository, 
                       TradeValidator tradeValidator,
                       NotificationService notificationService) {
        this.tradeRepository = tradeRepository;
        this.tradeValidator = tradeValidator;
        this.notificationService = notificationService;
    }
    
    public Trade createTrade(TradeRequest request) {
        // Clean separation of concerns
        tradeValidator.validate(request);
        Trade trade = Trade.from(request);
        Trade savedTrade = tradeRepository.save(trade);
        notificationService.notifyTradeCreated(savedTrade);
        return savedTrade;
    }
}
```

#### 2. Mixed JPA/JDBC to Consistent Data Access
```java
// ❌ Problematic: Mixed JPA and JDBC
public class AccountDataBean {
    @PersistenceContext
    private EntityManager entityManager;
    
    private DataSource dataSource;
    
    public Account getAccount(String accountId) {
        // Using JPA
        return entityManager.find(Account.class, accountId);
    }
    
    public List<Account> getAccountsByStatus(String status) {
        // Using raw JDBC - inconsistent!
        try (Connection conn = dataSource.getConnection();
             PreparedStatement ps = conn.prepareStatement(
                 "SELECT * FROM accounts WHERE status = ?")) {
            ps.setString(1, status);
            ResultSet rs = ps.executeQuery();
            // Manual result mapping...
        }
    }
}

// ✅ Improved: Consistent JPA with Spring Data
@Repository
public interface AccountRepository extends JpaRepository<Account, String> {
    
    @Query("SELECT a FROM Account a WHERE a.status = :status")
    List<Account> findByStatus(@Param("status") String status);
    
    @Query("""
        SELECT a FROM Account a 
        WHERE a.status = :status 
        AND a.createdDate > :since
        ORDER BY a.createdDate DESC
        """)
    List<Account> findRecentAccountsByStatus(@Param("status") String status, 
                                           @Param("since") LocalDateTime since);
    
    // For complex queries, use @Query with JPQL or native SQL consistently
    @Query(value = """
        SELECT a.*, p.profile_data 
        FROM accounts a 
        LEFT JOIN account_profiles p ON a.account_id = p.account_id 
        WHERE a.status = ?1 
        AND a.balance > ?2
        """, nativeQuery = true)
    List<Object[]> findAccountsWithProfilesByStatusAndBalance(String status, BigDecimal minBalance);
}

// Service layer becomes cleaner
@Service
@Transactional
public class AccountService {
    
    private final AccountRepository accountRepository;
    
    public AccountService(AccountRepository accountRepository) {
        this.accountRepository = accountRepository;
    }
    
    public List<Account> getAccountsByStatus(String status) {
        return accountRepository.findByStatus(status);
    }
}
```

#### 3. Legacy Configuration to Modern Configuration
```java
// ❌ Problematic: XML configuration with hardcoded values
<!-- persistence.xml -->
<persistence-unit name="tradePU">
    <jta-data-source>jdbc/TradeDataSource</jta-data-source>
    <properties>
        <property name="hibernate.dialect" value="org.hibernate.dialect.DerbyDialect"/>
        <property name="hibernate.hbm2ddl.auto" value="create-drop"/>
        <property name="hibernate.show_sql" value="true"/>
    </properties>
</persistence-unit>

// ✅ Improved: Modern Spring Boot configuration
// application.yml
spring:
  datasource:
    url: ${DATABASE_URL:jdbc:h2:mem:testdb}
    username: ${DATABASE_USERNAME:sa}
    password: ${DATABASE_PASSWORD:}
    driver-class-name: ${DATABASE_DRIVER:org.h2.Driver}
    
  jpa:
    hibernate:
      ddl-auto: ${HIBERNATE_DDL_AUTO:validate}
    show-sql: ${SHOW_SQL:false}
    properties:
      hibernate:
        dialect: ${HIBERNATE_DIALECT:org.hibernate.dialect.H2Dialect}
        format_sql: true
        use_sql_comments: true

// Configuration class for complex setups
@Configuration
@EnableJpaRepositories(basePackages = "com.trading.repository")
public class DatabaseConfiguration {
    
    @Bean
    @ConfigurationProperties(prefix = "spring.datasource")
    public DataSource dataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    public LocalContainerEntityManagerFactoryBean entityManagerFactory(DataSource dataSource) {
        LocalContainerEntityManagerFactoryBean em = new LocalContainerEntityManagerFactoryBean();
        em.setDataSource(dataSource);
        em.setPackagesToScan("com.trading.entity");
        
        HibernateJpaVendorAdapter vendorAdapter = new HibernateJpaVendorAdapter();
        em.setJpaVendorAdapter(vendorAdapter);
        
        Properties properties = new Properties();
        properties.put("hibernate.dialect", "${hibernate.dialect}");
        properties.put("hibernate.hbm2ddl.auto", "${hibernate.hbm2ddl.auto}");
        em.setJpaProperties(properties);
        
        return em;
    }
}
```

### Performance Fixes

#### 1. N+1 Query Problem
```java
// ❌ Problematic: N+1 queries
@Entity
public class Account {
    @OneToMany(mappedBy = "account", fetch = FetchType.LAZY)
    private List<Order> orders;
}

// Service causing N+1
@Service
public class ReportService {
    public List<AccountReport> generateAccountReports() {
        List<Account> accounts = accountRepository.findAll(); // 1 query
        return accounts.stream()
            .map(account -> {
                // N queries - one for each account's orders!
                int orderCount = account.getOrders().size();
                return new AccountReport(account, orderCount);
            })
            .collect(toList());
    }
}

// ✅ Fixed: Use fetch joins or entity graphs
@Repository
public interface AccountRepository extends JpaRepository<Account, String> {
    
    @Query("SELECT DISTINCT a FROM Account a LEFT JOIN FETCH a.orders")
    List<Account> findAllWithOrders();
    
    // Alternative: Using @EntityGraph
    @EntityGraph(attributePaths = {"orders"})
    @Query("SELECT a FROM Account a")
    List<Account> findAllWithOrdersUsingEntityGraph();
}

@Service
public class ReportService {
    public List<AccountReport> generateAccountReports() {
        // Single query fetches accounts with orders
        List<Account> accounts = accountRepository.findAllWithOrders();
        return accounts.stream()
            .map(account -> {
                // No additional queries needed
                int orderCount = account.getOrders().size();
                return new AccountReport(account, orderCount);
            })
            .collect(toList());
    }
}
```

#### 2. Inefficient Pagination
```java
// ❌ Problematic: Loading all data then paginating in memory
@Service
public class OrderService {
    public Page<Order> getOrders(int page, int size) {
        List<Order> allOrders = orderRepository.findAll(); // Loads everything!
        int start = page * size;
        int end = Math.min(start + size, allOrders.size());
        List<Order> pageOrders = allOrders.subList(start, end);
        return new PageImpl<>(pageOrders, PageRequest.of(page, size), allOrders.size());
    }
}

// ✅ Fixed: Database-level pagination
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    
    @Query("SELECT o FROM Order o WHERE o.status = :status ORDER BY o.createdDate DESC")
    Page<Order> findByStatusOrderByCreatedDateDesc(@Param("status") OrderStatus status, Pageable pageable);
}

@Service
public class OrderService {
    public Page<Order> getOrders(int page, int size, OrderStatus status) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdDate").descending());
        return orderRepository.findByStatusOrderByCreatedDateDesc(status, pageable);
    }
}
```

### Security Fixes

#### 1. Hardcoded Credentials
```java
// ❌ Problematic: Hardcoded credentials
@Configuration
public class DatabaseConfig {
    @Bean
    public DataSource dataSource() {
        DriverManagerDataSource dataSource = new DriverManagerDataSource();
        dataSource.setDriverClassName("com.mysql.cj.jdbc.Driver");
        dataSource.setUrl("jdbc:mysql://localhost:3306/trading");
        dataSource.setUsername("admin");  // ❌ Hardcoded!
        dataSource.setPassword("password123");  // ❌ Hardcoded!
        return dataSource;
    }
}

// ✅ Fixed: Environment-based configuration
@Configuration
public class DatabaseConfig {
    
    @Value("${spring.datasource.url}")
    private String databaseUrl;
    
    @Value("${spring.datasource.username}")
    private String databaseUsername;
    
    @Value("${spring.datasource.password}")
    private String databasePassword;
    
    @Bean
    public DataSource dataSource() {
        DriverManagerDataSource dataSource = new DriverManagerDataSource();
        dataSource.setDriverClassName("com.mysql.cj.jdbc.Driver");
        dataSource.setUrl(databaseUrl);
        dataSource.setUsername(databaseUsername);
        dataSource.setPassword(databasePassword);
        return dataSource;
    }
}

// application.yml (example - real values from environment/secrets)
spring:
  datasource:
    url: ${DATABASE_URL}
    username: ${DATABASE_USERNAME}
    password: ${DATABASE_PASSWORD}

// Or better yet, use Spring Boot's auto-configuration:
// Just set environment variables: DATABASE_URL, DATABASE_USERNAME, DATABASE_PASSWORD
// Spring Boot will automatically configure the DataSource
```

#### 2. SQL Injection Vulnerability
```java
// ❌ Problematic: SQL injection risk
@Repository
public class UserRepository {
    
    @PersistenceContext
    private EntityManager entityManager;
    
    public User findByUsername(String username) {
        // ❌ Vulnerable to SQL injection!
        String sql = "SELECT u FROM User u WHERE u.username = '" + username + "'";
        return entityManager.createQuery(sql, User.class)
                          .getSingleResult();
    }
}

// ✅ Fixed: Parameterized queries
@Repository
public class UserRepository {
    
    @PersistenceContext
    private EntityManager entityManager;
    
    // Option 1: JPQL with named parameters
    public User findByUsername(String username) {
        return entityManager
            .createQuery("SELECT u FROM User u WHERE u.username = :username", User.class)
            .setParameter("username", username)
            .getSingleResult();
    }
    
    // Option 2: Spring Data JPA (even better)
    @Query("SELECT u FROM User u WHERE u.username = :username")
    Optional<User> findByUsernameSecure(@Param("username") String username);
    
    // Option 3: For complex queries, use Criteria API
    public List<User> findUsersByCriteria(String username, String email) {
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<User> query = cb.createQuery(User.class);
        Root<User> user = query.from(User.class);
        
        List<Predicate> predicates = new ArrayList<>();
        
        if (username != null) {
            predicates.add(cb.equal(user.get("username"), username));
        }
        if (email != null) {
            predicates.add(cb.equal(user.get("email"), email));
        }
        
        query.where(predicates.toArray(new Predicate[0]));
        return entityManager.createQuery(query).getResultList();
    }
}
```

## Fix Priority Guidelines

### Critical Fixes (🔴)
- Security vulnerabilities
- Data corruption risks  
- Production-breaking issues

### High Priority Fixes (🟠)
- Performance bottlenecks
- Maintainability issues
- Technical debt blocking new features

### Medium Priority Fixes (🟡)
- Code quality improvements
- Non-critical performance optimizations
- Documentation improvements

### Information Only (⚠️)
- Best practice suggestions
- Future considerations
- Alternative approaches

## Implementation Guidance

### For Each Fix Provide:
1. **Clear Problem Description**
2. **Before/After Code Examples**
3. **Step-by-step Implementation**
4. **Testing Recommendations**
5. **Risk Assessment**
6. **Resource Links**

### Code Example Requirements:
- Use actual detected patterns from the codebase
- Show complete, working examples
- Include necessary imports and annotations
- Explain why the fix works
- Provide testing examples where relevant

This template ensures consistent, actionable recommendations across all agents while maintaining the framework's quality standards.