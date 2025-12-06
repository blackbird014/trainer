"""
Prompt Validation

Validates prompts for completeness, missing references, and circular dependencies.
"""

from typing import List, Set, Dict, Optional, Any
from pathlib import Path
from .template import PromptTemplate


class ValidationResult:
    """Result of prompt validation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, 
                 warnings: List[str] = None):
        """
        Initialize validation result.
        
        Args:
            is_valid: Whether validation passed
            errors: List of error messages
            warnings: List of warning messages
        """
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def __bool__(self):
        """Allow using ValidationResult in boolean context."""
        return self.is_valid
    
    def __str__(self):
        """String representation."""
        status = "VALID" if self.is_valid else "INVALID"
        parts = [f"Validation Result: {status}"]
        
        if self.errors:
            parts.append(f"\nErrors ({len(self.errors)}):")
            for error in self.errors:
                parts.append(f"  - {error}")
        
        if self.warnings:
            parts.append(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                parts.append(f"  - {warning}")
        
        return "\n".join(parts)


class PromptValidator:
    """Validates prompts and their dependencies."""
    
    def __init__(self, context_dir: Optional[str] = None):
        """
        Initialize the validator.
        
        Args:
            context_dir: Base directory for context files (optional)
        """
        self.context_dir = Path(context_dir) if context_dir else None
    
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
        errors = []
        warnings = []
        
        # Check for missing variables if params provided
        if params is not None:
            missing_vars = template.get_variables() - set(params.keys())
            if missing_vars:
                errors.append(
                    f"Missing required variables: {', '.join(sorted(missing_vars))}"
                )
        
        # Validate context file references
        if context_paths:
            for path in context_paths:
                if not self._validate_context_path(path):
                    errors.append(f"Context file not found: {path}")
        
        # Check for empty template
        if not template.content.strip():
            warnings.append("Template content is empty")
        
        # Check for unclosed braces (potential template errors)
        open_braces = template.content.count('{')
        close_braces = template.content.count('}')
        if open_braces != close_braces:
            warnings.append(
                f"Mismatched braces: {open_braces} opening, {close_braces} closing"
            )
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def validate_contexts(self, context_paths: List[str]) -> ValidationResult:
        """
        Validate that all context files exist.
        
        Args:
            context_paths: List of context file paths
            
        Returns:
            ValidationResult instance
        """
        errors = []
        
        for path in context_paths:
            if not self._validate_context_path(path):
                errors.append(f"Context file not found: {path}")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors)
    
    def _validate_context_path(self, path: str) -> bool:
        """Check if a context file path exists."""
        if self.context_dir and not Path(path).is_absolute():
            full_path = self.context_dir / path
        else:
            full_path = Path(path)
        
        return full_path.exists()
    
    def check_circular_dependencies(self, context_paths: List[str]) -> ValidationResult:
        """
        Check for circular dependencies in context file references.
        
        Note: This is a placeholder for future implementation if context files
        start referencing each other.
        
        Args:
            context_paths: List of context file paths
            
        Returns:
            ValidationResult instance
        """
        # For now, no circular dependency checking needed
        # This can be implemented if contexts start referencing each other
        return ValidationResult(True)

