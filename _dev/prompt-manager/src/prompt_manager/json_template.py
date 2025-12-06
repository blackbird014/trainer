"""
JSON Template System

Converts text templates to JSON structure and handles secure template filling.
"""

import json
import re
from typing import Dict, Any, Set, Optional, List
from pathlib import Path
from .template import PromptTemplate


class JSONTemplate:
    """
    JSON-based template with structured sections and secure user input handling.
    
    Structure:
    {
        "metadata": {
            "version": "1.0",
            "template_id": "...",
            "variables": ["var1", "var2"]
        },
        "sections": {
            "system": ["System instruction 1", "System instruction 2"],
            "context": ["Context content..."],
            "user_data": {
                "var1": "{{var1}}",  # Template variables
                "var2": "{{var2}}"
            },
            "instruction": "Main instruction with {{var1}}"
        }
    }
    """
    
    def __init__(self, structure: Dict[str, Any], path: Optional[str] = None):
        """
        Initialize JSON template from structure.
        
        Args:
            structure: JSON template structure
            path: Optional file path where template was loaded from
        """
        self.structure = structure
        self.path = path
        self._validate_structure()
        self._variables = self._extract_variables()
    
    def _validate_structure(self):
        """Validate template structure."""
        if "sections" not in self.structure:
            raise ValueError("Template must have 'sections' key")
        
        sections = self.structure["sections"]
        if not isinstance(sections, dict):
            raise ValueError("'sections' must be a dictionary")
    
    def _extract_variables(self) -> Set[str]:
        """Extract all template variables from structure."""
        variables = set()
        
        def find_variables(obj):
            if isinstance(obj, str):
                # Find {{variable}} patterns
                pattern = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
                matches = re.findall(pattern, obj)
                variables.update(matches)
            elif isinstance(obj, dict):
                for value in obj.values():
                    find_variables(value)
            elif isinstance(obj, list):
                for item in obj:
                    find_variables(item)
        
        find_variables(self.structure)
        return variables
    
    def get_variables(self) -> Set[str]:
        """Get all variable names required by this template."""
        return self._variables.copy()
    
    def fill(
        self,
        params: Dict[str, Any],
        security_module: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Fill template with user parameters, applying security.
        
        Args:
            params: Dictionary mapping variable names to values
            security_module: Optional SecurityModule for validation/escaping
            
        Returns:
            Filled JSON structure with user data properly isolated
            
        Raises:
            ValueError: If required variables are missing
        """
        # Validate required variables
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
        
        # Create filled structure
        filled_structure = self._deep_copy_structure()
        
        # Fill variables in structure (returns new structure)
        filled_structure = self._fill_variables(filled_structure, escaped_params)
        
        return filled_structure
    
    def _deep_copy_structure(self) -> Dict[str, Any]:
        """Create deep copy of template structure."""
        return json.loads(json.dumps(self.structure))
    
    def _fill_variables(self, obj: Any, params: Dict[str, Any]) -> Any:
        """Recursively fill variables in structure."""
        if isinstance(obj, str):
            # Replace {{variable}} patterns
            pattern = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
            def replace_var(match):
                var_name = match.group(1)
                return params.get(var_name, match.group(0))
            return re.sub(pattern, replace_var, obj)
        elif isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                result[key] = self._fill_variables(value, params)
            return result
        elif isinstance(obj, list):
            return [self._fill_variables(item, params) for item in obj]
        return obj
    
    def to_prompt_text(self, filled_structure: Optional[Dict[str, Any]] = None) -> str:
        """
        Convert filled JSON structure to text prompt for LLM.
        
        Args:
            filled_structure: Filled structure (uses self.structure if None)
            
        Returns:
            Formatted text prompt
        """
        if filled_structure is None:
            filled_structure = self.structure
        
        sections = filled_structure.get("sections", {})
        parts = []
        
        # System section
        if "system" in sections:
            system = sections["system"]
            if isinstance(system, list):
                parts.append("## System Instructions\n\n" + "\n".join(system))
            elif isinstance(system, str):
                parts.append("## System Instructions\n\n" + system)
        
        # Context section
        if "context" in sections:
            context = sections["context"]
            if isinstance(context, list):
                parts.append("## Context\n\n" + "\n\n".join(context))
            elif isinstance(context, str):
                parts.append("## Context\n\n" + context)
        
        # User data section (clearly marked)
        if "user_data" in sections:
            user_data = sections["user_data"]
            parts.append("## User Provided Data\n\n")
            if isinstance(user_data, dict):
                for key, value in user_data.items():
                    parts.append(f"**{key}**: {value}")
            elif isinstance(user_data, str):
                parts.append(user_data)
            parts.append("\n--- End User Data ---\n")
        
        # Instruction section
        if "instruction" in sections:
            instruction = sections["instruction"]
            parts.append("## Instruction\n\n" + str(instruction))
        
        return "\n\n".join(parts)
    
    def to_json_string(self, filled_structure: Optional[Dict[str, Any]] = None) -> str:
        """
        Convert filled structure to JSON string.
        
        Args:
            filled_structure: Filled structure (uses self.structure if None)
            
        Returns:
            JSON string representation
        """
        if filled_structure is None:
            filled_structure = self.structure
        return json.dumps(filled_structure, indent=2, ensure_ascii=False)
    
    @classmethod
    def from_text_template(
        cls,
        text_template: str,
        template_id: Optional[str] = None
    ) -> "JSONTemplate":
        """
        Convert text template to JSON structure.
        
        Args:
            text_template: Text template with {variable} placeholders
            template_id: Optional template identifier
            
        Returns:
            JSONTemplate instance
        """
        # Extract variables
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        variables = set(re.findall(pattern, text_template))
        
        # Simple conversion: treat entire template as instruction
        # User variables will be in user_data section
        structure = {
            "metadata": {
                "version": "1.0",
                "template_id": template_id or "converted_template",
                "variables": sorted(list(variables)),
                "source": "text_template"
            },
            "sections": {
                "instruction": text_template,
                "user_data": {}
            }
        }
        
        # Replace {var} with {{var}} in instruction and add to user_data
        instruction = text_template
        for var in variables:
            # Replace {name} with {{name}} - need proper escaping
            old_pattern = "{" + var + "}"
            new_pattern = "{{" + var + "}}"
            instruction = instruction.replace(old_pattern, new_pattern)
            structure["sections"]["user_data"][var] = "{{" + var + "}}"
        
        structure["sections"]["instruction"] = instruction
        
        return cls(structure)
    
    @classmethod
    def from_file(cls, file_path: str) -> "JSONTemplate":
        """
        Load JSON template from file.
        
        Supports both JSON (.json) and text (.md, .txt) files.
        
        Args:
            file_path: Path to template file
            
        Returns:
            JSONTemplate instance
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Template file not found: {file_path}")
        
        if path.suffix == '.json':
            # Load JSON template
            content = path.read_text(encoding='utf-8')
            structure = json.loads(content)
            return cls(structure, path=str(path))
        else:
            # Load text template and convert
            content = path.read_text(encoding='utf-8')
            template_id = path.stem
            json_template = cls.from_text_template(content, template_id)
            json_template.path = str(path)
            # Re-extract variables after conversion
            json_template._variables = json_template._extract_variables()
            return json_template
    
    def save_json(self, output_path: str):
        """
        Save template as JSON file (pre-processing).
        
        Args:
            output_path: Path to save JSON template
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        # Update metadata
        if "metadata" not in self.structure:
            self.structure["metadata"] = {}
        
        self.structure["metadata"]["preprocessed"] = True
        self.structure["metadata"]["source_file"] = self.path
        
        output.write_text(
            json.dumps(self.structure, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    @classmethod
    def from_text_template_file(
        cls,
        text_file_path: str,
        json_output_path: Optional[str] = None
    ) -> "JSONTemplate":
        """
        Load text template and optionally save as JSON (pre-processing).
        
        Args:
            text_file_path: Path to text template file
            json_output_path: Optional path to save JSON version
            
        Returns:
            JSONTemplate instance
        """
        json_template = cls.from_file(text_file_path)
        
        if json_output_path:
            json_template.save_json(json_output_path)
        
        return json_template

