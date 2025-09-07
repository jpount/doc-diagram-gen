# n8n Integration for Claude Code Agents

Automated workflow execution for Claude Code documentation agents using n8n.

## 🚀 Quick Start

### 1. Start Host Agent Server (on your Mac)

```bash
# Install dependencies (first time only)
pip install fastapi uvicorn httpx

# Start the server
python n8n/host_agent_server.py
```

Server runs on `http://localhost:8200` and executes Claude agents.

### 2. Start Docker Services

```bash
cd n8n
./start_n8n_minimal.sh

# Access n8n UI
open http://localhost:5678
# Username: admin, Password: changeme
```

### 3. Import and Run Workflows

Import from `n8n/workflows/`:
- **n8n_quick_analysis_manual.json** - Sequential execution with status checking
- **n8n_parallel_agents_simple.json** - Parallel agent execution (recommended)

## 📁 Directory Structure

```
n8n/
├── workflows/                          # n8n workflow files
│   ├── n8n_quick_analysis_manual.json # Sequential execution
│   ├── n8n_parallel_agents_simple.json # Parallel execution
│   └── n8n_parallel_agents.json       # Advanced parallel
├── services/                           # Core services
│   ├── logging_config.py              # Centralized logging
│   ├── n8n_claude_sdk_executor.py     # SDK agent executor
│   ├── n8n_workflow_executor.py       # Workflow orchestrator
│   └── n8n_agent_executor.py          # Agent executor
├── api/                                # API server
│   └── n8n_api_server.py              # Docker API server
├── docker/                             # Docker configuration
│   ├── docker-compose.minimal.yml     # Minimal stack
│   └── Dockerfile.n8n-api             # API container
├── host_agent_server.py               # Host-side executor
├── start_n8n_minimal.sh               # Start script
└── stop_n8n.sh                        # Stop script
```

## 🎯 Key Features

### Dual Mode Operation
- ✅ Works WITH n8n for automation
- ✅ Works WITHOUT n8n for manual operation
- ✅ No changes needed to existing manual workflow

### n8n-Specific Components
- **Dedicated API Server**: Runs on port 8100
- **n8n Workflow Templates**: Import directly into n8n
- **Docker Integration**: Everything runs in containers
- **Parallel Execution**: Run multiple agents simultaneously
- **Progress Monitoring**: Real-time status via API

### Pre-built Workflows

| Workflow | Trigger | Duration | Description |
|----------|---------|----------|-------------|
| Test API Connection | Manual | Instant | Test n8n can reach API |
| Quick Analysis (Manual) | Manual | 1-2 hours | Essential agents only - **USE THIS TO START** |
| Quick Analysis (Webhook) | Webhook | 1-2 hours | For external triggers |
| Comprehensive | Webhook | 3-4 hours | Full analysis with parallel execution |
| Security Focus | Manual | 2 hours | Security-focused assessment |
| Performance Focus | Manual | 2 hours | Performance optimization focus |

## 🔧 API Endpoints

All n8n-specific endpoints are prefixed with `/n8n/`:

- `POST /n8n/trigger` - Start a workflow
- `POST /n8n/execute` - Execute single agent
- `GET /n8n/status/{session_id}` - Check progress
- `GET /n8n/results/{session_id}/{agent}` - Get results
- `GET /n8n/workflows/templates` - List templates

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| n8n | 5678 | n8n workflow UI |
| API Server | 8100 | n8n integration API |
| Redis | 6379 | Queue and caching |
| Monitoring | 8200 | Optional dashboard |

## 📊 Using with n8n

### 1. Import Workflow
- Open n8n UI (http://localhost:5678)
- Import workflow from `workflows/` directory
- Configure webhook if needed

### 2. Trigger Analysis
```json
{
  "project_name": "my-project",
  "codebase_path": "/app/codebase/my-project"
}
```

### 3. Monitor Progress
- Watch execution in n8n UI
- Or poll API: `GET /n8n/status/{session_id}`

## 🔄 Manual Mode (Without n8n)

The original manual workflow still works:

```bash
# Traditional approach
python3 framework/scripts/agent_orchestrator.py

# Run agents manually
@mcp-orchestrator
@repomix-analyzer
@business-logic-analyst
```

## 🛠 Customization

### Add Custom Workflows
1. Create workflow in n8n
2. Export as JSON
3. Save to `workflows/` directory

### Modify Execution
Edit `services/n8n_workflow_executor.py` to:
- Add new workflow types
- Change parallel groups
- Adjust timeouts

## 📚 Documentation

- **Full Guide**: [N8N_INTEGRATION_GUIDE.md](N8N_INTEGRATION_GUIDE.md)
- **API Docs**: http://localhost:8100/docs
- **Framework Docs**: ../framework/docs/

## ⚠️ Important Notes

1. **Token Optimization**: Always run Repomix first
2. **Docker Memory**: Allocate 8GB+ RAM to Docker
3. **Codebase Location**: Place in `../codebase/your-project/`
4. **Results**: Find in `../output/docs/` and `../output/diagrams/`

## 🔐 Security

Default credentials (CHANGE THESE!):
- n8n: admin/changeme
- Edit in `docker/.env` file

## 🆘 Troubleshooting

```bash
# Check logs
docker logs doc-framework-api
docker logs n8n-workflow

# Restart services
./stop_n8n.sh
./start_n8n.sh

# Clean slate
docker-compose down -v
rm -rf ../output/context/*
```

---

**Version**: 1.0.0  
**Compatibility**: Works with existing manual framework  
**Requirements**: Docker, 8GB RAM, Ports 5678, 8100