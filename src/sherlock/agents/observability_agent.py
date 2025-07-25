"""CloudWatch MCP client factory for observability operations."""
import logging
import os
from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)

def get_cloudwatch_mcp_client():
    """Get CloudWatch MCP client for use in orchestrator."""
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
                    "awslabs/cloudwatch-mcp-server:latest"
                ],
                env={},
                timeout=30
            )
        )
    )