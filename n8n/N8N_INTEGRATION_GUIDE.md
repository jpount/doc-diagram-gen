# n8n Integration Guide for Documentation Framework

This guide explains how to use n8n workflow automation with the Documentation Framework for both automated and manual analysis workflows.

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Setup Instructions](#setup-instructions)
5. [Using n8n Workflows](#using-n8n-workflows)
6. [API Reference](#api-reference)
7. [Custom Workflows](#custom-workflows)
8. [Troubleshooting](#troubleshooting)

## Overview

The n8n integration provides:
- **Automated Workflows**: Run complete analysis without manual intervention
- **Parallel Execution**: Execute multiple agents simultaneously for faster results
- **Flexible Control**: Mix automated and manual steps as needed
- **Progress Monitoring**: Real-time status updates and webhooks
- **Docker Support**: Everything runs in containers for easy deployment

### Key Benefits

✅ **Dual Mode Operation**: Works with or without n8n - manual flow still available  
✅ **Scalability**: Queue-based execution supports scaling  
✅ **Reusability**: Pre-built workflow templates for common patterns  
✅ **Monitoring**: Real-time progress tracking via API  
✅ **Resilience**: Error handling and recovery built-in  

## Quick Start

### 1. Start the Services

#### Option A: Minimal Setup (Recommended)
```bash
cd n8n
./start_n8n_minimal.sh
```

This starts only:
- n8n workflow automation (http://localhost:5678)
- Documentation Framework API (http://localhost:8100)

#### Option B: Full Setup with Redis
```bash
cd n8n/docker
docker-compose up -d
```

This starts:
- n8n workflow automation (http://localhost:5678)
- Documentation Framework API (http://localhost:8100)
- Redis for queuing
- Optional: Celery workers (uncomment in docker-compose.yml)
- Optional: Monitoring dashboard (uncomment in docker-compose.yml)

### 2. Access n8n

Open http://localhost:5678 in your browser:
- Username: `admin`
- Password: `changeme` (change this!)

### 3. Import a Workflow

1. In n8n, click "Add workflow" → "Import from File"
2. Select one of the pre-built workflows:
   - `n8n/workflows/n8n_quick_analysis.json` - Fast 1-hour analysis
   - `n8n/workflows/n8n_comprehensive_parallel.json` - Full analysis with parallel execution

### 4. Configure and Run

1. Update the webhook trigger URL if needed
2. Place your codebase in `codebase/your-project/`
3. Execute the workflow in n8n
4. Monitor progress in n8n or via the API

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│     n8n     │────▶│   n8n API Server │────▶│ Agent Executors │
│  Workflows  │     │   (Port 8100)    │     │   (Workers)     │
└─────────────┘     └──────────────────┘     └─────────────────┘
       │                     │                         │
       │                     ▼                         ▼
       │            ┌──────────────┐         ┌──────────────┐
       │            │    Redis     │         │   Context    │
       └───────────▶│    Queue     │         │    Files     │
                    └──────────────┘         └──────────────┘
```

### Components

1. **n8n Workflows**: Orchestrate the analysis process
2. **n8n API Server**: FastAPI server providing endpoints for n8n
3. **Agent Executors**: Execute individual analysis agents
4. **Redis Queue**: Manages async tasks and caching
5. **Context Files**: Share data between agents

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- 8GB+ RAM recommended
- Ports 5678, 8100, 6379 available

### Installation Steps

#### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo>
cd doc-diagram-gen

# Create necessary directories
mkdir -p n8n/docker/n8n-workflows
mkdir -p output/{context,docs,diagrams,reports}
```

#### 2. Configure Environment

Edit `n8n/docker/docker-compose.yml`:

```yaml
environment:
  - N8N_BASIC_AUTH_USER=your-username
  - N8N_BASIC_AUTH_PASSWORD=your-secure-password
```

#### 3. Build and Start

```bash
cd n8n/docker
docker-compose build
docker-compose up -d
```

#### 4. Verify Services

```bash
# Check all services are running
docker-compose ps

# Test API health
curl http://localhost:8100/health

# Test n8n
curl http://localhost:5678
```

## Using n8n Workflows

### Pre-built Workflows

#### Quick Analysis (1-2 hours)
- Fast analysis with essential agents
- Good for initial assessment
- Agents: MCP, Repomix, Architecture, Business Logic, Diagrams

#### Comprehensive Analysis (3-4 hours)
- Full analysis with all agents
- Parallel execution for efficiency
- Includes security, performance, and modernization analysis

#### Security-Focused Analysis
- Prioritizes security assessment
- Vulnerability scanning and compliance checks
- Generates security remediation plan

### Running a Workflow

#### Via n8n UI

1. Open the workflow in n8n
2. Click "Execute Workflow"
3. Provide input data:
   ```json
   {
     "project_name": "my-project",
     "codebase_path": "/app/codebase/my-project"
   }
   ```
4. Monitor execution in n8n

#### Via API Call

```bash
curl -X POST http://localhost:8100/n8n/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "quick_analysis",
    "project_name": "my-project",
    "codebase_path": "/app/codebase/my-project",
    "callback_url": "http://your-webhook-url"
  }'
```

### Monitoring Progress

#### Via API

```bash
# Get status
curl http://localhost:8100/n8n/status/{session_id}

# Get specific agent results
curl http://localhost:8100/n8n/results/{session_id}/{agent_name}
```

#### Via WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8100/n8n/ws/{session_id}');
ws.onmessage = (event) => {
  const status = JSON.parse(event.data);
  console.log('Progress:', status.progress_percentage + '%');
};
```

## API Reference

### Core Endpoints

#### Start Workflow
```
POST /n8n/trigger
{
  "workflow_type": "quick_analysis|comprehensive|security_focus",
  "project_name": "string",
  "codebase_path": "string",
  "callback_url": "string (optional)"
}
```

#### Execute Agent
```
POST /n8n/execute
{
  "agent_name": "string",
  "session_id": "string",
  "wait_for_completion": boolean,
  "timeout": integer
}
```

#### Get Status
```
GET /n8n/status/{session_id}
Response: {
  "session_id": "string",
  "progress_percentage": number,
  "is_complete": boolean,
  "agents": {
    "completed": [],
    "running": [],
    "pending": [],
    "failed": []
  }
}
```

#### Get Results
```
GET /n8n/results/{session_id}/{agent_name}
Response: {
  "success": boolean,
  "summary": {},
  "data": {}
}
```

### Utility Endpoints

- `GET /n8n/info` - API information
- `GET /n8n/agents/available` - List available agents
- `GET /n8n/workflows/templates` - Get workflow templates
- `GET /health` - Health check

## Custom Workflows

### Creating Custom Workflows in n8n

1. **Define Agent Sequence**
   ```javascript
   const agents = [
     'mcp-orchestrator',
     'repomix-analyzer',
     'your-custom-agent'
   ];
   ```

2. **Add Parallel Groups**
   ```javascript
   const parallelGroups = [
     ['business-logic-analyst', 'security-analyst'],
     ['diagram-architect', 'documentation-specialist']
   ];
   ```

3. **Call API from n8n**
   - Use HTTP Request nodes
   - Set appropriate timeouts
   - Handle errors with IF nodes

### Custom Workflow Configuration

Create `n8n/config/n8n_workflows.json`:

```json
{
  "custom_workflow": {
    "name": "My Custom Workflow",
    "agents": [
      "mcp-orchestrator",
      "repomix-analyzer",
      "custom-agent-1",
      "custom-agent-2"
    ],
    "parallel_groups": [
      ["custom-agent-1", "custom-agent-2"]
    ],
    "timeout": 7200,
    "checkpoints": []
  }
}
```

## Manual Mode (Without n8n)

The framework still works without n8n:

```bash
# Traditional manual execution
python3 framework/scripts/agent_orchestrator.py

# Run individual agents
@mcp-orchestrator
@repomix-analyzer
@business-logic-analyst
```

## Troubleshooting

### Common Issues

#### n8n Can't Connect to API
```bash
# Check network
docker network ls
docker network inspect n8n_doc-framework-net

# Verify API is accessible
docker exec -it n8n-workflow curl http://doc-framework-api:8100/health
```

#### Agent Execution Fails
```bash
# Check logs
docker logs doc-framework-api
docker logs doc-framework-celery

# Verify agent exists
ls -la .claude/agents/
```

#### Workflow Timeout
- Increase timeout in workflow settings
- Check agent logs for stuck processes
- Verify codebase size isn't too large

### Debug Mode

Enable debug logging:

```python
# In n8n/api/n8n_api_server.py
logging.basicConfig(level=logging.DEBUG)
```

### Reset Everything

```bash
# Stop all containers
docker-compose down

# Clean up data
rm -rf output/context/*
rm -rf n8n/docker/n8n_data

# Restart
docker-compose up -d
```

## Best Practices

### 1. Codebase Preparation
- Run Repomix first for token optimization
- Exclude unnecessary files (.gitignore)
- Ensure codebase is under 500K lines

### 2. Workflow Design
- Use parallel execution where possible
- Set appropriate timeouts per agent
- Add error handling nodes

### 3. Monitoring
- Use webhooks for status updates
- Monitor Redis queue length
- Check agent context files

### 4. Performance
- Limit parallel agents to 3-5
- Use Redis for caching
- Clean up old sessions regularly

## Advanced Features

### Conditional Workflows

Based on technology detection:
```javascript
if (context.tech_stack.includes('java')) {
  agents.push('java-architect');
}
if (context.tech_stack.includes('angular')) {
  agents.push('angular-architect');
}
```

### Dynamic Agent Selection

Let architecture-selector determine specialists:
```javascript
const specialists = await getArchitectureRecommendations();
agents.push(...specialists);
```

### Checkpoint Handling

For GUIDED mode with user decisions:
```javascript
await waitForCheckpoint('architecture_review');
const userDecision = await getCheckpointDecision();
if (userDecision.approve) {
  continueWorkflow();
}
```

## Integration Examples

### CI/CD Integration

```yaml
# GitLab CI example
analyze-codebase:
  script:
    - |
      curl -X POST http://n8n-server:8100/n8n/trigger \
        -d '{"workflow_type": "quick_analysis", "project_name": "$CI_PROJECT_NAME"}'
```

### Slack Notifications

In n8n, add a Slack node after workflow completion to send results.

### Scheduled Analysis

Use n8n's Cron node to run analysis weekly/monthly.

## Support

- **Issues**: Report in GitHub Issues
- **Documentation**: See framework/docs/
- **API Docs**: http://localhost:8100/docs (FastAPI automatic docs)

---

## Quick Reference Card

### Start Services
```bash
cd n8n/docker && docker-compose up -d
```

### Run Quick Analysis
```bash
curl -X POST http://localhost:8100/n8n/trigger \
  -d '{"workflow_type": "quick_analysis", "project_name": "test"}'
```

### Check Status
```bash
curl http://localhost:8100/n8n/status/{session_id}
```

### Access UIs
- n8n: http://localhost:5678
- API: http://localhost:8100
- API Docs: http://localhost:8100/docs
- Monitoring: http://localhost:8200

### Stop Services
```bash
cd n8n/docker && docker-compose down
```