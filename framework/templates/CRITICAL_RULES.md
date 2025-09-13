# 🚨 CRITICAL RULES - ALL AGENTS 🚨

⚠️ **MANDATORY COMPLIANCE**: These rules apply to ALL agents in the documentation and diagram generation framework.
⚠️ **VIOLATION RESULTS IN INVALID OUTPUT**: Any agent that violates these rules produces unusable results.
⚠️ **NO EXCEPTIONS**: These rules must be followed strictly without compromise.

## Data Integrity Rules

1. **NO HARDCODED DATA**: Never use placeholder or example data
   - Use only actual data extracted from files
   - If data is not found, explicitly state "Not detected" or "Unable to determine"
   - Never fabricate metrics, counts, names, or examples

2. **NO FABRICATED METRICS**: Only use actual data from files
   - No made-up percentages, scores, or measurements
   - No estimated timelines, costs, or resource counts
   - Use actual file counts, sizes, and detected patterns only

3. **NO SERENA REFERENCES**: Do not use any MCP Serena tools
   - Use only standard tools: Read, Write, Bash, Glob, Grep, LS
   - No mcp__serena__* function calls
   - Use JSON context files for agent communication instead

4. **STATE UNKNOWN**: If data cannot be found, explicitly state "Not detected" or "Unable to determine"
   - Better to be honest about missing data than to guess
   - Helps users understand analysis limitations
   - Maintains framework credibility

## Cost, Timeline, and Metrics Policy

5. **NO FABRICATED MEASUREMENTS**: NEVER generate specific measurements, dates, timelines, costs, or metrics that cannot be backed up by actual data from the codebase.

**ABSOLUTELY FORBIDDEN:**
- Specific dollar amounts ($50K, $1M, etc.)
- Specific timelines (3 months, 6 weeks, Q1 2024, etc.)
- Precise percentages (75% improvement, 40% reduction, etc.)
- Exact dates (by December 2024, January release, etc.)
- Specific resource counts (5 developers, 2 DBAs, etc.)
- Made-up performance metrics (50ms response time, 99.9% uptime, etc.)
- Fabricated ROI calculations
- Invented team sizes or effort estimates
- Estimated completion dates
- Hypothetical performance improvements

**ALWAYS USE GENERIC QUALITATIVE TERMS:**
- **Effort Level**: Minimal/Low/Medium/High/Very High/Extreme
- **Complexity**: Simple/Moderate/Complex/Very Complex/Extremely Complex
- **Impact**: Low/Medium/High/Critical
- **Risk Level**: Low/Medium/High/Critical/Severe
- **Priority**: Low/Medium/High/Critical/Urgent
- **Timeline**: Short-term/Medium-term/Long-term/Multi-phase
- **Cost**: Low-cost/Moderate-cost/High-cost/Very High-cost
- **Performance**: Poor/Fair/Good/Excellent/Outstanding
- **Urgency**: Low/Medium/High/Critical/Immediate

## Quality Assurance Rules

6. **MERMAID VALIDATION**: ALL Mermaid diagrams MUST compile without errors
   - Use `python3 framework/scripts/simple_mermaid_validator.py [file]`
   - Agent cannot complete until all diagrams pass validation with zero errors
   - Applies to both embedded diagrams in .md files and standalone .mmd files
   - No exceptions - broken diagrams break the entire output

## Data Source Priority

ALL agents MUST read data in this strict order:

1. **PRIMARY**: `output/reports/repomix-summary.md` (compressed codebase)
2. **SECONDARY**: `output/context/*.json` (previous agent outputs)
3. **FALLBACK**: Raw codebase access (only if compressed data insufficient)

This hierarchy ensures:
- 80% token reduction through Repomix compression
- Efficient agent chaining through context files
- Raw access only when necessary

## Required Outputs

ALL agents MUST produce:
- `output/context/{agent-name}-summary.json` - Context for next agents
- `output/docs/{number}-{agent-name}.md` - Documentation
- `output/diagrams/{agent-name}-*.mmd` - Diagrams (if applicable)

## Compliance

Violation of these rules results in:
- ❌ Invalid framework output
- ❌ Broken agent chain
- ❌ Unusable documentation
- ❌ Failed diagram rendering

These rules ensure consistent, reliable, high-quality output across all agents.