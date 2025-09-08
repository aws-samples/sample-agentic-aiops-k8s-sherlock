#!/usr/bin/env python3
"""
Script to generate high traffic directly to the cart service using hey.
This will test DynamoDB read throughput and potentially crash the service.
"""
import argparse
import subprocess
import random
import string
import time
import signal
import sys
import os

def setup_port_forward(namespace="carts", local_port=8080):
    """Set up port forwarding to the cart service."""
    print(f"Setting up port forwarding to cart service in namespace {namespace}...")
    cmd = ["kubectl", "port-forward", f"service/carts", f"{local_port}:80", "-n", namespace]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Give it time to establish
    time.sleep(2)
    
    # Check if port forwarding was successful
    if process.poll() is not None:
        print("Error: Port forwarding failed")
        return None
    
    print(f"Port forwarding established: localhost:{local_port} -> carts:80")
    return process

def generate_random_customer_id():
    """Generate a random customer ID."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def run_hey(duration, concurrency, rate_limit=None):
    """Run hey to generate traffic directly to the cart service."""
    # Build the hey command
    cmd = ["hey"]
    
    # Add duration
    cmd.extend(["-z", f"{duration}s"])
    
    # Add concurrency
    cmd.extend(["-c", str(concurrency)])
    
    # Add rate limit if specified
    if rate_limit:
        cmd.extend(["-q", str(rate_limit)])
    
    # Add URL with random customer ID to avoid caching
    customer_id = generate_random_customer_id()
    target_url = f"http://localhost:8080/carts/{customer_id}"
    cmd.append(target_url)
    
    print(f"Running hey with command: {' '.join(cmd)}")
    
    # Run hey
    subprocess.run(cmd)

def cleanup(port_forward_process):
    """Clean up port forwarding process."""
    if port_forward_process:
        print("Stopping port forwarding...")
        port_forward_process.terminate()
        port_forward_process.wait()

def signal_handler(sig, frame, port_forward_process=None):
    """Handle Ctrl+C to clean up port forwarding."""
    print("\nInterrupted by user. Cleaning up...")
    cleanup(port_forward_process)
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Generate high traffic directly to the cart service")
    parser.add_argument("--cart-namespace", default="carts", help="Namespace of the cart service")
    parser.add_argument("--duration", type=int, default=600, help="Duration in seconds")
    parser.add_argument("--concurrency", type=int, default=500, help="Number of concurrent workers")
    parser.add_argument("--rate-limit", type=int, help="Rate limit in queries per second (QPS) per worker")
    parser.add_argument("--port", type=int, default=8080, help="Local port for port forwarding")
    args = parser.parse_args()
    
    # Set up port forwarding
    port_forward_process = setup_port_forward(args.cart_namespace, args.port)
    if not port_forward_process:
        return
    
    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, port_forward_process))
    
    try:
        print(f"Generating traffic directly to cart service")
        print(f"Duration: {args.duration}s, Concurrency: {args.concurrency}")
        if args.rate_limit:
            print(f"Rate limit: {args.rate_limit} QPS per worker")
        
        # Run hey
        run_hey(args.duration, args.concurrency, args.rate_limit)
    finally:
        # Clean up
        cleanup(port_forward_process)

if __name__ == "__main__":
    main()