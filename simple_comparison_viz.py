#!/usr/bin/env python3
"""
Simple comparison visualization for the rules vs no-rules experiment.
Shows the clear difference in policy violations.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def create_simple_comparison(json_file: str):
    """Create a simple, clear comparison visualization."""
    
    print(f"📊 Creating simple comparison from: {json_file}")
    
    # Load data
    with open(json_file, 'r') as f:
        raw_results = json.load(f)
    
    # Convert to DataFrame
    data = []
    for result in raw_results:
        config = result['config']
        data.append({
            'model': config['model_name'],
            'temperature': config['temperature'],
            'include_rules': config['include_rules'],
            'trial_id': config['run_number'],
            'policy_violations': result['policy_violations'],
            'success': result['success']
        })
    
    df = pd.DataFrame(data)
    df['rule_mode'] = df['include_rules'].map({True: 'With Rules', False: 'Without Rules'})
    
    # Calculate summary statistics
    summary = df.groupby('rule_mode')['policy_violations'].agg([
        'count', 'sum', 'mean', 'std'
    ]).round(2)
    
    print("\n📈 SUMMARY STATISTICS:")
    print(summary)
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. Simple bar chart of average violations
    rule_means = df.groupby('rule_mode')['policy_violations'].mean()
    rule_stds = df.groupby('rule_mode')['policy_violations'].std()
    
    colors = ['#2ecc71', '#e74c3c']  # Green for with rules, red for without
    bars = ax1.bar(rule_means.index, rule_means.values, 
                   yerr=rule_stds.values, capsize=5, 
                   color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    ax1.set_title('Average Policy Violations\nWith vs Without Rules in Prompt', 
                  fontsize=14, fontweight='bold')
    ax1.set_ylabel('Average Policy Violations', fontsize=12)
    ax1.set_ylim(0, max(rule_means.values) * 1.3)
    
    # Add value labels on bars
    for bar, mean_val, std_val in zip(bars, rule_means.values, rule_stds.values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + std_val + 0.05,
                f'{mean_val:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Distribution plot
    sns.boxplot(data=df, x='rule_mode', y='policy_violations', ax=ax2, palette=colors)
    ax2.set_title('Distribution of Policy Violations\nAcross All Trials', 
                  fontsize=14, fontweight='bold')
    ax2.set_ylabel('Policy Violations per Trial', fontsize=12)
    ax2.set_xlabel('')
    
    # Add sample size annotations
    for i, rule_mode in enumerate(['With Rules', 'Without Rules']):
        n_trials = len(df[df['rule_mode'] == rule_mode])
        ax2.text(i, ax2.get_ylim()[1] * 0.9, f'n={n_trials}', 
                ha='center', va='center', fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = Path(json_file).stem.split('_')[-2:]  # Extract timestamp
    output_file = f"simple_comparison_{'_'.join(timestamp)}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"💾 Saved plot to: {output_file}")
    
    # Show key insights
    print(f"\n🔍 KEY INSIGHTS:")
    with_rules_mean = rule_means['With Rules']
    without_rules_mean = rule_means['Without Rules']
    
    print(f"  • With rules in prompt: {with_rules_mean:.2f} violations on average")
    print(f"  • Without rules in prompt: {without_rules_mean:.2f} violations on average")
    print(f"  • Difference: {without_rules_mean - with_rules_mean:.2f} more violations without rules")
    
    if with_rules_mean == 0:
        print(f"  • Rules in prompt completely prevent policy violations!")
    
    plt.show()
    return df, summary

def create_success_rate_comparison(json_file: str):
    """Create a comparison of success rates and tool usage."""
    
    with open(json_file, 'r') as f:
        raw_results = json.load(f)
    
    data = []
    for result in raw_results:
        config = result['config']
        data.append({
            'rule_mode': 'With Rules' if config['include_rules'] else 'Without Rules',
            'policy_violations': result['policy_violations'],
            'total_tool_calls': result['total_tool_calls'],
            'success': result['success']
        })
    
    df = pd.DataFrame(data)
    
    # Create a simple summary table
    summary = df.groupby('rule_mode').agg({
        'policy_violations': ['mean', 'sum', 'count'],
        'total_tool_calls': 'mean',
        'success': 'mean'
    }).round(2)
    
    print("\n📋 DETAILED COMPARISON:")
    print(summary)
    
    return df

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        # Look for the most recent results file
        result_files = list(Path('.').glob('ablation_study_results_*.json'))
        if result_files:
            json_file = str(sorted(result_files)[-1])
            print(f"🔍 Using most recent results file: {json_file}")
        else:
            print("❌ No results file found. Please provide a JSON file path.")
            sys.exit(1)
    else:
        json_file = sys.argv[1]
    
    df, summary = create_simple_comparison(json_file)
    create_success_rate_comparison(json_file)
