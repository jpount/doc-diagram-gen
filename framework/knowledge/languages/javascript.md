# JavaScript/TypeScript Knowledge Base

## Detection Patterns
- JavaScript files: `.js`, `.mjs`, `.cjs`, `.jsx`
- TypeScript files: `.ts`, `.tsx`, `.d.ts`
- Config files: `package.json`, `tsconfig.json`, `jsconfig.json`, `.eslintrc`, `.prettierrc`
- Build files: `webpack.config.js`, `rollup.config.js`, `vite.config.js`, `esbuild.config.js`
- Lock files: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`

## Runtime Environments
- **Node.js**: Server-side JavaScript
- **Browser**: Client-side JavaScript
- **Deno**: Secure runtime for JS/TS
- **Bun**: Fast all-in-one JavaScript runtime
- **Electron**: Desktop applications
- **React Native**: Mobile applications

## Common Frameworks & Libraries

### Frontend Frameworks
- **React**: Component-based UI library
- **Vue.js**: Progressive framework
- **Angular**: Full-featured framework (see angular.md)
- **Svelte/SvelteKit**: Compile-time optimized
- **Next.js**: React framework with SSR/SSG
- **Nuxt.js**: Vue framework with SSR/SSG
- **Gatsby**: Static site generator

### Backend Frameworks (Node.js)
- **Express.js**: Minimal web framework
- **Fastify**: High-performance framework
- **NestJS**: Enterprise-grade TypeScript framework
- **Koa.js**: Next generation Express
- **Hapi.js**: Configuration-centric framework
- **AdonisJS**: Full-stack MVC framework
- **Meteor**: Full-stack platform

### Testing Frameworks
- **Jest**: Testing platform
- **Mocha/Chai**: Test framework and assertions
- **Vitest**: Vite-native testing
- **Cypress**: E2E testing
- **Playwright**: Browser automation
- **Testing Library**: Testing utilities

## Analysis Focus Areas

### Code Quality Checks
- **Large Files**: > 500 lines
- **Complex Functions**: Cyclomatic complexity > 10
- **Deep Nesting**: > 4 levels
- **Long Functions**: > 50 lines
- **Callback Hell**: Nested callbacks > 3 levels
- **Magic Numbers**: Hardcoded values
- **Dead Code**: Unreachable or unused code

### TypeScript-Specific
- **Type Safety**: Use of `any` type
- **Strict Mode**: Configuration settings
- **Type Assertions**: Overuse of `as` keyword
- **Optional Chaining**: Missing null checks
- **Generics**: Proper type constraints
- **Enums vs Unions**: Best practice usage
- **Declaration Files**: Missing type definitions

### Security Vulnerabilities
- **XSS**: Unsafe innerHTML, eval() usage
- **Injection**: SQL/NoSQL injection risks
- **Dependencies**: Vulnerable npm packages
- **CORS**: Misconfigured cross-origin policies
- **Authentication**: JWT implementation issues
- **Environment Variables**: Exposed secrets
- **Input Validation**: Missing sanitization
- **Prototype Pollution**: Object manipulation

### Performance Issues
- **Bundle Size**: Large JavaScript bundles
- **Memory Leaks**: Event listeners, closures
- **Blocking Operations**: Synchronous I/O
- **Inefficient Loops**: forEach vs for
- **Re-renders**: React/Vue rendering issues
- **Lazy Loading**: Missing code splitting
- **Caching**: Absent or poor caching strategy
- **Database Queries**: N+1 problems in ORMs

### Async Patterns
- **Callbacks**: Error-first callbacks
- **Promises**: Promise chains and error handling
- **Async/Await**: Proper error handling
- **Event Emitters**: Memory leak risks
- **Streams**: Backpressure handling
- **Workers**: Web/Worker threads usage

### Anti-patterns to Detect
- **Global Variables**: Namespace pollution
- **Monkey Patching**: Prototype modifications
- **Pyramid of Doom**: Nested callbacks
- **Promise Hell**: Unmanaged promise chains
- **Spaghetti Code**: Poor organization
- **God Objects**: Oversized modules
- **Copy-Paste Programming**: Code duplication
- **Premature Optimization**: Over-engineering

### Best Practices
- Use strict mode (`'use strict'`)
- Implement proper error handling
- Use const/let instead of var
- Leverage ES6+ features appropriately
- Implement proper logging
- Use environment variables for config
- Follow naming conventions
- Implement input validation
- Use linting and formatting tools
- Write comprehensive tests

## Modern JavaScript Features

### ES6+ Features to Check
- Arrow functions
- Template literals
- Destructuring
- Spread/Rest operators
- Classes
- Modules (import/export)
- Promises
- Map/Set/WeakMap/WeakSet
- Symbol
- Proxy/Reflect
- Async/Await
- Optional chaining (?.)
- Nullish coalescing (??)

### TypeScript Features
- Interfaces vs Types
- Generics
- Decorators
- Namespaces vs Modules
- Type guards
- Conditional types
- Mapped types
- Utility types
- Strict null checks

## Package Management

### NPM/Yarn/PNPM Checks
- **Lock File**: Presence and consistency
- **Audit**: Security vulnerabilities
- **Outdated**: Package updates available
- **Unused**: Dependencies not imported
- **Version Ranges**: Overly permissive
- **Dev vs Prod**: Proper dependency classification
- **Scripts**: Build/test/deploy commands

## Build & Bundling

### Build Tool Analysis
- **Webpack**: Configuration complexity
- **Vite**: Modern tooling adoption
- **Rollup**: Library bundling
- **Parcel**: Zero-config setup
- **ESBuild**: Build performance
- **SWC**: Rust-based compilation

### Optimization Checks
- Tree shaking
- Code splitting
- Minification
- Source maps
- Asset optimization
- Cache busting
- Compression (gzip/brotli)

## Migration Strategies

### JavaScript to TypeScript
1. **Gradual Migration**:
   - Add tsconfig.json with allowJs
   - Rename files .js → .ts incrementally
   - Add types progressively
   - Enable strict mode gradually

2. **Tooling Migration**:
   - ESLint → ESLint with TS support
   - Add @types/* packages
   - Configure IDE for TypeScript

### Legacy to Modern
- **CommonJS → ES Modules**
- **Callbacks → Promises → Async/Await**
- **Class Components → Functional (React)**
- **Options API → Composition API (Vue)**
- **Grunt/Gulp → Modern bundlers**

### Monolith to Microservices
1. Identify service boundaries
2. Extract shared utilities
3. Implement API gateway
4. Add service discovery
5. Implement distributed tracing

## Specific Checks for Agents

### For architect-agent
- Module organization (folders/files)
- Dependency graph analysis
- API structure (REST/GraphQL)
- Frontend/Backend separation
- Microservices boundaries

### For developer-agent
- Code style consistency
- Test coverage metrics
- Linting rule violations
- TypeScript strictness
- Bundle size analysis

### For analyst-agent
- Business logic location
- Data flow patterns
- State management approach
- API endpoint analysis
- Event handling patterns

### For diagram-agent
- Component hierarchy
- Data flow diagrams
- Module dependencies
- API sequence diagrams
- State machine diagrams

## Framework-Specific Patterns

### React Patterns
- Hooks usage and custom hooks
- Context API vs Redux/MobX
- Component composition
- Render props
- Higher-order components
- Error boundaries

### Vue Patterns
- Composition API usage
- Vuex/Pinia state management
- Component communication
- Mixins vs Composables
- Reactive data patterns

### Node.js Patterns
- Middleware architecture
- Error handling middleware
- Database connection patterns
- Authentication strategies
- API versioning
- Rate limiting

## Testing Patterns
- Unit test coverage
- Integration test presence
- E2E test scenarios
- Mocking strategies
- Test data management
- CI/CD integration