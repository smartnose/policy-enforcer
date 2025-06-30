# VS Code Debug Configurations

## Updated Launch Configurations for Policy Enforcer

The `.vscode/launch.json` file has been updated with new debug configurations specifically for the ablation study feature. Here are all available debug configurations:

### Main Application Debugging

#### 1. **Debug Policy Enforcer Main**
- **Description**: Default main application (with rules enabled by default)
- **Program**: `main.py`
- **Arguments**: None (uses default `--rules` behavior)
- **Use Case**: Standard debugging of the main application

#### 2. **Debug Policy Enforcer Main (Learning Mode)** ⭐ *NEW*
- **Description**: Main application in learning mode (no upfront rules)
- **Program**: `main.py`
- **Arguments**: `["--no-rules"]`
- **Use Case**: Debug the ablation study's learning mode where the agent discovers rules through tool execution

#### 3. **Debug Policy Enforcer Main (Explicit Rules)** ⭐ *NEW*
- **Description**: Main application with explicit rules mode
- **Program**: `main.py`
- **Arguments**: `["--rules"]`
- **Use Case**: Debug the ablation study's explicit rules mode for comparison

### Utility Debugging

#### 4. **Debug Prompt Comparison Demo** ⭐ *NEW*
- **Description**: Debug the simplified prompt comparison demo
- **Program**: `demo_prompt_comparison.py`
- **Arguments**: None
- **Use Case**: Debug prompt generation and comparison logic

#### 5. **Debug Prompt Export Utility** ⭐ *NEW*
- **Description**: Debug the unified prompt export utility
- **Program**: `prompt_export.py`
- **Arguments**: None
- **Use Case**: Debug prompt export functionality and comparison reports

### Legacy Configurations

#### 6. **Debug Policy Enforcer Demo**
- **Description**: Debug the business rules demo (no API key required)
- **Program**: `demo.py`
- **Arguments**: None
- **Use Case**: Debug the demonstration of business rule functionality

#### 7. **Debug Policy Enforcer with Mock API**
- **Description**: Debug main application with mock API
- **Program**: `main.py`
- **Arguments**: None
- **Use Case**: Debug with mocked external dependencies

#### 8. **Debug Current File**
- **Description**: Debug whatever file is currently open
- **Program**: `${file}`
- **Arguments**: None
- **Use Case**: Quick debugging of any Python file

## Usage Instructions

### For Ablation Study Research

1. **Set breakpoints** in `policy_enforcer/agents/__init__.py` at the `_create_agent()` method
2. **Choose debug configuration**:
   - **Learning Mode**: "Debug Policy Enforcer Main (Learning Mode)"
   - **Explicit Rules**: "Debug Policy Enforcer Main (Explicit Rules)"
3. **Compare behavior** by running both configurations with identical inputs

### For Prompt Development

1. **Set breakpoints** in `policy_enforcer/prompt_utils.py` at `generate_prompt_template()`
2. **Use configuration**: "Debug Prompt Comparison Demo"
3. **Step through** prompt generation logic to understand differences

### Quick Testing

1. **Use**: "Debug Prompt Export Utility" to test export functionality
2. **Use**: "Debug Policy Enforcer Demo" for rule testing without API keys

## Key Features

- **Environment Variables**: All configurations load from `.env` file
- **Python Path**: Correctly set for package imports
- **Console**: Uses integrated terminal for interactive debugging
- **Working Directory**: Set to workspace folder
- **Debugging Scope**: 
  - `justMyCode: false` for main app debugging (includes dependencies)
  - `justMyCode: true` for utility debugging (focuses on your code)

## Debugging Tips

### For Ablation Study
- Set breakpoints in `_create_agent()` to see prompt differences
- Compare `self.include_rules_in_prompt` values
- Step through `generate_prompt_template()` to see logic flow

### For Prompt Analysis
- Break at `compare_prompts()` to examine generated content
- Step through `quick_export()` to verify file generation
- Check statistics calculation in real-time

## Example Debug Session

1. **Open** `/Users/smartnose/GitHub/policy-enforcer/policy_enforcer/agents/__init__.py`
2. **Set breakpoint** on line with `generate_prompt_template(self.include_rules_in_prompt)`
3. **Select** "Debug Policy Enforcer Main (Learning Mode)" from debug dropdown
4. **Start debugging** (F5)
5. **Observe** `self.include_rules_in_prompt = False`
6. **Switch to** "Debug Policy Enforcer Main (Explicit Rules)"
7. **Compare** `self.include_rules_in_prompt = True`

This allows you to directly compare how the different modes affect agent initialization and prompt generation.
