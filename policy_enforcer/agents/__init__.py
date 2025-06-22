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


class PolicyEnforcerAgent:
    """ReAct agent with integrated business rule enforcement."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash", temperature: float = 0.1):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.tools = get_tools()
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """Create the ReAct agent with custom prompt."""
        
        # Get rule descriptions for the prompt
        rule_engine = get_rule_engine()
        rules_summary = rule_engine.get_rules_summary()
        
        prompt_template = """
You are a helpful assistant that helps users choose activities. You have access to tools that allow you to check weather, shop for items, choose activities, and check current state.

IMPORTANT: You must follow these business rules at all times:

{rules_summary}

CRITICAL: STATE AWARENESS INSTRUCTIONS:
- After EVERY tool call that changes state (shopping, weather check, activity choice), the tool output will show you the updated state
- PAY ATTENTION to the "📊 Current inventory:" and "📊 Weather status:" information in tool outputs
- If you're unsure about the current state, use the "check_state" tool to get the latest information
- The state persists across your actions - if you buy an item, it stays in inventory
- Always consider the CURRENT state when making decisions, not just the initial state

Available Tools:
{tools}

Tool Names: {tool_names}

Tool Input Format:
Use the following format when calling tools:

Action: tool_name
Action Input: {{"parameter": "value"}}

Instructions:
1. ALWAYS pay attention to state changes reported in tool outputs
2. Use "check_state" tool if you need to verify current inventory, weather, or activity
3. If a user asks to do something that violates business rules, explain why it's not allowed and suggest alternatives
4. Help users gather required items or check weather as needed
5. Be helpful and guide users through the process step by step
6. If rules prevent an action, explain the specific rule and what needs to be done to satisfy it
7. Remember that your actions have persistent effects - purchased items stay in inventory

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "rules_summary": rules_summary,
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


def create_agent(model_name: str = "gemini-1.5-flash", temperature: float = 0.1) -> PolicyEnforcerAgent:
    """Create a new policy enforcer agent instance."""
    return PolicyEnforcerAgent(model_name=model_name, temperature=temperature)
