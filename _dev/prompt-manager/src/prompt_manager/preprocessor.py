"""
Template Pre-processor

Pre-processes text templates to JSON format for better security and structure.
"""

from pathlib import Path
from typing import Optional
from .json_template import JSONTemplate


class TemplatePreprocessor:
    """Pre-processes text templates to JSON format."""
    
    @staticmethod
    def preprocess_template(
        text_file_path: str,
        json_output_path: Optional[str] = None,
        template_id: Optional[str] = None
    ) -> JSONTemplate:
        """
        Pre-process a text template to JSON format.
        
        Args:
            text_file_path: Path to text template file
            json_output_path: Path to save JSON template (auto-generated if None)
            template_id: Optional template identifier
            
        Returns:
            JSONTemplate instance
        """
        text_path = Path(text_file_path)
        
        if not text_path.exists():
            raise FileNotFoundError(f"Template file not found: {text_file_path}")
        
        # Generate output path if not provided
        if json_output_path is None:
            json_output_path = str(text_path.with_suffix('.json'))
        
        # Load and convert
        json_template = JSONTemplate.from_text_template_file(
            text_file_path,
            json_output_path
        )
        
        if template_id:
            json_template.structure["metadata"]["template_id"] = template_id
        
        # Save JSON version
        json_template.save_json(json_output_path)
        
        return json_template
    
    @staticmethod
    def preprocess_directory(
        input_dir: str,
        output_dir: Optional[str] = None,
        pattern: str = "*.md"
    ) -> list:
        """
        Pre-process all templates in a directory.
        
        Args:
            input_dir: Directory containing text templates
            output_dir: Directory to save JSON templates (same as input if None)
            pattern: File pattern to match (default: "*.md")
            
        Returns:
            List of JSONTemplate instances
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir) if output_dir else input_path
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        templates = []
        for text_file in input_path.glob(pattern):
            json_file = output_path / f"{text_file.stem}.json"
            template = TemplatePreprocessor.preprocess_template(
                str(text_file),
                str(json_file)
            )
            templates.append(template)
        
        return templates

