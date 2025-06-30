"""
ReAct agent with business rule enforcement.
"""

from typing import Any, Dict, List, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool

from ..state import get_state, reset_state
from ..rules import get_rule_engine
from ..tools import get_tools
from ..prompt_utils import generate_prompt_template


class PolicyEnforcerAgent:
    """ReAct agent with integrated business rule enforcement."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash", temperature: float = 0.1, include_rules_in_prompt: bool = True):
        self.model_name = model_name
        self.temperature = temperature
        self.include_rules_in_prompt = include_rules_in_prompt
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.tools = get_tools()
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create the ReAct agent with custom prompt."""
        
        # Use centralized prompt generation
        prompt_template = generate_prompt_template(self.include_rules_in_prompt)
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools])
            }
        )
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True)
    
    def run(self, user_input: str) -> str:
        """Run the agent with user input."""
        try:
            # Add current state information to the input
            state = get_state()
            state_summary = state.get_summary()
            
            enhanced_input = f"""
Current State:
{state_summary}

User Request: {user_input}
"""
            
            result = self.agent_executor.invoke({"input": enhanced_input})
            return result["output"]
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def reset(self):
        """Reset the agent state."""
        reset_state()
        print("🔄 Agent state has been reset.")
    
    def show_state(self) -> str:
        """Show current agent state."""
        state = get_state()
        return f"📊 Current State:\n{state.get_summary()}"
    
    def show_rules(self) -> str:
        """Show current business rules."""
        rule_engine = get_rule_engine()
        return rule_engine.get_rules_summary()


def create_agent(model_name: str = "gemini-1.5-flash", temperature: float = 0.1, include_rules_in_prompt: bool = True) -> PolicyEnforcerAgent:
    """Create a new policy enforcer agent instance.
    
    Args:
        model_name: The name of the model to use
        temperature: The temperature for the model
        include_rules_in_prompt: Whether to include business rules in the prompt.
                               If False, agent learns rules through tool execution feedback.
    """
    return PolicyEnforcerAgent(model_name=model_name, temperature=temperature, include_rules_in_prompt=include_rules_in_prompt)
