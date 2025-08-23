# User Interaction Guide for Documentation Generation

## Philosophy: Quality Over Token Optimization

While the framework includes token optimization strategies, **quality and completeness should always take priority**. If an agent needs more context to produce better results, it should use it. Token budgets are guidelines, not hard limits.

## When to Choose Each Documentation Mode

### QUICK Mode (Fully Automated)
Choose this when:
- You need rapid initial analysis
- The codebase is well-structured with clear patterns
- You're doing exploratory analysis
- Perfect accuracy isn't critical

### GUIDED Mode (Recommended - Default)
Choose this when:
- You need production-quality documentation
- Business context is important
- You want to validate findings
- You can invest 3-4 hours for better results

### TEMPLATE Mode (Maximum Control)
Choose this when:
- Compliance or audit documentation is required
- You have extensive domain knowledge to contribute
- You need 100% accuracy
- Time is available for manual completion

## User Interaction Points in GUIDED Mode

### 1. After Discovery Phase
**What Claude Code will ask:**
- "Is this technology stack complete?"
- "Are there any hidden integrations I missed?"
- "What's the primary business purpose of this system?"

**Why this matters:**
- Ensures all technologies are captured
- Identifies business context not evident in code
- Sets the foundation for all subsequent analysis

**Example interaction:**
```
Claude: I've identified Java 1.7 with Spring 3.2. Is this complete?
You: Also uses Apache Camel for integration and Quartz for scheduling
Claude: Thank you, I'll include those in the analysis.
```

### 2. After Business Logic Extraction
**What Claude Code will ask:**
- "I found 75 business rules. Here are the top 10 - do they look correct?"
- "What domain terminology should I use?"
- "Are there critical business rules I might have missed?"

**Why this matters:**
- Validates critical business logic
- Ensures proper terminology
- Captures undocumented rules

**Example interaction:**
```
Claude: I found a rule that orders over $5000 require approval. Correct?
You: Yes, but it's actually $3000 for new customers, $5000 for existing
Claude: I'll update that distinction in the documentation.
```

### 3. Before Diagram Generation
**What Claude Code will ask:**
- "Which diagrams are most important for your team?"
- "What level of detail do you need?"
- "Any specific components to highlight?"

**Why this matters:**
- Focuses effort on valuable diagrams
- Ensures appropriate detail level
- Highlights critical components

### 4. After Documentation Generation
**What Claude Code will ask:**
- "Please review this executive summary - is it accurate?"
- "Any historical context to add?"
- "What are the future plans for this system?"

**Why this matters:**
- Final accuracy check
- Adds context only humans know
- Documents future direction

## How to Provide Effective Input

### DO:
- **Be specific** about business rules and exceptions
- **Provide context** about why decisions were made
- **Identify critical flows** that must be documented perfectly
- **Share terminology** your team uses
- **Mention external systems** not visible in code

### DON'T:
- Rush through prompts - take time to think
- Assume Claude Code knows business context
- Skip validation of critical findings
- Worry about token usage if more context helps

## Token Usage Philosophy

### Quality-First Approach
```yaml
token_strategy:
  priority: quality_over_efficiency
  
  guidelines:
    - Use as many tokens as needed for completeness
    - Read full context when it improves accuracy
    - Perform multiple passes if necessary
    - Don't truncate important information
    
  when_to_optimize:
    - Only after quality is assured
    - For repeated similar analyses
    - When context is genuinely redundant
```

### Dynamic Token Allocation
Instead of fixed budgets, agents should:
1. Start with baseline allocation
2. Request more if needed for quality
3. Track usage for future optimization
4. Never sacrifice completeness for token savings

## Interactive Diagram Review Process

### Step 1: Initial Generation
Claude Code generates diagrams based on analysis

### Step 2: Review Prompt
```
Here's the architecture diagram I've created:
[Displays diagram]

Please review and let me know:
1. Are all components shown?
2. Are the relationships correct?
3. Should I add more detail anywhere?
4. Is the terminology correct?
```

### Step 3: Iterative Refinement
You provide feedback, Claude Code updates

### Step 4: Final Validation
You approve or request final changes

## Manual Completion Tasks (TEMPLATE Mode)

When using TEMPLATE mode, you'll receive:

### 1. Pre-filled Templates
- Partially completed with discovered information
- Clear markers for sections needing input
- Examples for guidance

### 2. Completion Checklist
```markdown
## Documentation Completion Checklist

### Required Information
- [ ] Business context and purpose
- [ ] External system integrations
- [ ] Business rule validations
- [ ] Performance requirements
- [ ] Security constraints
- [ ] Deployment procedures

### Optional but Valuable
- [ ] Historical decisions
- [ ] Known issues/workarounds
- [ ] Future roadmap
- [ ] Team contacts
```

### 3. Validation Guide
Instructions for verifying completeness

## Best Practices for User Input

### 1. Business Context
Always provide:
- Primary business purpose
- Key stakeholders
- Critical business processes
- Compliance requirements

### 2. Technical Context
Always provide:
- External integrations not in code
- Infrastructure dependencies
- Performance requirements
- Security constraints

### 3. Historical Context
When relevant, provide:
- Why architectural decisions were made
- Previous migration attempts
- Known issues and workarounds
- Team tribal knowledge

## Example User Interactions

### Example 1: Clarifying Business Logic
```
Claude: I found a complex pricing calculation. Can you explain the business rules?

You: Pricing has three tiers:
- Retail: List price
- Wholesale: 30% discount for orders > 100 units  
- Premium Partner: 40% discount plus free shipping
There's also seasonal pricing that adds 10% in Q4.

Claude: Thank you. I'll document these pricing tiers and the seasonal adjustment.
```

### Example 2: Identifying Missing Components
```
Claude: I've mapped the system architecture. Please review.

You: You're missing our integration with the Salesforce CRM. 
It's not in the code because it uses webhook URLs from environment variables.

Claude: I'll add the Salesforce integration to the architecture diagram and document the webhook pattern.
```

### Example 3: Adding Historical Context
```
Claude: The documentation is complete. Any historical context to add?

You: Yes - we tried migrating to microservices in 2019 but rolled back due to 
data consistency issues. The current monolith is intentional, not technical debt.

Claude: I'll add this to the architectural decisions section to prevent future misunderstandings.
```

## Quality Assurance

### Automated Validation
- Syntax checking for diagrams
- Completeness checking for documentation
- Cross-reference validation

### User Validation Prompts
- Review critical findings
- Verify business rules
- Approve diagrams
- Confirm terminology

### Iterative Improvement
- Each analysis improves the framework
- User feedback is incorporated
- Templates are refined over time

## Troubleshooting

### If Claude Code seems to miss important aspects:
1. Provide explicit guidance about what to focus on
2. Share example of what you're looking for
3. Don't worry about token usage - completeness matters more

### If documentation seems generic:
1. Provide more business context
2. Share team-specific terminology
3. Give examples of similar documentation you like

### If diagrams aren't quite right:
1. Describe what's wrong specifically
2. Provide sketch or description of desired layout
3. Iterate until satisfied - tokens are secondary to quality

## Remember

**The goal is comprehensive, accurate documentation that truly captures your system.** Token optimization is a means to efficiency, not an end in itself. When in doubt, choose the approach that yields better documentation, even if it uses more tokens.

## Getting Started

1. Run the setup script and choose your documentation mode
2. Place your codebase in the designated directory
3. Start the analysis with Claude Code
4. Respond thoughtfully to interaction prompts
5. Review and refine the output
6. Iterate as needed for quality

Your input and domain knowledge are invaluable - they transform good technical documentation into great system documentation that truly serves your team's needs.