"""MCP server for SRE Agent Toolkit."""
from mcp.server import FastMCP
from sherlock.orchestrator import orchestrate, format_investigation_results
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
def sherlock(query: str, diagnostic_agent: str = "k8sgpt") -> str:
    import asyncio
    logger.info(f"SRE Orchestrator investigating: {query}")
    logger.info(f"Using diagnostic agent: {diagnostic_agent}")
    
    try:
        # Execute orchestration
        result = asyncio.run(orchestrate(query, diagnostic_agent))
        
        # Format result for Amazon Q using shared formatter
        formatted_output = format_investigation_results(result)
        
        logger.info("SRE Orchestrator completed successfully")
        return formatted_output
            
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
