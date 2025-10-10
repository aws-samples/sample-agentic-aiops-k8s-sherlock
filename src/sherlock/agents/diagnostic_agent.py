"""K8sGPT MCP client factory for diagnostic operations."""
import logging
import os
from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)

def get_k8sgpt_mcp_client():
    """Get K8sGPT MCP client for use in orchestrator."""
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="k8sgpt",
                args=["serve", "--mcp", "--backend", "amazonbedrock"],
                env={
                    "KUBECONFIG": os.path.expanduser("~/.kube/config"),
                    "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
                    "AWS_DEFAULT_REGION": os.getenv("AWS_REGION", "us-east-1"),
                    "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID", ""),
                    "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
                    "AWS_SESSION_TOKEN": os.getenv("AWS_SESSION_TOKEN", ""),
                },
                timeout=300
            )
        )
    )

def get_eks_mcp_client():
    """Get EKS MCP client for use in orchestrator."""
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="docker",
                args=[
                    "run",
                    "--rm",
                    "--interactive",
                    "--env", f"AWS_REGION={aws_region}",
                    "--env", f"AWS_ACCESS_KEY_ID={os.getenv('AWS_ACCESS_KEY_ID', '')}",
                    "--env", f"AWS_SECRET_ACCESS_KEY={os.getenv('AWS_SECRET_ACCESS_KEY', '')}",
                    "--env", f"AWS_SESSION_TOKEN={os.getenv('AWS_SESSION_TOKEN', '')}",
                    "--env", "FASTMCP_LOG_LEVEL=ERROR",
                    "--volume", f"{os.path.expanduser('~')}/.aws:/root/.aws:ro",
                    "awslabs/eks-mcp-server:latest",
                    "--allow-sensitive-data-access"
                ],
                env={},
                timeout=30
            )
        )
    )