# Project Modularization Analysis

## Executive Summary

This document analyzes the current workflow of the trainer project and proposes a modular architecture that separates concerns into reusable, independently-packaged components. The goal is to transform this static POC into a generalized framework that can be used both for static site generation and as a foundation for more dynamic applications.

## Current Workflow Analysis

### Workflow Overview

The project follows a clear, linear workflow:

```
Context Files (information/context/)
    ↓
Data Retrieval (output/json/)
    ↓
Instruction Prompts (information/instructions/)
    ↓
Prompt Execution (with contexts + data)
    ↓
Markdown Output (output/report/)
    ↓
Format Conversion (output/html/, output/pdf/)
```

### Current Architecture Components

1. **Context Management**
   - Location: `information/context/`
   - Structure: Topic-organized markdown files (e.g., `biotech/01-introduction.md`, `molecular-biology-foundations.md`)
   - Purpose: Provide domain knowledge and background information
   - Usage: Referenced in instruction prompts via file paths

2. **Data Retrieval**
   - Location: `output/json/`
   - Method: Browser automation (MCP tools) scraping Yahoo Finance
   - Format: Structured JSON with financial metrics
   - Naming: Timestamped files (`stock_data_YYYYMMDD_HHMMSS.json`)

3. **Instruction Prompts**
   - Location: `information/instructions/`
   - Structure: Markdown templates with:
     - Context file references
     - Analysis framework definitions
     - Output format requirements
     - Quality standards
   - Examples: `prompt-for-biotech-single-company.md`, `company-metrics-table-prompt.md`

4. **Prompt Execution**
   - Current: Manual execution via AI assistant (Cursor)
   - Process: Load contexts + load data + fill instruction template + execute
   - Output: Markdown reports

5. **Format Conversion**
   - Input: Markdown reports (`output/report/*.md`)
   - Output: HTML (`output/html/*.html`), PDF (`output/pdf/`)
   - Method: Manual conversion following templates
   - Styling: Shared CSS (`output/css/report.css`)

### Strengths of Current Approach

✅ **Clear separation** between contexts, instructions, and data  
✅ **File-based** - easy to version control and review  
✅ **Reproducible** - same inputs produce same outputs  
✅ **Static-friendly** - perfect for GitHub Pages deployment  
✅ **Human-readable** - all prompts and contexts in markdown  

### Limitations

❌ **Manual execution** - requires AI assistant interaction  
❌ **No caching** - contexts reloaded each time  
❌ **No prompt composition** - static templates only  
❌ **Single provider** - tied to Cursor's AI assistant  
❌ **No programmatic API** - can't be called from scripts  
❌ **No validation** - no checks for missing contexts/data  

---

## Proposed Modular Architecture

### Module 1: Prompt Management System (`prompt-manager`)

**Purpose**: Handle prompt loading, parameter filling, dynamic composition, and cache management.

**Core Responsibilities**:
- Load prompts from filesystem
- Load context files and merge them
- Fill template parameters (e.g., `{COMPANY_NAME}`, `{TICKER}`)
- Compose prompts dynamically (combine multiple templates)
- Manage prompt cache to avoid hallucinations
- Validate prompt completeness (check referenced contexts exist)
- Version prompts and track changes

**API Design**:
```python
class PromptManager:
    def load_prompt(self, prompt_path: str) -> PromptTemplate
    def load_contexts(self, context_paths: List[str]) -> str
    def fill_template(self, template: PromptTemplate, params: Dict[str, Any]) -> str
    def compose(self, templates: List[PromptTemplate], strategy: str) -> str
    def get_cached(self, prompt_id: str) -> Optional[str]
    def cache_prompt(self, prompt_id: str, content: str, ttl: int)
    def validate(self, prompt: str) -> ValidationResult
```

**Features**:
- **Template Engine**: Support for variable substitution (`{variable}`)
- **Context Merging**: Intelligently combine multiple context files
- **Composition Strategies**: Sequential, parallel, hierarchical composition
- **Cache Management**: LRU cache with TTL, cache invalidation on file changes
- **Validation**: Check for missing variables, broken references, circular dependencies

**Package Structure**:
```
prompt-manager/
├── src/
│   ├── prompt_manager/
│   │   ├── loader.py          # File loading
│   │   ├── template.py         # Template engine
│   │   ├── composer.py         # Dynamic composition
│   │   ├── cache.py            # Cache management
│   │   └── validator.py        # Validation
│   └── tests/
├── pyproject.toml
└── README.md
```

**Dependencies**: None (pure Python, filesystem operations)

**Reusability**: High - can be used in any project requiring prompt management

---

### Module 2: LLM Provider Abstraction (`llm-provider`)

**Purpose**: Abstract interface for different LLM providers (cloud, local, etc.), leveraging existing libraries where possible.

**Rationale**: Rather than reinventing the wheel, this module builds upon proven solutions like **LiteLLM** (which supports 100+ LLM providers) while maintaining our own API design and adding custom features specific to our use case.

**Existing Solutions**:
- **LiteLLM**: Universal interface for 100+ LLM APIs (OpenAI, Anthropic, AWS Bedrock, Azure, Google Vertex AI, Ollama, etc.)
- **LangChain**: Comprehensive framework with LLM abstractions (heavier, focused on chains/agents)
- **LlamaIndex**: LLM abstractions focused on RAG/retrieval

**Our Approach**: **Hybrid** - Use LiteLLM as the foundation, wrap it with our own abstraction layer to:
- Maintain our specific API design
- Add custom features (prompt caching, validation, etc.)
- Provide flexibility to implement providers directly when needed
- Keep dependencies minimal and controlled

**Core Responsibilities**:
- Unified API for multiple providers (via LiteLLM wrapper)
- Custom API design tailored to our needs
- Request/response handling with our CompletionResult format
- Error handling and retries (leveraging LiteLLM's built-in retries)
- Rate limiting (via LiteLLM)
- Cost tracking (via LiteLLM + custom tracking)
- Streaming support
- Optional direct provider implementations for special cases

**API Design**:
```python
class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> CompletionResult
    
    @abstractmethod
    def stream(self, prompt: str, **kwargs) -> Iterator[str]
    
    @abstractmethod
    def get_cost(self, tokens: int) -> float
    
    # Optional provider-specific methods
    def list_models(self) -> List[str]:
        """List available models (Bedrock, Vertex AI, etc.)"""
        raise NotImplementedError
    
    def deploy_model(self, model_path: str, **kwargs) -> str:
        """Deploy custom model (SageMaker, Vertex AI)"""
        raise NotImplementedError

class CompletionResult:
    content: str
    tokens_used: int
    model: str
    provider: str
    cost: float
    metadata: Dict[str, Any]
```

**Implementation Strategy**:

Most providers use LiteLLM wrapper:
```python
from litellm import completion
from llm_provider.base import LLMProvider, CompletionResult

class LiteLLMProvider(LLMProvider):
    """Base wrapper around LiteLLM for our specific needs"""
    
    def __init__(self, provider: str, model: str, **kwargs):
        self.provider = provider
        self.model = model
        self.config = kwargs
    
    def complete(self, prompt: str, **kwargs) -> CompletionResult:
        # Use LiteLLM under the hood
        response = completion(
            model=f"{self.provider}/{self.model}",
            messages=[{"role": "user", "content": prompt}],
            **self.config,
            **kwargs
        )
        
        # Convert to our CompletionResult format
        return CompletionResult(
            content=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens,
            model=self.model,
            provider=self.provider,
            cost=self._calculate_cost(response.usage.total_tokens),
            metadata=response.model_dump()
        )
```

Specific providers inherit from LiteLLM wrapper:
```python
class OpenAIProvider(LiteLLMProvider):
    """OpenAI via LiteLLM"""
    def __init__(self, model: str = "gpt-4", **kwargs):
        super().__init__(provider="openai", model=model, **kwargs)

class AWSBedrockProvider(LiteLLMProvider):
    """AWS Bedrock via LiteLLM"""
    def __init__(self, model: str, region: str = "us-east-1", **kwargs):
        super().__init__(
            provider="bedrock",
            model=model,
            aws_region_name=region,
            **kwargs
        )
```

Direct implementations for special cases:
```python
class AWSSageMakerProvider(LLMProvider):
    """SageMaker endpoints - direct implementation for custom logic"""
    def __init__(self, endpoint_name: str, region: str):
        # Direct boto3 implementation for custom endpoints
        self.client = boto3.client('sagemaker-runtime', region_name=region)
        self.endpoint_name = endpoint_name
    
    def complete(self, prompt: str, **kwargs) -> CompletionResult:
        # Custom SageMaker invocation logic
        ...
```

**Cloud Provider Architecture**:

All cloud providers (AWS Bedrock, SageMaker, Google Vertex AI, Azure) fit within the same abstraction because they share the core capability: **LLM inference/completion**. 

**Implementation via LiteLLM**: Most cloud providers are implemented using LiteLLM, which handles:
- **Unified Interface**: All providers accept prompts and return completions
- **Authentication**: Provider-specific auth (AWS IAM, Google service accounts, Azure API keys)
- **Model Selection**: Dynamic model selection for multi-model providers
- **Error Handling**: Built-in retries and error handling
- **Cost Tracking**: Automatic cost calculation per provider

**Direct Implementation**: Some providers (like SageMaker custom endpoints) may require direct implementation for:
- **Custom Deployments**: SageMaker endpoints with custom inference logic
- **Special Requirements**: Providers needing custom request/response handling
- **Performance**: Direct implementation for performance-critical use cases

**Key Considerations**:

1. **AWS Bedrock**: Managed service accessing multiple foundation models (Claude, Llama, Titan). Requires AWS credentials and region selection.

2. **Amazon SageMaker**: Custom model endpoints deployed by the user. Still fits the abstraction because it provides the same prompt → completion interface, just with self-hosted models. Useful for fine-tuned models or proprietary models.

3. **Google Vertex AI**: Similar to Bedrock, provides access to Gemini, PaLM, and custom models. Supports batch prediction and custom tuning.

4. **Azure OpenAI & AI Services**: Microsoft's managed LLM services with integration to other Azure services.

**Authentication Handling**:

Most providers handle authentication via LiteLLM (which auto-detects from environment or accepts credentials):

```python
# AWS Bedrock - LiteLLM handles boto3/IAM automatically
class AWSBedrockProvider(LiteLLMProvider):
    def __init__(self, model: str, region: str = "us-east-1", **kwargs):
        # LiteLLM auto-detects AWS credentials from environment
        # or accepts explicit credentials via kwargs
        super().__init__(
            provider="bedrock",
            model=model,
            aws_region_name=region,
            **kwargs
        )

# Google Vertex AI - LiteLLM handles service account JSON
class GoogleVertexProvider(LiteLLMProvider):
    def __init__(self, model: str, project_id: str, **kwargs):
        # LiteLLM auto-detects from GOOGLE_APPLICATION_CREDENTIALS
        # or accepts credentials_path
        super().__init__(
            provider="vertex_ai",
            model=model,
            vertex_project=project_id,
            **kwargs
        )

# Azure OpenAI - LiteLLM handles API keys/Azure AD
class AzureOpenAIProvider(LiteLLMProvider):
    def __init__(self, model: str, endpoint: str, api_key: Optional[str] = None):
        # LiteLLM handles Azure authentication
        super().__init__(
            provider="azure",
            model=model,
            api_base=endpoint,
            api_key=api_key,  # Or auto-detects from environment
        )

# Direct implementation for SageMaker (custom logic)
class AWSSageMakerProvider(LLMProvider):
    def __init__(self, endpoint_name: str, region: str):
        # Direct boto3 for custom SageMaker endpoints
        import boto3
        self.client = boto3.client('sagemaker-runtime', region_name=region)
        self.endpoint_name = endpoint_name
```

**Provider Implementations**:

*Via LiteLLM Wrapper* (most providers):
- `OpenAIProvider` - GPT-4, GPT-3.5 (via LiteLLM)
- `AnthropicProvider` - Claude 3 (via LiteLLM)
- `OllamaProvider` - Local models (via LiteLLM)
- `AWSBedrockProvider` - AWS Bedrock (via LiteLLM)
- `GoogleVertexProvider` - Google Vertex AI (via LiteLLM)
- `AzureOpenAIProvider` - Azure OpenAI Service (via LiteLLM)
- `HuggingFaceProvider` - HuggingFace models (via LiteLLM)

*Direct Implementations* (special cases):
- `AWSSageMakerProvider` - Amazon SageMaker endpoints (custom fine-tuned models, direct boto3)
- Custom endpoints requiring special logic

*Extensibility*:
- `CustomProvider` - Plugin system for new providers
- Can implement directly or via LiteLLM wrapper

**Benefits of Hybrid Approach**:
- ✅ **Leverage LiteLLM**: 100+ providers supported out of the box
- ✅ **Our API Design**: Maintain our CompletionResult format and interface
- ✅ **Custom Features**: Add prompt caching, validation, custom retry logic
- ✅ **Flexibility**: Can implement directly when LiteLLM doesn't fit
- ✅ **Less Maintenance**: Don't need to maintain provider-specific code
- ✅ **Future-Proof**: Can swap LiteLLM for another library if needed

**Features**:
- **Provider Switching**: Change providers without code changes
- **Fallback**: Automatic fallback if primary provider fails
- **Cost Tracking**: Track token usage and costs per provider
- **Streaming**: Support for streaming responses
- **Configuration**: YAML/JSON config for API keys, models, etc.
- **Cloud Integration**: Native support for AWS, Google Cloud, and Azure
- **Custom Models**: Support for self-hosted and fine-tuned models via SageMaker/Vertex AI
- **Model Selection**: Dynamic model selection for providers with multiple models (Bedrock, Vertex AI)

**Package Structure**:
```
llm-provider/
├── src/
│   ├── llm_provider/
│   │   ├── base.py                    # Abstract base class
│   │   ├── litellm_wrapper.py         # LiteLLM wrapper base class
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── litellm_based/         # Providers using LiteLLM
│   │   │   │   ├── openai_provider.py
│   │   │   │   ├── anthropic_provider.py
│   │   │   │   ├── ollama_provider.py
│   │   │   │   ├── aws_bedrock_provider.py
│   │   │   │   ├── google_vertex_provider.py
│   │   │   │   └── azure_openai_provider.py
│   │   │   └── direct/                # Direct implementations
│   │   │       └── aws_sagemaker_provider.py
│   │   ├── registry.py              # Provider factory/registry
│   │   ├── config.py                # Configuration management
│   │   └── utils.py                 # Common utilities
│   └── tests/
├── pyproject.toml
└── README.md
```

**Dependencies**: 
- `litellm>=1.0.0` - **Core dependency** - Universal LLM interface (supports 100+ providers)
- `boto3>=1.28.0` (optional) - For AWS SageMaker direct implementation
- `google-cloud-aiplatform` (optional) - For Google Vertex AI direct implementation (if needed)
- `azure-identity` (optional) - For Azure direct implementation (if needed)

**Note**: LiteLLM handles most provider SDKs internally (OpenAI, Anthropic, Ollama, etc.), so we don't need to declare them as direct dependencies. Only declare SDKs needed for direct implementations (like SageMaker).

**Reusability**: Very High - core abstraction for any LLM application

---

### Module 3: Data Retrieval Abstraction (`data-retriever`)

**Purpose**: Abstract interface for data retrieval from various sources.

**Core Responsibilities**:
- Unified API for different data sources
- Source-specific implementations (Yahoo Finance, SEC filings, APIs, etc.)
- Data transformation and normalization
- Caching retrieved data
- Rate limiting and error handling

**API Design**:
```python
class DataRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: Dict[str, Any]) -> RetrievalResult
    
    @abstractmethod
    def get_schema(self) -> Schema

class RetrievalResult:
    data: Dict[str, Any]
    source: str
    retrieved_at: datetime
    metadata: Dict[str, Any]
```

**Source Implementations**:
- `YahooFinanceRetriever` - Browser automation or API
- `SECFilingsRetriever` - SEC EDGAR database
- `APIRetriever` - Generic REST API wrapper
- `DatabaseRetriever` - SQL database queries
- `FileRetriever` - Local file system

**Features**:
- **Source Abstraction**: Switch data sources easily
- **Normalization**: Convert to common schema
- **Caching**: Cache responses to avoid redundant requests
- **Validation**: Schema validation for retrieved data
- **Error Handling**: Graceful degradation

**Package Structure**:
```
data-retriever/
├── src/
│   ├── data_retriever/
│   │   ├── base.py
│   │   ├── yahoo_finance.py
│   │   ├── sec_filings.py
│   │   ├── api_retriever.py
│   │   ├── schema.py           # Common schemas
│   │   └── cache.py
│   └── tests/
├── pyproject.toml
└── README.md
```

**Dependencies**: 
- Browser automation tools (for Yahoo Finance)
- `requests` (for APIs)
- `pandas` (for data manipulation)

**Reusability**: High - can be used for any data retrieval needs

---

### Module 4: Format Conversion System (`format-converter`)

**Purpose**: Convert between different output formats (Markdown, HTML, PDF, JSON, etc.) with support for structured data and auto-detection.

**Core Responsibilities**:
- Convert markdown to HTML/PDF/LaTeX/DOCX
- Convert JSON to Markdown (schema-aware)
- Convert Markdown to JSON (with heuristics)
- Auto-detect input format (MD vs JSON)
- Apply templates and styling
- Support custom CSS/theme injection
- Handle complex markdown features (tables, code blocks, etc.)
- Support structured LLM outputs (JSON responses)

**API Design**:
```python
class FormatConverter:
    def convert(self, source: Union[str, Dict[str, Any]], 
                source_format: str = "auto",  # "markdown", "json", "text", "auto"
                target_format: str,           # "html", "pdf", "markdown", "json", "latex", "docx"
                **options) -> Union[str, bytes]
    
    def json_to_markdown(self, json_data: Dict[str, Any], 
                        schema: Optional[Schema] = None,
                        template: Optional[str] = None) -> str
    """Convert JSON structure to markdown representation."""
    
    def markdown_to_json(self, markdown: str, 
                        schema: Optional[Schema] = None) -> Dict[str, Any]
    """Convert markdown to JSON structure (heuristic-based)."""
    
    def detect_format(self, content: Union[str, Dict[str, Any]]) -> str
    """Auto-detect format of input content."""
    
    def apply_template(self, content: str, template_path: str) -> str
    def apply_styles(self, html: str, css_path: str) -> str
    def extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]
    """Extract JSON from text (handles code blocks, etc.)."""
```

**Supported Conversions**:
- Markdown → HTML
- Markdown → PDF
- Markdown → JSON (heuristic-based)
- JSON → Markdown (schema-aware)
- JSON → HTML/PDF (via Markdown)
- HTML → PDF
- Markdown → LaTeX
- Markdown → DOCX
- Auto-detection of input format

**Features**:
- **Auto-Detection**: Automatically detect MD vs JSON input
- **Schema-Aware Conversion**: Use schemas to guide JSON → MD conversion
- **Bidirectional Conversion**: MD ↔ JSON round-trip support
- **Structured Output Support**: Handle LLM JSON responses gracefully
- **Template Support**: Apply HTML templates
- **CSS Injection**: Inject stylesheets
- **Custom Renderers**: Extensible renderer system
- **Metadata Extraction**: Extract frontmatter/metadata
- **Asset Handling**: Handle images, fonts, etc.
- **Error Handling**: Graceful degradation for malformed inputs

**Package Structure**:
```
format-converter/
├── src/
│   ├── format_converter/
│   │   ├── __init__.py
│   │   ├── converter.py              # Main converter class
│   │   ├── detector.py               # Format auto-detection
│   │   ├── metrics.py                 # Prometheus metrics
│   │   ├── converters/
│   │   │   ├── __init__.py
│   │   │   ├── markdown_to_html.py
│   │   │   ├── markdown_to_pdf.py
│   │   │   ├── json_to_markdown.py   # Schema-aware JSON→MD
│   │   │   ├── markdown_to_json.py   # MD→JSON with heuristics
│   │   │   └── json_extractor.py     # Extract JSON from text
│   │   ├── template_engine.py        # Template system
│   │   └── schemas.py                # Schema definitions for conversion
│   └── tests/
├── examples/
│   ├── basic_usage.py
│   ├── json_conversion.py
│   ├── integration_all_modules.py
│   └── README.md
├── api_service.py                    # FastAPI service with metrics
├── pyproject.toml
└── README.md
```

**Dependencies**:
- `markdown` or `markdown-it-py` - Markdown parsing
- `weasyprint` - PDF generation (better CSS support than pdfkit)
- `jinja2` - Template engine
- `pydantic` (optional) - Schema validation
- `prometheus-client` - Metrics collection
- `fastapi` + `uvicorn` - API service

**Reusability**: Very High - general-purpose format conversion with structured data support

---

### Module 5: Training Integration (`model-trainer`) - Optional

**Purpose**: Integrate with local model training pipelines.

**Core Responsibilities**:
- Prepare training data from prompts and outputs
- Integrate with training frameworks (HuggingFace, PyTorch, etc.)
- Track training metrics
- Version model checkpoints
- Evaluate model performance

**API Design**:
```python
class ModelTrainer:
    def prepare_dataset(self, prompts: List[str], outputs: List[str]) -> Dataset
    def train(self, config: TrainingConfig) -> ModelCheckpoint
    def evaluate(self, model: Model, test_set: Dataset) -> Metrics
    def version_checkpoint(self, checkpoint: ModelCheckpoint) -> str
```

**Features**:
- **Data Preparation**: Convert prompts/outputs to training format
- **Framework Integration**: Support multiple training frameworks
- **Experiment Tracking**: Track hyperparameters and metrics
- **Model Versioning**: Version control for model checkpoints
- **Evaluation**: Automated evaluation pipelines

**Package Structure**:
```
model-trainer/
├── src/
│   ├── model_trainer/
│   │   ├── trainer.py
│   │   ├── data_prep.py
│   │   ├── evaluator.py
│   │   └── integrations/
│   └── tests/
├── pyproject.toml
└── README.md
```

**Dependencies**:
- `transformers` or `torch`
- `datasets` (HuggingFace)
- `wandb` or `mlflow` (for tracking)

**Reusability**: Medium - specific to training use cases

---

### Module 6: Testing Agent (`test-agent`)

**Purpose**: Automated testing framework for code and behavior validation across all modules.

**Core Responsibilities**:
- Test generation from code, docstrings, and type hints
- Test execution and discovery across modules
- Coverage analysis and reporting
- Integration testing for module interactions
- Mock/stub generation for external dependencies
- Behavior and end-to-end workflow testing
- Continuous testing with watch mode
- CI/CD integration

**API Design**:
```python
class TestAgent:
    def generate_tests(self, module_path: str, strategy: str = "comprehensive") -> List[Test]
    def run_tests(self, test_path: Optional[str] = None, 
                  module: Optional[str] = None) -> TestResults
    def run_integration_tests(self, modules: List[str]) -> TestResults
    def generate_mocks(self, dependencies: List[str]) -> Dict[str, Mock]
    def check_coverage(self, module: Optional[str] = None) -> CoverageReport
    def watch_and_test(self, module: str) -> None  # Auto-test on changes
    def validate_contracts(self, module: str, interface: Interface) -> ValidationResult

class TestResults:
    passed: int
    failed: int
    skipped: int
    duration: float
    failures: List[TestFailure]
    coverage: CoverageReport

class CoverageReport:
    percentage: float
    lines_covered: int
    lines_total: int
    branches_covered: int
    branches_total: int
    module_breakdown: Dict[str, float]
```

**Test Types Supported**:

1. **Unit Tests**: Test individual functions/classes in isolation
2. **Integration Tests**: Test module interactions and contracts
3. **Contract Tests**: Verify interfaces between modules
4. **End-to-End Tests**: Test full workflows (prompt → LLM → output → format conversion)
5. **Property-Based Tests**: Test invariants and properties
6. **Performance Tests**: Benchmark and regression detection
7. **Mock Tests**: Test with mocked external dependencies (LLM providers, APIs, etc.)

**Features**:
- **Auto-Test Generation**: Generate tests from docstrings, type hints, and code structure
- **Test Templates**: Pre-built templates for common patterns (provider tests, retriever tests, etc.)
- **Mock Library**: Pre-built mocks for LLM providers, data retrievers, file systems, etc.
- **Coverage Tracking**: Track coverage per module and overall project coverage
- **Continuous Testing**: Watch mode for auto-testing on file changes
- **Test Reports**: HTML/JSON reports with coverage, failures, and recommendations
- **Contract Validation**: Verify modules meet their interface contracts
- **Integration Testing**: Test module interactions automatically
- **CI/CD Integration**: Ready for GitHub Actions, GitLab CI, etc.

**Package Structure**:
```
test-agent/
├── src/
│   ├── test_agent/
│   │   ├── generator.py          # Test generation
│   │   ├── runner.py              # Test execution
│   │   ├── coverage.py            # Coverage analysis
│   │   ├── mocks.py               # Mock generation
│   │   ├── reporter.py            # Test reporting
│   │   ├── watcher.py             # File watching
│   │   ├── templates/             # Test templates
│   │   │   ├── provider_test.py.j2
│   │   │   ├── retriever_test.py.j2
│   │   │   └── integration_test.py.j2
│   │   └── mocks/                 # Pre-built mocks
│   │       ├── llm_provider_mock.py
│   │       ├── data_retriever_mock.py
│   │       └── file_system_mock.py
│   └── tests/
├── pyproject.toml
└── README.md
```

**Module Integration**:

Each module includes its own test directory:
```
prompt-manager/
├── src/
├── tests/              # Module-specific tests
│   ├── test_loader.py
│   ├── test_template.py
│   ├── test_composer.py
│   └── test_cache.py
└── .coverage.json

llm-provider/
├── src/
├── tests/
│   ├── test_openai_provider.py
│   ├── test_bedrock_provider.py
│   ├── test_sagemaker_provider.py
│   └── integration/
│       └── test_provider_switching.py
└── .coverage.json

data-retriever/
├── src/
├── tests/
│   ├── test_yahoo_finance.py
│   └── integration/
│       └── test_data_flow.py
└── .coverage.json
```

**Example Usage**:
```python
from test_agent import TestAgent

agent = TestAgent()

# Generate tests for a module
agent.generate_tests("prompt-manager", strategy="comprehensive")

# Run all tests
results = agent.run_tests()

# Run tests for specific module
module_results = agent.run_tests(module="llm-provider")

# Run integration tests
integration_results = agent.run_integration_tests([
    "prompt-manager",
    "llm-provider",
    "data-retriever"
])

# Check coverage
coverage = agent.check_coverage("llm-provider")
print(f"Coverage: {coverage.percentage}%")
print(f"Module breakdown: {coverage.module_breakdown}")

# Generate mocks for testing
mocks = agent.generate_mocks(["openai", "boto3", "requests"])

# Watch mode - auto-test on file changes
agent.watch_and_test("prompt-manager")

# Validate module contracts
validation = agent.validate_contracts(
    "llm-provider",
    interface=LLMProvider
)
```

**Agentic Testing Workflow**:

The testing agent integrates seamlessly with agentic development workflows:

1. **Code Change Detected**: Agent sees a module was modified
2. **Generate Tests**: Automatically create tests for new/changed code
3. **Run Tests**: Execute relevant tests (unit + integration)
4. **Check Coverage**: Ensure new code is adequately tested
5. **Integration Check**: Verify module still works with dependent modules
6. **Report Results**: Show test results, coverage, and suggest fixes
7. **Continuous Monitoring**: Watch mode keeps tests running on changes

**Benefits for Modular Architecture**:
- **Regression Prevention**: Catch breaking changes when modules are modified
- **Contract Validation**: Ensure modules meet their interface contracts
- **Integration Confidence**: Verify modules work together correctly
- **Documentation**: Tests serve as executable documentation
- **Refactoring Safety**: Enable safe refactoring with test coverage
- **CI/CD Ready**: Integrate with automated pipelines

**Dependencies**:
- `pytest` - Test framework
- `pytest-cov` - Coverage plugin
- `pytest-mock` - Mocking utilities
- `pytest-watch` - File watching
- `coverage` - Coverage analysis
- `hypothesis` (optional) - Property-based testing
- `faker` (optional) - Test data generation

**Reusability**: Very High - can be used for testing any Python project, not just trainer modules

---

### Module 7: Prompt Security System (`prompt-security`)

**Purpose**: Comprehensive security module for protecting against prompt injection attacks and validating user input in prompt templates.

**Core Responsibilities**:
- Input validation (length limits, character filtering, type checking)
- Input sanitization (control character removal, pattern blocking)
- Prompt injection detection (pattern matching, ML-based classification)
- Template escaping (safe variable insertion)
- Security logging and monitoring
- Risk scoring and threat assessment

**API Design**:
```python
class SecurityModule:
    def validate(self, user_input: Dict[str, Any]) -> Dict[str, Any]
    def sanitize(self, user_input: Dict[str, Any]) -> Dict[str, Any]
    def detect_injection(self, text: str) -> DetectionResult
    def escape(self, text: str, context: str = "template") -> str
    def validate_prompt(self, prompt: str) -> ValidationResult

class DetectionResult:
    is_safe: bool
    confidence: float
    flags: List[str]
    risk_score: float
    recommendations: List[str]

class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_input: Dict[str, Any]
```

**Features**:
- **Multi-Layer Defense**: Validation → Sanitization → Detection → Escaping
- **Pattern-Based Detection**: Regex patterns for common injection attempts
- **ML-Based Classification**: Optional ML classifier for advanced detection (future)
- **Configurable Security Levels**: Strict, moderate, permissive modes
- **Template Escaping**: Safe variable insertion with delimiters
- **Structured Templates**: Support for JSON/XML-based templating
- **Security Logging**: Comprehensive logging of security events
- **Rate Limiting**: Optional rate limiting per user/IP
- **Whitelist/Blacklist**: Configurable allowed/blocked patterns

**Package Structure**:
```
prompt-security/
├── src/
│   ├── prompt_security/
│   │   ├── __init__.py
│   │   ├── validator.py          # Input validation
│   │   ├── sanitizer.py           # Input sanitization
│   │   ├── detector.py             # Injection detection
│   │   ├── escaper.py             # Template escaping
│   │   ├── classifier.py          # ML-based detection (future)
│   │   ├── security_result.py     # Result types
│   │   ├── config.py              # Security configuration
│   │   └── patterns.py            # Injection patterns database
│   └── tests/
├── pyproject.toml
└── README.md
```

**Integration Points**:
- **PromptManager**: Integrated into template filling process
- **FastAPI Service**: Middleware for request validation
- **Express App**: Optional client-side validation
- **Template Engine**: Escaping layer during variable substitution
- **LLM Provider**: Pre-LLM prompt validation

**Dependencies**: 
- Pure Python (no external dependencies for core functionality)
- Optional: `scikit-learn` or `transformers` (for ML-based detection)
- Optional: `regex` (for advanced pattern matching)

**Reusability**: Very High - can be used in any prompt-based application, not just trainer modules

**Security Features**:
- **Input Length Limits**: Configurable max length per variable
- **Character Filtering**: Remove control characters, special sequences
- **Pattern Blocking**: Block common injection patterns (SYSTEM:, IGNORE, etc.)
- **Context Isolation**: Ensure user input doesn't override system instructions
- **Structured Delimiters**: Use XML/JSON tags for safe variable insertion
- **Validation Pipeline**: Multi-stage validation before template filling
- **Threat Detection**: Real-time detection of injection attempts
- **Security Metrics**: Track security events and threats

**Example Usage**:
```python
from prompt_security import SecurityModule
from prompt_manager import PromptManager, PromptTemplate

# Initialize security module
security = SecurityModule(
    max_length=1000,
    strict_mode=True,
    enable_ml_detection=False  # Future feature
)

# Use with PromptManager
manager = PromptManager(security_module=security)

# Template filling with automatic security
template = PromptTemplate("Hello {name}!")
filled = manager.fill_template(template, {"name": "World"})  # Automatically validated

# Direct security validation
result = security.validate({"name": "user input"})
if result.is_safe:
    # Use validated input
    pass
```

**Future Enhancements**:
- ML-based injection classifier
- Context-aware validation
- Advanced pattern learning
- Security agent for continuous monitoring
- Industry-standard security framework compliance

---

## Integration Architecture

### Core Application (`trainer-core`)

The main application that orchestrates all modules:

```python
from prompt_manager import PromptManager
from prompt_security import SecurityModule
from llm_provider import LLMProvider, OpenAIProvider
from data_retriever import DataRetriever, YahooFinanceRetriever
from format_converter import FormatConverter
from test_agent import TestAgent

class TrainerCore:
    def __init__(self):
        # Initialize security module
        self.security = SecurityModule(strict_mode=True)
        
        # Initialize prompt manager with security
        self.prompt_manager = PromptManager(
            context_dir="information/context",
            security_module=self.security
        )
        self.llm_provider = OpenAIProvider()
        self.data_retriever = YahooFinanceRetriever()
        self.format_converter = FormatConverter()
        self.test_agent = TestAgent()  # Optional, for development/testing
    
    def generate_report(self, 
                       instruction_path: str,
                       data_path: str,
                       output_format: str = "markdown"):
        # 1. Load instruction prompt
        instruction = self.prompt_manager.load_prompt(instruction_path)
        
        # 2. Load contexts referenced in instruction
        contexts = self.prompt_manager.load_contexts(
            instruction.get_context_refs()
        )
        
        # 3. Load data
        data = self.data_retriever.load_from_file(data_path)
        
        # 4. Compose full prompt
        full_prompt = self.prompt_manager.compose([
            contexts,
            instruction.fill_template({"data": data})
        ])
        
        # 5. Execute with LLM
        result = self.llm_provider.complete(full_prompt)
        
        # 6. Convert format if needed
        if output_format != "markdown":
            result = self.format_converter.convert(
                result, "markdown", output_format
            )
        
        return result
```

### Configuration

YAML configuration file:

```yaml
# config.yaml
prompt_manager:
  context_dir: "information/context"
  cache_enabled: true
  cache_ttl: 3600

llm_provider:
  provider: "openai"  # or "anthropic", "ollama", etc.
  model: "gpt-4"
  api_key: "${OPENAI_API_KEY}"
  temperature: 0.7

data_retriever:
  provider: "yahoo_finance"
  cache_enabled: true

format_converter:
  default_template: "templates/report.html"
  default_css: "output/css/report.css"

test_agent:
  enabled: true
  coverage_threshold: 80  # Minimum coverage percentage
  watch_mode: false
  auto_generate_tests: true
  test_framework: "pytest"

prompt_security:
  enabled: true
  strict_mode: true
  max_length: 1000  # Max characters per variable
  enable_ml_detection: false  # Future feature
  log_security_events: true
  rate_limiting:
    enabled: true
    requests_per_minute: 60
```

---

## Migration Strategy

### Phase 1: Extract Prompt Manager (Week 1-2)
1. Create `prompt-manager` package
2. Extract prompt loading logic
3. Implement template engine
4. Add caching
5. Update trainer to use new module
6. **Write tests** for prompt manager functionality

### Phase 2: Create Prompt Security Module (Week 3-4)
1. Create `prompt-security` package
2. Implement core security components:
   - Input validator (length, characters, types)
   - Input sanitizer (control chars, patterns)
   - Injection detector (pattern matching)
   - Template escaper (safe variable insertion)
3. Create security result types and configuration
4. Integrate with `prompt-manager` module
5. Add security to FastAPI service middleware
6. **Write tests** for security functionality
7. **Document** security best practices and threat model

### Phase 3: Extract LLM Provider (Week 5-6)
1. Create `llm-provider` package
2. Implement base abstraction
3. Add OpenAI provider
4. Add Ollama provider (for local)
5. Add cloud providers (AWS Bedrock, SageMaker, Vertex AI, Azure)
6. Update trainer to use new module
7. **Write tests** for each provider implementation

### Phase 4: Extract Data Retriever (Week 7-8)
1. Create `data-retriever` package
2. Extract Yahoo Finance logic
3. Add caching
4. Update trainer to use new module
5. **Write tests** for data retrieval and caching

### Phase 5: Extract Format Converter (Week 9-10)
1. Create `format-converter` package
2. Extract HTML conversion logic
3. Add PDF conversion
4. Update trainer to use new module
5. **Write tests** for format conversions

### Phase 6: Create Test Agent (Week 11-12)
1. Create `test-agent` package
2. Implement test generation
3. Implement test runner and coverage
4. Add mock library for common dependencies
5. Integrate with all modules
6. Set up CI/CD with automated testing
7. **Generate initial test suite** for all modules

### Phase 7: Refactor Core Application (Week 13-14)
1. Create `trainer-core` package
2. Integrate all modules (including security)
3. Add CLI interface
4. Add configuration management
5. **Run comprehensive test suite** via test-agent
6. **Achieve target coverage** (80%+)
7. **Security audit** of integrated system

### Phase 8: Optional Enhancements (Week 15+)
1. Add training integration module
2. Add web API (FastAPI) - already implemented
3. Add monitoring/logging - already implemented
4. Enhance CI/CD pipelines with test-agent
5. **Enhance security module** with ML-based detection
6. **Security agent** for continuous monitoring

---

## Benefits of Modularization

### 1. Reusability
- Each module can be used independently in other projects
- Prompt manager can be used for any prompt-based application
- **Prompt security module can be used in any prompt-based system**
- LLM provider can be used for any LLM application
- Format converter is general-purpose

### 2. Testability
- Each module can be tested in isolation
- Mock dependencies easily
- Faster test execution

### 3. Maintainability
- Clear separation of concerns
- Easier to understand and modify
- Smaller codebases per module

### 4. Scalability
- Add new providers without touching core logic
- Add new formats without changing other modules
- Parallel development possible

### 5. Flexibility
- Swap implementations easily
- Use different providers for different use cases
- Mix and match modules

### 6. Distribution
- Package each module separately
- Version independently
- Publish to PyPI

---

## Package Distribution Strategy

### Versioning
- Use semantic versioning (semver)
- Independent versioning per module
- Core application tracks compatible versions

### Publishing
- Publish to PyPI as separate packages:
  - `trainer-prompt-manager`
  - `trainer-prompt-security` (security module)
  - `trainer-llm-provider`
  - `trainer-data-retriever`
  - `trainer-format-converter`
  - `trainer-test-agent`
  - `trainer-core` (orchestrator)

### Dependencies
```
trainer-core
├── trainer-prompt-manager
│   └── trainer-prompt-security (required dependency)
├── trainer-prompt-security (standalone security module)
├── trainer-llm-provider
├── trainer-data-retriever
├── trainer-format-converter
└── trainer-test-agent (dev dependency)
```

**Security Module Dependencies**:
```
trainer-prompt-manager
└── trainer-prompt-security (required for production)
```

### Documentation
- Each module has its own README
- API documentation (Sphinx)
- Usage examples
- Migration guides

---

## Implementation Considerations

### 1. Backward Compatibility
- Maintain current file structure during migration
- Support both old and new APIs during transition
- Provide migration scripts

### 2. Performance
- Caching at multiple levels (prompts, LLM responses, data)
- Lazy loading of modules
- Async support for I/O operations

### 3. Error Handling
- Graceful degradation
- Clear error messages
- Retry logic for network operations

### 4. Security
- **Prompt Security Module**: Comprehensive protection against prompt injection
- Secure API key storage
- Input validation and sanitization (via `prompt-security` module)
- Template escaping and structured templating
- Injection detection and threat monitoring
- Security logging and audit trails
- Rate limiting and abuse prevention

### 5. Logging
- Structured logging
- Log levels
- Integration with monitoring tools

### 6. Agentic Development Support
- **Clear Module Boundaries**: Well-defined interfaces help AI agents understand scope
- **Comprehensive Documentation**: Docstrings and type hints guide agent understanding
- **Test-Driven Development**: Tests serve as specifications for agent-generated code
- **Incremental Changes**: Modular structure allows agents to work on one module at a time
- **Contract Validation**: Interface contracts prevent breaking changes across modules
- **Automated Testing**: Test-agent enables continuous validation during agentic development
- **Context Management**: Clear separation reduces token usage when agents load code

**Benefits for Agentic Workflows**:
- Agents can focus on single modules without full codebase context
- Tests provide immediate feedback on agent-generated code
- Module isolation prevents cascading errors
- Clear interfaces guide agent understanding of dependencies
- Test-agent can auto-generate tests for agent-created code

---

## Next Steps

1. **Review and Approve**: Review this analysis and approve the modularization approach
2. **Create Project Structure**: Set up repository structure for each module
3. **Start with Prompt Manager**: Begin with the most independent module
4. **Set Up Test Agent**: Create test-agent early to enable testing from the start
5. **Iterate**: Build and test each module incrementally
6. **Document**: Document APIs and usage as you go
7. **Refactor**: Gradually migrate existing code to use new modules
8. **Maintain Test Coverage**: Use test-agent to maintain high coverage throughout development

---

## Conclusion

The current trainer project has a solid foundation with clear separation between contexts, instructions, data, and outputs. By extracting this into modular, reusable packages, we can:

1. **Generalize** the workflow for use in other projects
2. **Improve** maintainability and testability
3. **Enable** programmatic usage via APIs
4. **Support** multiple LLM providers and data sources
5. **Create** reusable components for the broader community
6. **Ensure Quality** through automated testing with the test-agent module
7. **Protect** against security threats with the prompt-security module

The proposed architecture maintains the simplicity of the current file-based approach while adding the flexibility needed for more advanced use cases. Each module is independently useful and can be developed, tested, and distributed separately. 

**Key Architectural Decisions**:
- **Test-Agent Module**: Ensures testing is not an afterthought but a core part of the development workflow, enabling confident refactoring and safe agentic development practices.
- **Security Module**: Provides comprehensive protection against prompt injection attacks, making security a first-class concern from the start. The security module is designed to be reusable across any prompt-based application, not just the trainer project.

The security module (Phase 2) is prioritized early in the migration strategy to ensure all prompt operations are protected from the beginning, establishing security as a foundational concern rather than an afterthought.

