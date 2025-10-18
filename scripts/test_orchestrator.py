#!/usr/bin/env python3

"""
Test script for the new orchestrator implementation.
"""
import time
import logging
import os
import asyncio
import argparse
from sherlock.orchestrator import orchestrate
from sherlock.config import Config

# Setup development configuration
Config.setup_for_development()
logger = logging.getLogger(__name__)


async def main():
    """Main function for the orchestrator test."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test SRE Agent Orchestrator")
    parser.add_argument(
        "--diagnostic-agent", 
        choices=["eks-mcp"], 
        default="eks-mcp",
        help="Choose diagnostic agent: eks-mcp (default: eks-mcp)"
    )
    parser.add_argument(
        "--query",
        default="Could you analyze why the carts service is having issues?",
        help="Investigation query (default: analyze carts service issues)"
    )
    
    args = parser.parse_args()
    
    print(f"\n🔧 New SRE Agent Orchestrator Test")
    print(f"📊 Diagnostic Agent: {args.diagnostic_agent}")
    print(f"❓ Query: {args.query}\n")
    
    try:
        start_time = time.time()
        result = await orchestrate(args.query, args.diagnostic_agent)
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
        print(f"Diagnostic agent used: {args.diagnostic_agent}")

    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        print("Make sure you have:")
        print("- AWS credentials configured")
        print("- kubectl access to EKS cluster")
        print("- Docker running (if using eks-mcp agent)")

if __name__ == "__main__":
    asyncio.run(main())
