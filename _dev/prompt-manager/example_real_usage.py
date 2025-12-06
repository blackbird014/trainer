"""
Real-world example: Using PromptManager to load contexts, instructions, and JSON data

This demonstrates the actual workflow:
1. Load context files (large domain knowledge)
2. Load instruction prompt (template)
3. Load JSON data (stock/company data)
4. Compose everything into a final prompt
"""

import json
from pathlib import Path
from prompt_manager import PromptManager, PromptTemplate

# Get project root (assuming we're in _dev/phase1/prompt-manager)
# Script is at: _dev/phase1/prompt-manager/example_real_usage.py
# Project root is: trainer/ (3 levels up)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def main():
    print("=" * 80)
    print("Real-world PromptManager Example")
    print("=" * 80)
    print()
    
    # Initialize PromptManager with context directory and token tracking
    manager = PromptManager(
        context_dir=str(PROJECT_ROOT / "information" / "context"),
        cache_enabled=True,
        cache_max_size=100,
        cache_ttl=3600,
        track_tokens=True,  # Enable token tracking
        model="gpt-4"       # Set model for cost estimation
    )
    
    # Step 1: Load context files (domain knowledge - these are large!)
    print("Step 1: Loading context files...")
    context_files = [
        "biotech/01-introduction.md",
        "biotech/molecular-biology-foundations.md",
        "economical-context.md"
    ]
    
    try:
        contexts = manager.load_contexts(context_files)
        print(f"✓ Loaded {len(context_files)} context files")
        print(f"  Total context length: {len(contexts)} characters")
        print(f"  Preview: {contexts[:200]}...")
        print()
    except FileNotFoundError as e:
        print(f"✗ Error loading contexts: {e}")
        print("  Note: Some context files may not exist yet")
        print()
        contexts = ""  # Continue with empty contexts for demo
    
    # Step 2: Load instruction prompt template
    print("Step 2: Loading instruction prompt...")
    instruction_path = PROJECT_ROOT / "information" / "instructions" / "01-instruction.md"
    
    try:
        instruction_template = manager.load_prompt(str(instruction_path))
        print(f"✓ Loaded instruction: {instruction_path.name}")
        print(f"  Template variables: {instruction_template.get_variables()}")
        print()
    except FileNotFoundError:
        print(f"✗ Instruction file not found: {instruction_path}")
        print("  Creating a simple example template instead...")
        instruction_template = PromptTemplate(
            "Generate a comprehensive analysis for {COMPANY_NAME} ({TICKER}) using the provided data:\n\n{DATA_JSON}"
        )
        print()
    
    # Step 3: Load JSON data file
    print("Step 3: Loading JSON data...")
    json_files = list((PROJECT_ROOT / "output" / "json").glob("*.json"))
    
    if not json_files:
        print("✗ No JSON files found in output/json/")
        print("  Available JSON files should be in: output/json/")
        print("  Example: output/json/example_nvda_data.json")
        print()
        # Create example data
        data = {
            "ticker": "NVDA",
            "valuation": {"marketCap": "4.42T", "forwardPE": "26.95"},
            "financials": {"revenue": "165.22B", "profitMargin": "52.41%"}
        }
        data_json = json.dumps(data, indent=2)
        print("  Using example data instead...")
    else:
        # Use the first JSON file found
        json_file = json_files[0]
        print(f"✓ Found JSON file: {json_file.name}")
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(data, list) and len(data) > 0:
            # If it's a list, use the first item
            first_item = data[0]
            ticker_from_data = first_item.get('ticker', 'N/A')
            print(f"  Loaded data for {len(data)} ticker(s), first: {ticker_from_data}")
        elif isinstance(data, dict):
            ticker_from_data = data.get('ticker', 'N/A')
            print(f"  Loaded data for ticker: {ticker_from_data}")
        else:
            ticker_from_data = 'N/A'
            print(f"  Loaded JSON data (format: {type(data).__name__})")
        
        # Convert to formatted JSON string for the prompt
        data_json = json.dumps(data, indent=2)
    
    print()
    
    # Step 4: Fill the instruction template with data
    print("Step 4: Filling template with data...")
    
    # Extract ticker and company name from JSON if available
    if isinstance(data, list) and len(data) > 0:
        # If it's a list, use the first item
        first_item = data[0]
        ticker = first_item.get('ticker', 'UNKNOWN')
        company_name = ticker  # Could be enhanced to look up company name
    elif isinstance(data, dict):
        ticker = data.get('ticker', 'UNKNOWN')
        company_name = ticker  # Could be enhanced to look up company name
    else:
        ticker = "UNKNOWN"
        company_name = "Unknown Company"
    
    filled_instruction = manager.fill_template(instruction_template, {
        "COMPANY_NAME": company_name,
        "TICKER": ticker,
        "DATA_JSON": data_json
    })
    
    print(f"✓ Template filled with variables")
    print(f"  Company: {company_name}")
    print(f"  Ticker: {ticker}")
    print()
    
    # Step 5: Compose final prompt (contexts + filled instruction)
    print("Step 5: Composing final prompt...")
    
    # Create templates for composition
    context_template = PromptTemplate(contexts) if contexts else None
    instruction_template_filled = PromptTemplate(filled_instruction)
    
    if context_template:
        final_prompt = manager.compose(
            [context_template, instruction_template_filled],
            strategy="hierarchical"  # Contexts as background, instruction as main
        )
    else:
        final_prompt = filled_instruction
    
    print(f"✓ Final prompt composed")
    print(f"  Total prompt length: {len(final_prompt)} characters")
    print()
    
    # Step 6: Display summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Context files loaded: {len(context_files)}")
    print(f"Context size: {len(contexts)} chars")
    print(f"Instruction size: {len(filled_instruction)} chars")
    print(f"Final prompt size: {len(final_prompt)} chars")
    print()
    
    # Step 7: Show preview of final prompt
    print("=" * 80)
    print("Final Prompt Preview (first 500 chars)")
    print("=" * 80)
    print(final_prompt[:500])
    print("...")
    print()
    
    # Step 8: Optional - Save to file for inspection
    output_file = PROJECT_ROOT / "_dev" / "phase1" / "prompt-manager" / "example_output.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(final_prompt)
    
    print(f"✓ Full prompt saved to: {output_file}")
    print()
    # Step 9: Display token usage and cost
    print("=" * 80)
    print("Token Usage & Cost Analysis")
    print("=" * 80)
    print()
    print(manager.get_token_report())
    print()
    
    # Show cost breakdown
    total = manager.get_token_usage()
    print("Cost Breakdown:")
    print(f"  Input tokens: {total.get('total_input_tokens', 0):,}")
    print(f"  Estimated cost: ${total.get('total_cost', 0):.4f}")
    print()
    
    # Show per-operation costs
    stats = manager.get_operation_stats()
    if stats:
        print("Per-Operation Costs:")
        for operation, op_stats in stats.items():
            print(f"  {operation}: ${op_stats['total_cost']:.4f} "
                  f"({op_stats['count']} operations)")
        print()
    
    print("=" * 80)
    print("Next steps:")
    print("=" * 80)
    print("1. Review the generated prompt in: example_output.md")
    print("2. This prompt can now be sent to an LLM for analysis")
    print("3. The contexts provide domain knowledge, instruction provides structure")
    print("4. JSON data provides the actual company metrics to analyze")
    print("5. Token tracking shows you the cost before sending to LLM")
    print()
    print("💡 Tip: Use caching to reduce costs on repeated operations!")


if __name__ == "__main__":
    main()

