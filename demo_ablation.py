#!/usr/bin/env python3
"""
Interactive demo showing the difference between agents with and without rules in prompt.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from policy_enforcer.agents import create_agent
from policy_enforcer.state import reset_state


def demo_agent_differences():
    """Demonstrate the differences between the two agent configurations."""
    
    print("🔬 ABLATION STUDY DEMO: Rules in Prompt vs Learning Approach")
    print("="*70)
    
    # Create both types of agents
    print("\n🤖 Creating agents...")
    agent_with_rules = create_agent(include_rules_in_prompt=True)
    agent_without_rules = create_agent(include_rules_in_prompt=False)
    
    print(f"✅ Agent with rules: include_rules_in_prompt = {agent_with_rules.include_rules_in_prompt}")
    print(f"✅ Agent without rules: include_rules_in_prompt = {agent_without_rules.include_rules_in_prompt}")
    
    print("\n📊 Agent Configuration Comparison:")
    print(f"   Both agents use: {agent_with_rules.model_name} at temperature {agent_with_rules.temperature}")
    print(f"   Key difference: Rules included in prompt vs learned through feedback")
    
    print("\n📋 EXPECTED BEHAVIORAL DIFFERENCES:")
    print("\n🧠 Agent WITH explicit rules in prompt:")
    print("   • Knows all business rules upfront")
    print("   • Should immediately explain rule violations")
    print("   • More predictable initial behavior")
    print("   • Can preemptively guide users")
    print("   • Example: 'I can't help with camping in rain, let me check weather first'")
    
    print("\n🔍 Agent WITHOUT rules (learning approach):")
    print("   • Discovers rules through trial and error")
    print("   • Must attempt actions to learn constraints")
    print("   • May make 'mistakes' initially then adapt")
    print("   • Learns from tool execution feedback")
    print("   • Example: Tries camping → gets rule violation → adapts strategy")
    
    print("\n💡 TO TEST WITH REAL API:")
    print("   1. Set up Google API key in .env file")
    print("   2. Run the agents with identical inputs")
    print("   3. Compare their approach and number of attempts needed")
    print("   4. Measure success rates and user experience")
    
    # Show the different prompt instructions
    print("\n📝 PROMPT INSTRUCTION DIFFERENCES:")
    
    # Get rule engine to show what the explicit rules version knows
    from policy_enforcer.rules import get_rule_engine
    rule_engine = get_rule_engine()
    rules_summary = rule_engine.get_rules_summary()
    
    print("\n📋 EXPLICIT RULES VERSION gets this information upfront:")
    print("   " + "\n   ".join(rules_summary.split('\n')[:8]))  # Show first 8 lines
    print("   ... [full business rules provided]")
    
    print("\n🧠 LEARNING VERSION gets these instructions instead:")
    learning_instructions = """
   - Pay close attention to tool execution results
   - If a tool call fails due to a rule violation, the error message will explain what went wrong
   - Learn from these failures and adapt your approach accordingly
   - Use failed attempts to infer the underlying business constraints
   - Suggest alternative actions when rules block your initial approach"""
    print(learning_instructions)
    
    return agent_with_rules, agent_without_rules


def main():
    """Run the demo."""
    try:
        # Reset state to ensure clean demo
        reset_state()
        
        # Run the demo
        agent_with_rules, agent_without_rules = demo_agent_differences()
        
        print(f"\n🎯 RESEARCH QUESTIONS for your ablation study:")
        print("   • Which approach leads to better user experience?")
        print("   • How many attempts does each agent need to succeed?")
        print("   • Which agent explains constraints better to users?")
        print("   • How do they handle edge cases or rule conflicts?")
        print("   • Which approach is more robust to rule changes?")
        
        print(f"\n✅ Demo completed! Both agent types are ready for testing.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
