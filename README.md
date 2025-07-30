## Sample Agentic AIOps K8s Sherlock

An intelligent Kubernetes troubleshooting system using AI agents for automated incident response and root cause analysis.

### Overview

This project demonstrates how to build an agentic AIOps system that can automatically investigate Kubernetes issues, analyze observability data, and provide actionable insights for SRE teams.

### Features

- 🔍 **Intelligent Diagnostics**: AI-powered Kubernetes cluster analysis
- 📊 **Observability Integration**: CloudWatch metrics, logs, and alarms analysis  
- 💾 **Database Insights**: DynamoDB performance and throttling detection
- 🤖 **Multi-Agent Coordination**: Specialized agents working together
- 🔗 **Amazon Q Integration**: Natural language interface for investigations

### Quick Start

```bash
# Install dependencies and AWS credentials
uv sync
source .venv/bin/activate

# Testing
python scripts/test_orchestrator.py

```
#### Amazon Q CLI
```
# ~/.aws/amazonq/mcp.json

{
  "mcpServers": {
    "sherlock": {
      "command": "sherlock-mcp-server",
      "args": [],
      "env": {
        "AWS_REGION": "us-east-1",
        "KUBECONFIG": "~/.kube/config",
        "BYPASS_TOOL_CONSENT": "true"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

**Troubleshooting:**
```
tail -f ~/.aws/amazonq/sherlock-mcp.log
```

### Architecture

Coming soon...

### License

MIT License