# .NET Language Knowledge Base

## Detection Patterns
- File extensions: `.cs`, `.vb`, `.fs`, `.cshtml`, `.vbhtml`
- Project files: `.csproj`, `.vbproj`, `.fsproj`, `.sln`
- Config files: `appsettings.json`, `web.config`, `app.config`

## Common Frameworks
- ASP.NET Core / ASP.NET MVC
- Entity Framework Core / EF6
- WPF / WinForms
- Blazor
- Web API
- WCF (Windows Communication Foundation)
- Azure Functions

## Analysis Focus Areas

### Architecture Patterns
- Clean Architecture / Onion Architecture
- CQRS with MediatR
- Domain-Driven Design (DDD)
- Microservices with Service Fabric or Kubernetes
- Serverless with Azure Functions
- Event Sourcing

### Code Quality Checks
- **Large Classes**: > 500 lines
- **Complex Methods**: Cyclomatic complexity > 15
- **Async/Await Issues**: async void, missing ConfigureAwait
- **Disposal Issues**: Missing using statements/IDisposable
- **LINQ Performance**: Multiple enumerations, inefficient queries
- **Nullable Reference Types**: Not enabled or improperly used

### Security Vulnerabilities
- SQL Injection in raw SQL queries
- XSS in Razor views
- CSRF token missing
- Insecure deserialization (Newtonsoft.Json TypeNameHandling)
- Weak cryptography implementations
- Cleartext storage of sensitive data
- Missing authentication/authorization

### Performance Issues
- Entity Framework N+1 queries
- Missing async/await in I/O operations
- Large object graphs in memory
- Inefficient LINQ queries
- Missing output caching
- Database connection leaks
- Excessive allocations (boxing/unboxing)

### Legacy Patterns to Modernize
- **.NET Framework → .NET 6/7/8**
- **Web Forms → Blazor/MVC**
- **WCF → gRPC/REST**
- **ASMX Web Services → Web API**
- **ADO.NET → Entity Framework Core**
- **MSTest → xUnit/NUnit**

### Best Practices
- Use dependency injection (IServiceCollection)
- Implement IAsyncDisposable for async cleanup
- Use CancellationToken for async operations
- Leverage nullable reference types
- Use record types for DTOs
- Implement proper logging with ILogger
- Use configuration providers
- Apply SOLID principles

### Migration Paths
1. **.NET Framework to .NET Core/.NET 5+**:
   - Use .NET Portability Analyzer
   - Migrate to .NET Standard libraries first
   - Update NuGet packages
   - Replace System.Configuration with IConfiguration

2. **Legacy UI to Modern**:
   - Web Forms → Blazor Server/WASM
   - WPF → WPF on .NET Core or MAUI
   - WinForms → WinForms on .NET Core or MAUI

3. **Data Access Evolution**:
   - ADO.NET → Dapper (minimal change)
   - ADO.NET → Entity Framework Core (full ORM)
   - WCF Data Services → OData/GraphQL

## Specific Checks for Agents

### For architect-agent
- Identify layers (API, Business, Data)
- Detect dependency injection usage
- Find service boundaries
- Analyze NuGet dependencies

### For developer-agent
- Code analysis rule violations
- Async best practices
- Memory leak patterns
- Unit test quality

### For analyst-agent
- Business logic in controllers vs services
- Domain model completeness
- Validation rule extraction
- API endpoint analysis