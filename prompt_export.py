#!/usr/bin/env python3
"""
Prompt Export Utility - Simple, unified tool for prompt comparison.

Usage:
    python prompt_export.py                     # Export both versions with comparison
    python prompt_export.py --with-rules        # Export only with-rules version
    python prompt_export.py --no-rules          # Export only no-rules version
    python prompt_export.py --compare-only      # Generate comparison report only
"""

import argparse
import os
from datetime import datetime

from policy_enforcer.prompt_utils import quick_export, compare_prompts, save_prompt_to_file


def create_comparison_report(comparison_data: dict, output_file: str):
    """Create a simple comparison report."""
    stats = comparison_data['stats']
    
    content = f"""# Prompt Comparison Report

**Generated:** {datetime.now().isoformat()}

## Statistics

| Metric | With Rules | Without Rules | Difference |
|--------|------------|---------------|------------|
| Characters | {stats['with_rules_chars']:,} | {stats['without_rules_chars']:,} | {stats['char_difference']:+,} |
| Words | {stats['with_rules_words']:,} | {stats['without_rules_words']:,} | {stats['word_difference']:+,} |
| Lines | {stats['with_rules_lines']} | {stats['without_rules_lines']} | {stats['with_rules_lines'] - stats['without_rules_lines']:+} |

## Key Differences

- **With Rules**: Explicit business rules provided upfront for immediate planning
- **Without Rules**: Learning-based approach through tool execution feedback

---

## Prompt with Rules

```
{comparison_data['with_rules']}
```

---

## Prompt without Rules

```
{comparison_data['without_rules']}
```
"""
    
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(description="Export Policy Enforcer prompt templates")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--with-rules', action='store_true', help='Export only with-rules version')
    group.add_argument('--no-rules', action='store_true', help='Export only no-rules version')
    group.add_argument('--compare-only', action='store_true', help='Generate comparison report only')
    
    parser.add_argument('--output-dir', default='prompt_export', help='Output directory')
    
    args = parser.parse_args()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("📤 Policy Enforcer Prompt Export")
    print("=" * 40)
    
    if args.compare_only:
        # Generate comparison report only
        comparison_data = compare_prompts()
        report_file = f"{args.output_dir}/comparison_{timestamp}.md"
        create_comparison_report(comparison_data, report_file)
        print(f"✅ Comparison report: {report_file}")
        
    elif args.with_rules:
        # Export only with-rules version
        files = quick_export(True, args.output_dir)
        print(f"✅ Exported WITH rules: {files[0]}")
        
    elif args.no_rules:
        # Export only no-rules version
        files = quick_export(False, args.output_dir)
        print(f"✅ Exported WITHOUT rules: {files[0]}")
        
    else:
        # Export both versions and create comparison (default)
        files = quick_export(None, args.output_dir)
        comparison_data = compare_prompts()
        report_file = f"{args.output_dir}/comparison_{timestamp}.md"
        create_comparison_report(comparison_data, report_file)
        
        print(f"✅ Exported WITH rules: {files[0]}")
        print(f"✅ Exported WITHOUT rules: {files[1]}")
        print(f"✅ Comparison report: {report_file}")
        
        # Show quick stats
        stats = comparison_data['stats']
        print(f"\n📊 Quick Stats:")
        print(f"   WITH rules:    {stats['with_rules_chars']:,} chars")
        print(f"   WITHOUT rules: {stats['without_rules_chars']:,} chars")
        print(f"   Difference:    {stats['char_difference']:+,} chars")


if __name__ == "__main__":
    main()
