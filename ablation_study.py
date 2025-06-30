#!/usr/bin/env python3
"""
Ablation study script to compare agent behavior with and without rules in prompt.
"""

import os
import sys
from typing import List, Dict
from unittest.mock import patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from policy_enforcer.agents import create_agent
from policy_enforcer.state import reset_state


def mock_llm_response(scenario: str) -> str:
    """Mock LLM response for testing without API calls."""
    if "camping" in scenario.lower():
        return """I'll help you go camping! Let me check what you need.

Action: check_weather
Action Input: {}"""
    elif "games" in scenario.lower():
        return """I'll help you play games! Let me check what you need.

Action: check_state
Action Input: {}"""
    else:
        return """Let me help you with that.

Action: check_state
Action Input: {}"""


class AblationStudy:
    """Class to run ablation study comparing agents with and without rule knowledge."""
    
    def __init__(self):
        self.test_scenarios = [
            "I want to go camping",
            "I want to play games", 
            "I want to go swimming",
            "Can you help me choose an activity for today?"
        ]
    
    def run_scenario(self, scenario: str, include_rules: bool) -> Dict:
        """Run a single scenario with the specified rule configuration."""
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario}")
        print(f"Rules in prompt: {include_rules}")
        print(f"{'='*60}")
        
        # Reset state before each scenario
        reset_state()
        
        # Create agent with or without rules in prompt
        agent = create_agent(include_rules_in_prompt=include_rules)
        
        result = {
            'scenario': scenario,
            'include_rules': include_rules,
            'agent_config': {
                'model': agent.model_name,
                'temperature': agent.temperature,
                'include_rules_in_prompt': agent.include_rules_in_prompt
            }
        }
        
        try:
            print(f"✅ Agent configured successfully")
            print(f"   - Include rules in prompt: {agent.include_rules_in_prompt}")
            print(f"   - Model: {agent.model_name}")
            print(f"   - Temperature: {agent.temperature}")
            
            result['success'] = True
            
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ Error: {e}")
        
        return result
    
    def compare_prompts(self):
        """Compare the prompt templates between the two configurations."""
        print("\n" + "="*80)
        print("PROMPT TEMPLATE COMPARISON")
        print("="*80)
        
        # Create both agent types
        agent_with_rules = create_agent(include_rules_in_prompt=True)
        agent_without_rules = create_agent(include_rules_in_prompt=False)
        
        print(f"\n📊 CONFIGURATION COMPARISON:")
        print(f"   With rules    - include_rules_in_prompt: {agent_with_rules.include_rules_in_prompt}")
        print(f"   Without rules - include_rules_in_prompt: {agent_without_rules.include_rules_in_prompt}")
        
        print(f"\n🔍 KEY DIFFERENCES:")
        print(f"\n📋 EXPLICIT RULES VERSION:")
        print("   - Agent receives complete business rules in prompt")
        print("   - Can make informed decisions from the start")
        print("   - Should exhibit faster compliance")
        print("   - Prompt includes rule details upfront")
        
        print(f"\n🧠 LEARNING-BASED VERSION:")
        print("   - Agent learns rules through tool execution feedback")
        print("   - Must infer constraints from error messages")
        print("   - Uses trial-and-observation approach")
        print("   - Smaller initial prompt, learns incrementally")
    
    def run_study(self):
        """Run the complete ablation study."""
        print("🔬 ABLATION STUDY: Rules in Prompt vs Learning from Feedback")
        print("="*80)
        
        # First, compare the prompt templates
        self.compare_prompts()
        
        # Then run scenarios (demonstration only - would need API key for full execution)
        print(f"\n📝 SCENARIO ANALYSIS:")
        print("Note: Full execution requires Google API key. Showing configuration differences.")
        
        results = []
        
        for scenario in self.test_scenarios:
            # Test with rules in prompt
            result_with_rules = self.run_scenario(scenario, include_rules=True)
            results.append(result_with_rules)
            
            # Test without rules in prompt  
            result_without_rules = self.run_scenario(scenario, include_rules=False)
            results.append(result_without_rules)
        
        # Summary
        print(f"\n📊 STUDY SUMMARY:")
        print("="*80)
        
        with_rules_count = len([r for r in results if r['include_rules']])
        without_rules_count = len([r for r in results if not r['include_rules']])
        
        print(f"✅ Scenarios tested: {len(self.test_scenarios)}")
        print(f"   - With explicit rules: {with_rules_count}")
        print(f"   - With learning approach: {without_rules_count}")
        
        print(f"\n🎯 EXPECTED BEHAVIORAL DIFFERENCES:")
        print("   With explicit rules:")
        print("     + Faster initial compliance")
        print("     + More predictable behavior") 
        print("     + Better rule explanation to users")
        print("     - Larger prompt size")
        print("     - Less adaptable to rule changes")
        
        print("   With learning approach:")
        print("     + Smaller prompt size")
        print("     + More adaptable to rule changes")
        print("     + Mimics human learning process")
        print("     - Slower initial performance")
        print("     - May require multiple attempts to learn rules")
        print("     - Less predictable early behavior")
        
        print(f"\n💡 TO RUN FULL STUDY:")
        print("   1. Set up Google API key in .env file")
        print("   2. Modify this script to call agent.run() with test scenarios")
        print("   3. Compare actual agent responses and behavior")
        print("   4. Measure metrics like: success rate, turns to completion, rule violations")
        
        return results


def main():
    """Run the ablation study."""
    study = AblationStudy()
    results = study.run_study()
    
    print(f"\n🏁 Ablation study completed!")
    print(f"   Results: {len(results)} configurations tested")
    print(f"   See output above for detailed analysis")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
