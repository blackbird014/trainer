"""
Main PromptManager Class

Orchestrates prompt loading, template filling, composition, caching, and validation.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from .loader import PromptLoader
from .template import PromptTemplate
from .json_template import JSONTemplate
from .composer import PromptComposer
from .cache import PromptCache
from .validator import PromptValidator, ValidationResult
from .token_tracker import TokenTracker
from .logger import PromptManagerLogger, LogLevel, setup_logger


class PromptManager:
    """Main class for prompt management."""
    
    def __init__(self, context_dir: Optional[str] = None, 
                 cache_enabled: bool = True,
                 cache_max_size: int = 100,
                 cache_ttl: int = 3600,
                 track_tokens: bool = True,
                 model: str = "default",
                 logger: Optional[PromptManagerLogger] = None,
                 log_file: Optional[str] = None,
                 log_level: LogLevel = LogLevel.INFO,
                 enable_metrics: bool = True,
                 security_module: Optional[Any] = None,
                 use_json_templates: bool = False):
        """
        Initialize the PromptManager.
        
        Args:
            context_dir: Base directory for context files
            cache_enabled: Whether to enable caching
            cache_max_size: Maximum cache size
            cache_ttl: Cache time-to-live in seconds
            track_tokens: Whether to track token usage (default: True)
            model: Model name for cost estimation (default: "default")
            logger: Optional custom logger instance
            log_file: Optional log file path
            log_level: Logging level
            enable_metrics: Enable Prometheus metrics
            security_module: Optional SecurityModule for input validation/escaping
            use_json_templates: Whether to use JSON template format (default: False)
        """
        self.loader = PromptLoader(context_dir)
        self.composer = PromptComposer()
        self.cache = PromptCache(max_size=cache_max_size, default_ttl=cache_ttl) if cache_enabled else None
        self.validator = PromptValidator(context_dir)
        self.token_tracker = TokenTracker(model=model) if track_tokens else None
        self.security_module = security_module
        self.use_json_templates = use_json_templates
        
        # Setup logger
        if logger:
            self.logger = logger
        else:
            self.logger = setup_logger(
                name="prompt_manager",
                log_file=log_file,
                log_level=log_level,
                enable_metrics=enable_metrics
            )
    
    def load_prompt(self, prompt_path: str) -> PromptTemplate:
        """
        Load a prompt template from a file.
        
        Args:
            prompt_path: Path to the prompt file
            
        Returns:
            PromptTemplate instance (or JSONTemplate if use_json_templates=True)
        """
        if self.use_json_templates:
            return JSONTemplate.from_file(prompt_path)
        return self.loader.load_prompt(prompt_path)
    
    def load_contexts(self, context_paths: List[str]) -> str:
        """
        Load and merge multiple context files.
        
        Args:
            context_paths: List of paths to context files
            
        Returns:
            Merged context content as a single string
        """
        import time
        start_time = time.time()
        
        try:
            contexts = self.loader.load_contexts(context_paths)
            duration = time.time() - start_time
            
            # Track token usage
            tokens = None
            if self.token_tracker:
                usage = self.token_tracker.track_text(
                    "load_contexts",
                    contexts,
                    metadata={"context_files": context_paths, "count": len(context_paths)}
                )
                tokens = usage.input_tokens
            
            # Log operation
            self.logger.info(
                f"Loaded {len(context_paths)} context files",
                operation="load_contexts",
                duration=duration,
                tokens=tokens,
                context_files=context_paths,
                context_size_chars=len(contexts)
            )
            
            return contexts
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"Failed to load contexts: {str(e)}",
                operation="load_contexts",
                duration=duration,
                context_files=context_paths,
                error=str(e)
            )
            raise
    
    def fill_template(self, template: PromptTemplate, 
                     params: Dict[str, Any]) -> str:
        """
        Fill template variables with provided parameters.
        
        Args:
            template: PromptTemplate or JSONTemplate instance
            params: Dictionary mapping variable names to values
            
        Returns:
            Filled template string (or JSON string if JSONTemplate)
        """
        import time
        start_time = time.time()
        
        try:
            # Handle JSONTemplate
            if isinstance(template, JSONTemplate):
                filled_structure = template.fill(params, self.security_module)
                filled = template.to_prompt_text(filled_structure)
            else:
                # Handle regular PromptTemplate
                filled = template.fill(params, self.security_module)
            duration = time.time() - start_time
            
            # Track token usage
            tokens = None
            if self.token_tracker:
                usage = self.token_tracker.track_text(
                    "fill_template",
                    filled,
                    metadata={"template_path": template.path, "variables": list(params.keys())}
                )
                tokens = usage.input_tokens
            
            # Log operation
            self.logger.info(
                f"Filled template with {len(params)} variables",
                operation="fill_template",
                duration=duration,
                tokens=tokens,
                template_path=str(template.path) if template.path else None,
                variables=list(params.keys())
            )
            
            return filled
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"Failed to fill template: {str(e)}",
                operation="fill_template",
                duration=duration,
                error=str(e)
            )
            raise
    
    def compose(self, templates: List[PromptTemplate], 
               strategy: str = PromptComposer.STRATEGY_SEQUENTIAL) -> str:
        """
        Compose multiple templates into a single prompt.
        
        Args:
            templates: List of PromptTemplate instances
            strategy: Composition strategy (sequential, parallel, hierarchical)
            
        Returns:
            Composed prompt string
        """
        import time
        start_time = time.time()
        
        try:
            composed = self.composer.compose(templates, strategy)
            duration = time.time() - start_time
            
            # Track token usage
            tokens = None
            if self.token_tracker:
                usage = self.token_tracker.track_text(
                    "compose",
                    composed,
                    metadata={"template_count": len(templates), "strategy": strategy}
                )
                tokens = usage.input_tokens
            
            # Log operation
            self.logger.info(
                f"Composed {len(templates)} templates using {strategy} strategy",
                operation="compose",
                duration=duration,
                tokens=tokens,
                template_count=len(templates),
                strategy=strategy,
                composed_size_chars=len(composed)
            )
            
            return composed
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                f"Failed to compose templates: {str(e)}",
                operation="compose",
                duration=duration,
                error=str(e)
            )
            raise
    
    def get_cached(self, prompt_id: str, 
                  params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Get a cached prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            params: Optional parameters used to generate the prompt
            
        Returns:
            Cached prompt content or None if not found/expired
        """
        if not self.cache:
            return None
        
        cached = self.cache.get(prompt_id, params)
        
        if cached:
            self.logger.track_cache_hit("prompt_cache")
            self.logger.debug(
                f"Cache hit for prompt_id: {prompt_id}",
                prompt_id=prompt_id,
                cache_type="prompt_cache"
            )
        else:
            self.logger.track_cache_miss("prompt_cache")
            self.logger.debug(
                f"Cache miss for prompt_id: {prompt_id}",
                prompt_id=prompt_id,
                cache_type="prompt_cache"
            )
        
        return cached
    
    def cache_prompt(self, prompt_id: str, content: str,
                    params: Optional[Dict[str, Any]] = None, ttl: Optional[int] = None):
        """
        Cache a prompt.
        
        Args:
            prompt_id: Unique identifier for the prompt
            content: Prompt content to cache
            params: Optional parameters used to generate the prompt
            ttl: Time-to-live in seconds (uses default if not provided)
        """
        if self.cache:
            self.cache.set(prompt_id, content, params, ttl)
    
    def validate(self, template: PromptTemplate,
                params: Optional[Dict[str, Any]] = None,
                context_paths: Optional[List[str]] = None) -> ValidationResult:
        """
        Validate a prompt template.
        
        Args:
            template: PromptTemplate to validate
            params: Optional parameters to check against required variables
            context_paths: Optional list of context file paths to validate
            
        Returns:
            ValidationResult instance
        """
        return self.validator.validate(template, params, context_paths)
    
    def invalidate_cache(self, prompt_id: str):
        """
        Invalidate all cached entries for a prompt ID.
        
        Args:
            prompt_id: Prompt ID to invalidate
        """
        if self.cache:
            self.cache.invalidate(prompt_id)
    
    def clear_cache(self):
        """Clear all cached entries."""
        if self.cache:
            self.cache.clear()
    
    def get_token_usage(self) -> Dict:
        """
        Get total token usage statistics.
        
        Returns:
            Dictionary with usage statistics, or empty dict if tracking disabled
        """
        if not self.token_tracker:
            return {}
        return self.token_tracker.get_total_usage()
    
    def get_token_report(self) -> str:
        """
        Get a human-readable token usage report.
        
        Returns:
            Formatted report string, or empty string if tracking disabled
        """
        if not self.token_tracker:
            return "Token tracking is disabled."
        return self.token_tracker.get_report()
    
    def get_operation_stats(self) -> Dict[str, Dict]:
        """
        Get token usage statistics per operation.
        
        Returns:
            Dictionary mapping operation names to stats
        """
        if not self.token_tracker:
            return {}
        return self.token_tracker.get_operation_stats()
    
    def reset_token_tracking(self):
        """Reset token tracking data."""
        if self.token_tracker:
            self.token_tracker.reset()

