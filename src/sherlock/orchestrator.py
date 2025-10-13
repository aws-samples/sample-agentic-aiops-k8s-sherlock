"""SRE Agent Orchestrator for coordinating specialized agents."""
import logging
from datetime import datetime
from strands import Agent
from strands.multiagent.swarm import Swarm
from langfuse import get_client
from sherlock.agents.diagnostic_agent import get_k8sgpt_mcp_client, get_eks_mcp_client
from sherlock.agents.observability_agent import get_cloudwatch_mcp_client
from sherlock.agents.persistence_agent import get_dynamodb_mcp_client
from sherlock.prompts import (
    DIAGNOSTIC_AGENT_SWARM_PROMPT,
    OBSERVABILITY_AGENT_SWARM_PROMPT,
    PERSISTENCE_AGENT_SWARM_PROMPT,
)

logger = logging.getLogger(__name__)

def format_investigation_results(result: dict) -> str:
    """Format investigation results for display."""
    if isinstance(result, dict):
        formatted_output = "## SRE Investigation Results\n\n"
        
        for agent_name, agent_result in result.items():
            formatted_output += f"### {agent_name.replace('_', ' ').title()}\n"
            formatted_output += f"{agent_result}\n\n"
        
        return formatted_output
    else:
        return str(result)

async def orchestrate(query: str, diagnostic_agent: str = "k8sgpt"):
    """Orchestrate a comprehensive investigation using specialized agents.
    
    Args:
        query: The investigation query
        diagnostic_agent: Which diagnostic agent to use ("k8sgpt" or "eks-mcp")
    """
    logger.info(f"Starting orchestration for query: {query}")
    logger.info(f"Using diagnostic agent: {diagnostic_agent}")
    
    # Wrap entire orchestration in Langfuse span to control trace output
    langfuse = get_client()
    
    with langfuse.start_as_current_span(
        name="sherlock-investigation",
        input={"query": query, "diagnostic_agent": diagnostic_agent}
    ) as investigation_span:
        try:
            # Create multiple MCP clients for different services
            if diagnostic_agent == "eks-mcp":
                diagnostic_client = get_eks_mcp_client()
                diagnostic_name = "EKS MCP"
            elif diagnostic_agent == "k8sgpt":
                diagnostic_client = get_k8sgpt_mcp_client()
                diagnostic_name = "K8sGPT"
            else:
                raise ValueError(f"Invalid diagnostic agent: {diagnostic_agent}. Must be 'k8sgpt' or 'eks-mcp'")
                
            cloudwatch_client = get_cloudwatch_mcp_client()
            dynamodb_client = get_dynamodb_mcp_client()
            
            # Use all MCP clients together (as shown in MCP docs)
            with diagnostic_client, cloudwatch_client, dynamodb_client:
                # Get tools from all MCP servers
                diagnostic_tools = diagnostic_client.list_tools_sync()
                cloudwatch_tools = cloudwatch_client.list_tools_sync()
                dynamodb_tools = dynamodb_client.list_tools_sync()
                
                logger.info(f"Retrieved {len(diagnostic_tools)} {diagnostic_name} tools, {len(cloudwatch_tools)} CloudWatch tools, {len(dynamodb_tools)} DynamoDB tools")
                
                # Create agents with MCP tools and trace attributes
                diagnostic_agent_instance = Agent(
                    name="diagnostic_agent",
                    system_prompt=DIAGNOSTIC_AGENT_SWARM_PROMPT,
                    tools=diagnostic_tools,
                    trace_attributes={
                        "session.id": f"sherlock-{hash(query) % 10000}",
                        "user.id": "Sherlock",
                        "agent.type": "diagnostic",
                        "trace.name": "AIOps-Sherlock-Diagnostics",
                        "langfuse.tags": [
                            "AIOps-K8s-Sherlock",
                            "Diagnostics",
                            "Agent-Swarm"
                        ]
                    }
                )
                
                observability_agent = Agent(
                    name="observability_agent",
                    system_prompt=OBSERVABILITY_AGENT_SWARM_PROMPT,
                    tools=cloudwatch_tools,
                    trace_attributes={
                        "session.id": f"sherlock-{hash(query) % 10000}",
                        "user.id": "Sherlock",
                        "agent.type": "observability",
                        "trace.name": "AIOps-Sherlock-Observability",
                        "langfuse.tags": [
                            "AIOps-K8s-Sherlock",
                            "Observability",
                            "Agent-Swarm"
                        ]
                    }
                )
                
                persistence_agent = Agent(
                    name="persistence_agent",
                    system_prompt=PERSISTENCE_AGENT_SWARM_PROMPT,
                    tools=dynamodb_tools,
                    trace_attributes={
                        "session.id": f"sherlock-{hash(query) % 10000}",
                        "user.id": "Sherlock",
                        "agent.type": "persistence",
                        "trace.name": "AIOps-Sherlock-Persistence",
                        "langfuse.tags": [
                            "AIOps-K8s-Sherlock",
                            "Persistence",
                            "Agent-Swarm"
                        ]
                    }
                )
                
                # Create and execute swarm
                swarm = Swarm([diagnostic_agent_instance, observability_agent, persistence_agent])
                logger.info("Running comprehensive SRE swarm analysis...")
                
                # Enhance query with current time
                current_time = datetime.now().strftime("%A, %Y-%m-%d %H:%M:%S UTC")
                enhanced_query = f"Current time: {current_time}\n\nUser query: {query}"
                
                result = await swarm.invoke_async(enhanced_query)
            
            final_result = {
                "status": "success",
                "query": query,
                "cached": False,
                "swarm_status": result.status.value,
                "execution_time": result.execution_time,
                "agents_used": [node.node_id for node in result.node_history],
                "results": {name: getattr(node_result.result, 'content', str(node_result.result)) for name, node_result in result.results.items()}
            }
            
            # Format results and update trace output within our controlled span
            formatted_output = format_investigation_results(final_result["results"])
            logger.info(f"Formatted output length: {len(formatted_output)} characters")
            
            # Update the investigation span with the formatted output
            investigation_span.update(output=formatted_output)
            logger.info("Successfully updated investigation span with output")
                    
            return final_result["results"]
            
        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}")
            investigation_span.update(output=f"Error: {str(e)}")
            raise
