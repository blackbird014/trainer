"""
Prompt and Context Loader

Handles loading prompts and context files from the filesystem.
"""

from pathlib import Path
from typing import List, Optional
from .template import PromptTemplate


class PromptLoader:
    """Loads prompts and context files from the filesystem."""
    
    def __init__(self, context_dir: Optional[str] = None):
        """
        Initialize the loader.
        
        Args:
            context_dir: Base directory for context files (optional)
        """
        self.context_dir = Path(context_dir) if context_dir else None
    
    def load_prompt(self, prompt_path: str) -> PromptTemplate:
        """
        Load a prompt template from a file.
        
        Args:
            prompt_path: Path to the prompt file
            
        Returns:
            PromptTemplate instance
        """
        return PromptTemplate.from_file(prompt_path)
    
    def load_contexts(self, context_paths: List[str]) -> str:
        """
        Load and merge multiple context files.
        
        Args:
            context_paths: List of paths to context files
            
        Returns:
            Merged context content as a single string
        """
        if not context_paths:
            return ""
        
        contexts = []
        for path in context_paths:
            # Resolve path relative to context_dir if set
            if self.context_dir and not Path(path).is_absolute():
                full_path = self.context_dir / path
            else:
                full_path = Path(path)
            
            if not full_path.exists():
                raise FileNotFoundError(f"Context file not found: {full_path}")
            
            content = full_path.read_text(encoding='utf-8')
            contexts.append(content)
        
        # Merge contexts with separators
        return "\n\n---\n\n".join(contexts)
    
    def load_context(self, context_path: str) -> str:
        """
        Load a single context file.
        
        Args:
            context_path: Path to the context file
            
        Returns:
            Context content as string
        """
        return self.load_contexts([context_path])
    
    def find_context_files(self, pattern: str = "*.md") -> List[str]:
        """
        Find context files matching a pattern.
        
        Args:
            pattern: Glob pattern to match files
            
        Returns:
            List of matching file paths
        """
        if not self.context_dir:
            return []
        
        files = list(self.context_dir.rglob(pattern))
        return [str(f) for f in files]

