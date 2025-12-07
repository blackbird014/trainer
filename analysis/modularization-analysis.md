# Project Modularization Analysis

## Executive Summary

This document analyzes the current workflow of the trainer project and proposes a modular architecture that separates concerns into reusable, independently-packaged components. The goal is to transform this static POC into a generalized framework that can be used both for static site generation and as a foundation for more dynamic applications.

## Current Workflow Analysis

### Workflow Overview

The project follows a clear, linear workflow:

**Current Workflow (Legacy)**:
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

**Proposed Modular Workflow**:
```
Context Files (information/context/)
    ↓
Data Retrieval (data-retriever) → Data Store (data-store)
    ↓                                    ↓
Instruction Prompts (information/instructions/)  [Query Data Store]
    ↓                                    ↓
Prompt Execution (with contexts + data from store)
    ↓
Markdown Output (output/report/)
    ↓
Format Conversion (output/html/, output/pdf/)
```

**Key Architectural Change**: Data is retrieved once, stored persistently, and queried by prompt-manager. This decouples retrieval from consumption and enables ETL pipelines, analytics, and multi-consumer access.

### Current Architecture Components

1. **Context Management**
   - Location: `information/context/`
   - Structure: Topic-organized markdown files (e.g., `biotech/01-introduction.md`, `molecular-biology-foundations.md`)
   - Purpose: Provide domain knowledge and background information
   - Usage: Referenced in instruction prompts via file paths

2. **Data Retrieval**
   - Location: `output/json/` (legacy) → `data-store` (new architecture)
   - Method: Browser automation (MCP tools) scraping Yahoo Finance
   - Format: Structured JSON with financial metrics
   - Storage: Data automatically stored in `data-store` module
   - Access: Prompt-manager queries `data-store` instead of direct retrieval

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
- Write retrieved data to `data-store` module
- Rate limiting and error handling

**API Design**:
```python
class DataRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: Dict[str, Any], store: bool = True) -> RetrievalResult
    
    @abstractmethod
    def get_schema(self) -> Schema

class RetrievalResult:
    data: Dict[str, Any]
    source: str
    retrieved_at: datetime
    metadata: Dict[str, Any]
    storage_key: Optional[str]  # Key if stored in data-store
```

**Source Implementations**:
- `YahooFinanceRetriever` - Browser automation or API
- `SECFilingsRetriever` - SEC EDGAR database
- `APIRetriever` - Generic REST API wrapper
- `DatabaseRetriever` - SQL database queries
- `FileRetriever` - Local file system

**Integration with Data Store**:
- By default, retrieved data is automatically stored in `data-store`
- `store=False` option for one-off queries without persistence
- Storage key generated from query parameters and source
- Enables prompt-manager to query stored data instead of direct retrieval

**Features**:
- **Source Abstraction**: Switch data sources easily
- **Normalization**: Convert to common schema
- **Automatic Storage**: Write to data-store by default
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
│   │   ├── database_retriever.py
│   │   ├── file_retriever.py
│   │   ├── schema.py           # Common schemas
│   │   └── cache.py            # In-memory cache (complementary to data-store)
│   └── tests/
├── pyproject.toml
└── README.md
```

**Dependencies**: 
- Browser automation tools (for Yahoo Finance)
- `requests` (for APIs)
- `pandas` (for data manipulation)
- `data-store` (optional, for automatic persistence)

**Reusability**: High - can be used for any data retrieval needs

---

### Module 3.5: Data Persistence Layer (`data-store`)

**Purpose**: Centralized data persistence layer that decouples data retrieval from data consumption, enabling ETL pipelines, analytics, and transparent data source abstraction.

**Core Responsibilities**:
- Store data retrieved from various sources
- Provide unified query interface for consumers (prompt-manager, analytics, etc.)
- Support multiple storage backends (MongoDB, PostgreSQL, SQLite, Redis)
- Enable data versioning and timestamps
- Support analytics queries and aggregations
- Handle data freshness and TTL management

**Architecture Rationale**:
- **Decoupling**: Separates data retrieval (`data-retriever`) from data consumption (`prompt-manager`)
- **Persistence**: Data survives restarts and is available for multiple consumers
- **ETL Support**: Enables batch processing, transformations, and scheduled refreshes
- **Transparency**: Prompt-manager doesn't need to know the original data source
- **Analytics**: Foundation for data analysis and reporting
- **Scalability**: Independent scaling of retrieval and consumption

**API Design**:
```python
class DataStore(ABC):
    @abstractmethod
    def store(self, key: str, data: Any, metadata: Dict[str, Any]) -> str
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[StoredData]
    
    @abstractmethod
    def query(self, filters: Dict[str, Any], 
              limit: Optional[int] = None,
              sort: Optional[Dict[str, int]] = None) -> List[StoredData]
    
    @abstractmethod
    def update(self, key: str, data: Any, metadata: Optional[Dict] = None) -> bool
    
    @abstractmethod
    def delete(self, key: str) -> bool
    
    @abstractmethod
    def exists(self, key: str) -> bool
    
    @abstractmethod
    def get_freshness(self, key: str) -> Optional[datetime]
    
    # Analytics methods
    def aggregate(self, pipeline: List[Dict]) -> List[Dict]
    def count(self, filters: Dict[str, Any]) -> int
    def distinct(self, field: str, filters: Optional[Dict] = None) -> List[Any]

class StoredData:
    key: str
    data: Any
    source: str
    stored_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    version: int
    ttl: Optional[int]  # Time-to-live in seconds
```

**Storage Backend Implementations**:

**MongoDBStore** (Recommended for production):
- Pros: Flexible schema, JSON-like documents, excellent for varied data types, horizontal scaling
- Cons: More operational overhead, memory usage
- Use case: Production deployments with diverse data types

**PostgreSQLStore**:
- Pros: ACID compliance, JSONB support, mature ecosystem, excellent for structured data
- Cons: Schema changes can be heavier
- Use case: Structured data with relational queries

**SQLiteStore** (Development):
- Pros: Simple, file-based, zero configuration, perfect for development
- Cons: Limited concurrency, not ideal for high write loads
- Use case: Local development, small datasets

**RedisStore** (Caching layer):
- Pros: Very fast, pub/sub support, TTL built-in
- Cons: In-memory only, limited persistence
- Use case: Hot data caching, real-time data

**Hybrid Approach** (Optional):
- Redis for hot/cached data
- MongoDB/PostgreSQL for persistent storage
- SQLite for local development

**Features**:
- **Multi-Backend Support**: Pluggable storage backends
- **Automatic Storage**: Data-retriever writes to store by default
- **Query Interface**: Unified query API regardless of backend
- **Data Versioning**: Track data changes over time
- **TTL Management**: Automatic expiration of stale data
- **Analytics Support**: Aggregation pipelines, counting, distinct values
- **Metadata Storage**: Store source, timestamps, custom metadata
- **Freshness Tracking**: Check when data was last updated
- **Indexing**: Support for efficient queries (backend-dependent)

**Package Structure**:
```
data-store/
├── src/
│   ├── data_store/
│   │   ├── __init__.py
│   │   ├── base.py                    # Abstract base class
│   │   ├── stores/
│   │   │   ├── __init__.py
│   │   │   ├── mongodb_store.py       # MongoDB implementation
│   │   │   ├── postgresql_store.py    # PostgreSQL implementation
│   │   │   ├── sqlite_store.py        # SQLite implementation (dev)
│   │   │   └── redis_store.py         # Redis implementation (caching)
│   │   ├── registry.py                 # Store factory/registry
│   │   ├── models.py                   # Data models (StoredData, etc.)
│   │   ├── query_builder.py            # Query builder for analytics
│   │   ├── analytics.py                # Analytics helpers
│   │   └── config.py                   # Configuration management
│   └── tests/
├── examples/
│   ├── basic_usage.py
│   ├── analytics_example.py
│   └── integration_example.py
├── api_service.py                      # FastAPI service
├── pyproject.toml
└── README.md
```

**Dependencies**:
- `pymongo` (for MongoDB)
- `psycopg2` or `asyncpg` (for PostgreSQL, optional)
- `redis` (for Redis, optional)
- `pydantic` (for data models)
- `prometheus-client` (for metrics)
- `fastapi` + `uvicorn` (for API service)

**Development Setup**:
- **MongoDB**: Docker container for local development
- **SQLite**: Zero-configuration fallback
- **Configuration**: Environment-based backend selection

**Integration Points**:

**With Data-Retriever**:
```python
# data-retriever automatically stores results
retriever = YahooFinanceRetriever(data_store=mongodb_store)
result = retriever.retrieve({"ticker": "AAPL"})
# Data automatically stored with key: "yahoo_finance:AAPL:20240101"
```

**With Prompt-Manager**:
```python
# prompt-manager queries data-store instead of data-retriever
data = data_store.retrieve("yahoo_finance:AAPL:20240101")
# or query by filters
data = data_store.query({"source": "yahoo_finance", "ticker": "AAPL"})
```

**Reusability**: Very High - general-purpose data persistence layer

---

### Module 3.6: ETL Pipeline Extension (`data-etl`) - Optional

**Purpose**: Extract, Transform, Load pipeline for batch and real-time data processing, building on top of `data-retriever` and `data-store`.

**Core Responsibilities**:
- Scheduled data extraction from various sources
- Data transformation and normalization
- Batch processing workflows
- Real-time streaming pipelines
- Data quality checks and validation
- Error handling and retry logic
- Monitoring and alerting

**API Design**:
```python
class ETLPipeline:
    def extract(self, source: str, config: Dict) -> List[Dict]
    def transform(self, data: List[Dict], rules: List[TransformRule]) -> List[Dict]
    def load(self, data: List[Dict], target_store: DataStore) -> LoadResult
    
    def run_batch(self, pipeline_config: PipelineConfig) -> PipelineResult
    def run_streaming(self, source: str, callback: Callable) -> StreamHandle

class TransformRule:
    field: str
    operation: str  # "normalize", "validate", "enrich", "aggregate"
    params: Dict[str, Any]

class PipelineConfig:
    name: str
    schedule: Optional[str]  # Cron expression
    source: str
    transforms: List[TransformRule]
    target_store: str
    enabled: bool
```

**Features**:
- **Batch Processing**: Scheduled ETL jobs (cron-based)
- **Real-Time Streaming**: Event-driven data processing
- **Transformation Rules**: Configurable data transformations
- **Data Quality**: Validation, deduplication, completeness checks
- **Error Handling**: Retry logic, dead letter queues
- **Monitoring**: Track pipeline execution, success/failure rates
- **Scheduling**: Cron-based or event-driven triggers

**Package Structure**:
```
data-etl/
├── src/
│   ├── data_etl/
│   │   ├── __init__.py
│   │   ├── pipeline.py              # Main ETL pipeline
│   │   ├── extractors.py            # Data extraction
│   │   ├── transformers.py          # Data transformation
│   │   ├── loaders.py                # Data loading
│   │   ├── scheduler.py              # Job scheduling
│   │   ├── streaming.py              # Real-time processing
│   │   ├── validators.py             # Data quality checks
│   │   └── monitoring.py             # Pipeline monitoring
│   └── tests/
├── examples/
│   ├── batch_pipeline.py
│   ├── streaming_pipeline.py
│   └── scheduled_jobs.py
├── pyproject.toml
└── README.md
```

**Dependencies**:
- `data-retriever` (for extraction)
- `data-store` (for loading)
- `schedule` or `apscheduler` (for scheduling)
- `kafka-python>=2.0.0` (for Kafka streaming, optional)
- `pika>=1.3.0` (for RabbitMQ streaming, optional)

**Note**: Kafka/Pika are optional dependencies for real-time streaming support. If streaming is not needed, the module works with batch processing only. For simple streaming use cases, the module can use in-memory queues without external dependencies.

**Streaming Architecture**:
- **Current Approach**: Kafka/Pika are optional dependencies within `data-etl` module
- **Simple Streaming**: For basic use cases, can use in-memory queues or direct callbacks (no external dependencies)
- **Advanced Streaming**: For production-scale real-time pipelines, Kafka/Pika provide message queue infrastructure
- **Future Consideration**: If streaming becomes a core architectural concern across multiple modules, a separate `streaming-infrastructure` or `message-queue` abstraction module could be extracted. For now, keeping it as optional dependencies keeps the module focused and avoids unnecessary complexity.

**Example Usage - Simple Streaming**:
```python
from data_etl import ETLPipeline, TransformRule
from data_store import MongoDBStore
from data_retriever import YahooFinanceRetriever

# Initialize components
data_store = MongoDBStore(connection_string="mongodb://localhost:27017")
retriever = YahooFinanceRetriever(data_store=data_store)
pipeline = ETLPipeline()

# Define transformation rules
transforms = [
    TransformRule(field="price", operation="normalize", params={"decimal_places": 2}),
    TransformRule(field="timestamp", operation="validate", params={"format": "iso8601"})
]

# Simple streaming: process data as it arrives (in-memory, no Kafka needed)
def process_ticker_data(ticker: str):
    """Process a single ticker's data"""
    data = retriever.retrieve({"ticker": ticker})
    transformed = pipeline.transform([data.data], transforms)
    pipeline.load(transformed, data_store)
    print(f"Processed {ticker}")

# Stream processing with callback (simple, no message queue)
pipeline.run_streaming(
    source="yahoo_finance",
    callback=lambda event: process_ticker_data(event["ticker"])
)

# Advanced streaming with Kafka (requires kafka-python)
# pipeline.run_streaming_kafka(
#     topic="stock_data",
#     brokers=["localhost:9092"],
#     callback=process_ticker_data
# )
```

**Example Usage - Batch Processing**:
```python
from data_etl import ETLPipeline, PipelineConfig, TransformRule

# Configure batch pipeline
config = PipelineConfig(
    name="daily_stock_update",
    schedule="0 9 * * *",  # Run daily at 9 AM
    source="yahoo_finance",
    transforms=[
        TransformRule(field="price", operation="normalize"),
        TransformRule(field="volume", operation="validate")
    ],
    target_store="mongodb",
    enabled=True
)

# Run batch pipeline
pipeline = ETLPipeline()
result = pipeline.run_batch(config)
print(f"Processed {result.records_processed} records")
```

**Reusability**: High - general-purpose ETL framework

**Note**: This is an optional extension module. Basic data storage and retrieval can work without ETL, but ETL enables advanced workflows for batch processing and real-time data pipelines. Streaming support is optional - batch processing works without any message queue infrastructure.

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

### Module 8: Analytics Module (`analytics-module`)

**Purpose**: Analyze stored data in MongoDB to provide insights, statistics, and predictive capabilities for prompts, data usage, and system behavior.

**Core Responsibilities**:
- Analyze prompt patterns and usage statistics
- Identify most frequent prompts and data sources
- Generate prompt suggestions based on historical patterns
- Provide usage analytics and reporting
- Detect redundant prompts that could be automated
- Track data freshness and quality metrics
- Generate dashboards and visualizations

**API Design**:
```python
class AnalyticsModule:
    def analyze_prompt_patterns(self, filters: Optional[Dict] = None) -> PromptAnalysis
    """Analyze prompt usage patterns and clusters."""
    
    def get_top_prompts(self, limit: int = 10, 
                       time_range: Optional[TimeRange] = None) -> List[PromptStat]
    """Get most frequently used prompts."""
    
    def suggest_prompts(self, context: Dict[str, Any], 
                       limit: int = 5) -> List[SuggestedPrompt]
    """Suggest likely prompts based on context and history."""
    
    def generate_statistics(self, 
                           module: Optional[str] = None,
                           time_range: Optional[TimeRange] = None) -> StatisticsReport
    """Generate comprehensive statistics report."""
    
    def identify_redundancies(self, 
                              similarity_threshold: float = 0.8) -> List[RedundancyGroup]
    """Identify prompts that could be automated or consolidated."""
    
    def track_data_freshness(self, source: Optional[str] = None) -> FreshnessReport
    """Track data freshness across sources."""
    
    def get_usage_metrics(self, 
                         metric_type: str,  # "prompts", "data_sources", "formats"
                         time_range: Optional[TimeRange] = None) -> UsageMetrics

class PromptAnalysis:
    total_prompts: int
    unique_prompts: int
    top_patterns: List[PromptPattern]
    clusters: List[PromptCluster]
    trends: Dict[str, float]  # Usage trends over time

class PromptStat:
    prompt_text: str
    usage_count: int
    last_used: datetime
    avg_response_time: Optional[float]
    success_rate: Optional[float]

class SuggestedPrompt:
    prompt_template: str
    confidence: float
    reasoning: str
    similar_prompts: List[str]

class StatisticsReport:
    prompts: PromptStatistics
    data_sources: DataSourceStatistics
    formats: FormatStatistics
    llm_usage: LLMUsageStatistics
    time_range: TimeRange

class RedundancyGroup:
    prompts: List[str]
    similarity_score: float
    suggested_consolidation: str
    automation_potential: float
```

**Features**:
- **Pattern Detection**: Identify common prompt patterns using clustering algorithms
- **Usage Analytics**: Track prompt frequency, success rates, response times
- **Predictive Suggestions**: ML-based prompt suggestions based on context
- **Redundancy Detection**: Find prompts that could be automated or consolidated
- **Data Source Analytics**: Analyze which data sources are most used
- **Format Analytics**: Track format conversion patterns
- **Time-Series Analysis**: Track trends over time
- **Dashboard Integration**: Export data for Grafana/other dashboards
- **MongoDB Aggregation**: Leverage MongoDB aggregation pipelines for efficient queries
- **Statistical Analysis**: Descriptive statistics, correlations, trends

**Package Structure**:
```
analytics-module/
├── src/
│   ├── analytics/
│   │   ├── __init__.py
│   │   ├── analyzer.py              # Main analytics class
│   │   ├── prompt_analyzer.py        # Prompt-specific analytics
│   │   ├── pattern_detector.py      # Pattern detection and clustering
│   │   ├── predictor.py              # Predictive prompt suggestions
│   │   ├── redundancy_detector.py    # Redundancy identification
│   │   ├── statistics.py             # Statistical analysis
│   │   ├── visualizer.py             # Data visualization helpers
│   │   ├── models.py                 # Analytics result models
│   │   └── queries.py                # MongoDB aggregation queries
│   └── tests/
├── examples/
│   ├── prompt_analytics.py
│   ├── usage_statistics.py
│   ├── redundancy_analysis.py
│   └── dashboard_export.py
├── api_service.py                    # FastAPI service with analytics endpoints
├── pyproject.toml
└── README.md
```

**Dependencies**:
- `data-store` (required) - For querying stored data
- `pandas>=2.0.0` - Data manipulation and analysis
- `numpy>=1.24.0` - Numerical computations
- `scikit-learn>=1.3.0` - Clustering and ML algorithms (optional, for advanced analytics)
- `plotly>=5.0.0` (optional) - Interactive visualizations
- `prometheus-client` - Metrics integration
- `fastapi` + `uvicorn` - API service

**Integration Points**:
- **Data-Store**: Queries MongoDB for analytics data
- **Prompt-Manager**: Can suggest prompts based on analytics
- **Grafana**: Exports metrics for dashboard visualization
- **MongoDB Aggregation**: Uses aggregation pipelines for efficient queries

**Example Usage**:
```python
from analytics import AnalyticsModule
from data_store import create_store

# Initialize
store = create_store("mongodb", connection_string="mongodb://localhost:27017")
analytics = AnalyticsModule(data_store=store)

# Analyze prompt patterns
analysis = analytics.analyze_prompt_patterns()
print(f"Total prompts: {analysis.total_prompts}")
print(f"Top patterns: {analysis.top_patterns}")

# Get top prompts
top_prompts = analytics.get_top_prompts(limit=10)
for prompt in top_prompts:
    print(f"{prompt.prompt_text}: {prompt.usage_count} uses")

# Suggest prompts
suggestions = analytics.suggest_prompts(
    context={"data_source": "yahoo_finance", "ticker": "AAPL"},
    limit=5
)
for suggestion in suggestions:
    print(f"Suggested: {suggestion.prompt_template} (confidence: {suggestion.confidence})")

# Identify redundancies
redundancies = analytics.identify_redundancies(similarity_threshold=0.8)
for group in redundancies:
    print(f"Redundant prompts: {group.prompts}")
    print(f"Suggested consolidation: {group.suggested_consolidation}")
    print(f"Automation potential: {group.automation_potential}")

# Generate statistics
stats = analytics.generate_statistics()
print(f"Total data sources: {stats.data_sources.total}")
print(f"Most used format: {stats.formats.most_used}")
```

**Reusability**: High - general-purpose analytics framework for any MongoDB-based application

---

### Module 8.5: Vector Store Extension (`vector-store`)

**Purpose**: Extend `data-store` with vector embeddings and semantic search capabilities, enabling similarity-based retrieval without LLM calls.

**Core Responsibilities**:
- Generate embeddings for prompts and data pairs
- Store embeddings alongside data in MongoDB
- Perform semantic search using vector similarity
- Enable cached response retrieval for similar queries
- Support multiple embedding models (OpenAI, Sentence Transformers, Cohere)
- Integrate with MongoDB Atlas Vector Search or local vector search

**Architecture Rationale**:
- **Extension vs Separate Module**: Extends `data-store` rather than replacing it
- **Embedding Storage**: Embeddings stored as additional field in MongoDB documents
- **Semantic Search**: Enables finding similar prompts/data without exact text matching
- **Cost Reduction**: Retrieve cached responses for similar queries, reducing LLM calls
- **Pattern Discovery**: Identify similar prompts and data patterns

**API Design**:
```python
class VectorStore(DataStore):
    """Extended data store with vector search capabilities."""
    
    def store_with_embedding(self, 
                            key: str, 
                            data: Any,
                            text: str,  # Text to embed (prompt or data summary)
                            metadata: Optional[Dict] = None,
                            embedding_model: str = "openai") -> str
    """Store data with generated embedding."""
    
    def semantic_search(self, 
                       query: str,
                       limit: int = 10,
                       threshold: float = 0.7,
                       filters: Optional[Dict] = None) -> List[SearchResult]
    """Search for similar documents using semantic similarity."""
    
    def get_similar_prompts(self, 
                           prompt: str,
                           limit: int = 5) -> List[StoredData]
    """Find similar prompts in the database."""
    
    def get_answer_without_llm(self, 
                               query: str,
                               similarity_threshold: float = 0.85) -> Optional[Dict]
    """Retrieve cached answer for similar query without calling LLM."""
    
    def generate_embedding(self, 
                          text: str,
                          model: str = "openai") -> List[float]
    """Generate embedding for text using specified model."""
    
    def batch_embed(self, 
                   texts: List[str],
                   model: str = "openai") -> List[List[float]]
    """Generate embeddings for multiple texts efficiently."""

class SearchResult:
    item: StoredData
    similarity_score: float
    matched_text: str

class EmbeddingConfig:
    model: str  # "openai", "sentence-transformers", "cohere"
    model_name: str  # Specific model name
    dimensions: int
    api_key: Optional[str]  # For API-based models
```

**Embedding Model Support**:

**OpenAI `text-embedding-3-small`**:
- Cost: ~$0.02 per 1M tokens
- Dimensions: 1536
- Quality: Excellent
- Requires: API key

**Sentence Transformers** (Free, Local):
- Cost: FREE (runs locally)
- Dimensions: 384-768 (model-dependent)
- Quality: Very good
- Example: `sentence-transformers/all-MiniLM-L6-v2`
- No API key required

**Cohere Embed**:
- Cost: Similar to OpenAI
- Dimensions: 1024
- Quality: Excellent
- Requires: API key

**Features**:
- **Multi-Model Support**: Support for OpenAI, Sentence Transformers, Cohere
- **Automatic Embedding**: Generate embeddings automatically when storing data
- **Semantic Search**: Find similar documents using cosine similarity
- **Cached Responses**: Retrieve answers for similar queries without LLM calls
- **Batch Processing**: Efficient batch embedding generation
- **MongoDB Integration**: Store embeddings in MongoDB documents
- **Vector Indexing**: Create vector indexes for fast similarity search
- **Model Switching**: Switch embedding models without code changes
- **Cost Optimization**: Reduce LLM costs by reusing similar responses

**Package Structure**:
```
vector-store/
├── src/
│   ├── vector_store/
│   │   ├── __init__.py
│   │   ├── vector_store.py           # Main VectorStore class
│   │   ├── embeddings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Base embedding interface
│   │   │   ├── openai_embedder.py     # OpenAI embeddings
│   │   │   ├── sentence_transformers_embedder.py  # Sentence Transformers
│   │   │   └── cohere_embedder.py     # Cohere embeddings
│   │   ├── search.py                  # Vector search implementation
│   │   ├── indexer.py                 # Vector index management
│   │   ├── models.py                  # Search result models
│   │   └── config.py                  # Embedding configuration
│   └── tests/
├── examples/
│   ├── semantic_search.py
│   ├── cached_responses.py
│   ├── batch_embedding.py
│   └── model_comparison.py
├── api_service.py                     # FastAPI service with vector search endpoints
├── pyproject.toml
└── README.md
```

**Dependencies**:
- `data-store` (required) - Extends base data store
- `openai>=1.0.0` (optional) - For OpenAI embeddings
- `sentence-transformers>=2.2.0` (optional) - For local embeddings
- `cohere>=4.0.0` (optional) - For Cohere embeddings
- `numpy>=1.24.0` - Vector operations
- `scipy>=1.10.0` (optional) - Advanced similarity calculations
- `prometheus-client` - Metrics integration
- `fastapi` + `uvicorn` - API service

**MongoDB Vector Search Integration**:

**Option 1: MongoDB Atlas Vector Search** (Cloud):
- Built-in vector search in MongoDB Atlas
- Create vector index on embedding field
- Use `$vectorSearch` aggregation stage
- Requires: MongoDB Atlas subscription

**Option 2: Local MongoDB + Vector Search Extension**:
- Use local MongoDB with vector search extension
- Similar indexing and query capabilities
- Cost: Free (self-hosted)

**Option 3: Hybrid Approach**:
- Store embeddings in MongoDB
- Use external vector DB (Pinecone, Weaviate) for search
- Keep original data in MongoDB

**Example Usage**:
```python
from vector_store import VectorStore, create_vector_store
from data_store import create_store

# Initialize vector store (extends data-store)
store = create_vector_store(
    "mongodb",
    connection_string="mongodb://localhost:27017",
    database="trainer_data",
    embedding_model="sentence-transformers",  # or "openai", "cohere"
    embedding_model_name="all-MiniLM-L6-v2"
)

# Store with automatic embedding
key = store.store_with_embedding(
    key="prompt:stock:apple",
    data={"ticker": "AAPL", "price": 150.25},
    text="What is the price of Apple stock?",  # Text to embed
    metadata={"source": "prompt_manager"}
)

# Semantic search
results = store.semantic_search(
    query="How much does AAPL cost?",  # Different wording!
    limit=5,
    threshold=0.7
)
for result in results:
    print(f"Found: {result.item.key} (similarity: {result.similarity_score})")
    print(f"Data: {result.item.data}")

# Get answer without LLM call
answer = store.get_answer_without_llm(
    query="What's Apple's stock price?",
    similarity_threshold=0.85
)
if answer:
    print(f"Cached answer: {answer}")
else:
    print("No similar query found, need to call LLM")
```

**Reusability**: Very High - extends data-store with semantic search capabilities, useful for any application needing similarity search

---

### Module 9: App Builder Module (`app-builder`) - Optional/Advanced

**Purpose**: Analyze prompt patterns to identify redundant workflows and generate traditional applications that replace repetitive LLM-based operations, particularly for educational software with stable data.

**Core Responsibilities**:
- Analyze prompt patterns to identify automation opportunities
- Generate application code from prompt templates
- Extract business logic from prompt patterns
- Create traditional apps that don't require LLM calls
- Fine-tune LLMs to generate app code
- Validate and test generated applications
- Deploy generated applications

**Architecture Rationale**:
- **Pattern Analysis**: Identify repetitive prompt → data → format workflows
- **Code Generation**: Generate traditional app code (FastAPI, React, etc.)
- **Automation**: Replace LLM calls with direct data processing
- **Cost Reduction**: Eliminate LLM costs for common, stable use cases
- **Performance**: Faster responses than LLM-based workflows
- **Educational Focus**: Particularly valuable for educational software with stable data

**API Design**:
```python
class AppBuilder:
    def analyze_patterns(self, 
                        time_range: Optional[TimeRange] = None,
                        min_frequency: int = 10) -> List[AppPattern]
    """Analyze prompt patterns to identify app-worthy workflows."""
    
    def generate_app_template(self, 
                             pattern: AppPattern,
                             framework: str = "fastapi") -> AppTemplate
    """Generate app template from prompt pattern."""
    
    def generate_app_code(self, 
                         template: AppTemplate,
                         config: AppConfig) -> GeneratedApp
    """Generate complete application code."""
    
    def validate_app(self, 
                    app_code: GeneratedApp) -> ValidationResult
    """Validate generated app code."""
    
    def deploy_app(self, 
                  app: GeneratedApp,
                  target: str = "local") -> DeploymentResult
    """Deploy generated application."""
    
    def fine_tune_generator(self, 
                           training_data: List[PatternCodePair]) -> FineTunedModel
    """Fine-tune LLM to generate apps from patterns."""

class AppPattern:
    pattern_id: str
    prompts: List[str]
    frequency: int
    data_sources: List[str]
    output_formats: List[str]
    automation_score: float
    stability_score: float  # How stable is the data/logic?
    suggested_app_type: str  # "crud", "dashboard", "api", "web_app"

class AppTemplate:
    name: str
    framework: str
    structure: Dict[str, str]  # File paths → code templates
    dependencies: List[str]
    config_schema: Dict[str, Any]

class GeneratedApp:
    name: str
    framework: str
    code: Dict[str, str]  # File paths → generated code
    dependencies: List[str]
    tests: List[str]  # Generated test code
    documentation: str
    deployment_config: Dict[str, Any]

class AppConfig:
    app_name: str
    framework: str  # "fastapi", "flask", "react", "nextjs"
    database: str  # "mongodb", "postgresql", "sqlite"
    features: List[str]  # "crud", "api", "dashboard", "auth"
    styling: str  # "bootstrap", "tailwind", "material"
```

**Features**:
- **Pattern Detection**: Identify repetitive prompt workflows suitable for automation
- **Code Generation**: Generate application code from patterns
- **Multiple Frameworks**: Support FastAPI, Flask, React, Next.js
- **Template System**: Pre-built templates for common app types
- **Validation**: Validate generated code for syntax and logic
- **Testing**: Generate tests for generated applications
- **Deployment**: Deploy generated apps to various targets
- **Fine-Tuning**: Fine-tune LLM to improve code generation
- **Documentation**: Auto-generate documentation for generated apps
- **Incremental Updates**: Update apps when patterns change

**Implementation Phases**:

**Phase 1: MVP - Template Generation** (Weeks 1-4):
- Analyze patterns to identify app opportunities
- Generate app templates (not full apps)
- User manually fills templates
- Validate and deploy templates

**Phase 2: Code Generation** (Weeks 5-8):
- Generate complete app code from templates
- Support simple app types (CRUD, dashboards)
- Basic validation and testing
- Local deployment

**Phase 3: Advanced Generation** (Weeks 9-12):
- Support complex app types
- Fine-tune model for better generation
- Advanced validation and testing
- Cloud deployment support

**Package Structure**:
```
app-builder/
├── src/
│   ├── app_builder/
│   │   ├── __init__.py
│   │   ├── builder.py                 # Main AppBuilder class
│   │   ├── pattern_analyzer.py        # Pattern analysis
│   │   ├── code_generator.py          # Code generation
│   │   ├── template_engine.py         # Template system
│   │   ├── validators.py              # Code validation
│   │   ├── deployer.py                # Deployment
│   │   ├── fine_tuner.py              # Model fine-tuning
│   │   ├── templates/
│   │   │   ├── fastapi/
│   │   │   │   ├── crud_template.py.j2
│   │   │   │   ├── api_template.py.j2
│   │   │   │   └── dashboard_template.py.j2
│   │   │   ├── react/
│   │   │   │   └── dashboard_template.jsx.j2
│   │   │   └── flask/
│   │   │       └── web_app_template.py.j2
│   │   └── models.py                  # App models
│   └── tests/
├── examples/
│   ├── pattern_analysis.py
│   ├── template_generation.py
│   ├── code_generation.py
│   └── deployment.py
├── api_service.py                     # FastAPI service
├── pyproject.toml
└── README.md
```

**Dependencies**:
- `analytics-module` (required) - For pattern analysis
- `data-store` (required) - For accessing stored prompts/data
- `llm-provider` (required) - For code generation
- `jinja2>=3.1.0` - Template engine
- `ast` (built-in) - Code validation
- `black>=23.0.0` (optional) - Code formatting
- `pytest>=7.0.0` (optional) - Test generation
- `docker>=6.0.0` (optional) - Container deployment
- `kubernetes>=27.0.0` (optional) - K8s deployment

**Example Usage - MVP (Template Generation)**:
```python
from app_builder import AppBuilder
from analytics import AnalyticsModule

# Initialize
analytics = AnalyticsModule(data_store=store)
builder = AppBuilder(analytics=analytics)

# Analyze patterns
patterns = builder.analyze_patterns(min_frequency=10)
for pattern in patterns:
    print(f"Pattern: {pattern.pattern_id}")
    print(f"Frequency: {pattern.frequency}")
    print(f"Automation score: {pattern.automation_score}")
    print(f"Suggested app: {pattern.suggested_app_type}")

# Generate template for high-scoring pattern
high_score_pattern = max(patterns, key=lambda p: p.automation_score)
template = builder.generate_app_template(
    pattern=high_score_pattern,
    framework="fastapi"
)

print(f"Generated template: {template.name}")
print(f"Files: {list(template.structure.keys())}")

# User fills template manually, then validate and deploy
```

**Example Usage - Full Code Generation**:
```python
# Generate complete app
app = builder.generate_app_code(
    template=template,
    config=AppConfig(
        app_name="stock_dashboard",
        framework="fastapi",
        database="mongodb",
        features=["crud", "api", "dashboard"],
        styling="bootstrap"
    )
)

# Validate
validation = builder.validate_app(app)
if validation.is_valid:
    # Deploy
    deployment = builder.deploy_app(app, target="local")
    print(f"App deployed at: {deployment.url}")
else:
    print(f"Validation errors: {validation.errors}")
```

**Reusability**: Medium - specific to generating applications from prompt patterns, but framework is reusable

**Note**: This is an advanced, optional module. Start with MVP (template generation) and expand gradually. Full automation requires significant development effort but provides high value by eliminating redundant LLM calls.

---

## Integration Architecture

### Core Application (`trainer-core`)

The main application that orchestrates all modules:

```python
from prompt_manager import PromptManager
from prompt_security import SecurityModule
from llm_provider import LLMProvider, OpenAIProvider
from data_retriever import DataRetriever, YahooFinanceRetriever
from data_store import DataStore, MongoDBStore
from format_converter import FormatConverter
from test_agent import TestAgent

class TrainerCore:
    def __init__(self):
        # Initialize security module
        self.security = SecurityModule(strict_mode=True)
        
        # Initialize data store (MongoDB for production, SQLite for dev)
        self.data_store = MongoDBStore(
            connection_string=os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
            database="trainer_data"
        )
        
        # Initialize prompt manager with security
        self.prompt_manager = PromptManager(
            context_dir="information/context",
            security_module=self.security,
            data_store=self.data_store  # Prompt manager queries data-store
        )
        self.llm_provider = OpenAIProvider()
        
        # Data retriever writes to data-store automatically
        self.data_retriever = YahooFinanceRetriever(
            data_store=self.data_store
        )
        
        self.format_converter = FormatConverter()
        self.test_agent = TestAgent()  # Optional, for development/testing
    
    def generate_report(self, 
                       instruction_path: str,
                       data_key: Optional[str] = None,  # Key in data-store
                       data_query: Optional[Dict] = None,  # Query filters
                       output_format: str = "markdown"):
        # 1. Load instruction prompt
        instruction = self.prompt_manager.load_prompt(instruction_path)
        
        # 2. Load contexts referenced in instruction
        contexts = self.prompt_manager.load_contexts(
            instruction.get_context_refs()
        )
        
        # 3. Load data from data-store (or retrieve if not found)
        if data_key:
            data = self.data_store.retrieve(data_key)
        elif data_query:
            results = self.data_store.query(data_query)
            data = results[0] if results else None
        else:
            raise ValueError("Must provide data_key or data_query")
        
        # If data not found or stale, retrieve fresh data
        if data is None or self._is_stale(data):
            # Trigger retrieval and store
            result = self.data_retriever.retrieve(data_query or {"key": data_key})
            data = result.data
            # Data automatically stored by retriever
        
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
    
    def _is_stale(self, data: StoredData, max_age_hours: int = 24) -> bool:
        """Check if data is stale."""
        age = datetime.now() - data.updated_at
        return age.total_seconds() > (max_age_hours * 3600)
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

data_store:
  backend: "mongodb"  # or "postgresql", "sqlite", "redis"
  connection_string: "${MONGODB_URI}"
  database: "trainer_data"
  # Development: use SQLite (no setup required)
  # backend: "sqlite"
  # database_path: "data/trainer.db"

data_retriever:
  provider: "yahoo_finance"
  auto_store: true  # Automatically store retrieved data
  cache_enabled: true  # In-memory cache (complementary to data-store)

data_etl:
  enabled: false  # Optional ETL module
  streaming:
    enabled: false
    provider: "kafka"  # or "rabbitmq", "in_memory"
    kafka_brokers: ["localhost:9092"]  # If using Kafka
    rabbitmq_url: "amqp://localhost:5672"  # If using RabbitMQ
  batch:
    enabled: true
    scheduler: "apscheduler"  # or "schedule"
    default_schedule: "0 9 * * *"  # Daily at 9 AM

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

analytics:
  enabled: true
  data_store: "mongodb"  # Backend for analytics queries
  clustering_enabled: true  # Enable pattern clustering
  suggestion_enabled: true  # Enable prompt suggestions
  dashboard_export: true  # Export metrics to Grafana

vector_store:
  enabled: false  # Optional: Enable vector search capabilities
  embedding_model: "sentence-transformers"  # or "openai", "cohere"
  embedding_model_name: "all-MiniLM-L6-v2"
  auto_embed: false  # Automatically generate embeddings on store
  vector_search_backend: "mongodb"  # or "pinecone", "weaviate"
  similarity_threshold: 0.7  # Default similarity threshold

app_builder:
  enabled: false  # Optional: Enable app generation
  mode: "template"  # "template" (MVP) or "full" (code generation)
  min_pattern_frequency: 10  # Minimum frequency to consider for automation
  supported_frameworks: ["fastapi", "flask", "react"]
  auto_deploy: false  # Automatically deploy generated apps
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

### Phase 4: Create Data Store Module (Week 7-8)
1. Create `data-store` package
2. Implement base abstraction and MongoDB backend
3. Add SQLite backend for development
4. Implement query interface and analytics support
5. Add Prometheus metrics integration
6. **Write tests** for storage backends and queries
7. **Set up MongoDB** Docker container for development

### Phase 5: Extract Data Retriever with Store Integration (Week 9-10)
1. Create `data-retriever` package
2. Extract Yahoo Finance logic
3. Integrate with `data-store` for automatic persistence
4. Add caching (complementary to data-store)
5. Update trainer to use data-store for data access
6. **Write tests** for data retrieval, storage, and integration

### Phase 6: Extract Format Converter (Week 11-12)
1. Create `format-converter` package
2. Extract HTML conversion logic
3. Add PDF conversion
4. Update trainer to use new module
5. **Write tests** for format conversions

### Phase 7: Create Test Agent (Week 13-14)
1. Create `test-agent` package
2. Implement test generation
3. Implement test runner and coverage
4. Add mock library for common dependencies
5. Integrate with all modules
6. Set up CI/CD with automated testing
7. **Generate initial test suite** for all modules

### Phase 8: Optional ETL Pipeline Extension (Week 15-16)
1. Create `data-etl` package (optional)
2. Implement batch processing pipelines
3. Add simple streaming support (in-memory queues)
4. Add optional Kafka/Pika integration for advanced streaming
5. Implement transformation rules
6. Add scheduling and monitoring
7. **Write tests** for ETL workflows (batch and streaming)
8. **Document** ETL patterns and best practices
9. **Add examples** for simple streaming and Kafka-based streaming

### Phase 9: Refactor Core Application (Week 17-18)
1. Create `trainer-core` package
2. Integrate all modules (including security)
3. Add CLI interface
4. Add configuration management
5. **Run comprehensive test suite** via test-agent
6. **Achieve target coverage** (80%+)
7. **Security audit** of integrated system

### Phase 10: Analytics Module (Week 19-20)
1. Create `analytics-module` package
2. Implement MongoDB aggregation queries for analytics
3. Add pattern detection and clustering algorithms
4. Implement prompt suggestion system
5. Create redundancy detection functionality
6. Build Grafana dashboard integration
7. Add statistics and reporting APIs
8. **Write tests** for analytics functionality
9. **Document** analytics capabilities and use cases

### Phase 11: Vector Store Extension (Week 21-22)
1. Create `vector-store` package (extends `data-store`)
2. Implement embedding generation (OpenAI, Sentence Transformers, Cohere)
3. Add vector storage to MongoDB documents
4. Implement semantic search functionality
5. Create vector indexes for efficient search
6. Add cached response retrieval
7. Integrate with MongoDB Atlas Vector Search (optional)
8. **Write tests** for vector operations and search
9. **Document** embedding models and vector search usage

### Phase 12: App Builder MVP (Week 23-26)
1. Create `app-builder` package
2. Implement pattern analysis from analytics module
3. Create template generation system
4. Build code generation for simple app types (CRUD, dashboards)
5. Add code validation and testing
6. Implement local deployment
7. **Write tests** for pattern analysis and code generation
8. **Document** app generation workflow and limitations

### Phase 13: Optional Enhancements (Week 27+)
1. Add training integration module (`model-trainer`)
2. Add web API (FastAPI) - already implemented
3. Add monitoring/logging - already implemented
4. Enhance CI/CD pipelines with test-agent
5. **Enhance security module** with ML-based detection
6. **Security agent** for continuous monitoring
7. **Analytics Dashboard**: Build analytics UI on top of data-store
8. **Data Versioning**: Advanced versioning and rollback capabilities
9. **Multi-Tenancy**: Support for multiple tenants/users
10. **Data Lineage**: Track data provenance and transformations
11. **App Builder Full Version**: Expand to complex app types and fine-tuning

---

## Benefits of Modularization

### 1. Reusability
- Each module can be used independently in other projects
- Prompt manager can be used for any prompt-based application
- **Prompt security module can be used in any prompt-based system**
- LLM provider can be used for any LLM application
- Format converter is general-purpose
- **Data-store module** provides general-purpose persistence layer
- **Vector-store module** extends data-store with semantic search capabilities
- **ETL module** (optional) provides reusable batch and streaming pipelines
- **Analytics module** provides general-purpose analytics for MongoDB-based applications
- **App-builder module** (optional) provides framework for generating apps from patterns

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
  - `trainer-data-store` (data persistence layer)
  - `trainer-vector-store` (optional vector search extension)
  - `trainer-data-etl` (optional ETL extension)
  - `trainer-format-converter`
  - `trainer-test-agent`
  - `trainer-analytics` (optional analytics module)
  - `trainer-app-builder` (optional app generation module)
  - `trainer-core` (orchestrator)

### Dependencies
```
trainer-core
├── trainer-prompt-manager
│   ├── trainer-prompt-security (required dependency)
│   └── trainer-data-store (for data access)
├── trainer-prompt-security (standalone security module)
├── trainer-llm-provider
├── trainer-data-retriever
│   └── trainer-data-store (for automatic persistence)
├── trainer-data-store (core persistence layer)
│   └── trainer-vector-store (optional extension)
├── trainer-vector-store (optional, extends data-store)
├── trainer-format-converter
├── trainer-test-agent (dev dependency)
├── trainer-data-etl (optional, for ETL pipelines)
├── trainer-analytics (optional, for analytics and insights)
└── trainer-app-builder (optional, for app generation)
    ├── trainer-analytics (required dependency)
    └── trainer-vector-store (optional, for pattern analysis)
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
8. **Decouple Data Flow** with the data-store module, enabling ETL pipelines and analytics

The proposed architecture maintains the simplicity of the current file-based approach while adding the flexibility needed for more advanced use cases. Each module is independently useful and can be developed, tested, and distributed separately. 

**Key Architectural Decisions**:
- **Test-Agent Module**: Ensures testing is not an afterthought but a core part of the development workflow, enabling confident refactoring and safe agentic development practices.
- **Security Module**: Provides comprehensive protection against prompt injection attacks, making security a first-class concern from the start. The security module is designed to be reusable across any prompt-based application, not just the trainer project.
- **Data-Store Module**: Introduces a persistence layer that decouples data retrieval from consumption, enabling:
  - **ETL Pipelines**: Batch and real-time data processing (via optional `data-etl` extension)
  - **Analytics**: Data analysis and reporting capabilities
  - **Multi-Consumer Access**: Multiple modules can query the same data
  - **Data Transparency**: Prompt-manager doesn't need to know data sources
  - **Persistence**: Data survives restarts and is available for historical analysis
  - **Development Flexibility**: SQLite for local dev, MongoDB for production
- **Vector-Store Extension**: Extends data-store with semantic search capabilities, enabling:
  - **Semantic Search**: Find similar prompts/data without exact text matching
  - **Cost Reduction**: Retrieve cached responses for similar queries, reducing LLM calls
  - **Pattern Discovery**: Identify similar prompts and data patterns
  - **Multiple Embedding Models**: Support for OpenAI, Sentence Transformers (free), Cohere
- **Analytics Module**: Provides comprehensive analytics and insights:
  - **Pattern Detection**: Identify common prompt patterns and usage trends
  - **Predictive Suggestions**: ML-based prompt suggestions based on context
  - **Redundancy Detection**: Find prompts that could be automated or consolidated
  - **Usage Analytics**: Track system usage, data sources, and format conversions
  - **Dashboard Integration**: Export metrics for visualization
- **App-Builder Module**: Enables automation of repetitive workflows:
  - **Pattern Analysis**: Identify app-worthy prompt patterns
  - **Code Generation**: Generate traditional apps from patterns (MVP: templates, Full: complete apps)
  - **Cost Optimization**: Eliminate LLM costs for common, stable use cases
  - **Performance**: Faster responses than LLM-based workflows
  - **Educational Focus**: Particularly valuable for educational software with stable data

The security module (Phase 2) is prioritized early in the migration strategy to ensure all prompt operations are protected from the beginning, establishing security as a foundational concern rather than an afterthought.

The data-store module (Phase 4) is introduced before data-retriever integration (Phase 5) to establish the persistence foundation, enabling data-retriever to automatically store results and prompt-manager to query stored data transparently.

