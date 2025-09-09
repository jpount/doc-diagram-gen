# JSF (JavaServer Faces) Knowledge Base

## Detection Patterns
- Configuration files: `faces-config.xml`, `web.xml` with JSF servlet mapping
- View files: `.xhtml`, `.jsf`, `.faces` extensions
- Taglibs: `xmlns:h="http://java.sun.com/jsf/html"`, `xmlns:f="http://java.sun.com/jsf/core"`
- Annotations: `@ManagedBean`, `@Named`, `@ViewScoped`, `@SessionScoped`, `@RequestScoped`
- Dependencies: `jsf-api.jar`, `jsf-impl.jar`, `myfaces-*.jar`

## Architecture Patterns
- **MVC Pattern**: Model-View-Controller architecture
- **Component-Based**: UI built from reusable components
- **Managed Beans**: Server-side objects managing application state
- **Navigation Model**: Declarative navigation between pages
- **Event-Driven**: Action events and value change events

## Common Components
- **Facelets**: Primary view technology (.xhtml templates)
- **Managed Beans**: CDI beans or JSF managed beans
- **Converters**: Data conversion between UI and model
- **Validators**: Input validation components
- **Composite Components**: Custom reusable UI components
- **Resource Handling**: CSS, JS, image resource management

## Lifecycle Phases
1. **Restore View**: Restore/create component tree
2. **Apply Request Values**: Populate component tree with request data
3. **Process Validations**: Validate component values
4. **Update Model Values**: Update backing bean properties
5. **Invoke Application**: Process events and navigation
6. **Render Response**: Generate response

## Performance Considerations
- **View State Management**: Client vs server-side state saving
- **Component Tree Size**: Minimize component complexity
- **AJAX Optimization**: Partial page rendering
- **Resource Bundling**: Combine CSS/JS resources
- **Caching Strategies**: Template and resource caching

## Security Considerations
- **CSRF Protection**: Cross-site request forgery prevention
- **XSS Prevention**: Output escaping and validation
- **View State Tampering**: Protect view state integrity
- **Input Validation**: Server-side validation enforcement

## Common Anti-Patterns
- **God Bean**: Overly large managed beans
- **Stateful Abuse**: Excessive session state
- **Deep Component Trees**: Overly nested component structures
- **Logic in Views**: Business logic in XHTML templates