# n8n Workflow Usage Guide

## Available Workflows

### 1. Test API Connection (`n8n_test_api_manual.json`)
**Purpose**: Test that n8n can connect to the API server  
**Trigger**: Manual (click "Execute Workflow" button)  
**Use this first** to verify everything is working!

### 2. Quick Analysis - Manual Trigger (`n8n_quick_analysis_manual.json`)
**Purpose**: Run a quick documentation analysis  
**Trigger**: Manual (click "Execute Workflow" button)  
**Duration**: 1-2 hours  
**Configuration**: Edit the "Set Configuration" node to set your project details

### 3. Quick Analysis - Webhook (`n8n_quick_analysis.json`)
**Purpose**: Run analysis triggered by external webhook  
**Trigger**: Webhook (requires external HTTP call)  
**Use Case**: CI/CD integration, automated triggers

### 4. Comprehensive Analysis (`n8n_comprehensive_parallel.json`)
**Purpose**: Full analysis with parallel agent execution  
**Trigger**: Webhook  
**Duration**: 3-4 hours

## Step-by-Step Usage

### First Time Setup

1. **Start the services**:
   ```bash
   cd n8n
   ./start_n8n_minimal.sh
   ```

2. **Access n8n UI**:
   - Open http://localhost:5678
   - Login with admin/changeme

3. **Import Test Workflow**:
   - Click "Add workflow" → "Import from File"
   - Select `n8n/workflows/n8n_test_api_manual.json`
   - Click "Execute Workflow" to test the connection

### Running Your First Analysis

1. **Import the Manual Workflow**:
   - Import `n8n/workflows/n8n_quick_analysis_manual.json`

2. **Configure Your Project**:
   - Double-click the "Set Configuration" node
   - Edit these values:
     - `project_name`: Your project name (e.g., "my-app")
     - `codebase_path`: Path in container (e.g., "/app/codebase/daytrader")

3. **Place Your Code**:
   ```bash
   # Copy your code to analyze
   cp -r /path/to/your/code codebase/your-project/
   ```

4. **Execute the Workflow**:
   - Click "Execute Workflow" button
   - Watch the progress in n8n
   - The workflow will poll for status every 30 seconds

5. **Check Results**:
   - Documentation: `output/docs/`
   - Diagrams: `output/diagrams/`
   - Context files: `output/context/`

## Workflow Node Explanations

### Manual Trigger Workflows

```
[Manual Trigger] → [Set Config] → [Start Analysis] → [Check Status Loop] → [Get Results]
```

1. **Manual Trigger**: Start button you click
2. **Set Configuration**: Edit project settings here
3. **Start Analysis**: Calls API to begin
4. **Check Status Loop**: Polls until complete
5. **Get Results**: Shows final summary

### Understanding the Status Loop

The workflows use a polling loop:
1. Check if analysis is complete
2. If yes → Get results and finish
3. If no → Wait 30 seconds and check again

## Customizing Workflows

### Change Project Settings

In the "Set Configuration" node, modify:
```json
{
  "project_name": "your-project",
  "codebase_path": "/app/codebase/your-project",
  "workflow_type": "quick_analysis"
}
```

### Adjust Timing

- Initial wait: Change "Wait 10s" node
- Poll interval: Change "Wait 30s" node
- Timeout: Add a timeout node after X iterations

### Add Notifications

Add nodes after "Final Results":
- Email node: Send results via email
- Slack node: Post to Slack channel
- Webhook node: Notify external service

## Troubleshooting

### "Connection Refused" Error

1. Check API is running:
   ```bash
   docker ps | grep doc-framework-api
   ```

2. Test from n8n container:
   ```bash
   docker exec -it n8n-workflow curl http://doc-framework-api:8100/health
   ```

### Workflow Never Completes

1. Check API logs:
   ```bash
   docker logs doc-framework-api
   ```

2. Check session status manually:
   ```bash
   curl http://localhost:8100/n8n/status/{session_id}
   ```

### No Output Generated

1. Verify codebase exists:
   ```bash
   ls -la codebase/
   ```

2. Check output directory:
   ```bash
   ls -la output/docs/
   ```

## Workflow Types Explained

### Quick Analysis
- **Agents**: MCP, Repomix, Architecture, Business Logic, Diagrams
- **Time**: 1-2 hours
- **Good for**: Initial assessment, small projects

### Comprehensive Analysis
- **Agents**: All agents including Security, Performance, Documentation
- **Time**: 3-4 hours
- **Good for**: Full documentation, large projects

### Security Focus
- **Agents**: Security-specific analysis
- **Time**: 2 hours
- **Good for**: Security audits

## Tips

1. **Always test connection first** with the test workflow
2. **Start with Quick Analysis** to verify everything works
3. **Check logs** if something fails: `docker logs doc-framework-api`
4. **Use Manual triggers** for testing and development
5. **Use Webhook triggers** for automation and CI/CD

## Next Steps

After successful analysis:
1. Review generated documentation in `output/docs/`
2. Check diagrams in `output/diagrams/`
3. Read agent summaries in `output/context/`
4. Run comprehensive analysis for more detail
5. Customize workflows for your needs