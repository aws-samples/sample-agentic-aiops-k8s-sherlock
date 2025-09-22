"""SRE Agent Orchestrator for coordinating specialized agents."""
import logging
from datetime import datetime
from strands import Agent
from strands.multiagent.swarm import Swarm
from sherlock.agents.diagnostic_agent import get_k8sgpt_mcp_client
from sherlock.agents.observability_agent import get_cloudwatch_mcp_client
from sherlock.agents.persistence_agent import get_dynamodb_mcp_client
from sherlock.prompts import (
    DIAGNOSTIC_AGENT_SWARM_PROMPT,
    OBSERVABILITY_AGENT_SWARM_PROMPT,
    PERSISTENCE_AGENT_SWARM_PROMPT,
)

logger = logging.getLogger(__name__)

async def orchestrate(query: str):
    """Orchestrate a comprehensive investigation using specialized agents."""
    logger.info(f"Starting orchestration for query: {query}")
    
    try:
        # Create multiple MCP clients for different services
        k8sgpt_client = get_k8sgpt_mcp_client()
        cloudwatch_client = get_cloudwatch_mcp_client()
        dynamodb_client = get_dynamodb_mcp_client()
        
        # Use all MCP clients together (as shown in MCP docs)
        with k8sgpt_client, cloudwatch_client, dynamodb_client:
            # Get tools from all MCP servers
            k8sgpt_tools = k8sgpt_client.list_tools_sync()
            cloudwatch_tools = cloudwatch_client.list_tools_sync()
            dynamodb_tools = dynamodb_client.list_tools_sync()
            
            logger.info(f"Retrieved {len(k8sgpt_tools)} K8sGPT tools, {len(cloudwatch_tools)} CloudWatch tools, {len(dynamodb_tools)} DynamoDB tools")
            
            # Create agents with MCP tools and trace attributes
            diagnostic_agent = Agent(
                name="diagnostic_agent",
                system_prompt=DIAGNOSTIC_AGENT_SWARM_PROMPT,
                tools=k8sgpt_tools,
                trace_attributes={
                    "session.id": f"sherlock-{hash(query) % 10000}",
                    "user.id": "sre-team",
                    "agent.type": "diagnostic",
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
                    "user.id": "sre-team",
                    "agent.type": "observability",
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
                    "user.id": "sre-team",
                    "agent.type": "persistence",
                    "langfuse.tags": [
                        "AIOps-K8s-Sherlock",
                        "Persistence",
                        "Agent-Swarm"
                    ]
                }
            )
            
            # Create and execute swarm
            swarm = Swarm([diagnostic_agent, observability_agent, persistence_agent])
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
                
        return final_result["results"]
        
    except Exception as e:
        logger.error(f"Orchestration failed: {str(e)}")
        raise