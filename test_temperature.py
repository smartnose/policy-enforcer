#!/usr/bin/env python3
"""
Temperature sensitivity test to validate the violation pattern.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def temperature_sensitivity_test():
    """Test if the violation pattern holds across different temperatures."""
    from quantitative_ablation_study import setup_deterministic_environment, run_single_experiment, ExperimentConfig
    from policy_enforcer.state import reset_state
    import numpy as np
    
    print("🌡️ TEMPERATURE SENSITIVITY TEST")
    print("=" * 40)
    
    # Setup deterministic environment
    original_choice = setup_deterministic_environment()
    
    try:
        temperatures = [0.0, 0.3, 0.7]
        trials_per_temp = 5
        
        results = {}
        
        for temp in temperatures:
            print(f"\n🌡️ Testing Temperature: {temp}")
            print("-" * 30)
            
            with_rules_violations = []
            without_rules_violations = []
            
            for trial in range(trials_per_temp):
                # With rules
                reset_state()
                config_with = ExperimentConfig("gemini-1.5-flash", temp, True, trial)
                result_with = run_single_experiment(config_with)
                with_rules_violations.append(result_with.policy_violations)
                
                # Without rules
                reset_state()
                config_without = ExperimentConfig("gemini-1.5-flash", temp, False, trial)
                result_without = run_single_experiment(config_without)
                without_rules_violations.append(result_without.policy_violations)
                
                print(f"  Trial {trial+1}: With={result_with.policy_violations}, Without={result_without.policy_violations}")
            
            # Calculate statistics
            with_mean = np.mean(with_rules_violations)
            without_mean = np.mean(without_rules_violations)
            difference = without_mean - with_mean
            
            results[temp] = {
                'with_rules_mean': with_mean,
                'without_rules_mean': without_mean,
                'difference': difference,
                'with_rules_violations': with_rules_violations,
                'without_rules_violations': without_rules_violations
            }
            
            print(f"  📊 With rules: {with_mean:.2f} avg violations")
            print(f"  📊 Without rules: {without_mean:.2f} avg violations")
            print(f"  📊 Difference: {difference:.2f}")
        
        # Summary analysis
        print(f"\n📈 TEMPERATURE ANALYSIS SUMMARY:")
        print("=" * 40)
        
        for temp in temperatures:
            data = results[temp]
            print(f"T={temp}: Diff={data['difference']:.2f} (Without - With)")
        
        # Check if pattern is consistent
        all_diffs = [results[temp]['difference'] for temp in temperatures]
        consistent_pattern = all(diff < 0 for diff in all_diffs)  # Without rules has fewer violations
        
        print(f"\n🎯 PATTERN CONSISTENCY:")
        if consistent_pattern:
            print("✅ Pattern CONSISTENT: Without rules always has fewer violations")
            print("   This suggests the effect is not due to randomness")
        else:
            print("❌ Pattern INCONSISTENT: Effect varies with temperature")
            print("   This suggests randomness or temperature-dependent behavior")
        
        # Temperature sensitivity
        diff_range = max(all_diffs) - min(all_diffs)
        print(f"📊 Temperature sensitivity: {diff_range:.2f} range in differences")
        
        if diff_range < 0.3:
            print("   Low temperature sensitivity - pattern is robust")
        else:
            print("   High temperature sensitivity - temperature affects results")
        
        return results
        
    finally:
        # Restore original
        import random
        random.choice = original_choice

if __name__ == "__main__":
    temperature_sensitivity_test()
