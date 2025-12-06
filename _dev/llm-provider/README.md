# LLM Provider Abstraction Layer

Unified interface for multiple LLM providers via LiteLLM. Supports OpenAI, Anthropic, AWS Bedrock, Google Vertex AI, Azure OpenAI, Ollama, and custom SageMaker endpoints.

## Features

- **Unified API**: Single interface for all LLM providers
- **100+ Providers**: Via LiteLLM integration
- **Cost Tracking**: Automatic cost calculation per provider
- **Streaming Support**: Stream completions as they arrive
- **Provider Switching**: Change providers without code changes
- **Configuration Management**: YAML/JSON config support
- **Custom Providers**: Direct implementation support for special cases

## Installation

```bash
pip install trainer-llm-provider
```

### Optional Dependencies

```bash
# AWS support
pip install trainer-llm-provider[aws]

# Azure support
pip install trainer-llm-provider[azure]

# Google Cloud support
pip install trainer-llm-provider[google]

# All optional dependencies
pip install trainer-llm-provider[all]
```

## Quick Start

### Basic Usage

```python
from llm_provider import OpenAIProvider

# Create provider
provider = OpenAIProvider(model="gpt-4")

# Complete a prompt
result = provider.complete("What is the capital of France?")
print(result.content)
print(f"Tokens: {result.tokens_used}, Cost: ${result.cost:.4f}")
```

### Using Registry

```python
from llm_provider import create_provider

# Create provider from registry
provider = create_provider("openai", model="gpt-4")

# Complete prompt
result = provider.complete("Hello, world!")
print(result.content)
```

### Streaming

```python
from llm_provider import OpenAIProvider

provider = OpenAIProvider(model="gpt-4")

# Stream completion
for chunk in provider.stream("Tell me a story"):
    print(chunk, end="", flush=True)
```

## Supported Providers

### LiteLLM-based Providers

- **OpenAI**: GPT-4, GPT-3.5, and other OpenAI models
- **Anthropic**: Claude 3 (Opus, Sonnet, Haiku)
- **Ollama**: Local models (llama2, mistral, codellama, etc.)
- **AWS Bedrock**: Claude, Llama, Titan, and other Bedrock models
- **Google Vertex AI**: Gemini, PaLM, and custom models
- **Azure OpenAI**: GPT-4, GPT-3.5 via Azure

### Direct Providers

- **AWS SageMaker**: Custom endpoints with fine-tuned models

## Provider Examples

### OpenAI

```python
from llm_provider import OpenAIProvider

provider = OpenAIProvider(
    model="gpt-4",
    api_key="your-api-key"  # Optional, uses OPENAI_API_KEY env var
)

result = provider.complete("Hello!", temperature=0.7, max_tokens=100)
```

### Anthropic

```python
from llm_provider import AnthropicProvider

provider = AnthropicProvider(
    model="claude-3-opus-20240229",
    api_key="your-api-key"  # Optional, uses ANTHROPIC_API_KEY env var
)

result = provider.complete("Explain quantum computing")
```

### AWS Bedrock

```python
from llm_provider import AWSBedrockProvider

provider = AWSBedrockProvider(
    model="anthropic.claude-3-opus-20240229-v1:0",
    region="us-east-1"
    # Uses AWS credentials from environment or boto3 config
)

result = provider.complete("What is machine learning?")
```

### Ollama (Local)

```python
from llm_provider import OllamaProvider

provider = OllamaProvider(
    model="llama2",
    base_url="http://localhost:11434"  # Default
)

result = provider.complete("Write a Python function")
```

### Google Vertex AI

```python
from llm_provider import GoogleVertexProvider

provider = GoogleVertexProvider(
    model="gemini-pro",
    project_id="your-project-id",
    location="us-central1"
    # Uses Google Cloud credentials from environment
)

result = provider.complete("Explain neural networks")
```

### Azure OpenAI

```python
from llm_provider import AzureOpenAIProvider

provider = AzureOpenAIProvider(
    model="gpt-4",
    endpoint="https://your-resource.openai.azure.com/",
    api_key="your-api-key",
    api_version="2024-02-15-preview"
)

result = provider.complete("Hello from Azure!")
```

### AWS SageMaker (Direct)

```python
from llm_provider import AWSSageMakerProvider

provider = AWSSageMakerProvider(
    endpoint_name="my-custom-endpoint",
    region="us-east-1"
    # Uses AWS credentials from environment
)

result = provider.complete("Custom model completion")
```

## Configuration

### Environment Variables

```bash
# OpenAI
export OPENAI_API_KEY="your-key"

# Anthropic
export ANTHROPIC_API_KEY="your-key"

# AWS (for Bedrock/SageMaker)
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export AWS_DEFAULT_REGION="us-east-1"

# Google Cloud (for Vertex AI)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### YAML Configuration

```yaml
# config.yaml
providers:
  openai:
    provider: openai
    model: gpt-4
    api_key: ${OPENAI_API_KEY}
  
  anthropic:
    provider: anthropic
    model: claude-3-opus-20240229
    api_key: ${ANTHROPIC_API_KEY}

default_provider: openai
```

```python
from llm_provider import LLMProviderConfig, create_provider

# Load configuration
config = LLMProviderConfig.from_file("config.yaml")

# Get provider config
provider_config = config.get_provider("openai")

# Create provider
provider = create_provider(
    provider_config.provider,
    model=provider_config.model,
    **provider_config.config
)
```

## Provider Registry

```python
from llm_provider import get_registry, register_provider

# Get registry
registry = get_registry()

# List registered providers
print(registry.list_providers())
# ['openai', 'anthropic', 'ollama', 'bedrock', 'vertex', 'azure', 'sagemaker']

# Register custom provider
class CustomProvider(LLMProvider):
    # ... implementation ...

register_provider("custom", CustomProvider)

# Create provider
provider = create_provider("custom", model="custom-model")
```

## Cost Tracking

```python
from llm_provider import OpenAIProvider, calculate_total_cost

provider = OpenAIProvider(model="gpt-4")

results = []
for prompt in prompts:
    result = provider.complete(prompt)
    results.append(result)

# Calculate total cost
total_cost = calculate_total_cost(results)
print(f"Total cost: ${total_cost:.4f}")
```

## Error Handling

```python
from llm_provider import OpenAIProvider

provider = OpenAIProvider(model="gpt-4")

try:
    result = provider.complete("Hello!")
except Exception as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

## Advanced Usage

### Custom Provider

```python
from llm_provider import LLMProvider, CompletionResult

class MyCustomProvider(LLMProvider):
    def __init__(self, model: str, **kwargs):
        super().__init__("custom", model, **kwargs)
    
    def complete(self, prompt: str, **kwargs) -> CompletionResult:
        # Custom implementation
        content = self._call_custom_api(prompt)
        return CompletionResult(
            content=content,
            tokens_used=len(content) // 4,
            model=self.model,
            provider="custom",
            cost=0.0
        )
    
    def stream(self, prompt: str, **kwargs):
        # Streaming implementation
        yield "chunk1"
        yield "chunk2"
    
    def get_cost(self, tokens: int) -> float:
        return tokens * 0.0001  # Custom pricing
```

### Fallback Provider

```python
from llm_provider import OpenAIProvider, AnthropicProvider

def complete_with_fallback(prompt: str):
    providers = [
        OpenAIProvider(model="gpt-4"),
        AnthropicProvider(model="claude-3-opus-20240229")
    ]
    
    for provider in providers:
        try:
            return provider.complete(prompt)
        except Exception as e:
            print(f"{provider.provider_name} failed: {e}")
            continue
    
    raise RuntimeError("All providers failed")
```

## API Reference

### CompletionResult

```python
@dataclass
class CompletionResult:
    content: str              # Generated content
    tokens_used: int          # Total tokens used
    model: str                # Model name
    provider: str             # Provider name
    cost: float              # Cost in USD
    metadata: Dict[str, Any] # Additional metadata
    created_at: datetime      # Timestamp
```

### LLMProvider Methods

- `complete(prompt: str, **kwargs) -> CompletionResult`: Complete a prompt
- `stream(prompt: str, **kwargs) -> Iterator[str]`: Stream completion
- `get_cost(tokens: int) -> float`: Calculate cost for tokens
- `list_models() -> List[str]`: List available models (optional)
- `deploy_model(model_path: str, **kwargs) -> str`: Deploy model (optional)

## Dependencies

- `litellm>=1.0.0` - Core dependency for provider support
- `boto3>=1.28.0` (optional) - For AWS SageMaker
- `azure-identity>=1.15.0` (optional) - For Azure
- `google-cloud-aiplatform>=1.38.0` (optional) - For Google Vertex AI

## License

MIT

## Contributing

Contributions welcome! Please see the main project repository for contribution guidelines.

