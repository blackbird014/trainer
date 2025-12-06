# LLM Provider Examples

This directory contains example scripts demonstrating various features of the LLM Provider module.

## Basic Examples

### `basic_usage.py`
Basic usage examples including:
- Simple completion
- Streaming responses
- Custom parameters
- Cost calculation

**Run:**
```bash
python examples/basic_usage.py
```

### `all_providers.py`
Examples for all available providers:
- OpenAI
- Anthropic
- Ollama (local)
- AWS Bedrock
- Google Vertex AI
- Azure OpenAI
- HuggingFace
- AWS SageMaker

**Run:**
```bash
python examples/all_providers.py
```

**Note:** Most examples will fail without proper API keys/credentials - this is expected.

### `registry_usage.py`
Demonstrates using the provider registry:
- Listing providers
- Creating providers from registry
- Registering custom providers
- Registry information

**Run:**
```bash
python examples/registry_usage.py
```

### `configuration_example.py`
Shows configuration management:
- Environment variable configuration
- Dictionary configuration
- File-based configuration (JSON/YAML)
- Multi-provider configuration

**Run:**
```bash
python examples/configuration_example.py
```

## Integration Examples

### `integration_prompt_manager.py`
Integration with the Prompt Manager module:
- Loading prompts and executing with LLM
- Context loading and LLM execution
- Prompt composition with LLM
- Provider switching

**Run:**
```bash
python examples/integration_prompt_manager.py
```

**Requirements:**
- `prompt-manager` module installed
- Context files available (optional)

### `integration_security.py`
Integration with the Prompt Security module:
- Secure prompt validation
- Input sanitization
- Template escaping
- Security configuration
- End-to-end secure workflow

**Run:**
```bash
python examples/integration_security.py
```

**Requirements:**
- `prompt-security` module installed

## Prerequisites

1. **Virtual Environment**: Activate your virtual environment
   ```bash
   source /path/to/venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   cd _dev/llm-provider
   pip install -e ".[all]"
   ```

3. **Set API Keys** (for examples that make actual API calls):
   ```bash
   export OPENAI_API_KEY="your-key"
   export ANTHROPIC_API_KEY="your-key"
   # etc.
   ```

## Notes

- Most examples use mocks or will gracefully handle missing credentials
- Examples that make actual API calls require valid API keys
- Some examples require other modules (`prompt-manager`, `prompt-security`) to be installed
- Examples are designed to be educational - modify them for your use case

## Running All Examples

To run all examples (where dependencies are available):

```bash
for example in examples/*.py; do
    echo "Running $example..."
    python "$example"
    echo ""
done
```
