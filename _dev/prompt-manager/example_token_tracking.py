"""
Example: Token Tracking and Cost Estimation

Demonstrates how to track token usage and estimate costs programmatically.
"""

import json
from pathlib import Path
from prompt_manager import PromptManager

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def main():
    print("=" * 80)
    print("Token Tracking Example")
    print("=" * 80)
    print()
    
    # Initialize PromptManager with token tracking enabled
    manager = PromptManager(
        context_dir=str(PROJECT_ROOT / "information" / "context"),
        cache_enabled=True,
        track_tokens=True,  # Enable token tracking
        model="gpt-4"       # Set model for cost estimation
    )
    
    print("Step 1: Loading contexts (tracked automatically)...")
    context_files = [
        "biotech/01-introduction.md",
        "biotech/molecular-biology-foundations.md",
        "economical-context.md"
    ]
    
    try:
        contexts = manager.load_contexts(context_files)
        print(f"✓ Loaded {len(context_files)} context files")
        print(f"  Context size: {len(contexts):,} characters")
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        contexts = ""
    
    print()
    
    print("Step 2: Loading instruction template...")
    instruction_path = PROJECT_ROOT / "information" / "instructions" / "01-instruction.md"
    
    try:
        instruction_template = manager.load_prompt(str(instruction_path))
        print(f"✓ Loaded instruction template")
    except FileNotFoundError:
        instruction_template = manager.load_prompt(str(PROJECT_ROOT / "prompt" / "generate_stock_analysis_report.md"))
        print(f"✓ Loaded alternative instruction template")
    
    print()
    
    print("Step 3: Loading JSON data...")
    json_files = list((PROJECT_ROOT / "output" / "json").glob("*.json"))
    
    if json_files:
        json_file = json_files[0]
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            ticker = first_item.get('ticker', 'N/A')
        elif isinstance(data, dict):
            ticker = data.get('ticker', 'N/A')
        else:
            ticker = 'N/A'
        
        data_json = json.dumps(data, indent=2)
        print(f"✓ Loaded JSON data for ticker: {ticker}")
    else:
        data = {"ticker": "NVDA", "valuation": {"marketCap": "4.42T"}}
        data_json = json.dumps(data, indent=2)
        ticker = "NVDA"
        print("✓ Using example data")
    
    print()
    
    print("Step 4: Filling template (tracked automatically)...")
    filled_instruction = manager.fill_template(instruction_template, {
        "COMPANY_NAME": ticker,
        "TICKER": ticker,
        "DATA_JSON": data_json
    })
    print(f"✓ Template filled ({len(filled_instruction):,} chars)")
    print()
    
    print("Step 5: Composing final prompt (tracked automatically)...")
    context_template = manager.loader.load_prompt(str(PROJECT_ROOT / "information" / "context" / "biotech" / "01-introduction.md")) if contexts else None
    
    if context_template:
        from prompt_manager import PromptTemplate
        filled_template = PromptTemplate(filled_instruction)
        final_prompt = manager.compose([context_template, filled_template], strategy="hierarchical")
    else:
        final_prompt = filled_instruction
    
    print(f"✓ Final prompt composed ({len(final_prompt):,} chars)")
    print()
    
    # Display token usage report
    print("=" * 80)
    print("Token Usage Report")
    print("=" * 80)
    print()
    print(manager.get_token_report())
    print()
    
    # Show detailed operation stats
    print("=" * 80)
    print("Operation Statistics")
    print("=" * 80)
    stats = manager.get_operation_stats()
    
    for operation, op_stats in stats.items():
        print(f"\n{operation}:")
        print(f"  Count: {op_stats['count']}")
        print(f"  Total Input Tokens: {op_stats['total_input_tokens']:,}")
        print(f"  Avg Input Tokens: {op_stats['avg_input_tokens']:.0f}")
        print(f"  Total Cost: ${op_stats['total_cost']:.4f}")
        print(f"  Avg Cost: ${op_stats['avg_cost']:.4f}")
    
    print()
    
    # Show total usage summary
    print("=" * 80)
    print("Total Usage Summary")
    print("=" * 80)
    total = manager.get_token_usage()
    
    print(f"Model: {total.get('model', 'N/A')}")
    print(f"Total Operations: {total.get('operation_count', 0)}")
    print(f"Total Input Tokens: {total.get('total_input_tokens', 0):,}")
    print(f"Total Output Tokens: {total.get('total_output_tokens', 0):,}")
    print(f"Total Tokens: {total.get('total_tokens', 0):,}")
    print(f"Total Cost: ${total.get('total_cost', 0):.4f}")
    print()
    
    # Demonstrate multiple operations to show accumulation
    print("=" * 80)
    print("Running Additional Operations to Show Tracking...")
    print("=" * 80)
    
    # Load contexts again (should be similar token count)
    print("\nLoading contexts again...")
    manager.load_contexts(context_files[:1])  # Just one context
    
    # Compose again
    print("Composing again...")
    if context_template:
        manager.compose([context_template], strategy="sequential")
    
    print("\nUpdated Report:")
    print(manager.get_token_report())
    print()
    
    print("=" * 80)
    print("Key Takeaways")
    print("=" * 80)
    print("1. Token tracking is automatic when enabled")
    print("2. Costs are estimated based on model pricing")
    print("3. You can track usage per operation")
    print("4. Use get_token_report() for formatted output")
    print("5. Use get_token_usage() for programmatic access")
    print("6. Reset with reset_token_tracking() to start fresh")


if __name__ == "__main__":
    main()

