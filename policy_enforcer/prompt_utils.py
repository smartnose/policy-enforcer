#!/usr/bin/env python3
"""
Centralized prompt utilities for the Policy Enforcer ablation study.

This module provides a single source of truth for prompt generation,
eliminating code duplication across multiple files.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional

from policy_enforcer.state import reset_state
from policy_enforcer.rules import get_rule_engine
from policy_enforcer.tools import get_tools


def generate_prompt_template(include_rules: bool = True) -> str:
    """
    Generate the complete prompt template for the Policy Enforcer agent.
    
    This is the single source of truth for prompt generation, used by both
    the agent itself and the ablation study utilities.
    
    Args:
        include_rules: Whether to include business rules in the prompt
        
    Returns:
        The fully rendered prompt template string with placeholders for LangChain
    """
    # Get rule descriptions for the prompt (if enabled)
    rule_engine = get_rule_engine()
    
    if include_rules:
        rules_section = f"""
IMPORTANT: You must follow these business rules at all times:

{rule_engine.get_rules_summary()}"""
        instructions_section = """Instructions:
1. ALWAYS pay attention to state changes reported in tool outputs. Latest state and tool outputs will be provided after each action.
2. Use "check_state" tool if you need to verify current inventory, weather, or activity
3. If a user asks to do something that violates business rules, explain why it's not allowed and suggest alternatives
4. Help users gather required items or check weather as needed
5. Be helpful and guide users through the process step by step
6. If rules prevent an action, explain the specific rule and what needs to be done to satisfy it
7. Remember that your actions have persistent effects - purchased items stay in inventory"""
    else:
        rules_section = """
IMPORTANT: Business rules are enforced automatically during tool execution. You are not given the specific rules upfront, but you should:
- Pay close attention to tool execution results
- If a tool call fails due to a rule violation, the error message will explain what went wrong
- Learn from these failures and adapt your approach accordingly
- Use failed attempts to infer the underlying business constraints
- Suggest alternative actions when rules block your initial approach"""
        instructions_section = """Instructions:
1. ALWAYS pay attention to state changes reported in tool outputs. Latest state and tool outputs will be provided after each action.
2. Use "check_state" tool if you need to verify current inventory, weather, or activity
3. When tool calls fail due to rule violations, carefully read the error messages to understand the constraints
4. Adapt your strategy based on rule violation feedback and suggest compliant alternatives
5. Help users gather required items or check weather as needed
6. Be helpful and guide users through the process step by step, learning from any failures
7. Remember that your actions have persistent effects - purchased items stay in inventory
8. Use trial and observation to infer business rules when they're not explicitly provided"""
    
    prompt_template = f"""
You are a helpful assistant that helps users choose activities. You have access to tools that allow you to check weather, shop for items, choose activities, and check current state.
{rules_section}

CRITICAL: STATE AWARENESS INSTRUCTIONS:
- After EVERY tool call that changes state (shopping, weather check, activity choice), the tool output will show you the updated state
- PAY ATTENTION to the "📊 Current inventory:" and "📊 Weather status:" information in tool outputs
- If you're unsure about the current state, use the "check_state" tool to get the latest information
- The state persists across your actions - if you buy an item, it stays in inventory
- Always consider the CURRENT state when making decisions, not just the initial state

Available Tools:
{{tools}}

Tool Names: {{tool_names}}

Tool Input Format:
Use the following format when calling tools:

Action: tool_name
Action Input: {{{{"parameter": "value"}}}}

{instructions_section}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {{input}}
Thought: {{agent_scratchpad}}"""
    
    return prompt_template


def generate_prompt_with_tools(include_rules: bool = True) -> str:
    """
    Generate a fully rendered prompt template with tools filled in.
    Used for export utilities and comparison reports.
    
    Args:
        include_rules: Whether to include business rules in the prompt
        
    Returns:
        The fully rendered prompt template string with tools filled in
    """
    # Get the base template
    template = generate_prompt_template(include_rules)
    
    # Get tools and fill them in
    tools = get_tools()
    tool_descriptions = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
    tool_names = ", ".join([tool.name for tool in tools])
    
    # Replace placeholders with actual content
    filled_template = template.replace("{{tools}}", tool_descriptions)
    filled_template = filled_template.replace("{{tool_names}}", tool_names)
    filled_template = filled_template.replace("{{input}}", "{input}")
    filled_template = filled_template.replace("{{agent_scratchpad}}", "{agent_scratchpad}")
    
    return filled_template


def save_prompt_to_file(include_rules: bool, output_file: str) -> str:
    """
    Generate and save a prompt template to a file.
    
    Args:
        include_rules: Whether to include business rules in the prompt
        output_file: Path to save the prompt
        
    Returns:
        The generated prompt content
    """
    # Reset state to ensure clean generation
    reset_state()
    
    # Generate prompt
    prompt_content = generate_prompt_with_tools(include_rules)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    # Write to file with metadata
    with open(output_file, 'w') as f:
        mode_name = "WITH Business Rules" if include_rules else "WITHOUT Business Rules (Learning Mode)"
        f.write(f"# Prompt Template - {mode_name}\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Mode: include_rules_in_prompt={include_rules}\n\n")
        f.write(prompt_content)
    
    return prompt_content


def compare_prompts() -> Dict[str, Any]:
    """
    Generate both prompt versions and return comparison data.
    
    Returns:
        Dictionary with prompt contents and statistics
    """
    reset_state()
    
    prompt_with_rules = generate_prompt_with_tools(True)
    prompt_without_rules = generate_prompt_with_tools(False)
    
    return {
        'with_rules': prompt_with_rules,
        'without_rules': prompt_without_rules,
        'stats': {
            'with_rules_chars': len(prompt_with_rules),
            'without_rules_chars': len(prompt_without_rules),
            'with_rules_words': len(prompt_with_rules.split()),
            'without_rules_words': len(prompt_without_rules.split()),
            'with_rules_lines': len(prompt_with_rules.split('\n')),
            'without_rules_lines': len(prompt_without_rules.split('\n')),
            'char_difference': len(prompt_with_rules) - len(prompt_without_rules),
            'word_difference': len(prompt_with_rules.split()) - len(prompt_without_rules.split()),
        }
    }


def quick_export(include_rules: Optional[bool] = None, output_dir: str = "prompt_export") -> list[str]:
    """
    Quick export of prompt templates.
    
    Args:
        include_rules: If None, export both; if True/False, export only that version
        output_dir: Directory to save files
        
    Returns:
        List of generated file paths
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    files = []
    
    if include_rules is None:
        # Export both
        for rules_mode in [True, False]:
            mode_name = "with_rules" if rules_mode else "without_rules"
            filename = f"{output_dir}/prompt_{mode_name}_{timestamp}.txt"
            save_prompt_to_file(rules_mode, filename)
            files.append(filename)
    else:
        # Export single version
        mode_name = "with_rules" if include_rules else "without_rules"
        filename = f"{output_dir}/prompt_{mode_name}_{timestamp}.txt"
        save_prompt_to_file(include_rules, filename)
        files.append(filename)
    
    return files
