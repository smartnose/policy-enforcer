# Test Suite Documentation

This document provides detailed information about the comprehensive test suite for the Policy Enforcer project.

## Test Overview

The Policy Enforcer includes 101 unit tests across 5 test modules, achieving 86% code coverage. The test suite validates all core functionality including business rules, state management, tool execution, and error handling.

## Test Modules

### 1. `tests/test_items.py` (9 tests)
Tests the Item enum and ItemRequirements functionality:
- Item string conversion and validation
- Activity-specific item requirements
- Missing item detection
- Item validation helpers

**Coverage**: 100% of `policy_enforcer/items.py`

### 2. `tests/test_state.py` (14 tests)  
Tests the AgentState and state management:
- State initialization and persistence
- Inventory management (add, check, duplicates)
- Weather and activity setting
- State serialization and summaries
- Global state singleton pattern

**Coverage**: 100% of `policy_enforcer/state/__init__.py`

### 3. `tests/test_rules.py` (32 tests)
Tests all business rules and the rule engine:
- Equipment requirement rules (TV/Xbox, Hiking Boots, Goggles)
- Weather constraint rules (camping in rain, swimming in snow)
- Unknown weather rules (only games allowed)
- Weather check limitation rule
- Rule engine integration and error messaging
- Rule result formatting

**Coverage**: 98% of `policy_enforcer/rules/__init__.py`

### 4. `tests/test_tools.py` (34 tests)
Tests all LangChain tools and policy enforcement:
- CheckWeatherTool: Weather generation and caching
- ShoppingTool: Item purchasing and validation
- ChooseActivityTool: Activity selection and rule checking
- CheckStateTool: State reporting
- PolicyEnforcedTool base class functionality
- LangChain parameter mapping and JSON parsing
- Tool integration with rule engine

**Coverage**: 93% of `policy_enforcer/tools/__init__.py`

### 5. `tests/test_integration.py` (12 tests)
Integration tests covering complete workflows:
- End-to-end camping workflow (weather → shopping → activity)
- End-to-end gaming workflow
- Weather-based activity restrictions
- Rule violation scenarios
- Error handling for invalid inputs
- State persistence across tool calls
- Enhanced state reporting features
- LangChain JSON input compatibility

**Coverage**: Tests integration between all modules

## Test Categories

### Unit Tests (89 tests)
- **Individual Component Testing**: Each module tested in isolation
- **Boundary Condition Testing**: Edge cases and invalid inputs
- **State Validation**: Proper state transitions and data integrity
- **Rule Logic Verification**: All business rule combinations

### Integration Tests (12 tests)
- **Complete Workflows**: End-to-end user scenarios
- **Cross-Module Integration**: Proper communication between components
- **Error Propagation**: Error handling across module boundaries
- **Real Usage Patterns**: Simulated user interactions

### Error Handling Tests (included throughout)
- **Invalid Input Handling**: Malformed JSON, missing parameters
- **Business Rule Violations**: Graceful failure with explanations
- **Type Safety**: Enum validation and conversion errors
- **Recovery Scenarios**: State reset and continuation after errors

## Coverage Report

```
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
policy_enforcer/__init__.py              1      0   100%
policy_enforcer/agents/__init__.py      42     42     0%   (Live API calls)
policy_enforcer/items.py                41      0   100%
policy_enforcer/rules/__init__.py      112      2    98%   
policy_enforcer/state/__init__.py       45      0   100%
policy_enforcer/tools/__init__.py      136     10    93%   
------------------------------------------------------------------
TOTAL                                  377     54    86%
```

**Note**: The `agents` module has 0% coverage because it requires live Google API calls. This is intentional to avoid API dependencies in tests.

## Running Tests

### Basic Test Execution
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_tools.py -v

# Run specific test class
python -m pytest tests/test_rules.py::TestPlayGamesRule -v

# Run specific test method
python -m pytest tests/test_tools.py::TestShoppingTool::test_execute_valid_item -v
```

### Coverage Testing
```bash
# Generate coverage report
python -m pytest --cov=policy_enforcer --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=policy_enforcer --cov-report=html

# Open HTML report
open htmlcov/index.html
```

### VS Code Integration
Use the following VS Code tasks (Cmd+Shift+P → "Tasks: Run Task"):
- **Run Tests**: Execute all tests with detailed output
- **Run Tests with Coverage**: Generate coverage reports
- **Run Specific Test**: Prompted input for specific test paths

## Test Design Principles

### 1. **Isolation**
Each test is independent and can run in any order. State is reset between tests.

### 2. **Determinism**
Tests use fixed inputs and mock random elements (like weather) for consistent results.

### 3. **Comprehensive Coverage**
Tests cover happy paths, error cases, edge conditions, and integration scenarios.

### 4. **Clear Assertions**
Each test has specific, focused assertions with descriptive failure messages.

### 5. **Realistic Scenarios**
Tests simulate real user interactions and business rule applications.

### 6. **Performance**
Tests run quickly (< 1 second total) to enable frequent execution during development.

## Adding New Tests

When adding new functionality:

1. **Add Unit Tests**: Test the new component in isolation
2. **Update Integration Tests**: Include new functionality in workflows
3. **Test Error Cases**: Verify proper error handling
4. **Maintain Coverage**: Aim for >90% coverage on new code
5. **Update Documentation**: Update this file and README.md

### Test File Template
```python
import unittest
from policy_enforcer.your_module import YourClass

class TestYourClass(unittest.TestCase):
    """Test the YourClass functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.instance = YourClass()
    
    def test_basic_functionality(self):
        """Test basic functionality works as expected."""
        result = self.instance.do_something()
        self.assertEqual(result, expected_value)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        with self.assertRaises(ValueError):
            self.instance.do_something_invalid()
```

## Continuous Integration

The test suite is designed to run in CI/CD environments:
- No external dependencies (API keys, network access)
- Fast execution (< 1 second)
- Clear exit codes (0 = success, non-zero = failure)
- Detailed output for debugging failures

## Test Quality Metrics

- **101 Total Tests**: Comprehensive coverage of all functionality
- **86% Code Coverage**: High confidence in code quality
- **0 Flaky Tests**: All tests are deterministic and reliable
- **< 1 Second Runtime**: Fast feedback during development
- **5 Test Categories**: Organized by functionality and scope
