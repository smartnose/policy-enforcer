#!/usr/bin/env python3
"""
Multi-trial test to check for statistical differences in policy violation rates.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def multi_trial_test(num_trials=10):
    """Run multiple trials to see if differences emerge statistically."""
    from quantitative_ablation_study import setup_deterministic_environment, run_single_experiment, ExperimentConfig
    from policy_enforcer.state import reset_state
    import numpy as np
    
    print(f"🔬 Multi-Trial Ablation Test ({num_trials} trials each)")
    print("=" * 50)
    
    # Setup deterministic environment
    original_choice = setup_deterministic_environment()
    
    try:
        with_rules_violations = []
        without_rules_violations = []
        
        # Run multiple trials for each configuration
        for trial in range(num_trials):
            print(f"\n📊 Trial {trial + 1}/{num_trials}")
            
            # Test with rules
            reset_state()
            config_with = ExperimentConfig("gemini-1.5-flash", 0.1, True, trial)
            result_with = run_single_experiment(config_with)
            with_rules_violations.append(result_with.policy_violations)
            print(f"   With rules:    {result_with.policy_violations} violations")
            
            # Test without rules
            reset_state()
            config_without = ExperimentConfig("gemini-1.5-flash", 0.1, False, trial)
            result_without = run_single_experiment(config_without)
            without_rules_violations.append(result_without.policy_violations)
            print(f"   Without rules: {result_without.policy_violations} violations")
        
        # Statistical analysis
        print(f"\n📈 STATISTICAL ANALYSIS:")
        print("=" * 30)
        
        with_rules_array = np.array(with_rules_violations)
        without_rules_array = np.array(without_rules_violations)
        
        print(f"WITH RULES:")
        print(f"  Mean: {with_rules_array.mean():.2f}")
        print(f"  Std:  {with_rules_array.std():.2f}")
        print(f"  Min:  {with_rules_array.min()}")
        print(f"  Max:  {with_rules_array.max()}")
        print(f"  Distribution: {np.bincount(with_rules_array, minlength=3)}")
        
        print(f"\nWITHOUT RULES:")
        print(f"  Mean: {without_rules_array.mean():.2f}")
        print(f"  Std:  {without_rules_array.std():.2f}")
        print(f"  Min:  {without_rules_array.min()}")
        print(f"  Max:  {without_rules_array.max()}")
        print(f"  Distribution: {np.bincount(without_rules_array, minlength=3)}")
        
        # Difference analysis
        diff_mean = without_rules_array.mean() - with_rules_array.mean()
        print(f"\nDIFFERENCE ANALYSIS:")
        print(f"  Mean difference: {diff_mean:.2f}")
        print(f"  Effect size: {diff_mean / max(with_rules_array.std(), 0.1):.2f}")
        
        # Simple statistical test (paired t-test approximation)
        differences = without_rules_array - with_rules_array
        print(f"  Paired differences: {differences}")
        print(f"  Mean paired diff: {differences.mean():.2f}")
        print(f"  Std paired diff:  {differences.std():.2f}")
        
        # Count how many times without-rules had more violations
        more_violations = sum(1 for i in range(num_trials) if without_rules_violations[i] > with_rules_violations[i])
        equal_violations = sum(1 for i in range(num_trials) if without_rules_violations[i] == with_rules_violations[i])
        fewer_violations = sum(1 for i in range(num_trials) if without_rules_violations[i] < with_rules_violations[i])
        
        print(f"\nTRIAL OUTCOMES:")
        print(f"  Without rules had MORE violations:  {more_violations}/{num_trials} ({more_violations/num_trials*100:.1f}%)")
        print(f"  Without rules had EQUAL violations: {equal_violations}/{num_trials} ({equal_violations/num_trials*100:.1f}%)")
        print(f"  Without rules had FEWER violations: {fewer_violations}/{num_trials} ({fewer_violations/num_trials*100:.1f}%)")
        
        # Interpretation
        print(f"\n🎯 INTERPRETATION:")
        if diff_mean > 0.2:
            print("✅ Strong evidence that removing rules increases violations")
        elif diff_mean > 0.1:
            print("⚠️  Moderate evidence that removing rules increases violations")
        elif abs(diff_mean) < 0.1:
            print("❓ No clear difference - may need more trials or different scenario")
        else:
            print("❌ Unexpected: removing rules seems to decrease violations")
        
        return {
            'with_rules': with_rules_violations,
            'without_rules': without_rules_violations,
            'mean_difference': diff_mean,
            'more_violations_pct': more_violations/num_trials
        }
        
    finally:
        # Restore original
        import random
        random.choice = original_choice

if __name__ == "__main__":
    # Run with 10 trials first, then optionally more
    results = multi_trial_test(10)
    
    print(f"\n🤔 Want to run more trials? The current results show:")
    print(f"   Mean difference: {results['mean_difference']:.2f}")
    print(f"   More violations without rules: {results['more_violations_pct']*100:.1f}%")
