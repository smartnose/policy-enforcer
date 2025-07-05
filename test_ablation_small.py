#!/usr/bin/env python3
"""
Small subset test of the ablation study - just a few configurations.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from quantitative_ablation_study import run_experiment_suite, analyze_results, plot_results, save_results, create_summary_table

def run_small_test():
    """Run a small subset of the experiment for testing."""
    
    print("🧪 Small Ablation Study Test")
    print("=" * 40)
    
    # Temporarily modify the experiment parameters for a quick test
    import quantitative_ablation_study as qs
    
    # Backup original parameters
    original_code = """
    models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    temperatures = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    rule_modes = [True, False]  # With rules, without rules
    runs_per_config = 20
    """
    
    # Modify for quick test (monkey patch the function)
    def quick_experiment_suite():
        # Quick test parameters
        models = ["gemini-1.5-flash"]  # Just one model
        temperatures = [0.0, 0.4, 0.8]  # Just three temperatures
        rule_modes = [True, False]  # Both rule modes
        runs_per_config = 3  # Just 3 runs per config
        
        print("🔬 Starting Small Ablation Study")
        print("=" * 60)
        print(f"Models: {models}")
        print(f"Temperatures: {temperatures}")
        print(f"Rule modes: With rules, Without rules")
        print(f"Runs per configuration: {runs_per_config}")
        print(f"Total experiments: {len(models) * len(temperatures) * len(rule_modes) * runs_per_config}")
        print()
        
        # Use the same logic as the main function but with smaller parameters
        from quantitative_ablation_study import setup_deterministic_environment, run_single_experiment, ExperimentConfig
        import time
        import numpy as np
        
        # Setup deterministic environment
        original_choice = setup_deterministic_environment()
        
        results = []
        total_experiments = len(models) * len(temperatures) * len(rule_modes) * runs_per_config
        experiment_count = 0
        
        try:
            for model in models:
                for temperature in temperatures:
                    for include_rules in rule_modes:
                        print(f"📊 Running: {model}, temp={temperature}, rules={'ON' if include_rules else 'OFF'}")
                        
                        for run_num in range(runs_per_config):
                            experiment_count += 1
                            config = ExperimentConfig(
                                model_name=model,
                                temperature=temperature,
                                include_rules=include_rules,
                                run_number=run_num + 1
                            )
                            
                            result = run_single_experiment(config)
                            results.append(result)
                            
                            # Progress indicator
                            progress = (experiment_count / total_experiments) * 100
                            print(f"   Progress: {experiment_count}/{total_experiments} ({progress:.1f}%)")
                            
                            # Brief pause to avoid API rate limits
                            time.sleep(0.5)
                        
                        # Show summary for this configuration
                        config_results = [r for r in results if 
                                        r.config.model_name == model and 
                                        r.config.temperature == temperature and 
                                        r.config.include_rules == include_rules]
                        
                        violations = sum(r.policy_violations for r in config_results)
                        successes = sum(1 for r in config_results if r.success)
                        avg_time = np.mean([r.execution_time for r in config_results])
                        
                        print(f"   ✅ Total violations: {violations}, Success rate: {successes}/{runs_per_config}, Avg time: {avg_time:.2f}s")
        
        finally:
            # Restore original random.choice
            import random
            random.choice = original_choice
        
        return results
    
    # Run the experiment
    results = quick_experiment_suite()
    
    # Analyze results
    df, summary = analyze_results(results)
    
    # Print summary
    create_summary_table(df)
    
    # Save results
    results_file = save_results(results, "small_test_results.json")
    
    # Plot results  
    plot_results(df, "small_test_chart.png")
    
    print(f"\n✅ Small test completed!")
    print(f"📁 Results: {results_file}")
    
    return results, df

if __name__ == "__main__":
    run_small_test()
