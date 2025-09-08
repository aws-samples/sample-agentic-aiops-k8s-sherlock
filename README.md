## Sample Agentic AIOps K8s Sherlock

An intelligent Kubernetes troubleshooting system using AI agents for automated incident response and root cause analysis.

### Overview

This project demonstrates how to build an agentic AIOps system that can automatically investigate Kubernetes issues, analyze observability data, and provide actionable insights for SRE teams.

### Architecture

![Architecture](docs/sherlock-arc.png)

### Features

- 🔍 **Intelligent Diagnostics**: AI-powered Kubernetes cluster analysis
- 📊 **Observability Integration**: CloudWatch metrics, logs, and alarms analysis  
- 💾 **Database Insights**: DynamoDB performance and throttling detection
- 🤖 **Multi-Agent Coordination**: Specialized agents working together
- 🔗 **Amazon Q Integration**: Natural language interface for investigations


### Pre requisites
- k8sgpt 0.4.22+ (and make sure amazonbedrock has been configured [here](https://github.com/k8sgpt-ai/k8sgpt?tab=readme-ov-file#llm-ai-backends) )
- docker 27.3.1+
- python 3.13+
- kubectl 1.33+
- aws cli 2.27.2+
- Export AWS credentials into terminal
- Install [retail-store-sample-app](https://github.com/aws-containers/retail-store-sample-app)
  - Install manually cloudwatch container insights ([doc](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/deploy-container-insights-EKS.html))
- Make sure you have docker daemon running (e.g. Docker Desktop)
- Install ([AWS MCP Server for CloudWatch](https://github.com/awslabs/mcp/tree/main/src/cloudwatch-mcp-server) and ([AWS MCP Server for DynamoDB](https://github.com/awslabs/mcp/tree/main/src/dynamodb-mcp-server))
### Quick Start

```bash
# Install dependencies
uv sync

#(optional) create package
uv pip install -e .

# Execute the aws eks update-kubeconfig command to bridge the authentication gap between your local tools and the remote AWS EKS cluster. 
# This is needed by k8sgpt to analyze pods, deployments, events in the EKS cluster
aws eks update-kubeconfig --region us-east-1 --name retail-store


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


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

