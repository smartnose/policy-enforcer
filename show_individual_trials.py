#!/usr/bin/env python3
"""
Show individual trial results to demonstrate the clear pattern.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def show_trial_by_trial(json_file: str, max_trials: int = 10):
    """Show individual trial results for the first few trials of each condition."""
    
    with open(json_file, 'r') as f:
        raw_results = json.load(f)
    
    # Separate results by rule condition
    with_rules = []
    without_rules = []
    
    for result in raw_results:
        config = result['config']
        trial_data = {
            'trial': config['run_number'],
            'violations': result['policy_violations'],
            'tool_calls': result['total_tool_calls'],
            'model': config['model_name'],
            'temp': config['temperature']
        }
        
        if config['include_rules']:
            with_rules.append(trial_data)
        else:
            without_rules.append(trial_data)
    
    print("🔬 TRIAL-BY-TRIAL COMPARISON (First 10 trials each)")
    print("=" * 60)
    
    print(f"\n{'WITH RULES IN PROMPT:':<25} {'WITHOUT RULES IN PROMPT:'}")
    print(f"{'Trial':<5} {'Violations':<10} {'Tools':<8} {'Trial':<5} {'Violations':<10} {'Tools'}")
    print("-" * 60)
    
    for i in range(min(max_trials, len(with_rules), len(without_rules))):
        w = with_rules[i]
        wo = without_rules[i]
        print(f"{w['trial']:<5} {w['violations']:<10} {w['tool_calls']:<8} "
              f"{wo['trial']:<5} {wo['violations']:<10} {wo['tool_calls']}")
    
    # Calculate and show summary
    with_violations = [t['violations'] for t in with_rules[:max_trials]]
    without_violations = [t['violations'] for t in without_rules[:max_trials]]
    
    print("\n" + "=" * 60)
    print(f"SUMMARY (first {max_trials} trials):")
    print(f"With rules:    {sum(with_violations)}/{len(with_violations)} total violations ({sum(with_violations)/len(with_violations):.1f} avg)")
    print(f"Without rules: {sum(without_violations)}/{len(without_violations)} total violations ({sum(without_violations)/len(without_violations):.1f} avg)")
    
    # Show the pattern across different models/temperatures
    print(f"\n🌡️ PATTERN ACROSS CONDITIONS:")
    print("-" * 40)
    
    df = pd.DataFrame(raw_results)
    
    for _, result in df.head(20).iterrows():  # Show first 20 results
        config = result['config']
        rules_status = "WITH" if config['include_rules'] else "WITHOUT"
        print(f"{config['model_name']:<15} T={config['temperature']:<3} {rules_status:<7} rules → {result['policy_violations']} violations")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        result_files = list(Path('.').glob('ablation_study_results_*.json'))
        if result_files:
            json_file = str(sorted(result_files)[-1])
            print(f"🔍 Using most recent results file: {json_file}")
        else:
            print("❌ No results file found.")
            sys.exit(1)
    else:
        json_file = sys.argv[1]
    
    show_trial_by_trial(json_file)
