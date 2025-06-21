# Policy Enforcer

A ReAct agent demo showcasing business rule enforcement in autonomous AI agents using LangChain and OpenAI GPT-4.

## Overview

This project demonstrates how to build an AI agent that enforces business rules without hardcoding workflows. The agent helps users choose activities (Play games, Go Camping, Swimming) while automatically enforcing predefined business policies.

## Features

- **ReAct Agent**: Uses LangChain's ReAct (Reasoning + Acting) pattern with OpenAI GPT-4
- **Business Rule Enforcement**: Automatic validation of business rules before tool execution
- **State Management**: Tracks user inventory, weather conditions, and activity choices
- **Policy Engine**: Flexible rule system with explainable failures
- **Command Line Interface**: Interactive CLI for demonstration

## Business Rules

The demo implements the following business rules:

1. The user must have a TV and an Xbox before they can play games
2. The user must have Hiking Boots before they can go camping
3. The user must have Goggles before they can go swimming
4. If the weather is raining, the user cannot go camping
5. If the weather is snowing, the user cannot go swimming
6. If the weather is unknown, the user can only play games
7. If the weather is already known, the weather tool cannot be called again

## Available Tools

1. **Check Weather**: Returns a random weather condition (sunny, raining, snowing)
2. **Shopping**: Mock API to purchase items and add them to inventory
3. **Choose Activity**: Validates and sets the user's chosen activity

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd policy-enforcer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

Run the demo:
```bash
python main.py
```

### Example Interactions

```
👤 You: I want to go camping
🤖 Agent: I'll help you go camping! Let me first check what you need and the current conditions...

👤 You: Check the weather
🤖 Agent: Weather check complete! Current weather: sunny

👤 You: Buy hiking boots
🤖 Agent: Successfully purchased: Hiking Boots. Added to inventory!

👤 You: Now I want to go camping
🤖 Agent: Activity chosen: Go Camping! Have fun!
```

### CLI Commands

- `help` - Show available commands
- `rules` - Display current business rules
- `state` - Show current agent state (inventory, weather, etc.)
- `reset` - Reset agent state
- `quit`/`exit` - Exit the application

## Project Structure

```
policy-enforcer/
├── main.py                     # CLI application entry point
├── requirements.txt            # Python dependencies
├── setup.py                   # Package setup
├── policy_enforcer/           # Main package
│   ├── __init__.py
│   ├── agents/                # ReAct agent implementation
│   │   └── __init__.py
│   ├── rules/                 # Business rules engine
│   │   └── __init__.py
│   ├── state/                 # State management
│   │   └── __init__.py
│   └── tools/                 # LangChain tools
│       └── __init__.py
```

## Architecture

### State Management
- `AgentState`: Pydantic model tracking user inventory, weather, and activity choices
- Global state instance accessible throughout the application
- State updates occur during tool execution

### Business Rules Engine
- `BusinessRule`: Abstract base class for all rules
- `RuleEngine`: Evaluates rules and provides explanations for failures
- Rules are checked before tool execution and activity selection
- Explainable failures help the LLM replan gracefully

### Tools with Policy Enforcement
- `PolicyEnforcedTool`: Base class that automatically checks rules before execution
- Tools return rule violation messages when business rules are not satisfied
- Each tool updates the agent state appropriately

### ReAct Agent
- Uses LangChain's `create_react_agent` with custom prompt
- Integrates business rules into the prompt for initial planning
- Handles rule violations gracefully with explanations

## Key Design Principles

1. **Separation of Concerns**: Business rules are separate from agent logic
2. **Explainability**: Rule violations provide clear explanations
3. **Flexibility**: New rules can be added without changing agent code
4. **State Tracking**: Consistent state management across all components
5. **Graceful Failure**: Rules guide the agent to alternative actions

## Requirements

- Python 3.8+
- OpenAI API key
- LangChain 0.1.0+
- Pydantic 2.0+

## License

MIT License - see LICENSE file for details.
