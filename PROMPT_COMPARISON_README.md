# Prompt Comparison for Ablation Studies

This directory contains utilities for comparing prompt templates in the Policy Enforcer ablation study.

## Quick Start

### Generate Both Prompts with Comparison
```bash
python prompt_export.py
```

### Export Specific Versions
```bash
python prompt_export.py --with-rules     # Only explicit rules version
python prompt_export.py --no-rules       # Only learning mode version
python prompt_export.py --compare-only   # Only comparison report
```

### Run the Demo
```bash
python demo_prompt_comparison.py
```

### Use in Main Application
```bash
python main.py --rules      # Run with explicit rules (default)
python main.py --no-rules   # Run in learning mode
```

## Files

- **`prompt_export.py`** - Main utility for exporting prompts and generating comparisons
- **`demo_prompt_comparison.py`** - Simple demonstration of the prompt comparison features
- **`policy_enforcer/prompt_utils.py`** - Core prompt generation functions (centralized)

## Architecture

### Centralized Prompt Generation
All prompt generation logic is centralized in `policy_enforcer/prompt_utils.py` to eliminate code duplication:

- `generate_prompt_template(include_rules)` - Core prompt generation
- `compare_prompts()` - Generate both versions and statistics
- `quick_export()` - Export prompts to files
- `save_prompt_to_file()` - Save single prompt with metadata

### Agent Integration
The `PolicyEnforcerAgent` class uses the centralized prompt generation:

```python
from policy_enforcer.prompt_utils import generate_prompt_template

# In _create_agent():
prompt_template = generate_prompt_template(self.include_rules_in_prompt)
```

## Key Differences

### With Rules (`--rules`)
- Complete business rules provided upfront
- Agent can plan optimal paths immediately  
- Larger prompt size
- More predictable behavior

### Without Rules (`--no-rules`)
- Learning-based approach through tool execution feedback
- Smaller prompt size
- More adaptive and flexible
- May require trial-and-error

## Research Usage

1. **Generate Baselines**: Export both prompt versions for documentation
2. **Run Experiments**: Use `--rules` vs `--no-rules` flags in main.py
3. **Measure Metrics**: Success rates, API calls, rule violations, etc.
4. **Analyze Results**: Compare agent behavior between approaches

## Example Output Structure

```
prompt_export/
├── prompt_with_rules_20250630_133113.txt
├── prompt_without_rules_20250630_133113.txt
└── comparison_20250630_133113.md
```

The comparison report includes statistics, key differences, and full prompt content for both versions.
