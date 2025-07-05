#!/usr/bin/env python3
"""
Simple test run of the ablation study with minimal configurations.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def simple_test():
    """Run a very simple test of the ablation functionality."""
    from quantitative_ablation_study import setup_deterministic_environment, run_single_experiment, ExperimentConfig, count_policy_violations
    from policy_enforcer.state import reset_state
    
    print("🔬 Simple Ablation Test")
    print("=" * 30)
    
    # Setup deterministic environment
    original_choice = setup_deterministic_environment()
    
    try:
        results = []
        
        # Test configurations: just 2 configs, 1 run each
        configs = [
            ExperimentConfig("gemini-1.5-flash", 0.0, True, 1),   # With rules
            ExperimentConfig("gemini-1.5-flash", 0.0, False, 1),  # Without rules
        ]
        
        for config in configs:
            print(f"\n📊 Testing: rules={'ON' if config.include_rules else 'OFF'}")
            reset_state()
            
            result = run_single_experiment(config)
            results.append(result)
            
            print(f"   ✅ Success: {result.success}")
            print(f"   🚨 Violations: {result.policy_violations}")
            if not result.success:
                print(f"   ❌ Error: {result.error_message}")
        
        # Show comparison
        print(f"\n📈 COMPARISON:")
        with_rules = results[0]
        without_rules = results[1]
        
        print(f"With rules:    {with_rules.policy_violations} violations")
        print(f"Without rules: {without_rules.policy_violations} violations")
        print(f"Difference:    {without_rules.policy_violations - with_rules.policy_violations}")
        
        return results
        
    finally:
        # Restore original
        import random
        random.choice = original_choice

if __name__ == "__main__":
    simple_test()
