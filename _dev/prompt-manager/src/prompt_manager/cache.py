"""
Cache Management

Handles prompt caching with LRU cache and TTL support.
"""

import hashlib
import time
from typing import Optional, Dict, Any
from collections import OrderedDict


class PromptCache:
    """LRU cache for prompts with TTL support."""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of cached items
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._timestamps: Dict[str, float] = {}
    
    def _generate_key(self, prompt_id: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate a cache key from prompt ID and parameters."""
        if params:
            # Create a stable hash of parameters
            param_str = str(sorted(params.items()))
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            return f"{prompt_id}:{param_hash}"
        return prompt_id
    
    def get(self, prompt_id: str, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Get a cached prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            params: Optional parameters used to generate the prompt
            
        Returns:
            Cached prompt content or None if not found/expired
        """
        key = self._generate_key(prompt_id, params)
        
        if key not in self._cache:
            return None
        
        # Check TTL
        if key in self._timestamps:
            ttl = self._cache[key].get('ttl', self.default_ttl)
            age = time.time() - self._timestamps[key]
            if age > ttl:
                # Expired, remove it
                del self._cache[key]
                del self._timestamps[key]
                return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return self._cache[key]['content']
    
    def set(self, prompt_id: str, content: str, 
            params: Optional[Dict[str, Any]] = None, ttl: Optional[int] = None):
        """
        Cache a prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            content: Prompt content to cache
            params: Optional parameters used to generate the prompt
            ttl: Time-to-live in seconds (uses default if not provided)
        """
        key = self._generate_key(prompt_id, params)
        
        # Remove oldest if at capacity
        if len(self._cache) >= self.max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            if oldest_key in self._timestamps:
                del self._timestamps[oldest_key]
        
        # Add new entry
        self._cache[key] = {
            'content': content,
            'ttl': ttl if ttl is not None else self.default_ttl
        }
        self._timestamps[key] = time.time()
    
    def invalidate(self, prompt_id: str):
        """
        Invalidate all cached entries for a prompt ID.
        
        Args:
            prompt_id: Prompt ID to invalidate
        """
        keys_to_remove = [
            k for k in self._cache.keys() 
            if k == prompt_id or k.startswith(f"{prompt_id}:")
        ]
        for key in keys_to_remove:
            del self._cache[key]
            if key in self._timestamps:
                del self._timestamps[key]
    
    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()
        self._timestamps.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)

