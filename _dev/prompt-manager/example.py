"""
Example usage of PromptManager
"""

from prompt_manager import PromptManager, PromptTemplate, PromptComposer

def main():
    # Initialize PromptManager
    manager = PromptManager(
        context_dir="../../information/context",
        cache_enabled=True,
        cache_max_size=100,
        cache_ttl=3600
    )
    
    # Example 1: Create and fill a template
    print("=== Example 1: Template Filling ===")
    template = PromptTemplate(
        "Analyze {COMPANY_NAME} ({TICKER}) with the following data:\n{DATA}"
    )
    
    filled = manager.fill_template(template, {
        "COMPANY_NAME": "Example Corp",
        "TICKER": "EXMP",
        "DATA": '{"revenue": 1000000, "employees": 50}'
    })
    print(filled)
    print()
    
    # Example 2: Compose multiple prompts
    print("=== Example 2: Prompt Composition ===")
    composer = PromptComposer()
    
    template1 = PromptTemplate("## Main Analysis\n\nAnalyze {COMPANY_NAME}")
    template2 = PromptTemplate("## Additional Context\n\nConsider market trends")
    
    composed = composer.compose([template1, template2], strategy="sequential")
    print(composed)
    print()
    
    # Example 3: Cache usage
    print("=== Example 3: Caching ===")
    prompt_id = "analysis_prompt"
    
    # First call - not cached
    cached = manager.get_cached(prompt_id, params={"COMPANY_NAME": "Test Corp"})
    print(f"Cached result: {cached}")
    
    # Cache the prompt
    manager.cache_prompt(prompt_id, filled, params={"COMPANY_NAME": "Test Corp"})
    
    # Second call - cached
    cached = manager.get_cached(prompt_id, params={"COMPANY_NAME": "Test Corp"})
    print(f"Cached result after caching: {cached[:50]}...")
    print()
    
    # Example 4: Validation
    print("=== Example 4: Validation ===")
    validation = manager.validate(template, params={"COMPANY_NAME": "Test"})
    print(f"Validation result: {validation.is_valid}")
    if not validation.is_valid:
        print(f"Errors: {validation.errors}")
    if validation.warnings:
        print(f"Warnings: {validation.warnings}")

if __name__ == "__main__":
    main()

