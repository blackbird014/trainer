"""
Template Engine

Handles variable substitution and template filling.
Supports both text-based and JSON-based templates.
"""

import re
from typing import Dict, Any, Set, Optional
from pathlib import Path


class PromptTemplate:
    """Represents a prompt template with variable substitution support."""
    
    def __init__(self, content: str, path: str = None):
        """
        Initialize a prompt template.
        
        Args:
            content: The template content with {variable} placeholders
            path: Optional file path where this template was loaded from
        """
        self.content = content
        self.path = path
        self._variables = self._extract_variables(content)
    
    def _extract_variables(self, content: str) -> Set[str]:
        """Extract all variable names from the template."""
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        return set(re.findall(pattern, content))
    
    def fill(
        self,
        params: Dict[str, Any],
        security_module: Optional[Any] = None
    ) -> str:
        """
        Fill template variables with provided parameters.
        
        Args:
            params: Dictionary mapping variable names to values
            security_module: Optional SecurityModule for validation/escaping
            
        Returns:
            Filled template string
            
        Raises:
            ValueError: If required variables are missing
        """
        missing_vars = self._variables - set(params.keys())
        if missing_vars:
            raise ValueError(
                f"Missing required variables: {', '.join(sorted(missing_vars))}"
            )
        
        # Apply security if module provided
        if security_module:
            try:
                validated_params = security_module.validate(params)
            except Exception as e:
                # In non-strict mode, sanitize but continue
                if hasattr(security_module, 'config') and not security_module.config.strict_mode:
                    validated_params = security_module.sanitize(params)
                else:
                    raise
            
            # Detect injections
            for key, value in validated_params.items():
                detection = security_module.detect_injection(str(value))
                if not detection.is_safe and security_module.config.strict_mode:
                    from prompt_security import InjectionDetectedError
                    raise InjectionDetectedError(
                        f"Injection detected in '{key}': {', '.join(detection.flags[:2])}",
                        detection
                    )
            
            # Escape user input
            escaped_params = {}
            for key, value in validated_params.items():
                escaped_params[key] = security_module.escape(str(value))
        else:
            # No security - just convert to strings
            escaped_params = {k: str(v) for k, v in params.items()}
        
        filled = self.content
        for var, value in escaped_params.items():
            filled = filled.replace(f"{{{var}}}", value)
        
        return filled
    
    def get_variables(self) -> Set[str]:
        """Get all variable names required by this template."""
        return self._variables.copy()
    
    def has_variables(self) -> bool:
        """Check if template has any variables."""
        return len(self._variables) > 0
    
    @classmethod
    def from_file(cls, file_path: str) -> "PromptTemplate":
        """Load template from a file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        return cls(content, path=str(path))

