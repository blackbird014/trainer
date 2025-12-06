"""
Prompt Composition

Handles dynamic composition of multiple prompts.
"""

from typing import List, Optional
from .template import PromptTemplate


class PromptComposer:
    """Composes multiple prompts using different strategies."""
    
    STRATEGY_SEQUENTIAL = "sequential"
    STRATEGY_PARALLEL = "parallel"
    STRATEGY_HIERARCHICAL = "hierarchical"
    
    def __init__(self):
        """Initialize the composer."""
        self.strategies = {
            self.STRATEGY_SEQUENTIAL: self._compose_sequential,
            self.STRATEGY_PARALLEL: self._compose_parallel,
            self.STRATEGY_HIERARCHICAL: self._compose_hierarchical,
        }
    
    def compose(self, templates: List[PromptTemplate], 
                strategy: str = STRATEGY_SEQUENTIAL) -> str:
        """
        Compose multiple templates into a single prompt.
        
        Args:
            templates: List of PromptTemplate instances
            strategy: Composition strategy (sequential, parallel, hierarchical)
            
        Returns:
            Composed prompt string
        """
        if not templates:
            return ""
        
        if len(templates) == 1:
            return templates[0].content
        
        composer_func = self.strategies.get(strategy)
        if not composer_func:
            raise ValueError(
                f"Unknown strategy: {strategy}. "
                f"Available: {', '.join(self.strategies.keys())}"
            )
        
        return composer_func(templates)
    
    def _compose_sequential(self, templates: List[PromptTemplate]) -> str:
        """Compose templates sequentially (one after another)."""
        parts = [template.content for template in templates]
        return "\n\n---\n\n".join(parts)
    
    def _compose_parallel(self, templates: List[PromptTemplate]) -> str:
        """Compose templates in parallel (side by side)."""
        parts = []
        for i, template in enumerate(templates, 1):
            parts.append(f"## Section {i}\n\n{template.content}")
        return "\n\n".join(parts)
    
    def _compose_hierarchical(self, templates: List[PromptTemplate]) -> str:
        """
        Compose templates hierarchically.
        First template is the main prompt, others are sub-contexts.
        """
        if not templates:
            return ""
        
        main = templates[0].content
        if len(templates) == 1:
            return main
        
        contexts = "\n\n".join([
            f"### Context {i}\n\n{template.content}"
            for i, template in enumerate(templates[1:], 1)
        ])
        
        return f"{main}\n\n---\n\n## Additional Context\n\n{contexts}"
    
    def compose_strings(self, prompts: List[str], 
                       strategy: str = STRATEGY_SEQUENTIAL) -> str:
        """
        Compose multiple prompt strings directly.
        
        Args:
            prompts: List of prompt strings
            strategy: Composition strategy
            
        Returns:
            Composed prompt string
        """
        templates = [PromptTemplate(p) for p in prompts]
        return self.compose(templates, strategy)

