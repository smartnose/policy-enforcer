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
        
        # Save results for visualization
        from datetime import datetime
        import json
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_data = []
        
        for result in results:
            results_data.append({
                'config': result.config._asdict(),
                'policy_violations': result.policy_violations,
                'total_tool_calls': result.total_tool_calls,
                'success': result.success,
                'error_message': result.error_message,
                'execution_time': result.execution_time
            })
        
        output_file = f"simple_test_results_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"💾 Results saved to: {output_file}")
        print(f"📊 Create visualization with: python create_simple_chart.py {output_file}")
        
        return results
        
    finally:
        # Restore original
        import random
        random.choice = original_choice

if __name__ == "__main__":
    simple_test()
