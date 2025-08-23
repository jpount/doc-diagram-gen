# Analysis Mode Configuration

## Selected Mode
**Mode:** {{ANALYSIS_MODE}}

## Available Modes

### 1. DOCUMENTATION_ONLY (Default)
Primary focus on documenting and analyzing the existing codebase:
- Comprehensive documentation generation
- Architecture diagrams and visualizations
- Technical debt analysis
- Performance bottleneck identification
- Security vulnerability assessment
- Code quality metrics
- Dependency analysis
- Business logic extraction
- Improvement recommendations for current stack
- NO modernization planning

### 2. DOCUMENTATION_WITH_MODERNIZATION
Everything from DOCUMENTATION_ONLY plus:
- Modernization strategy and roadmap
- Migration phases and timelines
- Target architecture design
- Technology translation matrix
- Risk assessment for migration
- Domain-driven design boundaries
- Microservices decomposition strategy
- Cloud migration planning
- Requires TARGET_TECH_STACK.md configuration

### 3. FULL_MODERNIZATION_ASSISTED
Everything from DOCUMENTATION_WITH_MODERNIZATION plus:
- Claude Code assists with technology recommendations
- Automated gap analysis
- Interactive modernization planning
- AI-suggested TARGET_TECH_STACK.md generation
- Continuous modernization guidance
- Implementation approach suggestions
- Best practices recommendations

## Configuration

### Mode Selection
```yaml
analysis_mode: DOCUMENTATION_ONLY
```

### Mode-Specific Settings

#### DOCUMENTATION_ONLY Settings
```yaml
documentation:
  include_diagrams: true
  include_metrics: true
  include_recommendations: true
  tech_debt_analysis: true
  performance_analysis: true
  security_analysis: true
```

#### DOCUMENTATION_WITH_MODERNIZATION Settings
```yaml
modernization:
  target_tech_stack: "TARGET_TECH_STACK.md"
  include_roadmap: true
  include_risk_assessment: true
  migration_phases: true
  domain_boundaries: true
```

#### FULL_MODERNIZATION_ASSISTED Settings
```yaml
ai_assistance:
  suggest_tech_stack: true
  interactive_planning: true
  continuous_guidance: true
  implementation_suggestions: true
```

## Quick Start

To use this configuration:
1. Copy this template to project root as `ANALYSIS_MODE.md`
2. Replace `{{ANALYSIS_MODE}}` with your chosen mode
3. Adjust settings as needed
4. Run the analysis framework

## Notes
- Default mode is DOCUMENTATION_ONLY if this file doesn't exist
- TARGET_TECH_STACK.md is only required for modernization modes
- You can change modes at any time by editing this file