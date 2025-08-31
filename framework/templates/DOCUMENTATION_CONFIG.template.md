# Documentation Configuration

This file controls which documentation components and diagrams are generated during analysis. Customize this file based on your project needs and stakeholder requirements.

## Analysis Scope Configuration

### Core Analysis (Always Generated)
```yaml
core_analysis:
  enabled: true
  components:
    - codebase_overview          # Technology detection and metrics
    - architecture_analysis      # System architecture documentation
    - executive_summary         # High-level stakeholder summary

required_agents:
  - legacy-code-detective
  - architecture-selector  
  - executive-summary
```

### Backend Analysis
```yaml
backend_analysis:
  enabled: true
  components:
    - component_inventory       # Backend component catalog
    - api_documentation        # API endpoints and interfaces
    - data_model_analysis      # Database and entity analysis
    - business_logic_flows     # Process flows and business rules
    - performance_analysis     # Backend performance bottlenecks
    - security_analysis        # Security vulnerabilities

  detailed_analysis:
    include_class_diagrams: true
    include_sequence_diagrams: true
    include_er_diagrams: true
    
required_agents:
  - legacy-code-detective
  - api-documentation-specialist  
  - data-model-specialist
  - business-logic-analyst
  - performance-analyst
  - security-analyst
```

### Frontend Analysis
```yaml
frontend_analysis:
  enabled: true  # Set to false for backend-only applications
  components:
    - ui_technology_analysis    # Frontend framework detection
    - ui_component_inventory    # Component catalog and hierarchy
    - ui_flow_analysis         # User journeys and interactions
    - frontend_backend_integration # API integration patterns
    - ui_state_management      # State management analysis
    - ui_performance_accessibility # Performance and a11y assessment

  detailed_analysis:
    include_component_hierarchy: true
    include_user_flow_diagrams: true
    include_state_diagrams: true
    
required_agents:
  - ui-analysis-specialist
```

### Modernization Analysis
```yaml
modernization_analysis:
  enabled: true  # Set to false for documentation-only projects
  components:
    - domain_boundary_analysis  # Domain-driven design analysis
    - strangler_fig_strategy   # Extraction planning
    - modernization_assessment # Technology migration planning
    - ui_modernization_assessment # Frontend migration strategy
    - component_mapping        # Legacy to modern mappings
    - migration_roadmap        # Detailed implementation plan

  detailed_analysis:
    include_domain_diagrams: true
    include_migration_timeline: true
    include_extraction_sequence: true
    
required_agents:
  - domain-boundary-analyst
  - modernization-architect
```

## Diagram Configuration

### Architecture Diagrams
```yaml
architecture_diagrams:
  system_architecture: true      # Overall system overview
  deployment_diagram: true       # Current and target deployment
  security_architecture: true    # Security boundaries and flows
  backend_component_diagram: true # Backend component relationships
```

### Data Diagrams  
```yaml
data_diagrams:
  er_diagram: true               # Entity relationship diagram
  data_flow_diagram: true        # Data movement patterns
  database_architecture: true    # Database system overview
  data_access_layers: true       # Data access pattern visualization
```

### UI Diagrams
```yaml
ui_diagrams:
  ui_component_hierarchy: true   # Component relationships
  user_journey_flows: true       # User interaction flows
  page_navigation_flow: true     # Navigation patterns  
  ui_state_transitions: true     # State management flows
  api_integration_flow: true     # Frontend-backend integration
  authentication_flow: true      # Auth implementation
  realtime_data_flow: true       # Real-time features
```

### Business Process Diagrams
```yaml
business_diagrams:
  business_flows: true           # Core business processes
  business_state_machines: true  # Entity state transitions
  integration_sequences: true    # System integration flows
```

### Modernization Diagrams
```yaml
modernization_diagrams:
  domain_boundaries: true        # Domain boundary visualization
  domain_dependencies: true      # Inter-domain dependencies
  extraction_sequence: true      # Migration phases timeline
  strangler_fig_patterns: true   # Implementation patterns
  target_architecture: true      # Future state architecture
  migration_states: true         # Strangler fig in action
  network_topology: true         # Target infrastructure
  ui_current_vs_target: true     # UI migration comparison
  ui_migration_timeline: true    # Frontend migration roadmap
```

### Performance & Quality Diagrams
```yaml
performance_diagrams:
  performance_bottlenecks: true  # Performance issue visualization
  class_hierarchy: true          # Object-oriented design analysis
  ui_performance_bottlenecks: true # Frontend performance issues
  accessibility_compliance: true # A11y assessment visualization
```

## Output Structure Configuration

### Documentation Organization
```yaml
output_structure:
  group_by_domain: false         # Group docs by business domain
  group_by_type: true           # Group by analysis type (current default)
  include_index_pages: true     # Generate navigation indexes
  cross_reference_links: true   # Add cross-references between docs
```

### File Naming Convention
```yaml
file_naming:
  use_sequential_numbering: true # 01-, 02-, 03- prefixes
  include_agent_name: false     # Include agent name in filename
  use_descriptive_names: true   # Use descriptive vs generic names
```

## Agent Execution Configuration

### Execution Order
```yaml
execution_phases:
  phase_0_setup:
    - mcp-orchestrator
    - repomix-analyzer
    
  phase_1_discovery:
    - architecture-selector
    - legacy-code-detective
    
  phase_2_detailed_analysis:
    parallel_execution: true
    agents:
      - api-documentation-specialist
      - data-model-specialist  
      - ui-analysis-specialist     # Only if frontend_analysis.enabled
      - business-logic-analyst
      
  phase_3_cross_cutting:
    parallel_execution: true  
    agents:
      - performance-analyst
      - security-analyst
      
  phase_4_modernization:
    sequential_execution: true
    agents:
      - domain-boundary-analyst    # Only if modernization_analysis.enabled
      - modernization-architect    # Only if modernization_analysis.enabled
      
  phase_5_documentation:
    - diagram-architect
    - documentation-specialist
    - executive-summary
```

### Agent-Specific Configuration
```yaml
agent_config:
  legacy_code_detective:
    include_dependency_analysis: true
    include_technical_debt_metrics: true
    
  ui_analysis_specialist:
    analyze_accessibility: true
    analyze_performance: true
    include_component_testing: true
    
  data_model_specialist:
    include_query_analysis: true
    generate_schema_migration: true
    
  diagram_architect:
    validate_mermaid_syntax: true
    generate_both_formats: true  # .mmd files + inline diagrams
    include_diagram_descriptions: true
```

## Stakeholder-Specific Views

### Developer Focus
```yaml
developer_view:
  priority_sections:
    - component_inventory
    - api_documentation  
    - data_model_analysis
    - performance_analysis
    
  reduced_sections:
    - executive_summary
    - business_justification
```

### Management Focus  
```yaml
management_view:
  priority_sections:
    - executive_summary
    - modernization_assessment
    - migration_roadmap
    - risk_analysis
    
  reduced_sections:
    - detailed_technical_analysis
    - component_specifications
```

### Architecture Focus
```yaml
architecture_view:
  priority_sections:
    - architecture_analysis
    - domain_boundary_analysis
    - integration_patterns
    - target_architecture
    
  enhanced_diagrams: true
  include_decision_records: true
```

## Quality Assurance Configuration

### Validation Rules
```yaml
validation:
  mermaid_diagrams:
    validate_syntax: true
    require_descriptions: true
    
  documentation:
    min_business_rules: 25      # Minimum business rules to extract
    require_code_references: true
    check_cross_references: true
    
  coverage:
    min_component_coverage: 80   # % of components documented
    min_api_coverage: 90        # % of API endpoints documented
```

### Output Quality Metrics
```yaml
quality_metrics:
  track_token_usage: true
  measure_completeness: true
  validate_diagram_syntax: true
  check_broken_references: true
  assess_stakeholder_coverage: true
```

---

## Usage Instructions

1. **Customize for Your Project**: Edit the enabled flags based on your needs
2. **Stakeholder Requirements**: Enable specific views based on your audience
3. **Resource Constraints**: Disable optional components to reduce token usage
4. **Iterative Refinement**: Start with core analysis, then add detailed components

## Examples

### Backend-Only Application
```yaml
frontend_analysis:
  enabled: false
ui_diagrams:
  # All set to false
modernization_analysis:
  components:
    - ui_modernization_assessment: false
```

### Documentation-Only Project (No Modernization)
```yaml
modernization_analysis:
  enabled: false
modernization_diagrams:
  # All set to false
```

### Quick Assessment (Minimal Diagrams)
```yaml
# Enable only essential diagrams
architecture_diagrams:
  system_architecture: true
  # Others false
data_diagrams:
  er_diagram: true  
  # Others false
```