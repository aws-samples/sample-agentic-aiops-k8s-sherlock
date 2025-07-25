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
        result = await orchestrate("Diagnose why carts service is crashing? Table name: retail-store-carts. AWS region: us-east-1")   # orchestrate uses hardcoded task
        elapsed = time.time() - start_time
        
        print(str(result))

        # Show metrics if available
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