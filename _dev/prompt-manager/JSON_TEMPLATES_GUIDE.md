# JSON Templates Guide

## Overview

The prompt-manager now supports JSON-based templates for enhanced security and structure. JSON templates provide:

- **Clear boundaries** between system instructions, context, user data, and instructions
- **Automatic security** - user input is validated, sanitized, and escaped
- **Structured format** - easier to validate, version, and manipulate programmatically
- **Pre-processing support** - convert text templates to JSON format

## JSON Template Structure

```json
{
  "metadata": {
    "version": "1.0",
    "template_id": "greeting_template",
    "variables": ["name", "age"],
    "preprocessed": true,
    "source_file": "greeting.md"
  },
  "sections": {
    "system": [
      "You are a helpful assistant.",
      "Always be polite and professional."
    ],
    "context": [
      "User context information..."
    ],
    "user_data": {
      "name": "{{name}}",
      "age": "{{age}}"
    },
    "instruction": "Generate a greeting for {{name}} who is {{age}} years old."
  }
}
```

## Usage

### Option 1: Pre-process Text Templates (Recommended)

Convert existing text templates to JSON format:

```python
from prompt_manager import TemplatePreprocessor

# Pre-process a single template
json_template = TemplatePreprocessor.preprocess_template(
    "information/instructions/greeting.md",
    "information/instructions/greeting.json"
)

# Pre-process entire directory
templates = TemplatePreprocessor.preprocess_directory(
    "information/instructions/",
    "information/instructions/json/",
    pattern="*.md"
)
```

### Option 2: Use JSON Templates Directly

```python
from prompt_manager import PromptManager, JSONTemplate
from prompt_security import SecurityModule

# Initialize with security
security = SecurityModule(strict_mode=True)
manager = PromptManager(
    security_module=security,
    use_json_templates=True
)

# Load JSON template
template = manager.load_prompt("greeting.json")

# Fill with user data (automatically secured)
filled = manager.fill_template(
    template,
    {"name": "John", "age": "30"}
)
```

### Option 3: Create JSON Templates Manually

```python
from prompt_manager import JSONTemplate

structure = {
    "metadata": {
        "version": "1.0",
        "template_id": "custom_template"
    },
    "sections": {
        "instruction": "Hello {{name}}!",
        "user_data": {
            "name": "{{name}}"
        }
    }
}

template = JSONTemplate(structure)
```

## Security Integration

JSON templates automatically apply security when filling:

1. **Validation**: Checks length, characters, types
2. **Sanitization**: Removes control characters, dangerous patterns
3. **Detection**: Detects prompt injection attempts
4. **Escaping**: Escapes user input with delimiters

```python
# Security is applied automatically
filled = template.fill(
    {"name": "User input"},
    security_module=security  # Optional, but recommended
)
```

## Template Sections

### System Section
System-level instructions that should never be overridden:
```json
"system": [
  "You are a helpful assistant.",
  "Always follow these guidelines..."
]
```

### Context Section
Background information and domain knowledge:
```json
"context": [
  "Context file 1 content...",
  "Context file 2 content..."
]
```

### User Data Section
User-provided data (automatically validated and escaped):
```json
"user_data": {
  "company_name": "{{company_name}}",
  "ticker": "{{ticker}}"
}
```

### Instruction Section
Main task instruction:
```json
"instruction": "Analyze {{company_name}} ({{ticker}})..."
```

## Converting Text to JSON

Text templates use `{variable}` syntax:
```
Hello {name}! You are {age} years old.
```

JSON templates use `{{variable}}` syntax in sections:
```json
{
  "sections": {
    "instruction": "Hello {{name}}! You are {{age}} years old.",
    "user_data": {
      "name": "{{name}}",
      "age": "{{age}}"
    }
  }
}
```

The pre-processor automatically converts `{var}` → `{{var}}` and moves variables to `user_data` section.

## Output Formats

### Text Prompt (for LLM)
```python
prompt_text = template.to_prompt_text(filled_structure)
# Returns formatted text with clear section boundaries
```

### JSON String
```python
json_string = template.to_json_string(filled_structure)
# Returns JSON representation
```

## Migration Strategy

1. **Pre-process existing templates**:
   ```bash
   python -c "from prompt_manager import TemplatePreprocessor; \
               TemplatePreprocessor.preprocess_directory('information/instructions/', 'information/instructions/json/')"
   ```

2. **Update code to use JSON templates**:
   ```python
   manager = PromptManager(use_json_templates=True)
   ```

3. **Keep text templates** for editing, use JSON for runtime

## Benefits

- ✅ **Security**: Automatic validation and escaping
- ✅ **Structure**: Clear boundaries between sections
- ✅ **Validation**: JSON schema validation possible
- ✅ **Versioning**: Track template changes easily
- ✅ **Flexibility**: Can output text or JSON
- ✅ **Backward Compatible**: Text templates still work

## Example Workflow

```python
# 1. Pre-process templates (one-time)
from prompt_manager import TemplatePreprocessor
TemplatePreprocessor.preprocess_directory("prompts/", "prompts/json/")

# 2. Use in application
from prompt_manager import PromptManager
from prompt_security import SecurityModule

security = SecurityModule(strict_mode=True)
manager = PromptManager(
    security_module=security,
    use_json_templates=True
)

# 3. Load and fill
template = manager.load_prompt("prompts/json/greeting.json")
prompt = manager.fill_template(template, {"name": "World"})

# 4. Send to LLM
response = llm.complete(prompt)
```

## Best Practices

1. **Pre-process templates** during build/deployment
2. **Use JSON templates** in production for security
3. **Keep text templates** for human editing
4. **Enable security module** for all user input
5. **Use strict mode** in production
6. **Review JSON structure** after pre-processing

