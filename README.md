# Policy Enforcer

A ReAct agent demo showcasing business rule enforcement in autonomous AI agents using LangChain and Google's Gemini 1.5 Flash model.

## Overview

This project demonstrates how to build an AI agent that enforces business rules without hardcoding workflows. The agent helps users choose activities (Play games, Go Camping, Swimming) while automatically enforcing predefined business policies.

## Features

- **ReAct Agent**: Uses LangChain's ReAct (Reasoning + Acting) pattern with Google's Gemini 1.5 Flash
- **Business Rule Enforcement**: Automatic validation of business rules before tool execution
- **State Management**: Tracks user inventory, weather conditions, and activity choices
- **Policy Engine**: Flexible rule system with explainable failures
- **Command Line Interface**: Interactive CLI for demonstration
- **Comprehensive Testing**: 101 unit tests with 86% code coverage
- **VS Code Integration**: Full debugging and testing support

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

## Quick Start

### 1. Try the Demo (No API Key Required)
```bash
git clone <repository-url>
cd policy-enforcer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python demo.py
```

### 2. Use the Full Agent (Requires Google API Key)
```bash
# Set up environment
cp .env.example .env
# Edit .env and add: GOOGLE_API_KEY=your_key_here

# Run the interactive agent
python main.py
```

### 3. Run Tests and Coverage
```bash
# Install development dependencies first
pip install -r requirements-dev.txt

# Run all tests
python -m pytest tests/ -v

# Run tests with coverage report
python -m pytest tests/ --cov=policy_enforcer --cov-report=html --cov-report=term-missing

# Run specific test
python -m pytest tests/test_tools.py::TestShoppingTool::test_execute_valid_item -v
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd policy-enforcer
```

2. Install dependencies:
```bash
pip install -r requirements.txt

# For development (includes testing dependencies)
pip install -r requirements-dev.txt
```

3. Set up your Google API key:
```bash
cp .env.example .env
# Edit .env and add your Google API key
```

## Usage

Run the demo:
```bash
python main.py
```

## Example Output

```
👤 You: I want to go camping
🤖 Agent: I'll help you go camping! Let me first check what you need...

Action: check_weather
Action Input: {}
Observation: 🌤️ Weather check complete! Current weather: sunny

Action: shopping  
Action Input: {"item": "Hiking Boots"}
Observation: 🛒 Successfully purchased: Hiking Boots. Added to inventory!

Action: choose_activity
Action Input: {"activity": "Go Camping"}  
Observation: 🎯 Activity chosen: Go Camping! Have fun!

🤖 Agent: Perfect! I've checked the weather (it's sunny), purchased the required hiking boots for you, and successfully selected camping as your activity. You're all set to go camping!
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
├── demo.py                     # Demo without API key
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── setup.py                   # Package setup
├── .env.example               # Environment template
├── pytest.ini                # Test configuration
├── .vscode/                   # VS Code configuration
│   ├── launch.json           # Debug configurations
│   ├── settings.json         # Python settings
│   └── tasks.json            # Build/test tasks
├── tests/                     # Comprehensive test suite
│   ├── test_integration.py   # Integration tests
│   ├── test_items.py         # Item enum tests
│   ├── test_rules.py         # Business rules tests
│   ├── test_state.py         # State management tests
│   └── test_tools.py         # Tool execution tests
├── policy_enforcer/           # Main package
│   ├── __init__.py
│   ├── items.py              # Item constants and enums
│   ├── agents/               # ReAct agent implementation
│   │   └── __init__.py
│   ├── rules/                # Business rules engine
│   │   └── __init__.py
│   ├── state/                # State management
│   │   └── __init__.py
│   └── tools/                # LangChain tools
│       └── __init__.py
└── htmlcov/                  # Coverage reports (generated)
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

## Testing

The project includes a comprehensive test suite with 101 unit tests covering all major components:

### Test Coverage
- **86% Overall Coverage**: High test coverage across all modules
- **Items Module**: 100% coverage - Item enums, validation, and requirements
- **State Module**: 100% coverage - State management, persistence, and transitions  
- **Rules Module**: 98% coverage - All business rules and rule engine logic
- **Tools Module**: 93% coverage - Tool execution, parameter parsing, and integration
- **Integration Tests**: Complete workflow testing including error handling

### Test Categories
1. **Unit Tests**: Individual component testing (items, state, rules, tools)
2. **Integration Tests**: End-to-end workflow testing
3. **Error Handling**: Comprehensive error scenario coverage
4. **LangChain Compatibility**: JSON parameter mapping and tool integration

### Running Tests
```bash
# Install development dependencies first
pip install -r requirements-dev.txt

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=policy_enforcer --cov-report=html --cov-report=term-missing

# Run specific test categories
python -m pytest tests/test_rules.py -v              # Rules tests only
python -m pytest tests/test_integration.py -v       # Integration tests only

# Run specific test
python -m pytest tests/test_tools.py::TestShoppingTool::test_execute_valid_item -v
```

### VS Code Testing
The project includes VS Code tasks for easy testing:
- **Run Tests**: Execute all tests with detailed output
- **Run Tests with Coverage**: Generate HTML and terminal coverage reports
- **Run Specific Test**: Run individual test files or functions

## Requirements

- Python 3.8+
- Google API key (for full agent functionality)
- LangChain 0.1.0+
- Pydantic 2.0+

### Development Requirements
- pytest 7.0+ (for running tests)
- pytest-cov 4.0+ (for coverage reports)

## License

MIT License - see LICENSE file for details.
