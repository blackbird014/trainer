"""
Module and test discovery functionality.
"""

from typing import List, Dict, Optional
from pathlib import Path
import os


class ModuleDiscovery:
    """Discover modules and tests in the project."""

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize module discovery.

        Args:
            project_root: Root directory of the project. If None, auto-detects.
        """
        if project_root is None:
            # Auto-detect: look for _dev directory
            current = Path.cwd()
            while current != current.parent:
                if (current / "_dev").exists():
                    project_root = str(current)
                    break
                current = current.parent
            
            if project_root is None:
                project_root = str(Path.cwd())

        self.project_root = Path(project_root)
        self.dev_dir = self.project_root / "_dev"

    def discover_modules(self) -> List[str]:
        """
        Discover all modules in _dev directory.

        Returns:
            List of module names (directory names)
        """
        if not self.dev_dir.exists():
            return []

        modules = []
        for item in self.dev_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                # Check if it looks like a module (has src/ or pyproject.toml)
                if (item / "src").exists() or (item / "pyproject.toml").exists():
                    modules.append(item.name)

        return sorted(modules)

    def discover_tests(self, module: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Discover test files in modules.

        Args:
            module: Specific module name, or None for all modules

        Returns:
            Dictionary mapping module names to lists of test file paths
        """
        modules_to_check = [module] if module else self.discover_modules()
        if not modules_to_check:
            return {}

        test_files = {}
        for mod_name in modules_to_check:
            mod_path = self.dev_dir / mod_name
            if not mod_path.exists():
                continue

            # Look for tests directory
            tests_dir = mod_path / "tests"
            if not tests_dir.exists():
                test_files[mod_name] = []
                continue

            # Find test files
            test_paths = []
            for test_file in tests_dir.rglob("test_*.py"):
                # Get relative path from module root
                rel_path = test_file.relative_to(mod_path)
                test_paths.append(str(rel_path))

            test_files[mod_name] = sorted(test_paths)

        return test_files

    def get_module_path(self, module: str) -> Optional[Path]:
        """
        Get path to a module.

        Args:
            module: Module name

        Returns:
            Path to module directory, or None if not found
        """
        mod_path = self.dev_dir / module
        return mod_path if mod_path.exists() else None

    def get_tests_path(self, module: str) -> Optional[Path]:
        """
        Get path to tests directory for a module.

        Args:
            module: Module name

        Returns:
            Path to tests directory, or None if not found
        """
        mod_path = self.get_module_path(module)
        if mod_path is None:
            return None

        tests_path = mod_path / "tests"
        return tests_path if tests_path.exists() else None

