# Cost Analysis: Large Prompts and Token Usage

## The Problem

Yes, sending large prompts to LLMs **is expensive** in terms of tokens. Here's why:

### Example from Our Test

From `example_real_usage.py`:
- **Context files**: ~17KB (16,897 characters)
- **Instruction**: ~1.4KB (1,361 characters)  
- **JSON data**: ~5KB (varies)
- **Total prompt**: ~18KB (18,303 characters)

### Token Estimation

**Rough calculation**:
- 1 token ≈ 4 characters (English text)
- 18KB ≈ **4,500-5,000 input tokens**
- Plus response tokens: **2,000-5,000 tokens** (typical analysis)
- **Total per request**: ~7,000-10,000 tokens

### Cost Examples (as of 2024)

**GPT-4 Pricing**:
- Input: $0.03 per 1K tokens
- Output: $0.06 per 1K tokens

**Per request cost**:
- Input (5K tokens): $0.15
- Output (3K tokens): $0.18
- **Total: ~$0.33 per analysis**

**If you run 100 analyses**: $33
**If you run 1,000 analyses**: $330

## Why This Architecture Helps

The modular design actually **reduces costs** through caching:

### 1. Context Caching (Already Implemented)

```python
# Contexts rarely change - cache them!
manager.cache_prompt("biotech_contexts", contexts, ttl=86400)  # Cache for 24 hours

# Next request uses cached version - no reload needed
cached = manager.get_cached("biotech_contexts")
```

**Savings**: If contexts are 15KB and you make 100 requests:
- **Without cache**: 100 × 15KB = 1.5MB sent to LLM
- **With cache**: 15KB sent once, reused 100 times
- **Token savings**: ~375K tokens = **$11.25 saved**

### 2. Prompt Composition Caching

```python
# Cache the composed prompt (contexts + instruction)
prompt_id = f"analysis_{company}_{ticker}"
cached_prompt = manager.get_cached(prompt_id, params={"company": company})

if not cached_prompt:
    # Only compose if not cached
    prompt = compose_prompt(contexts, instruction, data)
    manager.cache_prompt(prompt_id, prompt, params={"company": company})
```

**Savings**: If same company analyzed multiple times:
- **Without cache**: Full prompt sent each time
- **With cache**: Only send once, reuse
- **Token savings**: Significant for repeated analyses

### 3. Selective Context Loading

Instead of loading ALL contexts every time, load only what's needed:

```python
# Bad: Load everything
contexts = manager.load_contexts([
    "biotech/01-introduction.md",           # 8KB
    "biotech/molecular-biology-foundations.md",  # 10KB
    "economical-context.md"                 # 2KB
])  # Total: 20KB

# Good: Load only relevant context
if analysis_type == "biotech":
    contexts = manager.load_contexts(["biotech/01-introduction.md"])  # 8KB
elif analysis_type == "general":
    contexts = manager.load_contexts(["01-introduction.md"])  # 2KB
```

**Savings**: 50-60% reduction in context size = **$0.10-0.15 saved per request**

## Cost Optimization Strategies

### Strategy 1: Context Summarization

Create shorter "summary" versions of contexts:

```python
# Full context: 10KB
# Summary context: 2KB (80% reduction)

# Use summary for initial analysis
# Load full context only if needed
```

### Strategy 2: Context Chunking

Split large contexts into smaller chunks, load only relevant ones:

```python
# Instead of loading entire 10KB context
# Load only relevant sections (2KB)
contexts = manager.load_contexts([
    "biotech/01-introduction.md#pipeline-structure",  # Only this section
    "biotech/01-introduction.md#market-opportunity"  # And this section
])
```

### Strategy 3: Use Cheaper Models for Context

```python
# Use GPT-3.5 to summarize contexts (cheaper)
# Then use GPT-4 only for final analysis
summarized_context = summarize_with_gpt35(full_context)  # $0.001
analysis = analyze_with_gpt4(summarized_context + data)   # $0.20
```

### Strategy 4: Embedding-Based Context Retrieval

Instead of sending full contexts, use embeddings to retrieve only relevant parts:

```python
# 1. Embed contexts into vector database
# 2. Query for relevant context chunks based on company/data
# 3. Only include relevant chunks in prompt

# Reduces 20KB context to 2-3KB relevant chunks
```

## Recommended Approach

### For Development/Testing:
- Use **caching** (already implemented)
- Load **full contexts** for accuracy
- Accept higher costs for better results

### For Production:
1. **Enable aggressive caching** (24+ hour TTL for contexts)
2. **Create context summaries** for common use cases
3. **Use selective loading** - only load relevant contexts
4. **Monitor token usage** per request
5. **Consider cheaper models** for simpler analyses

### Implementation Example

```python
# Production-optimized version
class OptimizedPromptManager(PromptManager):
    def load_contexts_optimized(self, context_paths, analysis_type):
        # Use cached summaries if available
        cache_key = f"context_summary_{analysis_type}"
        cached = self.get_cached(cache_key)
        
        if cached:
            return cached
        
        # Load full contexts
        full_contexts = self.load_contexts(context_paths)
        
        # Create summary (or use pre-generated)
        summary = self._summarize_contexts(full_contexts, analysis_type)
        
        # Cache summary
        self.cache_prompt(cache_key, summary, ttl=86400)
        
        return summary
```

## Cost Monitoring

Add token tracking to your PromptManager:

```python
class PromptManager:
    def __init__(self, ...):
        self.token_tracker = TokenTracker()
    
    def compose(self, templates, strategy="sequential"):
        prompt = super().compose(templates, strategy)
        
        # Track token usage
        tokens = self.token_tracker.estimate_tokens(prompt)
        self.token_tracker.log_usage("prompt_composition", tokens)
        
        return prompt
```

## Summary

**Yes, large prompts are expensive**, but:

✅ **Caching reduces costs** (contexts reused many times)  
✅ **Modular design enables optimization** (selective loading)  
✅ **Architecture supports cost-saving strategies** (summarization, chunking)  
✅ **Costs are manageable** with proper caching (~$0.10-0.20 per analysis with caching)

**Key takeaway**: The modular architecture doesn't just organize code—it enables cost optimization through intelligent caching and selective loading.

