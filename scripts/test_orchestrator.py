#!/usr/bin/env python3

"""
Test script for the new orchestrator implementation.
"""
import time
import logging
import os
import asyncio
from sherlock.orchestrator import orchestrate
from sherlock.config import Config

# Setup development configuration
Config.setup_for_development()
logger = logging.getLogger(__name__)


async def main():
    """Main function for the orchestrator test."""
    print("\n🔧 New SRE Agent Orchestrator Test\n")
    
    try:
        start_time = time.time()
        result = await orchestrate("Could you analyze why the carts service is having issues?")
#        result = await orchestrate("My catalog pod had a restart. Why did it happen? When? Is everything recovered? Any issues still pending due to the pod termination?")   # orchestrate uses hardcoded task
        #result = await orchestrate("What is the cpu utilization of carts service in yesterday?")   # orchestrate uses hardcoded task

#        result = await orchestrate("Can you tell me what was the last error from the carts service? And when it did take place?")   # orchestrate uses hardcoded task
#     result = await orchestrate("Can you provide me a detailed summary of my retail store application? What are the nodes, the pods and the services? Their names, their status? Their latest metrics and logs? I want to understand the existing system status.")   # orchestrate uses hardcoded task
        elapsed = time.time() - start_time
        
        print(str(result))

        # Show metrics if available.
        if hasattr(result, 'metrics'):
            print("\nMetrics Summary:")
            print("===============")
            metrics_summary = result.metrics.get_summary()
            print(f"Total tokens: {metrics_summary.get('accumulated_usage', {}).get('totalTokens', 'N/A')}")
            print(f"Cycles: {metrics_summary.get('total_cycles', 'N/A')}")
            print(f"Tools used: {list(metrics_summary.get('tool_usage', {}).keys())}")
            print(f"Average cycle time: {metrics_summary.get('average_cycle_time', 'N/A'):.2f}s")
        
        print(f"\nExecution time: {elapsed:.2f} seconds")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())