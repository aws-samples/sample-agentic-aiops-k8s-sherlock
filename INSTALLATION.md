# 🚀 Sherlock SRE Investigation System - Installation Guide

This guide will help you set up the complete Sherlock SRE Investigation System with all required dependencies and MCP servers.

## 📋 Prerequisites

- Amazon Linux 2023(64bit arm or x64) or compatible Linux distribution
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

### 2. Install Docker

Install and configure Docker for container management:

```bash
# Install Docker
sudo dnf install -y docker

# Add current user to docker group
sudo usermod -aG docker $(whoami)

# Start Docker service
sudo systemctl start docker.service
sudo systemctl enable docker.service

# Verify Docker installation
echo "Docker installed. Checking configuration"
docker --version
sudo systemctl status docker.service
```

**Note:** You may need to log out and log back in from terminal for the docker group changes to take effect.

### 3. Install Python 3.11

Install Python 3.11 and set up aliases:

```bash
# Install Python 3.11
sudo dnf install -y python3.11 python3.11-pip python3.11-devel

# Create python alias for current session
alias python=python3.11
alias pip=pip3.11

# Add aliases to bashrc for persistence
echo 'alias python=python3.11' >> ~/.bashrc
echo 'alias pip=pip3.11' >> ~/.bashrc

# Verify installation
python --version
pip --version
```

### 4. Install UV (Python Package Manager)

UV is a fast Python package manager:

```bash
# Download and install uv
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh
bash /tmp/uv-install.sh
rm -f /tmp/uv-install.sh

# Add uv to PATH for current session
export PATH="$HOME/.local/bin:$PATH"

# Verify installation
uv --version
```

### 5. Install oha (HTTP Load Testing Tool)

Install oha for load testing the cart service:

```bash
# Detect architecture and download appropriate oha binary
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    curl -L -o oha https://github.com/hatoo/oha/releases/download/v1.10.0/oha-linux-amd64
elif [ "$ARCH" = "aarch64" ]; then
    curl -L -o oha https://github.com/hatoo/oha/releases/download/v1.10.0/oha-linux-arm64
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

chmod +x oha
sudo mv oha /usr/local/bin/

# Verify installation
oha --version
```

### 6. Install Kubernetes CLI (kubectl)

Install kubectl with automatic architecture detection:

```bash
# Detect architecture and download appropriate kubectl binary
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    KUBECTL_ARCH="amd64"
elif [ "$ARCH" = "aarch64" ]; then
    KUBECTL_ARCH="arm64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

# Download and install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/${KUBECTL_ARCH}/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client
```

### 7. Configure Shell Environment

Set up PATH for installed tools:

```bash
# Add uv to PATH for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Apply changes
source ~/.bashrc
source $HOME/.local/bin/env
```

### 8. Clone and Setup MCP Repository

Download the AWS MCP servers:

```bash
# Clone MCP repository
git clone https://github.com/awslabs/mcp
cd mcp

# Checkout specific release branch
git fetch --all
git checkout -b release-2025-08-22 origin/release/2025.08.20250822184623
```

### 9. Build MCP Server Docker Images

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

### 10. Clone Required Repositories

Set up the required repositories in your home directory:

```bash
# Navigate to home directory
cd ~

# Clone required repositories
git clone https://github.com/aws-samples/sample-agentic-aiops-k8s-sherlock.git
git clone https://github.com/aws-containers/retail-store-sample-app.git
```

### 11. Setup Jaeger Tracing (Optional)

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
echo "oha: $(oha --version 2>/dev/null || echo 'oha not found')"
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
which terraform oha kubectl python uv docker

# Check Docker images
docker images | grep -E "(eks-mcp-server|cloudwatch-mcp-server|dynamodb-mcp-server)"

# Check Python environment
python --version
uv --version
oha --version
```

### Getting Help

- Verify AWS credentials: `aws sts get-caller-identity`
- Test Kubernetes access: `kubectl get pods`
- Review the main README.md for usage examples

## 📚 Next Steps

After successful installation and deployment:

1. Start using Sherlock to investigate your retail store application
2. Explore different types of queries about your infrastructure
3. Set up monitoring and observability for your applications

## 🎉 You're Ready!

Your Sherlock SRE Investigation System is now installed and ready to help you troubleshoot your Kubernetes infrastructure with AI-powered insights!

Start investigating your retail store application with Sherlock's intelligent analysis capabilities.
