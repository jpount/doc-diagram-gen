---
name: run-parallel
description: Coordinate running multiple independent agents in separate Claude sessions for true parallel execution
arguments:
  - name: agents
    description: "Comma-separated list of agents to run (e.g., 'business-logic-analyst,security-analyst,performance-analyst')"
    required: false
---

You are helping the user coordinate parallel agent execution across multiple Claude Code sessions.

**IMPORTANT:** True parallel execution requires each agent to run in a SEPARATE Claude Code session/tab to maintain independent contexts.

## Prerequisites Check

First verify the required agents have completed:
```bash
python3 -c "
import json
from pathlib import Path
progress_file = Path('output/context/session-progress.json')
if progress_file.exists():
    with open(progress_file) as f:
        data = json.load(f)
        required = ['mcp-orchestrator', 'repomix-analyzer', 'architecture-selector']
        completed = data['progress']['completed_agents']
        if all(agent in completed for agent in required):
            print('✅ Required sequence complete - can run agents in parallel')
        else:
            missing = [a for a in required if a not in completed]
            print(f'❌ Must complete first: {missing}')
else:
    print('❌ No session found - run /status first')
"
```

## Default Agent Groups

If no agents specified, offer these parallel groups:

**Group 1: Core Analysis** (can all run together)
- @business-logic-analyst
- @security-analyst  
- @performance-analyst

**Group 2: Specialized Analysis** (can all run together)
- @ui-analysis-specialist
- @data-model-specialist
- Technology-specific architects (based on what architecture-selector found)

**Group 3: Documentation** (run after analysis)
- @diagram-architect
- @documentation-specialist

## Parallel Execution Strategy

**IMPORTANT:** Each agent must run in a SEPARATE Claude Code session/context to ensure true parallel execution without interference.

### Approach 1: Manual Parallel (Multiple Claude Windows)
Tell the user to:
1. Open multiple Claude Code windows/tabs (one per agent)
2. In each window, run a different agent:
   - Window 1: `@business-logic-analyst`
   - Window 2: `@security-analyst`
   - Window 3: `@performance-analyst`
3. Each agent works independently, reading from and writing to context files
4. Monitor completion via `/status` command

### Approach 2: Use Parallel Coordinator Script
Use the provided coordinator to manage parallel execution:

```bash
# Show recommended agent groups
python3 framework/scripts/parallel_agent_launcher.py --groups

# Launch parallel session with specific agents
python3 framework/scripts/parallel_agent_launcher.py --launch \
  business-logic-analyst \
  security-analyst \
  performance-analyst

# Monitor progress from any session
python3 framework/scripts/parallel_agent_launcher.py --status
```

The coordinator will:
1. Create a parallel execution session
2. Provide clear instructions for opening multiple Claude sessions
3. Track which agents have completed via their context files
4. Show real-time progress updates

### Why Separate Contexts Are Critical:
- Each agent needs its own Claude conversation context
- Prevents token/memory interference between agents
- Ensures true parallel execution without conflicts
- Maintains agent independence as designed

## Benefits
- Reduces total analysis time by 50-70%
- All agents after the required sequence can run independently
- Each agent writes to its own context file
- No conflicts or dependencies

## Session Update
After agents complete, update the session:
```python
from framework.scripts.session_manager import SessionManager
manager = SessionManager()
for agent in completed_agents:
    manager.update_agent_status(agent, "completed")
```

This command is valuable because:
- Significantly speeds up analysis
- Leverages the new simplified agent ordering
- Makes SUPERVISED mode more efficient
- Clear visualization of parallel execution