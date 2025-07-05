#!/usr/bin/env python3
"""
Create a small test dataset to demonstrate visualization capabilities.
"""

import json
import os
import sys
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_dataset():
    """Create a small test dataset based on our multi-trial results."""
    from quantitative_ablation_study import ExperimentConfig, ExperimentResult
    from dataclasses import asdict
    
    print("🧪 Creating test dataset for visualization demo...")
    
    # Create synthetic results based on observed patterns
    results = []
    
    models = ["gemini-1.5-flash", "gemini-2.0-flash"]
    temperatures = [0.0, 0.2, 0.4, 0.6, 0.8]
    
    for model in models:
        for temp in temperatures:
            for include_rules in [True, False]:
                for trial in range(5):  # 5 trials each
                    
                    # Simulate violations based on observed patterns
                    if include_rules:
                        violations = 0  # With rules: consistently 0
                    else:
                        # Without rules: 1-2 violations, varying by temperature
                        base_violations = 1.4
                        temp_effect = temp * 0.3  # Higher temp = slightly more violations
                        violations = max(1, int(base_violations + temp_effect + (trial % 2)))
                    
                    config = ExperimentConfig(
                        model_name=model,
                        temperature=temp,
                        include_rules=include_rules,
                        run_number=trial + 1
                    )
                    
                    result = ExperimentResult(
                        config=config,
                        policy_violations=violations,
                        total_tool_calls=3 + violations,  # More violations = more tool calls
                        success=True,
                        execution_time=2.0 + temp + (violations * 0.5)  # Realistic timing
                    )
                    
                    results.append(result)
    
    # Convert to JSON format
    json_results = []
    for result in results:
        result_dict = asdict(result)
        result_dict['config'] = asdict(result.config)
        json_results.append(result_dict)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ablation_study_results_test_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"✅ Test dataset created: {filename}")
    print(f"📊 Contains {len(results)} experiment results")
    print(f"🎯 Models: {models}")
    print(f"🌡️  Temperatures: {temperatures}")
    
    return filename

if __name__ == "__main__":
    test_file = create_test_dataset()
    
    print(f"\n🎨 Now you can run:")
    print(f"   ./venv/bin/python visualize_results.py")
    print(f"   to visualize the test results!")
