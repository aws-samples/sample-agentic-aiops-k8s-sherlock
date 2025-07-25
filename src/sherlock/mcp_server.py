"""MCP server for SRE Agent Toolkit."""
from mcp.server import FastMCP
from sherlock.orchestrator import orchestrate
from sherlock.config import Config
import logging
import os
import nest_asyncio
nest_asyncio.apply()

# Setup MCP-specific configuration
Config.setup_for_mcp()
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("SRE Agent Toolkit")

@mcp.tool(
    name="sherlock", 
    description="Comprehensive SRE investigation using K8s diagnostics, CloudWatch observability, and DynamoDB analysis"
)
def sherlock(query: str) -> str:
    import asyncio
    logger.info(f"SRE Orchestrator investigating: {query}")
    
    try:
        # Execute orchestration
        result = asyncio.run(orchestrate(query))
        
        # Format result for Amazon Q
        if isinstance(result, dict):
            # Extract agent results for better readability
            formatted_output = "## SRE Investigation Results\n\n"
            
            for agent_name, agent_result in result.items():
                formatted_output += f"### {agent_name.replace('_', ' ').title()}\n"
                formatted_output += f"{agent_result}\n\n"
            
            logger.info("SRE Orchestrator completed successfully")
            return formatted_output
        else:
            return str(result)
            
    except Exception as e:
        error_msg = f"SRE investigation failed: {str(e)}"
        logger.error(error_msg)
        return f"❌ **Error**: {error_msg}\n\nPlease check your AWS credentials, Kubernetes access, and MCP server connections."

def main():
    """Run the MCP server for Amazon Q integration."""
    try:
        logger.info("Starting SRE Agent Toolkit MCP Server")
        logger.info("Available tool: sherlock - Comprehensive investigation")
        logger.info(f"Environment: AWS_REGION={os.getenv('AWS_REGION')}, KUBECONFIG={os.getenv('KUBECONFIG')}")
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"MCP Server failed to start: {e}")
        raise

if __name__ == "__main__":
    main()
