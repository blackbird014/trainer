# Testing and Releasing Independent Modules

## Overview

When modules are developed independently in separate repositories, two critical challenges arise:

1. **How to test modules together** when they're developed separately
2. **How to ensure consistent releases** with all modules aligned by version

This document addresses both challenges with practical solutions and best practices.

---

## Part 1: Testing Modules Together

### The Challenge

If modules are developed separately:
- `prompt-manager` repo doesn't have `llm-provider` code
- `llm-provider` repo doesn't have `prompt-manager` code
- How can test-agent test them together?

### Solution: Integration Test Layer

Integration tests live in a separate location that brings modules together.

#### Option 1: Integration Tests in `trainer-core`

```
trainer-core/
├── src/
│   └── trainer_core/
├── tests/
│   ├── unit/              # Test core itself
│   └── integration/       # Test modules together
│       ├── test_prompt_llm_integration.py
│       ├── test_data_retriever_integration.py
│       └── test_full_workflow.py
└── pyproject.toml
    dependencies = [
        "trainer-prompt-manager",
        "trainer-llm-provider",
        "trainer-data-retriever",
        # All modules installed here
    ]
```

`trainer-core` installs all modules as dependencies, so integration tests can import and test them together.

#### Option 2: Dedicated Integration Test Repository

```
trainer-integration-tests/
├── tests/
│   ├── test_prompt_manager_llm_provider.py
│   ├── test_data_retriever_format_converter.py
│   └── test_end_to_end.py
└── pyproject.toml
    dependencies = [
        "trainer-prompt-manager",
        "trainer-llm-provider",
        "trainer-data-retriever",
        "trainer-format-converter",
        "trainer-test-agent",  # Test-agent can run these!
    ]
```

### Test-Agent Architecture for Integration

The test-agent operates in different modes:

```python
class TestAgent:
    def __init__(self, mode: str = "isolated"):
        self.mode = mode  # "isolated" or "integration"
    
    def run_integration_tests(self, modules: List[str]):
        """Test modules together"""
        # 1. Check if modules are installed
        installed_modules = self._check_installed_modules(modules)
        
        if not all(installed_modules):
            missing = [m for m, installed in zip(modules, installed_modules) 
                      if not installed]
            raise ValueError(f"Modules not installed: {missing}")
        
        # 2. Discover integration test files
        # Look for tests/integration/ directory
        integration_tests = self._discover_integration_tests()
        
        # 3. Run tests with all modules available
        return self._run_tests(integration_tests, use_real_implementations=True)
    
    def _check_installed_modules(self, modules: List[str]) -> List[bool]:
        """Check if modules are installed via pip"""
        results = []
        for module in modules:
            try:
                importlib.import_module(module.replace("-", "_"))
                results.append(True)
            except ImportError:
                results.append(False)
        return results
```

### Practical Workflow

#### Development Phase (Isolated)

```bash
# Developer working on prompt-manager
cd trainer-prompt-manager/

# Install only this module's dependencies
pip install -e ".[dev]"

# Run isolated tests (uses mocks)
test-agent run --module prompt-manager --mode isolated
```

#### Integration Phase (Together)

```bash
# In trainer-core or CI/CD
cd trainer-core/

# Install ALL modules
pip install trainer-prompt-manager
pip install trainer-llm-provider
pip install trainer-data-retriever
pip install -e ".[dev]"

# Run integration tests (uses real implementations)
test-agent run --mode integration --modules prompt-manager,llm-provider,data-retriever
```

### Test Discovery Strategy

Test-agent discovers tests differently based on mode:

```python
class TestAgent:
    def discover_tests(self, mode: str = "isolated"):
        if mode == "isolated":
            # Look for tests/ in current module only
            return self._discover_module_tests()
        
        elif mode == "integration":
            # Look for integration tests in:
            # 1. tests/integration/ in current repo
            # 2. Integration test repo if separate
            # 3. Cross-module test patterns
            return self._discover_integration_tests()
    
    def _discover_integration_tests(self):
        tests = []
        
        # Pattern 1: Integration tests in trainer-core
        if os.path.exists("tests/integration"):
            tests.extend(self._find_tests("tests/integration"))
        
        # Pattern 2: Integration test repo
        integration_repo = os.getenv("INTEGRATION_TESTS_REPO")
        if integration_repo:
            tests.extend(self._find_tests(f"{integration_repo}/tests"))
        
        # Pattern 3: Generate integration tests from module contracts
        tests.extend(self._generate_integration_tests())
        
        return tests
```

### Example: Integration Test Generation

Test-agent can generate integration tests by analyzing interfaces:

```python
class TestAgent:
    def generate_integration_tests(self, modules: List[str]):
        """Generate integration tests from module interfaces"""
        
        # 1. Import installed modules
        imported_modules = {}
        for module_name in modules:
            module = importlib.import_module(module_name.replace("-", "_"))
            imported_modules[module_name] = module
        
        # 2. Find interfaces between modules
        # e.g., prompt-manager uses LLMProvider interface
        interfaces = self._find_module_interfaces(imported_modules)
        
        # 3. Generate integration tests
        tests = []
        for interface in interfaces:
            # Test: prompt-manager works with any LLMProvider implementation
            test_code = f"""
def test_{interface['consumer']}_with_{interface['provider']}():
    from {interface['consumer_module']} import {interface['consumer_class']}
    from {interface['provider_module']} import {interface['provider_class']}
    
    # Create real instances
    provider = {interface['provider_class']}()
    consumer = {interface['consumer_class']}(provider)
    
    # Test integration
    result = consumer.execute("test")
    assert result is not None
"""
            tests.append(test_code)
        
        return tests
```

### CI/CD Strategy

#### Per-Module CI (Isolated Testing)

```yaml
# .github/workflows/prompt-manager.yml (in prompt-manager repo)
name: Test prompt-manager
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run isolated tests
        run: test-agent run --module prompt-manager --mode isolated
```

#### Integration CI (Together Testing)

```yaml
# .github/workflows/integration.yml (in trainer-core repo)
name: Integration Tests
on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:
jobs:
  integration-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install all modules
        run: |
          pip install trainer-prompt-manager
          pip install trainer-llm-provider
          pip install trainer-data-retriever
          pip install trainer-format-converter
          pip install -e ".[dev]"
      - name: Run integration tests
        run: test-agent run --mode integration
```

### Recommended Structure

```
# Separate repos for development
trainer-prompt-manager/     # Own tests (isolated)
trainer-llm-provider/       # Own tests (isolated)
trainer-data-retriever/     # Own tests (isolated)

# Integration layer
trainer-core/               # Integration tests (together)
  tests/
    integration/
      test_prompt_llm.py    # Tests prompt-manager + llm-provider
      test_full_workflow.py # Tests all modules

# Or separate integration repo
trainer-integration-tests/  # Dedicated integration tests
  tests/
    test_all_modules.py
```

### Key Insights

1. **Integration tests live where modules come together** - Either in `trainer-core` or a dedicated integration repo
2. **Test-agent has two modes**:
   - Isolated: Tests one module with mocks
   - Integration: Tests modules together when installed
3. **Test discovery** - Looks for `tests/integration/` when in integration mode
4. **Dependency check** - Verifies modules are installed before integration testing
5. **CI/CD separation** - Separate pipelines for isolated (per-module) and integration (together)

---

## Part 2: Consistent Release Management

### The Challenge

When you release `trainer-core v1.0.0`, you need:
- `trainer-prompt-manager v1.0.0` (compatible)
- `trainer-llm-provider v1.0.0` (compatible)
- `trainer-data-retriever v1.0.0` (compatible)
- All tested together
- All published to PyPI

But modules are developed independently—how do you coordinate?

### Solution 1: Version Catalog / Manifest (Recommended)

Create a central version manifest that defines compatible versions:

```yaml
# versions.yaml (in trainer-core or separate repo)
trainer:
  version: "1.0.0"  # Overall suite version
  
modules:
  prompt-manager: "1.0.0"
  llm-provider: "1.0.0"
  data-retriever: "1.0.0"
  format-converter: "1.0.0"
  test-agent: "1.0.0"

compatibility:
  "1.0.0":
    prompt-manager: "1.0.0"
    llm-provider: "1.0.0"
    data-retriever: "1.0.0"
    format-converter: "1.0.0"
    test-agent: "1.0.0"
  
  "1.1.0":
    prompt-manager: "1.1.0"
    llm-provider: "1.0.1"  # Patch update
    data-retriever: "1.1.0"
    format-converter: "1.0.0"  # No change
    test-agent: "1.0.1"
```

#### Usage in trainer-core:

```python
# trainer-core/pyproject.toml
[tool.trainer.versions]
# Read from versions.yaml
prompt-manager = "1.0.0"
llm-provider = "1.0.0"
data-retriever = "1.0.0"
format-converter = "1.0.0"
```

### Solution 2: Release Automation Script

Automated release script that coordinates everything:

```python
# scripts/release.py
import subprocess
import yaml
from pathlib import Path

class ReleaseManager:
    def __init__(self, version: str):
        self.version = version
        self.versions = self._load_versions()
    
    def release_all(self):
        """Release all modules in correct order"""
        # 1. Update versions in all modules
        self._update_versions()
        
        # 2. Run tests for each module
        self._test_modules()
        
        # 3. Run integration tests
        self._test_integration()
        
        # 4. Build packages
        self._build_packages()
        
        # 5. Publish to PyPI (in dependency order)
        self._publish_packages()
        
        # 6. Create git tags
        self._tag_releases()
    
    def _update_versions(self):
        """Update version in all module pyproject.toml files"""
        modules = [
            "trainer-prompt-manager",
            "trainer-llm-provider",
            "trainer-data-retriever",
            "trainer-format-converter",
            "trainer-test-agent",
        ]
        
        for module in modules:
            version = self.versions['modules'][module]
            self._update_module_version(module, version)
    
    def _publish_packages(self):
        """Publish in dependency order"""
        # Order: dependencies first, dependents last
        order = [
            "trainer-prompt-manager",    # No dependencies
            "trainer-llm-provider",      # No dependencies
            "trainer-data-retriever",    # No dependencies
            "trainer-format-converter",  # No dependencies
            "trainer-test-agent",        # Depends on others
            "trainer-core",              # Depends on all
        ]
        
        for module in order:
            print(f"Publishing {module}...")
            subprocess.run([
                "python", "-m", "build",
                f"packages/{module}"
            ])
            subprocess.run([
                "twine", "upload", 
                f"packages/{module}/dist/*"
            ])
```

### Solution 3: Monorepo with Workspace Management

If using a monorepo, use workspace tools:

#### Using Poetry Workspaces:

```toml
# pyproject.toml (root)
[tool.poetry]
name = "trainer-workspace"
version = "1.0.0"

[tool.poetry.dependencies]
# Shared dependencies

[tool.poetry.group.dev.dependencies]
trainer-prompt-manager = {path = "packages/prompt-manager", develop = true}
trainer-llm-provider = {path = "packages/llm-provider", develop = true}
trainer-data-retriever = {path = "packages/data-retriever", develop = true}
trainer-core = {path = "apps/core", develop = true}
```

#### Using Python's PEP 621 with version sync:

```python
# scripts/sync_versions.py
import toml
from pathlib import Path

def sync_versions(target_version: str):
    """Sync version across all modules"""
    modules = Path("packages").glob("*/pyproject.toml")
    
    for module_file in modules:
        data = toml.load(module_file)
        data['project']['version'] = target_version
        toml.dump(data, module_file)
        print(f"Updated {module_file} to {target_version}")
```

### Solution 4: CI/CD Release Pipeline

Automated release via CI/CD:

```yaml
# .github/workflows/release.yml
name: Release Suite
on:
  push:
    tags:
      - 'v*.*.*'  # Trigger on version tag

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Extract version
        id: version
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT
      
      - name: Sync versions
        run: |
          python scripts/sync_versions.py ${{ steps.version.outputs.version }}
      
      - name: Test all modules
        run: |
          for module in packages/*/; do
            cd $module
            pytest
            cd ../..
          done
      
      - name: Test integration
        run: |
          pip install -e packages/prompt-manager
          pip install -e packages/llm-provider
          pip install -e packages/data-retriever
          pytest tests/integration
      
      - name: Build packages
        run: |
          for module in packages/*/; do
            cd $module
            python -m build
            cd ../..
          done
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          # Publish in dependency order
          twine upload packages/prompt-manager/dist/*
          twine upload packages/llm-provider/dist/*
          twine upload packages/data-retriever/dist/*
          twine upload packages/format-converter/dist/*
          twine upload packages/test-agent/dist/*
          twine upload apps/core/dist/*
```

### Solution 5: Version Ranges with Compatibility Testing

Use version ranges and test compatibility:

```python
# trainer-core/pyproject.toml
[project]
dependencies = [
    "trainer-prompt-manager>=1.0.0,<2.0.0",
    "trainer-llm-provider>=1.0.0,<2.0.0",
    "trainer-data-retriever>=1.0.0,<2.0.0",
]

# But test with specific versions
[tool.trainer.test-versions]
prompt-manager = "1.0.0"
llm-provider = "1.0.0"
data-retriever = "1.0.0"
```

```python
# scripts/test_compatibility.py
def test_version_compatibility():
    """Test that declared versions work together"""
    versions = load_test_versions()
    
    # Install specific versions
    for module, version in versions.items():
        subprocess.run([
            "pip", "install", 
            f"{module}=={version}"
        ])
    
    # Run integration tests
    subprocess.run(["pytest", "tests/integration"])
```

### Solution 6: Release Manifest File

Create a release manifest that gets published:

```json
// trainer-core-1.0.0-manifest.json
{
  "suite_version": "1.0.0",
  "released_at": "2024-01-15T10:00:00Z",
  "modules": {
    "trainer-prompt-manager": {
      "version": "1.0.0",
      "pypi_url": "https://pypi.org/project/trainer-prompt-manager/1.0.0/"
    },
    "trainer-llm-provider": {
      "version": "1.0.0",
      "pypi_url": "https://pypi.org/project/trainer-llm-provider/1.0.0/"
    },
    "trainer-data-retriever": {
      "version": "1.0.0",
      "pypi_url": "https://pypi.org/project/trainer-data-retriever/1.0.0/"
    }
  },
  "tested_with": {
    "python": "3.9, 3.10, 3.11",
    "platforms": ["linux", "macos", "windows"]
  }
}
```

Users can verify they have compatible versions:

```python
# trainer-core/src/trainer_core/__init__.py
import json
from pathlib import Path

def check_version_compatibility():
    """Check if installed modules match release manifest"""
    manifest = json.load(Path(__file__).parent / "manifest.json")
    
    for module_name, expected in manifest['modules'].items():
        installed = importlib.metadata.version(module_name)
        if installed != expected['version']:
            raise VersionMismatchError(
                f"{module_name}: expected {expected['version']}, "
                f"got {installed}"
            )
```

### Recommended Approach: Hybrid

Combine multiple strategies:

#### 1. Development: Monorepo with workspace
```
trainer/
├── packages/          # All modules
├── scripts/
│   ├── sync_versions.py
│   └── release.py
├── versions.yaml      # Single source of truth
└── .github/workflows/
    └── release.yml
```

#### 2. Version Management:

```python
# scripts/release_manager.py
class ReleaseManager:
    def __init__(self):
        self.versions = self._load_versions_yaml()
    
    def prepare_release(self, suite_version: str):
        """Prepare all modules for release"""
        # 1. Update versions.yaml
        self._update_versions_yaml(suite_version)
        
        # 2. Sync versions to all pyproject.toml
        self._sync_pyproject_versions()
        
        # 3. Update trainer-core dependencies
        self._update_core_dependencies()
        
        # 4. Run full test suite
        self._run_tests()
        
        # 5. Create release commit
        self._create_release_commit(suite_version)
        
        # 6. Create git tag
        self._create_git_tag(f"v{suite_version}")
    
    def execute_release(self):
        """Actually publish to PyPI"""
        # Publish in order
        for module in self._dependency_order():
            self._publish_module(module)
```

#### 3. Usage:

```bash
# Prepare release
python scripts/release_manager.py prepare 1.0.0

# Review changes, then execute
python scripts/release_manager.py execute 1.0.0

# Or use CI/CD (safer)
git tag v1.0.0
git push origin v1.0.0  # Triggers release workflow
```

### Best Practices Summary

1. **Single source of truth**: `versions.yaml` defines compatible versions
2. **Automated sync**: Scripts sync versions across modules
3. **Dependency order**: Publish dependencies before dependents
4. **Integration testing**: Test all versions together before release
5. **Version manifest**: Publish manifest with each release
6. **CI/CD automation**: Automate the release process
7. **Semantic versioning**: Use semver consistently

### Example Workflow

```bash
# 1. Update versions.yaml
vim versions.yaml  # Set all to 1.0.0

# 2. Run release script
python scripts/release_manager.py prepare 1.0.0

# 3. Review changes
git diff

# 4. Commit and tag
git add .
git commit -m "Release v1.0.0"
git tag v1.0.0

# 5. Push (triggers CI/CD)
git push origin main --tags

# 6. CI/CD automatically:
#    - Tests all modules
#    - Tests integration
#    - Builds packages
#    - Publishes to PyPI in order
#    - Creates GitHub release
```

---

## Summary

### Testing Independent Modules

- **Integration tests** live where modules come together (`trainer-core` or dedicated repo)
- **Test-agent** has two modes: isolated (per-module) and integration (together)
- **Modules are installed** as dependencies for integration testing
- **CI/CD separation** between isolated and integration tests

### Release Management

- **Version catalog** (`versions.yaml`) as single source of truth
- **Automated release scripts** to sync versions and coordinate publishing
- **Dependency order** for publishing (dependencies before dependents)
- **Integration testing** before release to ensure compatibility
- **CI/CD automation** for consistent, repeatable releases
- **Release manifests** for version verification

This approach ensures that independently developed modules can be tested together and released consistently with aligned versions.

