"""
Semantic Kernel agents for policy enforcement.

This module ports the LangChain-based PolicyEnforcerAgent to use Semantic Kernel
with the custom ReAct agent implementation.
"""

import os
from typing import Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.google.google_ai import GoogleAIChatCompletion

from .react_agent import ReActAgent
from .sk_tools import get_sk_plugins
from .state import get_state, reset_state
from .rules import get_rule_engine
from .sk_prompt_utils import generate_sk_prompt_instructions


class PolicyEnforcerSKAgent:
    """Semantic Kernel-based policy enforcer agent with ReAct pattern."""
    
    def __init__(
        self, 
        model_name: str = "gemini-1.5-flash", 
        temperature: float = 0.1, 
        include_rules_in_prompt: bool = True,
        api_key: Optional[str] = None
    ):
        """
        Initialize the Semantic Kernel policy enforcer agent.
        
        Args:
            model_name: Google AI model name
            temperature: Model temperature for randomness
            include_rules_in_prompt: Whether to include business rules in prompt
            api_key: Google AI API key (if not provided, will use environment)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.include_rules_in_prompt = include_rules_in_prompt
        
        # Initialize Semantic Kernel
        self.kernel = Kernel()
        
        # Set up Google AI service
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
        
        # Add Google AI chat completion service
        self.kernel.add_service(
            GoogleAIChatCompletion(
                service_id="google_ai",
                gemini_model_id=model_name,
                api_key=api_key
            )
        )
        
        # Add plugins (tools)
        plugins = get_sk_plugins()
        for plugin in plugins:
            plugin_name = plugin.__class__.__name__.replace("Plugin", "").lower()
            self.kernel.add_plugin(plugin, plugin_name=plugin_name)
        
        # Generate instructions based on mode
        instructions = generate_sk_prompt_instructions(include_rules_in_prompt)
        
        # Create ReAct agent
        self.react_agent = ReActAgent(
            kernel=self.kernel,
            service_id="google_ai",
            name="PolicyEnforcer",
            instructions=instructions,
            max_iterations=10,
            verbose=True
        )
    
    def run(self, user_input: str) -> str:
        """
        Run the agent with user input.
        
        Args:
            user_input: User's input/question
            
        Returns:
            Agent's response
        """
        try:
            # Add current state information to the input
            state = get_state()
            state_summary = state.get_summary()
            
            enhanced_input = f"""
Current State:
{state_summary}

User Request: {user_input}
"""
            
            # Run the ReAct agent
            result = self.react_agent.run(enhanced_input)
            return result
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def reset(self):
        """Reset the agent state."""
        reset_state()
        self.react_agent.reset()
        print("🔄 Agent state has been reset.")
    
    def show_state(self) -> str:
        """Show current agent state."""
        state = get_state()
        return f"📊 Current State:\n{state.get_summary()}"
    
    def show_rules(self) -> str:
        """Show current business rules."""
        rule_engine = get_rule_engine()
        return rule_engine.get_rules_summary()


def create_sk_agent(
    model_name: str = "gemini-1.5-flash", 
    temperature: float = 0.1, 
    include_rules_in_prompt: bool = True,
    api_key: Optional[str] = None
) -> PolicyEnforcerSKAgent:
    """
    Create a new Semantic Kernel policy enforcer agent instance.
    
    Args:
        model_name: The name of the Google AI model to use
        temperature: The temperature for the model
        include_rules_in_prompt: Whether to include business rules in the prompt.
                                If False, agent learns rules through tool execution feedback.
        api_key: Google AI API key (optional if set in environment)
        
    Returns:
        Configured PolicyEnforcerSKAgent instance
    """
    return PolicyEnforcerSKAgent(
        model_name=model_name,
        temperature=temperature,
        include_rules_in_prompt=include_rules_in_prompt,
        api_key=api_key
    )