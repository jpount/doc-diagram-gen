# Agent Ordering Configuration

## Simplified Agent Dependencies

### Required Sequential Order (Dependencies)
Only these agents MUST run in this specific order:

1. **mcp-orchestrator** (REQUIRED FIRST)
   - Sets up token optimization strategy
   - Determines available MCPs
   - Writes: `output/context/mcp-orchestrator-summary.json`

2. **repomix-analyzer** (REQUIRED SECOND) 
   - Analyzes compressed codebase if available
   - Provides initial technology detection
   - Writes: `output/context/repomix-analyzer-summary.json`

3. **architecture-selector** (REQUIRED THIRD)
   - Recommends specialist agents based on detected technologies
   - Writes: `output/context/architecture-selector-summary.json`

### Parallel Execution (No Dependencies)
After the required sequence above, ALL other agents can run in ANY order or in parallel:

#### Core Analysis Agents
- **business-logic-analyst**
- **security-analyst** 
- **performance-analyst**
- **ui-analysis-specialist**
- **data-model-specialist**

#### Technology Specialists (run based on architecture-selector recommendations)
- **java-architect** (if Java/Spring detected)
- **dotnet-architect** (if .NET/C# detected)  
- **angular-architect** (if Angular detected)
- **legacy-code-detective** (fallback for unknown/complex stacks)

#### Documentation & Visualization
- **diagram-architect** (can run anytime after core analysis)
- **documentation-specialist** (typically run last to synthesize all findings)
- **executive-summary** (run last for stakeholder overview)

## Agent Selection Strategy

### UNSUPERVISED Mode
Runs a predefined sequence automatically:
```yaml
default_sequence:
  required:
    - mcp-orchestrator
    - repomix-analyzer  
    - architecture-selector
  automatic:
    - business-logic-analyst
    - security-analyst
    - performance-analyst
    - diagram-architect
    - documentation-specialist
  specialist: "auto-detected"  # Based on architecture-selector output
```

### SUPERVISED Mode  
User controls agent selection after required sequence:
```yaml
guided_sequence:
  required:
    - mcp-orchestrator
    - repomix-analyzer
    - architecture-selector
  user_selectable:
    - business-logic-analyst
    - security-analyst
    - performance-analyst
    - ui-analysis-specialist
    - data-model-specialist
    - java-architect
    - dotnet-architect
    - angular-architect
    - legacy-code-detective
    - diagram-architect
    - documentation-specialist
    - executive-summary
```

## Context JSON Requirements

### ALL Agents Must Write Context Files
Every agent MUST write a JSON context file to `output/context/[agent-name]-summary.json` with this structure:

```json
{
  "agent": "agent-name",
  "timestamp": "ISO-8601 timestamp", 
  "status": "completed|in_progress|failed",
  "token_usage": {
    "input": 12500,
    "output": 3200, 
    "total": 15700
  },
  "summary": {
    "key_findings": ["Finding 1", "Finding 2"],
    "priority_items": ["Priority 1", "Priority 2"], 
    "warnings": ["Warning 1"],
    "recommendations_for_next": {
      "next-agent": ["Recommendation 1"]
    }
  },
  "data": {
    "specific_agent_data": "varies by agent"
  },
  "session_info": {
    "session_id": "uuid",
    "phase": "discovery|analysis|documentation", 
    "can_continue_in_new_session": true
  }
}
```

### Context File Validation
Each context file must include:
- ✅ Agent completion status
- ✅ Key findings summary  
- ✅ Token usage tracking
- ✅ Session continuity info
- ✅ Recommendations for subsequent agents
- ✅ Structured data for reuse

## Parallel Execution Guidelines

### Safe for Parallel Execution
These agents can run simultaneously without conflicts:
- business-logic-analyst + security-analyst + performance-analyst
- ui-analysis-specialist + data-model-specialist  
- Any technology specialist + any core analysis agent
- diagram-architect + any analysis agent (as long as some analysis is complete)

### Best Parallel Groups
```yaml
parallel_group_1:
  - business-logic-analyst
  - security-analyst
  - performance-analyst

parallel_group_2:  
  - ui-analysis-specialist
  - data-model-specialist
  - java-architect  # if detected

parallel_group_3:
  - diagram-architect
  - documentation-specialist  # can start while others finishing
```

## Session Persistence Support

### Progress Tracking File
Each run maintains: `output/context/session-progress.json`

```json
{
  "session_id": "unique-session-id",
  "project_name": "codebase-name",
  "mode": "UNSUPERVISED|SUPERVISED",
  "started": "2025-01-01T10:00:00Z",
  "last_updated": "2025-01-01T12:30:00Z", 
  "progress": {
    "phase": "discovery|analysis|documentation|complete",
    "required_sequence_complete": true,
    "completed_agents": [
      "mcp-orchestrator",
      "repomix-analyzer", 
      "architecture-selector",
      "business-logic-analyst"
    ],
    "running_agents": [
      "security-analyst"
    ],
    "pending_agents": [
      "performance-analyst",
      "diagram-architect", 
      "documentation-specialist"
    ],
    "failed_agents": [],
    "skipped_agents": []
  },
  "user_selections": {
    "specialist_agents": ["java-architect"],
    "focus_areas": ["business_logic", "security"],
    "diagram_types": ["architecture", "sequence", "data_flow"]
  },
  "checkpoints": {
    "discovery_review": "completed",
    "business_logic_review": "pending", 
    "diagram_planning": "pending",
    "final_review": "pending"
  }
}
```

## Agent Communication Protocol

### Reading Previous Context
Every agent should check for available context from previous agents:

```python
import json
from pathlib import Path

def load_previous_context(agent_names):
    """Load context from multiple previous agents"""
    context = {}
    for agent_name in agent_names:
        context_file = Path(f"output/context/{agent_name}-summary.json")
        if context_file.exists():
            with open(context_file) as f:
                context[agent_name] = json.load(f)
    return context

# Usage in any agent
previous_context = load_previous_context([
    "mcp-orchestrator", 
    "repomix-analyzer", 
    "architecture-selector"
])
```

### Writing Context for Next Agents
Every agent must write context for future agents:

```python
def write_agent_context(agent_name, summary_data, session_info):
    """Write standardized context file"""
    context = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
        "token_usage": get_current_token_usage(),
        "summary": summary_data,
        "data": extract_structured_data(),
        "session_info": session_info
    }
    
    with open(f"output/context/{agent_name}-summary.json", "w") as f:
        json.dump(context, f, indent=2)
```

This simplified ordering reduces complexity while maintaining quality and enabling flexible, session-aware execution.