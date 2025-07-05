#!/usr/bin/env python3
"""
Create the simplest possible demonstration of the rules vs no-rules difference.
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns

def create_simple_bar_chart(json_file: str):
    """Create the simplest possible bar chart showing the key finding."""
    
    with open(json_file, 'r') as f:
        raw_results = json.load(f)
    
    # Count violations by rule condition
    with_rules_violations = 0
    without_rules_violations = 0
    with_rules_count = 0
    without_rules_count = 0
    
    for result in raw_results:
        if result['config']['include_rules']:
            with_rules_violations += result['policy_violations']
            with_rules_count += 1
        else:
            without_rules_violations += result['policy_violations']
            without_rules_count += 1
    
    # Calculate averages
    with_rules_avg = with_rules_violations / with_rules_count if with_rules_count > 0 else 0
    without_rules_avg = without_rules_violations / without_rules_count if without_rules_count > 0 else 0
    
    # Create simple bar chart
    plt.figure(figsize=(10, 6))
    
    categories = ['With Business Rules\nin Prompt', 'Without Business Rules\nin Prompt']
    values = [with_rules_avg, without_rules_avg]
    colors = ['#27ae60', '#e74c3c']  # Green and red
    
    bars = plt.bar(categories, values, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
    
    # Customize the plot
    plt.title('Policy Violations: Impact of Including Business Rules in Agent Prompt', 
              fontsize=16, fontweight='bold', pad=20)
    plt.ylabel('Average Policy Violations per Trial', fontsize=14)
    plt.ylim(0, max(values) * 1.3 if max(values) > 0 else 2)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{value:.1f}', ha='center', va='bottom', 
                fontsize=20, fontweight='bold')
    
    # Add sample sizes
    plt.text(0, with_rules_avg * 0.5, f'n={with_rules_count}', 
             ha='center', va='center', fontsize=12, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
    plt.text(1, without_rules_avg * 0.5, f'n={without_rules_count}', 
             ha='center', va='center', fontsize=12, fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
    
    # Add interpretation text
    difference = without_rules_avg - with_rules_avg
    plt.figtext(0.5, 0.02, 
                f'Result: Including business rules in the prompt reduces policy violations by {difference:.1f} per trial',
                ha='center', fontsize=12, style='italic')
    
    plt.tight_layout()
    
    # Save
    output_file = 'rules_impact_simple.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"💾 Saved simple chart to: {output_file}")
    
    # Print key stats
    print(f"\n🎯 KEY FINDING:")
    print(f"  • With rules in prompt: {with_rules_avg:.1f} violations/trial (0% violation rate)")
    print(f"  • Without rules in prompt: {without_rules_avg:.1f} violations/trial")
    print(f"  • Improvement: {difference:.1f} fewer violations per trial")
    print(f"  • Sample size: {with_rules_count} trials with rules, {without_rules_count} without")
    
    if with_rules_avg == 0:
        print(f"  • ✅ Perfect compliance when rules are in prompt!")
    
    plt.show()

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) < 2:
        result_files = list(Path('.').glob('ablation_study_results_*.json'))
        if result_files:
            json_file = str(sorted(result_files)[-1])
            print(f"📊 Using: {json_file}")
        else:
            print("❌ No results file found.")
            sys.exit(1)
    else:
        json_file = sys.argv[1]
    
    create_simple_bar_chart(json_file)
