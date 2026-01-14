#!/usr/bin/env python3
"""
Script to generate high traffic directly to the cart service using oha.
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
import json

def setup_loadbalancer(namespace="carts", service_name="carts"):
    """Expose the cart service as LoadBalancer type."""
    print(f"Exposing service {service_name} as LoadBalancer in namespace {namespace}...")
    
    cmd = [
        "kubectl", "patch", "service", service_name, 
        "-n", namespace,
        "-p", '{"spec":{"type":"LoadBalancer"}}'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Warning: Failed to patch service: {result.stderr}")
        print("Service might already be LoadBalancer type")
    else:
        print(f"✓ Service exposed as LoadBalancer")
    
    return result.returncode == 0

def restrict_deployment_resources(namespace="carts", deployment_name="carts", 
                                  cpu_limit="500m", memory_limit="512Mi"):
    """Restrict deployment resources to create resource pressure for testing."""
    print(f"\nRestricting deployment {deployment_name} resources in namespace {namespace}...")
    print(f"  CPU: {cpu_limit}, Memory: {memory_limit}")
    
    patch = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [{
                        "name": deployment_name,
                        "resources": {
                            "limits": {
                                "cpu": cpu_limit,
                                "memory": memory_limit
                            },
                            "requests": {
                                "cpu": cpu_limit,
                                "memory": memory_limit
                            }
                        }
                    }]
                }
            }
        }
    }
    
    cmd = [
        "kubectl", "patch", "deployment", deployment_name,
        "-n", namespace,
        "--patch", json.dumps(patch)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: Failed to patch deployment: {result.stderr}")
        return False
    
    print(f"✓ Deployment resources restricted")
    print(f"  This will create resource pressure for AI agent demonstration")
    return True

def wait_for_loadbalancer_url(namespace="carts", service_name="carts", timeout=300):
    """Wait for LoadBalancer URL to be assigned."""
    print(f"\nWaiting for LoadBalancer URL to be assigned (timeout: {timeout}s)...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        lb_url = get_loadbalancer_url(namespace, service_name)
        if lb_url:
            elapsed = int(time.time() - start_time)
            print(f"✓ LoadBalancer URL assigned: {lb_url} (took {elapsed}s)")
            return lb_url
        
        print("  LoadBalancer not ready yet, waiting 10s...")
        time.sleep(10)
    
    print(f"Error: LoadBalancer not ready after {timeout}s")
    return None

def wait_for_loadbalancer_health(lb_url, timeout=120):
    """Wait for LoadBalancer to be fully provisioned and healthy."""
    print(f"\n⏳ Waiting for LoadBalancer to be fully provisioned and healthy...")
    print(f"   Checking health endpoint: http://{lb_url}/carts/healthcheck")
    
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < timeout:
        attempt += 1
        try:
            # Try to connect to the health check endpoint
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 f"http://{lb_url}/carts/healthcheck"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            status_code = result.stdout.strip()
            
            if status_code == "200":
                elapsed = int(time.time() - start_time)
                print(f"✓ LoadBalancer is healthy! (took {elapsed}s, {attempt} attempts)")
                return True
            else:
                print(f"   Attempt {attempt}: Got HTTP {status_code}, retrying in 10s...")
        
        except subprocess.TimeoutExpired:
            print(f"   Attempt {attempt}: Connection timeout, retrying in 10s...")
        except Exception as e:
            print(f"   Attempt {attempt}: Error ({str(e)}), retrying in 10s...")
        
        time.sleep(10)
    
    elapsed = int(time.time() - start_time)
    print(f"⚠ LoadBalancer health check timed out after {elapsed}s")
    print(f"   Proceeding anyway, but load test might fail initially...")
    return False
    """Wait for LoadBalancer to be fully provisioned and healthy."""
    print(f"\n⏳ Waiting for LoadBalancer to be fully provisioned and healthy...")
    print(f"   Checking health endpoint: http://{lb_url}/carts/healthcheck")
    
    start_time = time.time()
    attempt = 0
    
    while time.time() - start_time < timeout:
        attempt += 1
        try:
            # Try to connect to the health check endpoint
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 f"http://{lb_url}/carts/healthcheck"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            status_code = result.stdout.strip()
            
            if status_code == "200":
                elapsed = int(time.time() - start_time)
                print(f"✓ LoadBalancer is healthy! (took {elapsed}s, {attempt} attempts)")
                return True
            else:
                print(f"   Attempt {attempt}: Got HTTP {status_code}, retrying in 2s...")
        
        except subprocess.TimeoutExpired:
            print(f"   Attempt {attempt}: Connection timeout, retrying in 2s...")
        except Exception as e:
            print(f"   Attempt {attempt}: Error ({str(e)}), retrying in 2s...")
        
        time.sleep(2)
    
    elapsed = int(time.time() - start_time)
    print(f"⚠ LoadBalancer health check timed out after {elapsed}s")
    print(f"   Proceeding anyway, but load test might fail initially...")
    return False

def get_loadbalancer_url(namespace="carts", service_name="carts"):
    """Get the LoadBalancer URL for the cart service."""
    cmd = ["kubectl", "get", "service", service_name, "-n", namespace, "-o", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return None
    
    try:
        service_data = json.loads(result.stdout)
        ingress = service_data.get("status", {}).get("loadBalancer", {}).get("ingress", [])
        
        if not ingress:
            return None
        
        # Get hostname (for AWS ELB) or IP (for other cloud providers)
        lb_url = ingress[0].get("hostname") or ingress[0].get("ip")
        return lb_url
        
    except (json.JSONDecodeError, KeyError):
        return None

def generate_random_customer_id():
    """Generate a random customer ID."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def run_oha(duration, concurrency, rate_limit, lb_url, num_customers=100):
    """Run oha to generate traffic directly to the cart service via LoadBalancer."""
    # Pre-generate a pool of customer IDs to simulate multiple customers
    customer_ids = [generate_random_customer_id() for _ in range(num_customers)]
    
    print(f"\nGenerated {num_customers} customer IDs to simulate realistic traffic")
    print(f"Sample customer IDs: {', '.join(customer_ids[:5])}...")
    
    customer_id = random.choice(customer_ids)
    
    # Build the oha command
    cmd = ["oha"]
    
    # Add duration
    cmd.extend(["-z", f"{duration}s"])
    
    # Add concurrency
    cmd.extend(["-c", str(concurrency)])
    
    # Add rate limit
    cmd.extend(["-q", str(rate_limit)])
    
    # Add latency correction and disable keepalive for realistic testing
    cmd.append("--latency-correction")
    cmd.append("--disable-keepalive")
    
    # Build target URL
    target_url = f"http://{lb_url}/carts/{customer_id}"
    cmd.append(target_url)
    
    print(f"\nRunning oha with command: {' '.join(cmd)}")
    print(f"Target: {target_url}")
    
    # Run oha
    subprocess.run(cmd)

def cleanup():
    """Clean up resources (no longer needed without port-forward)."""
    print("Cleanup complete")

def signal_handler(sig, frame):
    """Handle Ctrl+C to clean up."""
    print("\nInterrupted by user. Cleaning up...")
    cleanup()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Generate high traffic directly to the cart service via LoadBalancer")
    parser.add_argument("--cart-namespace", default="carts", help="Namespace of the cart service")
    parser.add_argument("--service-name", default="carts", help="Name of the cart service")
    parser.add_argument("--deployment-name", default="carts", help="Name of the cart deployment")
    parser.add_argument("--duration", type=int, default=600, help="Duration in seconds")
    parser.add_argument("--concurrency", type=int, default=1000, help="Number of concurrent workers (default: 1000)")
    parser.add_argument("--rate-limit", type=int, default=50, help="Rate limit in queries per second (QPS) per worker (default: 50)")
    parser.add_argument("--num-customers", type=int, default=100, help="Number of unique customer IDs to generate (default: 100)")
    parser.add_argument("--lb-url", help="LoadBalancer URL (optional, will auto-detect if not provided)")
    parser.add_argument("--setup", action="store_true", help="Automatically setup LoadBalancer and restrict resources")
    parser.add_argument("--cpu-limit", default="500m", help="CPU limit for deployment (default: 500m)")
    parser.add_argument("--memory-limit", default="512Mi", help="Memory limit for deployment (default: 512Mi)")
    parser.add_argument("--skip-resource-restriction", action="store_true", help="Skip restricting deployment resources")
    args = parser.parse_args()
    
    # Set up signal handler for clean exit
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Setup phase (if requested)
        if args.setup:
            print(f"\n{'='*60}")
            print(f"SETUP PHASE: Preparing environment for load test")
            print(f"{'='*60}\n")
            
            # Step 1: Expose service as LoadBalancer
            setup_loadbalancer(args.cart_namespace, args.service_name)
            
            # Step 2: Restrict deployment resources (unless skipped)
            if not args.skip_resource_restriction:
                restrict_deployment_resources(
                    args.cart_namespace, 
                    args.deployment_name,
                    args.cpu_limit,
                    args.memory_limit
                )
            else:
                print("\n⊘ Skipping resource restriction (--skip-resource-restriction)")
            
            # Step 3: Wait for LoadBalancer URL to be assigned
            lb_url = wait_for_loadbalancer_url(args.cart_namespace, args.service_name)
            if not lb_url:
                print("\nSetup failed. Please check your cluster and try again.")
                return
            
            # Step 4: Wait for LoadBalancer to be fully provisioned and healthy
            wait_for_loadbalancer_health(lb_url)
            
            print(f"\n{'='*60}")
            print(f"✓ Setup complete! LoadBalancer URL: {lb_url}")
            print(f"{'='*60}\n")
        else:
            # Get LoadBalancer URL if not provided
            lb_url = args.lb_url
            if not lb_url:
                print(f"Getting LoadBalancer URL for service {args.service_name}...")
                lb_url = get_loadbalancer_url(args.cart_namespace, args.service_name)
                if not lb_url:
                    print("\nFailed to get LoadBalancer URL. Please ensure:")
                    print("1. The service is exposed as LoadBalancer type")
                    print("2. The LoadBalancer has been provisioned (may take a few minutes)")
                    print("\nOr run with --setup to automatically configure everything:")
                    print("  python scripts/generate_traffic.py --setup")
                    print("\nOr provide the URL manually with --lb-url")
                    return
                print(f"✓ LoadBalancer URL: {lb_url}\n")
        
        print(f"\n{'='*60}")
        print(f"LOAD TEST PHASE: Generating traffic")
        print(f"{'='*60}")
        print(f"LoadBalancer URL: {lb_url}")
        print(f"Duration: {args.duration}s")
        print(f"Concurrency: {args.concurrency} workers")
        print(f"Rate limit: {args.rate_limit} QPS per worker")
        print(f"Total expected QPS: ~{args.concurrency * args.rate_limit}")
        print(f"Customer pool size: {args.num_customers} unique customers")
        print(f"{'='*60}\n")
        
        # Run oha
        run_oha(args.duration, args.concurrency, args.rate_limit, lb_url, args.num_customers)
        
    finally:
        # Clean up
        cleanup()

if __name__ == "__main__":
    main()
