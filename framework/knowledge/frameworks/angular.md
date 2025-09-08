# Angular Framework Knowledge Base

## Detection Patterns
- Files: `angular.json`, `angular-cli.json`, `.angular-cli.json`
- Package.json: `@angular/core`, `@angular/cli`
- File patterns: `*.component.ts`, `*.service.ts`, `*.module.ts`
- AngularJS: `angular.js`, `ng-app` directives

## Version-Specific Features
- **AngularJS (1.x)**: Two-way binding, $scope, directives
- **Angular 2-8**: Components, TypeScript, RxJS
- **Angular 9+**: Ivy renderer, improved tree-shaking
- **Angular 14+**: Standalone components, typed forms
- **Angular 17+**: New control flow, signals

## Analysis Focus Areas

### Architecture Patterns
- Module-based architecture
- Lazy loading modules
- Micro-frontends with Module Federation
- State management (NgRx, Akita, NgXs)
- Smart vs Presentation components
- Feature modules organization

### Code Quality Checks
- **Large Components**: > 300 lines
- **Complex Templates**: > 150 lines HTML
- **Memory Leaks**: Unsubscribed observables
- **Change Detection Issues**: Inefficient strategies
- **Circular Dependencies**: Between modules/services
- **Direct DOM Manipulation**: Outside Angular's renderer

### Security Vulnerabilities
- XSS in templates (bypassSecurityTrust usage)
- Unsafe innerHTML binding
- Missing CSP headers
- Insecure API calls
- Local storage for sensitive data
- Missing authentication guards
- CSRF token implementation

### Performance Issues
- Change detection running too frequently
- Large bundle sizes
- Missing lazy loading
- Unoptimized images
- Memory leaks from subscriptions
- Inefficient RxJS operators
- Missing OnPush strategy
- Excessive HTTP calls

### Legacy Patterns to Modernize
- **AngularJS → Angular 2+**: Complete rewrite
- **Promises → Observables**: RxJS migration
- **HTTP → HttpClient**: Modern HTTP service
- **Template-driven → Reactive Forms**: Better validation
- **NgModules → Standalone Components**: Simpler architecture

### Best Practices
- Use OnPush change detection
- Implement proper unsubscribe patterns
- Use async pipe in templates
- Leverage Angular CLI schematics
- Implement proper error handling
- Use TypeScript strict mode
- Implement lazy loading
- Use trackBy for ngFor
- Implement proper form validation
- Use Angular DevTools

### RxJS Patterns
- **Common Operators**: map, filter, switchMap, mergeMap
- **Error Handling**: catchError, retry, retryWhen
- **Subscription Management**: takeUntil, take, first
- **Performance**: debounceTime, throttleTime, distinctUntilChanged
- **Combination**: combineLatest, forkJoin, merge

### State Management
1. **NgRx**:
   - Actions, Reducers, Effects, Selectors
   - DevTools integration
   - Entity adapter patterns

2. **Alternatives**:
   - Akita for simpler state
   - NgXs for class-based approach
   - Native services for small apps

## Specific Checks for Agents

### For architect-agent
- Module structure and dependencies
- Routing configuration
- Service architecture
- State management approach

### For developer-agent
- Component complexity
- Template syntax issues
- TypeScript usage quality
- Test coverage (Karma/Jest)

### For analyst-agent
- Form validation rules
- Business logic in services
- API integration patterns
- User flow through routes

### For diagram-agent
- Component hierarchy
- Module dependencies
- Data flow diagrams
- Route structure visualization

## Migration Strategies

### AngularJS to Angular
1. Hybrid approach with ngUpgrade
2. Incremental component migration
3. Route-by-route migration
4. Complete rewrite for smaller apps

### Version Upgrades
1. Use Angular Update Guide
2. Update one major version at a time
3. Fix breaking changes incrementally
4. Update dependencies in sync