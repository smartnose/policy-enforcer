#!/usr/bin/env python3
"""
Visualization script for saved ablation study results.
This allows modifying graphs without re-running the entire experiment.
"""

import json
import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any

def load_experiment_results(json_file: str) -> pd.DataFrame:
    """Load experiment results from JSON file and convert to DataFrame."""
    
    print(f"📁 Loading results from: {json_file}")
    
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
            'total_tool_calls': result['total_tool_calls'],
            'success': result['success'],
            'execution_time': result['execution_time'],
            'error_message': result.get('error_message', '')
        })
    
    df = pd.DataFrame(data)
    
    # Add rule mode label
    df['rule_mode'] = df['include_rules'].map({True: 'With Rules', False: 'Without Rules'})
    
    print(f"✅ Loaded {len(df)} experiment results")
    print(f"📊 Models: {sorted(df['model'].unique())}")
    print(f"🌡️  Temperatures: {sorted(df['temperature'].unique())}")
    print(f"📋 Rule modes: {sorted(df['rule_mode'].unique())}")
    
    return df

def create_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Create summary statistics from the detailed results."""
    
    summary = df.groupby(['model', 'temperature', 'rule_mode']).agg({
        'policy_violations': ['count', 'sum', 'mean', 'std'],
        'success': 'mean',
        'execution_time': 'mean',
        'total_tool_calls': 'mean'
    }).round(3)
    
    # Flatten column names
    summary.columns = ['_'.join(col).strip() for col in summary.columns]
    summary = summary.reset_index()
    
    return summary

def plot_main_results(df: pd.DataFrame, save_path: str = None):
    """Create the main clustered bar chart showing violations by temperature and model."""
    
    # Create summary for plotting
    plot_data = df.groupby(['model', 'temperature', 'rule_mode']).agg({
        'policy_violations': 'sum'
    }).reset_index()
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Create the main comparison plot
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Policy Enforcer Ablation Study: Rule Impact Analysis', fontsize=16, fontweight='bold')
    
    models = sorted(df['model'].unique())
    temperatures = sorted(df['temperature'].unique())
    
    # Define colors for models
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green
    model_colors = {model: colors[i % len(colors)] for i, model in enumerate(models)}
    
    # Plot 1: Total violations by temperature and model (with rules)
    ax1 = axes[0, 0]
    with_rules = plot_data[plot_data['rule_mode'] == 'With Rules']
    x = np.arange(len(temperatures))
    width = 0.25
    
    for i, model in enumerate(models):
        model_data = with_rules[with_rules['model'] == model]
        violations = [model_data[model_data['temperature'] == temp]['policy_violations'].values[0] 
                     if len(model_data[model_data['temperature'] == temp]) > 0 else 0 
                     for temp in temperatures]
        
        ax1.bar(x + i * width, violations, width, label=model, color=model_colors[model], alpha=0.8)
    
    ax1.set_title('Policy Violations - With Rules in Prompt', fontweight='bold')
    ax1.set_xlabel('Temperature')
    ax1.set_ylabel('Total Policy Violations (20 trials)')
    ax1.set_xticks(x + width)
    ax1.set_xticklabels([f'{t:.1f}' for t in temperatures])
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Total violations by temperature and model (without rules)
    ax2 = axes[0, 1]
    without_rules = plot_data[plot_data['rule_mode'] == 'Without Rules']
    
    for i, model in enumerate(models):
        model_data = without_rules[without_rules['model'] == model]
        violations = [model_data[model_data['temperature'] == temp]['policy_violations'].values[0] 
                     if len(model_data[model_data['temperature'] == temp]) > 0 else 0 
                     for temp in temperatures]
        
        ax2.bar(x + i * width, violations, width, label=model, color=model_colors[model], alpha=0.8)
    
    ax2.set_title('Policy Violations - Without Rules in Prompt', fontweight='bold')
    ax2.set_xlabel('Temperature')
    ax2.set_ylabel('Total Policy Violations (20 trials)')
    ax2.set_xticks(x + width)
    ax2.set_xticklabels([f'{t:.1f}' for t in temperatures])
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Difference (Without Rules - With Rules)
    ax3 = axes[1, 0]
    diff_data = []
    temp_labels = []
    
    for model in models:
        for temp in temperatures:
            with_val = with_rules[(with_rules['model'] == model) & (with_rules['temperature'] == temp)]['policy_violations'].values
            without_val = without_rules[(without_rules['model'] == model) & (without_rules['temperature'] == temp)]['policy_violations'].values
            
            if len(with_val) > 0 and len(without_val) > 0:
                diff = without_val[0] - with_val[0]
                diff_data.append(diff)
                temp_labels.append(f'{model}\nT={temp}')
    
    colors_diff = ['red' if x > 0 else 'green' for x in diff_data]
    bars = ax3.bar(range(len(diff_data)), diff_data, color=colors_diff, alpha=0.7)
    ax3.set_title('Violation Increase without Rules', fontweight='bold')
    ax3.set_xlabel('Model and Temperature')
    ax3.set_ylabel('Violation Difference\n(Without Rules - With Rules)')
    ax3.set_xticks(range(len(temp_labels)))
    ax3.set_xticklabels(temp_labels, rotation=45, ha='right')
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Success rate comparison
    ax4 = axes[1, 1]
    success_data = df.groupby(['model', 'temperature', 'rule_mode'])['success'].mean().reset_index()
    
    with_success = success_data[success_data['rule_mode'] == 'With Rules']
    without_success = success_data[success_data['rule_mode'] == 'Without Rules']
    
    x = np.arange(len(temperatures))
    width = 0.35
    
    # Average across models for simplicity
    with_avg = with_success.groupby('temperature')['success'].mean()
    without_avg = without_success.groupby('temperature')['success'].mean()
    
    ax4.bar(x - width/2, with_avg, width, label='With Rules', alpha=0.8)
    ax4.bar(x + width/2, without_avg, width, label='Without Rules', alpha=0.8)
    
    ax4.set_title('Success Rate by Temperature', fontweight='bold')
    ax4.set_xlabel('Temperature')
    ax4.set_ylabel('Success Rate')
    ax4.set_xticks(x)
    ax4.set_xticklabels([f'{t:.1f}' for t in temperatures])
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, 1.1)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Main plot saved to: {save_path}")
    
    plt.show()

def plot_detailed_analysis(df: pd.DataFrame, save_path: str = None):
    """Create detailed analysis plots."""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Detailed Ablation Study Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Distribution of violations
    ax1 = axes[0, 0]
    for rule_mode in ['With Rules', 'Without Rules']:
        data = df[df['rule_mode'] == rule_mode]['policy_violations']
        ax1.hist(data, bins=range(0, max(df['policy_violations'])+2), alpha=0.7, label=rule_mode)
    ax1.set_title('Distribution of Policy Violations')
    ax1.set_xlabel('Number of Violations')
    ax1.set_ylabel('Frequency')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Violations by model
    ax2 = axes[0, 1]
    model_summary = df.groupby(['model', 'rule_mode'])['policy_violations'].sum().reset_index()
    pivot_model = model_summary.pivot(index='model', columns='rule_mode', values='policy_violations')
    pivot_model.plot(kind='bar', ax=ax2, alpha=0.8)
    ax2.set_title('Total Violations by Model')
    ax2.set_xlabel('Model')
    ax2.set_ylabel('Total Violations')
    ax2.legend()
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Execution time by rule mode
    ax3 = axes[0, 2]
    df.boxplot(column='execution_time', by='rule_mode', ax=ax3)
    ax3.set_title('Execution Time by Rule Mode')
    ax3.set_xlabel('Rule Mode')
    ax3.set_ylabel('Execution Time (seconds)')
    
    # Plot 4: Tool calls by rule mode
    ax4 = axes[1, 0]
    df.boxplot(column='total_tool_calls', by='rule_mode', ax=ax4)
    ax4.set_title('Tool Calls by Rule Mode')
    ax4.set_xlabel('Rule Mode')
    ax4.set_ylabel('Number of Tool Calls')
    
    # Plot 5: Temperature sensitivity
    ax5 = axes[1, 1]
    temp_summary = df.groupby(['temperature', 'rule_mode'])['policy_violations'].mean().reset_index()
    for rule_mode in ['With Rules', 'Without Rules']:
        data = temp_summary[temp_summary['rule_mode'] == rule_mode]
        ax5.plot(data['temperature'], data['policy_violations'], marker='o', label=rule_mode, linewidth=2)
    ax5.set_title('Temperature Sensitivity')
    ax5.set_xlabel('Temperature')
    ax5.set_ylabel('Average Violations per Trial')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # Plot 6: Success rate heatmap
    ax6 = axes[1, 2]
    success_pivot = df.groupby(['model', 'rule_mode'])['success'].mean().reset_index()
    success_matrix = success_pivot.pivot(index='model', columns='rule_mode', values='success')
    sns.heatmap(success_matrix, annot=True, fmt='.3f', ax=ax6, cmap='RdYlGn', vmin=0, vmax=1)
    ax6.set_title('Success Rate Heatmap')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"📊 Detailed analysis saved to: {save_path}")
    
    plt.show()

def print_summary_statistics(df: pd.DataFrame):
    """Print comprehensive summary statistics."""
    
    print("\n" + "="*60)
    print("📈 COMPREHENSIVE ABLATION STUDY RESULTS")
    print("="*60)
    
    # Overall statistics
    total_experiments = len(df)
    successful_experiments = len(df[df['success'] == True])
    
    print(f"📊 Total Experiments: {total_experiments}")
    print(f"✅ Successful Experiments: {successful_experiments} ({successful_experiments/total_experiments*100:.1f}%)")
    
    # Key findings by rule mode
    for rule_mode in ['With Rules', 'Without Rules']:
        data = df[df['rule_mode'] == rule_mode]
        total_violations = data['policy_violations'].sum()
        avg_violations = data['policy_violations'].mean()
        std_violations = data['policy_violations'].std()
        
        print(f"\n🎯 {rule_mode.upper()}:")
        print(f"   Total violations: {total_violations}")
        print(f"   Average per trial: {avg_violations:.3f} ± {std_violations:.3f}")
        print(f"   Success rate: {data['success'].mean()*100:.1f}%")
        print(f"   Avg execution time: {data['execution_time'].mean():.2f}s")
        print(f"   Avg tool calls: {data['total_tool_calls'].mean():.1f}")
    
    # Model comparison
    print(f"\n🤖 MODEL COMPARISON:")
    model_summary = df.groupby(['model', 'rule_mode']).agg({
        'policy_violations': ['sum', 'mean'],
        'success': 'mean'
    }).round(3)
    
    for model in df['model'].unique():
        with_rules = df[(df['model'] == model) & (df['rule_mode'] == 'With Rules')]['policy_violations'].sum()
        without_rules = df[(df['model'] == model) & (df['rule_mode'] == 'Without Rules')]['policy_violations'].sum()
        diff = without_rules - with_rules
        print(f"   {model}: +{diff} violations without rules ({with_rules} → {without_rules})")
    
    # Temperature analysis
    print(f"\n🌡️  TEMPERATURE ANALYSIS:")
    temp_analysis = df.groupby(['temperature', 'rule_mode'])['policy_violations'].sum().reset_index()
    for temp in sorted(df['temperature'].unique()):
        with_rules = temp_analysis[(temp_analysis['temperature'] == temp) & (temp_analysis['rule_mode'] == 'With Rules')]['policy_violations'].values[0]
        without_rules = temp_analysis[(temp_analysis['temperature'] == temp) & (temp_analysis['rule_mode'] == 'Without Rules')]['policy_violations'].values[0]
        diff = without_rules - with_rules
        print(f"   T={temp}: +{diff} violations without rules ({with_rules} → {without_rules})")

def main():
    """Main function to load and visualize results."""
    
    print("🎨 Ablation Study Visualization Tool")
    print("=" * 40)
    
    # Look for the most recent results file
    results_files = list(Path(".").glob("ablation_study_results_*.json"))
    
    if not results_files:
        print("❌ No results files found. Please run the experiment first.")
        print("   Expected format: ablation_study_results_YYYYMMDD_HHMMSS.json")
        return
    
    # Use the most recent file
    latest_file = max(results_files, key=lambda x: x.stat().st_mtime)
    
    # Load results
    df = load_experiment_results(str(latest_file))
    
    # Print summary statistics
    print_summary_statistics(df)
    
    # Create visualizations
    timestamp = latest_file.stem.split('_')[-2:]  # Extract timestamp
    timestamp_str = '_'.join(timestamp)
    
    print(f"\n🎨 Creating visualizations...")
    plot_main_results(df, f"ablation_main_results_{timestamp_str}.png")
    plot_detailed_analysis(df, f"ablation_detailed_analysis_{timestamp_str}.png")
    
    # Save summary statistics
    summary_df = create_summary_statistics(df)
    summary_file = f"ablation_summary_{timestamp_str}.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"📊 Summary statistics saved to: {summary_file}")

if __name__ == "__main__":
    main()
