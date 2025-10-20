# 🔍 Sherlock SRE Investigation System

An intelligent Kubernetes troubleshooting system using AI agents for automated incident response and root cause analysis.

## 🎯 Overview

Sherlock is an agentic AIOps system that automatically investigates Kubernetes issues, analyzes observability data, and provides actionable insights for SRE teams. It combines multiple AI agents to deliver comprehensive infrastructure analysis through natural language queries.

## 🏗️ Architecture

![Architecture](docs/sherlock-arc.png)

The system uses a multi-agent architecture where specialized agents collaborate to provide comprehensive analysis:

- **🔧 Diagnostic Agent**: Kubernetes cluster analysis and pod troubleshooting
- **📊 Observability Agent**: CloudWatch metrics, logs, and alarms analysis  
- **💾 Persistence Agent**: DynamoDB performance and throttling detection
- **🎯 Orchestrator**: Coordinates agent interactions and synthesizes results

## ✨ Features

- 🔍 **Intelligent Diagnostics**: AI-powered Kubernetes cluster analysis using EKS-MCP
- 📊 **Observability Integration**: Real-time CloudWatch metrics, logs, and alarms analysis  
- 💾 **Database Insights**: DynamoDB performance monitoring and throttling detection
- 🤖 **Multi-Agent Coordination**: Specialized agents working together for comprehensive analysis
- 🔗 **MCP Integration**: Model Context Protocol for seamless tool integration
- 🌐 **Natural Language Interface**: Ask questions about your infrastructure in plain English
- 📈 **Langfuse Telemetry**: Advanced observability and tracing for agent interactions

## 🚀 Quick Installation

For a complete setup including all dependencies and the retail store sample application, see our comprehensive installation guide:

**📖 [Complete Installation Guide](INSTALLATION.md)**

The installation guide covers:
- System dependencies (Terraform, kubectl, UV)
- AWS MCP server setup
- Retail store sample application deployment
- Sherlock configuration and testing

## ⚡ Quick Start (If Already Installed)

If you already have the system installed, you can quickly test it:

```bash
# Navigate to Sherlock directory
cd ~/sample-agentic-aiops-k8s-sherlock

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Configure Langfuse telemetry
export LANGFUSE_SECRET_KEY=your_langfuse_secret_key
export LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
export LANGFUSE_HOST="https://us.cloud.langfuse.com"

# Configure kubectl access to retail store cluster
aws eks --region us-east-1 update-kubeconfig --name retail-store

# Intentionally restrict carts deployment resources to create incidents for AI agent demonstration
kubectl patch deployment carts -n carts --patch '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "carts",
          "resources": {
            "limits": {
              "cpu": "500m",
              "memory": "512Mi"
            },
            "requests": {
              "cpu": "500m", 
              "memory": "512Mi"
            }
          }
        }]
      }
    }
  }
}'

# Intentionally throttle DynamoDB table to create database incidents for AI agent demonstration
aws dynamodb modify-table \
    --table-name retail-store-carts \
    --billing-mode PROVISIONED \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1

# Test the orchestrator (AI agents will detect and analyze K8s, DynamoDB constraints and traffic patterns). Default model id is: "us.anthropic.claude-sonnet-4-20250514-v1:0" 
python scripts/test_orchestrator.py

# Test with a specific Bedrock model
python scripts/test_orchestrator.py --model-id "us.anthropic.claude-sonnet-4-20250514-v1:0"

# Test with custom query and model
python scripts/test_orchestrator.py --query "Analyze the carts service performance issues" --model-id "amazon.nova-pro-v1:0"

# View available options
python scripts/test_orchestrator.py --help

```

### Available Models
You can reference the [AWS Bedrock Supported Models documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) to find appropriate models for your specific requirements.

**Default Models:**
- Test Orchestrator: `us.anthropic.claude-sonnet-4-20250514-v1:0`
- MCP Server: `anthropic.claude-3-5-sonnet-20241022-v2:0`

## 🚦 Generate Traffic Load

To create realistic load and trigger the resource constraints, run the traffic generator in a separate terminal:

```bash
# Open a new terminal and navigate to Sherlock directory
cd ~/sample-agentic-aiops-k8s-sherlock

# Activate virtual environment
source .venv/bin/activate

# Configure kubectl access
aws eks --region us-east-1 update-kubeconfig --name retail-store

# Generate continuous traffic to carts service
python scripts/generate_traffic.py
```

This will create load on the constrained carts service, making the resource and database throttling issues more observable by the AI agents.


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
