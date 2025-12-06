"""
Token Tracking and Cost Estimation

Tracks token usage and estimates costs for prompt operations.
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class TokenUsage:
    """Represents token usage for a single operation."""
    operation: str
    input_tokens: int
    output_tokens: int = 0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)
    
    @property
    def total_tokens(self) -> int:
        """Total tokens (input + output)."""
        return self.input_tokens + self.output_tokens
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class CostEstimate:
    """Cost estimate for token usage."""
    input_cost: float
    output_cost: float = 0.0
    
    @property
    def total_cost(self) -> float:
        """Total cost."""
        return self.input_cost + self.output_cost


class TokenTracker:
    """Tracks token usage and estimates costs."""
    
    # Common LLM pricing (per 1K tokens) - update as needed
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "default": {"input": 0.03, "output": 0.06},  # GPT-4 as default
    }
    
    def __init__(self, model: str = "default"):
        """
        Initialize token tracker.
        
        Args:
            model: Model name for cost calculation (default: "default")
        """
        self.model = model
        self.usage_history: List[TokenUsage] = []
        self.operation_stats: Dict[str, Dict] = defaultdict(lambda: {
            "count": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0
        })
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Uses a simple heuristic: ~4 characters per token for English text.
        More accurate for English, reasonable approximation for code/markdown.
        
        For production, consider using tiktoken library:
        ```python
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(text))
        ```
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Simple heuristic: ~4 characters per token
        # This is reasonably accurate for English text
        # For more accuracy, use tiktoken library
        char_count = len(text)
        
        # Adjust for markdown/code (slightly more tokens per char)
        if any(marker in text[:100] for marker in ['#', '```', '|', '```']):
            # Markdown/code tends to have more tokens per character
            return int(char_count / 3.5)
        
        return int(char_count / 4)
    
    def calculate_cost(self, input_tokens: int, output_tokens: int = 0) -> CostEstimate:
        """
        Calculate cost estimate for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            CostEstimate object
        """
        pricing = self.PRICING.get(self.model, self.PRICING["default"])
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return CostEstimate(input_cost=input_cost, output_cost=output_cost)
    
    def track_usage(self, operation: str, input_tokens: int, 
                    output_tokens: int = 0, metadata: Optional[Dict] = None) -> TokenUsage:
        """
        Track token usage for an operation.
        
        Args:
            operation: Name of the operation (e.g., "load_contexts", "compose_prompt")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            metadata: Optional metadata dictionary
            
        Returns:
            TokenUsage object
        """
        usage = TokenUsage(
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata=metadata or {}
        )
        
        self.usage_history.append(usage)
        
        # Update statistics
        stats = self.operation_stats[operation]
        stats["count"] += 1
        stats["total_input_tokens"] += input_tokens
        stats["total_output_tokens"] += output_tokens
        
        cost = self.calculate_cost(input_tokens, output_tokens)
        stats["total_cost"] += cost.total_cost
        
        return usage
    
    def track_text(self, operation: str, text: str, 
                  output_text: Optional[str] = None, metadata: Optional[Dict] = None) -> TokenUsage:
        """
        Track token usage by estimating from text.
        
        Args:
            operation: Name of the operation
            text: Input text
            output_text: Optional output text
            metadata: Optional metadata
            
        Returns:
            TokenUsage object
        """
        input_tokens = self.estimate_tokens(text)
        output_tokens = self.estimate_tokens(output_text) if output_text else 0
        
        return self.track_usage(operation, input_tokens, output_tokens, metadata)
    
    def get_total_usage(self) -> Dict:
        """
        Get total usage statistics.
        
        Returns:
            Dictionary with total usage stats
        """
        total_input = sum(u.input_tokens for u in self.usage_history)
        total_output = sum(u.output_tokens for u in self.usage_history)
        total_tokens = total_input + total_output
        
        cost = self.calculate_cost(total_input, total_output)
        
        return {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_tokens,
            "total_cost": cost.total_cost,
            "input_cost": cost.input_cost,
            "output_cost": cost.output_cost,
            "operation_count": len(self.usage_history),
            "model": self.model
        }
    
    def get_operation_stats(self) -> Dict[str, Dict]:
        """
        Get statistics per operation.
        
        Returns:
            Dictionary mapping operation names to stats
        """
        result = {}
        for operation, stats in self.operation_stats.items():
            cost = self.calculate_cost(
                stats["total_input_tokens"],
                stats["total_output_tokens"]
            )
            result[operation] = {
                **stats,
                "avg_input_tokens": stats["total_input_tokens"] / stats["count"] if stats["count"] > 0 else 0,
                "avg_cost": stats["total_cost"] / stats["count"] if stats["count"] > 0 else 0,
            }
        return result
    
    def get_report(self) -> str:
        """
        Generate a human-readable usage report.
        
        Returns:
            Formatted report string
        """
        total = self.get_total_usage()
        operation_stats = self.get_operation_stats()
        
        lines = [
            "=" * 80,
            "Token Usage Report",
            "=" * 80,
            f"Model: {total['model']}",
            f"Total Operations: {total['operation_count']}",
            "",
            "Total Usage:",
            f"  Input Tokens:  {total['total_input_tokens']:,}",
            f"  Output Tokens: {total['total_output_tokens']:,}",
            f"  Total Tokens:   {total['total_tokens']:,}",
            "",
            "Total Cost:",
            f"  Input Cost:  ${total['input_cost']:.4f}",
            f"  Output Cost: ${total['output_cost']:.4f}",
            f"  Total Cost:  ${total['total_cost']:.4f}",
            "",
            "Per Operation:",
        ]
        
        for operation, stats in sorted(operation_stats.items()):
            lines.append(f"  {operation}:")
            lines.append(f"    Count: {stats['count']}")
            lines.append(f"    Avg Input Tokens: {stats['avg_input_tokens']:.0f}")
            lines.append(f"    Avg Cost: ${stats['avg_cost']:.4f}")
            lines.append(f"    Total Cost: ${stats['total_cost']:.4f}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset all tracking data."""
        self.usage_history.clear()
        self.operation_stats.clear()
    
    def export_history(self) -> List[Dict]:
        """Export usage history as list of dictionaries."""
        return [u.to_dict() for u in self.usage_history]

