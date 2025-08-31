---
name: status
description: Check analysis progress and session status across Claude Code restarts
---

You are checking the current analysis session status for the documentation framework.

## Check Session Status

Run the session manager to get current progress:
```bash
python3 framework/scripts/session_manager.py
```

## Interpret Results

If a session exists, show:
1. **Project Name** - Which codebase is being analyzed
2. **Mode** - UNSUPERVISED or SUPERVISED
3. **Phase** - Current phase (discovery/analysis/documentation/complete)
4. **Progress**:
   - ✅ Completed agents
   - 🏃 Running agents (if any)
   - ⏳ Pending agents
   - ❌ Failed agents (if any)
5. **Next Steps** - What the user should do next

## Session Recovery Options

If in SUPERVISED mode with an active session, offer options:
1. **Continue** - Resume from where you left off
2. **Restart Phase** - Restart current phase only
3. **New Session** - Start completely fresh

## No Session Found

If no session exists:
1. Check if setup has been run
2. Suggest running setup if needed
3. Explain how to start a new analysis

## Context Files

Also check for agent context files:
```bash
ls -la output/context/*-summary.json 2>/dev/null | tail -10
```

Show which agents have already generated context to give a fuller picture of progress.

This command is especially valuable for:
- Resuming work after Claude Code restarts
- Understanding what's been completed
- Deciding what to run next
- Recovering from interruptions