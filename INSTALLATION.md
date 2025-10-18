# 🚀 Sherlock SRE Investigation System - Installation Guide

This guide will help you set up the complete Sherlock SRE Investigation System with all required dependencies and MCP servers.

## 📋 Prerequisites

- Amazon Linux 2 or compatible Linux distribution
- Docker installed and running
- Internet connectivity for downloading packages
- Sudo privileges

## 🛠️ Installation Steps

### 1. Install System Tools and Terraform

First, we'll install essential system tools including Terraform:

```bash
# Install system tools and Terraform
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
sudo yum -y install terraform
```

### 2. Install Kubernetes CLI (kubectl)

Install kubectl for ARM64 architecture:

```bash
# Download and install kubectl for ARM64
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/arm64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

### 3. Install UV (Python Package Manager)

UV is a fast Python package manager:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 4. Configure Shell Environment

Set up Python alias and PATH:

```bash
# Add Python alias and uv to PATH
echo 'alias python=python3' >> ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Apply changes
source ~/.bashrc
source $HOME/.local/bin/env
```

### 5. Clone and Setup MCP Repository

Download the AWS MCP servers:

```bash
# Clone MCP repository
git clone https://github.com/awslabs/mcp
cd mcp

# Checkout specific release branch
git fetch --all
git checkout -b release-2025-08-22 origin/release/2025.08.20250822184623
```

### 6. Build MCP Server Docker Images

Build the required MCP server images:

#### EKS MCP Server
```bash
cd src/eks-mcp-server/
docker build -t awslabs/eks-mcp-server:latest .
```

#### CloudWatch MCP Server
```bash
cd ../../src/cloudwatch-mcp-server
docker build -t awslabs/cloudwatch-mcp-server:latest .
```

#### DynamoDB MCP Server
```bash
cd ../../src/dynamodb-mcp-server
docker build -t awslabs/dynamodb-mcp-server:latest .
```

### 7. Clone Required Repositories

Set up the required repositories in your home directory:

```bash
# Navigate to home directory
cd ~

# Clone required repositories
git clone https://github.com/aws-samples/sample-agentic-aiops-k8s-sherlock.git
git clone https://github.com/aws-containers/retail-store-sample-app.git
```

### 8. Setup Jaeger Tracing (Optional)

**Note**: This step is optional as the current configuration uses Langfuse for telemetry.

```bash
# Pull and run Jaeger all-in-one container
docker run -d --name jaeger \
  -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 \
  -e COLLECTOR_OTLP_ENABLED=true \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 14250:14250 \
  -p 14268:14268 \
  -p 14269:14269 \
  -p 9411:9411 \
  jaegertracing/all-in-one:latest
```

## ✅ Verification

After installation, verify all components are working:

```bash
echo "=== Installation Verification ==="
echo "Architecture: $(uname -m)"
echo "Terraform: $(terraform --version | head -1)"
echo "kubectl: $(kubectl version --client --short 2>/dev/null || echo 'kubectl installed')"
echo "Python: $(python --version 2>/dev/null || python3 --version)"
echo "uv: $(uv --version)"

echo -e "\nDocker images built:"
docker images | grep -E "(eks-mcp-server|cloudwatch-mcp-server|dynamodb-mcp-server)"

echo -e "\nRepositories cloned:"
ls -la ~/ | grep -E "(mcp|sample-agentic|retail-store)"
```

## 🏪 Deploy Retail Store Sample Application

After installation, deploy the retail store sample application to have a working Kubernetes environment for Sherlock to analyze:

### Navigate to Terraform Directory
```bash
cd ~/retail-store-sample-app/terraform/eks/default
```

### Initialize Terraform
```bash
terraform init
```

### Plan Terraform Deployment
```bash
terraform plan
```

### Apply Terraform Configuration 
```bash
terraform apply -auto-approve
```

**Expected Output:**
The deployment will take approximately 17-18 minutes and will show progress like:
```
time_sleep.restart_pods: Still creating... [00m20s elapsed]
time_sleep.restart_pods: Still creating... [00m30s elapsed]
time_sleep.restart_pods: Creation complete after 30s [id=2025-09-25T12:19:32Z]
null_resource.restart_pods: Creating...
null_resource.restart_pods: Provisioning with 'local-exec'...
null_resource.restart_pods (local-exec): (output suppressed due to sensitive value in config)
...
Apply complete! Resources: 144 added, 0 changed, 0 destroyed.

Outputs:
configure_kubectl = "aws eks --region us-east-1 update-kubeconfig --name retail-store"
retail_app_url = "http://k8s-ui-ui-cce8b5e9e6-9b3bf298644646a8.elb.us-east-1.amazonaws.com"
```

### Configure kubectl Access
```bash
aws eks --region us-east-1 update-kubeconfig --name retail-store
```

### Verify Deployment
```bash
kubectl get pods -A
kubectl get services -A
```

## 🔍 Troubleshooting

### Common Issues

1. **Architecture Mismatch**: Ensure you're using ARM64 packages on ARM64 systems
2. **Permission Denied**: Make sure you have sudo privileges
3. **Docker Issues**: Ensure Docker daemon is running
4. **Network Issues**: Check internet connectivity for downloads

### Verification Commands

```bash
# Check if all tools are installed
which terraform kubectl python uv docker

# Check Docker images
docker images | grep -E "(eks-mcp-server|cloudwatch-mcp-server|dynamodb-mcp-server)"

# Check Python environment
python --version
uv --version
```

### Getting Help

- Check the logs in `~/.aws/amazonq/sherlock-mcp.log`
- Verify AWS credentials: `aws sts get-caller-identity`
- Test Kubernetes access: `kubectl get pods`
- Review the main README.md for usage examples

## 📚 Next Steps

After successful installation and deployment:

1. Start using Sherlock to investigate your retail store application
2. Explore different types of queries about your infrastructure
3. Set up monitoring and observability for your applications
4. Experiment with the MCP server integration

## 🎉 You're Ready!

Your Sherlock SRE Investigation System is now installed and ready to help you troubleshoot your Kubernetes infrastructure with AI-powered insights!

Start investigating your retail store application with Sherlock's intelligent analysis capabilities.
