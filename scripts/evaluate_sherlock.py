#!/usr/bin/env python3
"""
Evaluate Sherlock - A program to evaluate traces and datasets using Langfuse Python SDK

This program implements evaluation in multiple steps:
1. Fetch existing traces (by session/timestamp)
2. Single evaluation using custom evaluators and add scores to traces
3. Dataset evaluation using existing datasets
4. Multiple evaluators support

Usage:
    python scripts/evaluate_sherlock.py
"""

import os
import argparse
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from langfuse import get_client


class SherlockEvaluator:
    """Main evaluator class for Sherlock traces and datasets"""
    
    def __init__(self):
        """Initialize Langfuse client"""
        self.langfuse = get_client()
        print("✅ Langfuse client initialized")
    
    # STEP 1: Implement getting existing traces
    def fetch_traces_by_session(self, session_id: str, limit: int = 10) -> List[Any]:
        """Fetch traces by session ID"""
        try:
            traces = self.langfuse.api.trace.list(
                session_id=session_id,
                limit=limit
            )
            print(f"📊 Found {len(traces.data)} traces for session: {session_id}")
            return traces.data
        except Exception as e:
            print(f"❌ Error fetching traces by session: {e}")
            return []
    

    
    # STEP 2: Single evaluation using LLM as judge

    
    def evaluate_trace(self, trace_id: str) -> bool:
        """Evaluate a trace with multiple evaluators"""
        try:
            # Fetch the trace
            trace = self.langfuse.api.trace.get(trace_id)
            if not trace:
                print(f"❌ Trace not found: {trace_id}")
                return False
            
            # Apply multiple evaluators
            evaluations = [
                self.observation_count_score_evaluator(trace),
                self.latency_score_evaluator(trace),
                self.input_token_count_evaluator(trace),
                self.total_cost_evaluator(trace)
            ]
            
            # Add scores to trace
            for evaluation in evaluations:
                self.langfuse.create_score(
                    name=evaluation["name"],
                    value=evaluation["value"],
                    trace_id=trace_id,
                    comment=evaluation["comment"]
                )
                print(f"✅ Applied {evaluation['name']}: {evaluation['comment']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error evaluating trace {trace_id}: {e}")
            return False
    
    def evaluate_traces_batch(self, traces: List[Any]) -> int:
        """Evaluate multiple traces"""
        success_count = 0
        for trace in traces:
            if self.evaluate_trace(trace.id):
                success_count += 1
        
        print(f"📈 Successfully evaluated {success_count}/{len(traces)} traces")
        return success_count
    
    # STEP 4: Dataset evaluation
    def evaluate_dataset(self, dataset_name: str) -> bool:
        """Evaluate all items in a dataset"""
        try:
            # Get dataset
            dataset = self.langfuse.get_dataset(dataset_name)
            if not dataset:
                print(f"❌ Dataset not found: {dataset_name}")
                return False
            
            print(f"📊 Evaluating dataset: {dataset_name}")
            success_count = 0
            
            # Evaluate each dataset item
            for item in dataset.items:
                try:
                    # Apply input_length_evaluator to dataset item
                    evaluation = self.input_length_evaluator(item.input)
                    
                    # If there's a linked trace, add score to it
                    if hasattr(item, 'source_trace_id') and item.source_trace_id:
                        self.langfuse.create_score(
                            name=evaluation["name"],
                            value=evaluation["value"],
                            trace_id=item.source_trace_id,
                            comment=f"Dataset evaluation: {evaluation['comment']}"
                        )
                        success_count += 1
                        print(f"✅ Evaluated dataset item {item.id}")
                    else:
                        print(f"⚠️  Dataset item {item.id} has no linked trace")
                        
                except Exception as e:
                    print(f"❌ Error evaluating dataset item {item.id}: {e}")
            
            print(f"📈 Successfully evaluated {success_count} dataset items")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error evaluating dataset {dataset_name}: {e}")
            return False
    
    # STEP 5: Multiple evaluators
    def latency_score_evaluator(self, trace: Any) -> Dict[str, Any]:
        """Evaluator based on trace latency (lower latency = higher score)"""
        try:
            # Get latency from trace (in milliseconds, convert to seconds)
            latency_ms = getattr(trace, 'latency', 0) or 0
            latency_sec = latency_ms / 1000.0
            
            # Score based on latency ranges
            if latency_sec <= 10:
                score = 1.0
                comment = "Excellent latency"
            elif latency_sec <= 30:
                score = 0.8
                comment = "Good latency"
            elif latency_sec <= 60:
                score = 0.6
                comment = "Fair latency"
            elif latency_sec <= 120:
                score = 0.4
                comment = "Poor latency"
            elif latency_sec <= 200:
                score = 0.3
                comment = "Very poor latency"
            else:
                score = 0.2
                comment = "Critical latency"
            
            return {
                "name": "latency_score",
                "value": score,
                "comment": f"{comment} ({latency_sec:.2f}s)"
            }
        except Exception as e:
            return {"name": "latency_score", "value": 0.5, "comment": f"Error getting latency: {e}"}

    def input_token_count_evaluator(self, trace: Any) -> Dict[str, Any]:
        """Evaluator using input token count as direct score"""
        try:
            input_tokens = 0
            
            # Check observations for token usage
            if hasattr(trace, 'observations') and trace.observations:
                for obs in trace.observations:
                    if hasattr(obs, 'usage') and obs.usage:
                        input_tokens += getattr(obs.usage, 'input', 0) or 0
            
            # Use token count directly as score
            return {
                "name": "input_token_count",
                "value": input_tokens,
                "comment": f"Input tokens: {input_tokens}"
            }
        except Exception as e:
            return {"name": "input_token_count", "value": 0, "comment": f"Error getting input tokens: {e}"}

    def total_cost_evaluator(self, trace: Any) -> Dict[str, Any]:
        """Evaluator using total cost as direct score"""
        try:
            total_cost = 0.0
            
            # Check observations for cost
            if hasattr(trace, 'observations') and trace.observations:
                for obs in trace.observations:
                    if hasattr(obs, 'calculated_total_cost') and obs.calculated_total_cost:
                        total_cost += obs.calculated_total_cost
            
            # Use cost directly as score
            score = min(total_cost, 1.0) if total_cost > 0 else 0.0
            
            return {
                "name": "total_cost",
                "value": score,
                "comment": f"Total cost: ${total_cost:.6f}"
            }
        except Exception as e:
            return {"name": "total_cost", "value": 0.0, "comment": f"Error getting total cost: {e}"}



    def observation_count_score_evaluator(self, trace: Any) -> Dict[str, Any]:
        """Evaluator based on observation levels count (fewer levels = higher score)"""
        try:
            # Count observations in the trace
            obs_count = len(trace.observations) if hasattr(trace, 'observations') and trace.observations else 0
            
            # Score inversely based on observation count
            if obs_count <= 10:
                score = 1.0
                comment = "Excellent - very few observations"
            elif obs_count <= 20:
                score = 0.8
                comment = "Good - moderate observations"
            elif obs_count <= 40:
                score = 0.6
                comment = "Fair - many observations"
            elif obs_count <= 60:
                score = 0.4
                comment = "Poor - too many observations"
            elif obs_count <= 90:
                score = 0.2
                comment = "Very poor - excessive observations"
            else:
                score = 0.1
                comment = "Critical - way too many observations"
            
            return {
                "name": "observation_count_score",
                "value": score,
                "comment": f"{comment} ({obs_count} observations)"
            }
        except Exception as e:
            return {
                "name": "observation_count_score", 
                "value": 0.5,
                "comment": f"Error counting observations: {e}"
            }


    



def main():
    """Main function to demonstrate the evaluator"""
    parser = argparse.ArgumentParser(description="Evaluate Sherlock traces")
    parser.add_argument("--session", required=True, help="Session ID to evaluate traces for")
    args = parser.parse_args()
    
    print("🔍 Starting Sherlock Evaluator")
    
    evaluator = SherlockEvaluator()
    
    # STEP 1: Fetch traces
    print("\n📋 STEP 1: Fetching existing traces")
    
    print(f"🎯 Fetching traces for session: {args.session}")
    recent_traces = evaluator.fetch_traces_by_session(args.session, limit=5)
    
    if recent_traces:
        print(f"Found {len(recent_traces)} traces")
        
        # STEP 2: Evaluate first trace
        print(f"\n📋 STEP 2: Multi-metric evaluation (4 metrics: observation_count_score + latency_score + input_token_count + total_cost)")
        
        first_trace = recent_traces[0]
        success = evaluator.evaluate_trace(first_trace.id)
        
        if success:
            print("✅ Multi-metric trace evaluation completed")
        
        print("\n📋 STEP 3: Check Langfuse UI to verify the evaluation scores were added")
        
        # STEP 5: Multiple evaluators on second trace if available
        if len(recent_traces) > 1:
            print("\n📋 STEP 5: Additional trace evaluation")
            second_trace = recent_traces[1]
            evaluator.evaluate_trace(second_trace.id)
    
    else:
        print("⚠️  No traces found for the specified session. Please ensure the session ID exists in your Langfuse project.")
    
    print("\n🎉 Sherlock Evaluator completed!")


if __name__ == "__main__":
    main()
