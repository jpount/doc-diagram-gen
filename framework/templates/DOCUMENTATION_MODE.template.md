# Documentation Generation Mode Configuration

## Selected Mode
**Mode:** {{DOCUMENTATION_MODE}}

## Available Documentation Modes

### 1. QUICK (Fully Automated)
Best for initial analysis and quick documentation generation.
- **User Interaction:** None
- **Speed:** Fast (1-2 hours for medium projects)
- **Accuracy:** 70-80% (best effort)
- **Use When:** 
  - Initial codebase exploration
  - Time-constrained analysis
  - Well-structured codebases with clear patterns

### 2. GUIDED (Recommended)
Optimal balance between automation and accuracy.
- **User Interaction:** Checkpoints at key phases
- **Speed:** Moderate (3-4 hours with user input)
- **Accuracy:** 90-95%
- **Use When:**
  - Production documentation needed
  - Complex business logic requires clarification
  - External system integrations need explanation
  - Historical context is important

### 3. TEMPLATE (User-Driven)
Maximum accuracy with user completing templates.
- **User Interaction:** High (user fills templates)
- **Speed:** Slow (depends on user)
- **Accuracy:** 95-100%
- **Use When:**
  - Compliance/audit documentation required
  - Complex legacy systems with tribal knowledge
  - Documentation for handover/training

## Mode-Specific Settings

### QUICK Mode Settings
```yaml
quick_mode:
  auto_detect_patterns: true
  skip_user_prompts: true
  use_default_names: true
  diagram_generation: automatic
  confidence_threshold: 0.7
```

### GUIDED Mode Settings
```yaml
guided_mode:
  checkpoint_phases:
    - after_discovery       # Review discovered architecture
    - after_business_logic  # Validate business rules
    - before_diagrams      # Confirm diagram requirements
    - after_diagrams       # Review generated diagrams
  user_prompts:
    - system_purpose       # Confirm system's business purpose
    - external_systems     # Identify external integrations
    - critical_flows       # Prioritize business processes
    - terminology         # Confirm domain terminology
  allow_corrections: true
  save_user_inputs: true
```

### TEMPLATE Mode Settings
```yaml
template_mode:
  generate_templates:
    - business_context.md
    - system_overview.md
    - integration_points.md
    - business_rules.md
    - deployment_guide.md
  provide_examples: true
  include_instructions: true
  validation_checklist: true
```

## User Interaction Points (GUIDED Mode)

### Phase 1: Discovery Review
After initial codebase analysis:
- Confirm detected technology stack
- Identify missing components
- Clarify ambiguous patterns

### Phase 2: Business Logic Validation
After business rule extraction:
- Validate critical business rules
- Add missing business context
- Clarify domain terminology

### Phase 3: Diagram Planning
Before diagram generation:
- Prioritize diagram types needed
- Specify diagram detail level
- Identify key components to visualize

### Phase 4: Documentation Review
After documentation generation:
- Review accuracy of findings
- Add historical context
- Provide future recommendations

## Configuration Examples

### For Quick Analysis
```yaml
documentation_mode: QUICK
analysis_mode: DOCUMENTATION_ONLY
max_time_minutes: 120
auto_approve_all: true
```

### For Production Documentation
```yaml
documentation_mode: GUIDED
analysis_mode: DOCUMENTATION_ONLY
require_user_validation: true
save_checkpoint_files: true
generate_confidence_scores: true
```

### For Compliance Documentation
```yaml
documentation_mode: TEMPLATE
analysis_mode: DOCUMENTATION_WITH_MODERNIZATION
require_completeness_check: true
include_audit_trail: true
generate_evidence_links: true
```

## Token Budget Allocation by Mode

### QUICK Mode
- Discovery: 30% of budget
- Analysis: 50% of budget
- Documentation: 20% of budget

### GUIDED Mode
- Discovery: 25% of budget
- Analysis: 40% of budget
- User interaction: 10% of budget
- Documentation: 25% of budget

### TEMPLATE Mode
- Discovery: 20% of budget
- Template generation: 30% of budget
- Examples creation: 30% of budget
- Instructions: 20% of budget

## Output Differences by Mode

### QUICK Mode Outputs
- Executive summary
- Basic architecture diagrams
- Key findings report
- Technology inventory

### GUIDED Mode Outputs
- Comprehensive documentation
- Detailed diagrams with annotations
- Validated business rules
- Improvement recommendations
- User-provided context integrated

### TEMPLATE Mode Outputs
- Fillable documentation templates
- Completion guidelines
- Example content
- Validation checklists
- User completion tracking

## Switching Modes
You can change the documentation mode at any time by:
1. Editing this file to change the mode
2. Re-running the analysis agents
3. Existing findings will be preserved

## Notes
- Default mode is GUIDED if this file doesn't exist
- User inputs in GUIDED mode are saved to `output/context/user_inputs.md`
- Templates in TEMPLATE mode are created in `output/templates/`
- Confidence scores are included in GUIDED and TEMPLATE modes