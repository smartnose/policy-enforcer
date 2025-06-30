#!/usr/bin/env python3
"""
Simple demo of the prompt comparison feature for ablation studies.
"""

from policy_enforcer.prompt_utils import compare_prompts, quick_export


def main():
    print("🔬 Policy Enforcer Prompt Comparison Demo")
    print("=" * 50)
    
    # Generate and compare prompts
    print("📋 Generating prompt comparison...")
    comparison = compare_prompts()
    stats = comparison['stats']
    
    # Show statistics
    print(f"\n📊 Prompt Statistics:")
    print(f"   WITH rules:    {stats['with_rules_chars']:,} chars, {stats['with_rules_words']:,} words")
    print(f"   WITHOUT rules: {stats['without_rules_chars']:,} chars, {stats['without_rules_words']:,} words")
    print(f"   Difference:    {stats['char_difference']:+,} chars, {stats['word_difference']:+,} words")
    
    # Verify key differences
    print(f"\n🔍 Content Verification:")
    has_rules = 'Business Rules:' in comparison['with_rules']
    has_learning = 'Learn from these failures' in comparison['without_rules']
    print(f"   WITH rules has business rules: {'✅' if has_rules else '❌'}")
    print(f"   WITHOUT rules has learning instructions: {'✅' if has_learning else '❌'}")
    
    # Export files
    print(f"\n📤 Exporting prompts...")
    files = quick_export()
    for file in files:
        print(f"   ✅ {file}")
    
    print(f"\n🎯 Demo complete! Use 'python prompt_export.py' for full functionality.")


if __name__ == "__main__":
    main()
