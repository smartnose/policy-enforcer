#!/usr/bin/env python3
"""
Quick test of the ablation study functionality.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from policy_enforcer.agents import create_agent
from policy_enforcer.state import reset_state, get_state, WeatherCondition
from quantitative_ablation_study import setup_deterministic_environment, count_policy_violations

def test_quick_experiment():
    """Quick test with 2 runs to verify functionality."""
    
    print("🧪 Quick Ablation Study Test")
    print("=" * 40)
    
    # Setup deterministic environment
    original_choice = setup_deterministic_environment()
    
    try:
        # Test both rule modes
        for include_rules in [True, False]:
            print(f"\n📋 Testing with rules: {include_rules}")
            
            # Reset state
            reset_state()
            
            # Create agent
            agent = create_agent(
                model_name="gemini-1.5-flash",
                temperature=0.0,
                include_rules_in_prompt=include_rules
            )
            
            # Run test
            print("  Running: 'I wanna go camping'")
            try:
                result = agent.run("I wanna go camping")
                
                # Count violations  
                final_state = get_state()
                state_info = {
                    'chosen_activity': final_state.chosen_activity.value if final_state.chosen_activity else None,
                    'inventory': list(final_state.inventory),
                    'weather': final_state.weather.value if final_state.weather else None,
                    'weather_checked': final_state.weather_checked
                }
                violations = count_policy_violations(result, state_info)
                print(f"  ✅ Policy violations detected: {violations}")
                
                # Show final state
                final_state = get_state()
                print(f"  📊 Final activity: {final_state.chosen_activity}")
                print(f"  🌧️  Weather: {final_state.weather}")
                print(f"  🎒 Inventory: {list(final_state.inventory)}")
                
                # Show brief response
                print(f"  💬 Response (first 200 chars): {result[:200]}...")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                import traceback
                traceback.print_exc()
    
    finally:
        # Restore original random.choice
        import random
        random.choice = original_choice
    
    print("\n✅ Quick test completed!")

if __name__ == "__main__":
    test_quick_experiment()
