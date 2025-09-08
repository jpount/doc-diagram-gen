# Supported Technologies

The framework now provides comprehensive support for analyzing and documenting applications built with the following technologies:

## Programming Languages

### Java & J2EE/Jakarta EE
- **Core Java**: All versions from Java 7 to Java 21
- **J2EE Components**: Servlets, JSP, EJB, JMS, JTA, JNDI
- **Application Servers**: WebSphere, WebLogic, JBoss/WildFly, Tomcat
- **Frameworks**: Spring, Spring Boot, Hibernate, Struts
- **Build Tools**: Maven, Gradle, Ant
- **Knowledge Files**: `languages/java.md`, `languages/j2ee.md`

### JavaScript/TypeScript
- **Runtime**: Node.js, Browser, Deno, Bun
- **Languages**: JavaScript (ES5-ES2023), TypeScript
- **Frontend**: React, Vue, Angular, Svelte, Next.js, Nuxt.js
- **Backend**: Express, Fastify, NestJS, Koa, Hapi
- **Testing**: Jest, Mocha, Cypress, Playwright
- **Build Tools**: Webpack, Vite, Rollup, ESBuild
- **Knowledge File**: `languages/javascript.md`

### Python
- **Versions**: Python 2.7 (legacy), Python 3.6-3.12
- **Web Frameworks**: Django, Flask, FastAPI, Pyramid
- **Data Science**: NumPy, Pandas, Scikit-learn, TensorFlow, PyTorch
- **Async**: asyncio, Celery, aiohttp
- **ORMs**: SQLAlchemy, Django ORM, Peewee
- **Package Management**: pip, pipenv, poetry, conda
- **Knowledge File**: `languages/python.md`

### .NET
- **Languages**: C#, VB.NET, F#
- **Frameworks**: .NET Framework, .NET Core, .NET 5+
- **Web**: ASP.NET, ASP.NET Core, Blazor
- **Desktop**: WPF, WinForms, MAUI
- **ORMs**: Entity Framework, Entity Framework Core
- **Knowledge File**: `languages/dotnet.md`

## Web Frameworks (Detailed Support)

### Angular
- All versions from AngularJS to Angular 17+
- Complete migration path analysis
- RxJS patterns and memory leak detection
- Knowledge File: `frameworks/angular.md`

## Detection Capabilities

The framework automatically detects:

### Language Detection
- File extensions and patterns
- Configuration files (pom.xml, package.json, requirements.txt)
- Framework-specific files (angular.json, settings.py)
- Build and deployment descriptors

### Framework Detection
- Framework-specific configuration files
- Directory structures
- Dependency declarations
- Import patterns

### J2EE/Jakarta EE Specific
- Deployment descriptors (web.xml, ejb-jar.xml)
- EAR/WAR file structures
- Application server configurations
- JPA persistence configurations

### JavaScript/TypeScript Specific
- Package.json dependencies
- TypeScript configurations
- Framework-specific files (next.config.js, vue.config.js)
- Build tool configurations

### Python Specific
- Virtual environment detection
- Package management files
- Framework-specific patterns (manage.py for Django)
- Jupyter notebook detection

## Analysis Capabilities

For each technology, the framework provides:

### Architecture Analysis
- Design pattern identification
- Component structure mapping
- Dependency analysis
- Integration point detection

### Code Quality Assessment
- Language-specific anti-patterns
- Framework best practices
- Security vulnerability detection
- Performance bottleneck identification

### Business Logic Extraction
- Framework-specific business rule patterns
- API endpoint documentation
- Data flow analysis
- Domain model extraction

### Migration Planning
- Version upgrade paths
- Framework migration strategies
- Modernization recommendations
- Technology stack updates

## How Agents Use Knowledge

1. **Technology Detection**: Setup script detects technologies in codebase
2. **Knowledge Loading**: Agents load relevant knowledge files
3. **Contextual Analysis**: Apply technology-specific patterns and checks
4. **Targeted Recommendations**: Provide framework-specific improvements

## Adding New Technologies

To add support for a new technology:

1. Create knowledge file in appropriate directory:
   - `framework/knowledge/languages/` for programming languages
   - `framework/knowledge/frameworks/` for frameworks
   - `framework/knowledge/patterns/` for architectural patterns

2. Include in the knowledge file:
   - Detection patterns
   - Common frameworks and libraries
   - Analysis focus areas
   - Anti-patterns and best practices
   - Migration strategies
   - Agent-specific checks

3. Update detection rules in `setup_simple.py`

4. Agents will automatically use the new knowledge

## Technology Combinations

The framework intelligently handles common technology combinations:

- **Full-Stack Java**: Java + Spring + Angular/React
- **MEAN Stack**: MongoDB + Express + Angular + Node.js
- **Django + React**: Python backend with JavaScript frontend
- **.NET + Angular**: C# backend with TypeScript frontend
- **J2EE + JSF**: Traditional enterprise Java stack

## Output Customization

Documentation is tailored based on detected technologies:

- **J2EE Projects**: EJB documentation, deployment descriptors, JNDI resources
- **Node.js Projects**: NPM scripts, middleware documentation, async patterns
- **Python Projects**: Virtual environment setup, package management, WSGI configuration
- **Hybrid Projects**: Clear separation of frontend/backend documentation