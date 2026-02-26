# RegulAite LLM Configuration

This directory contains configuration classes and utilities for the RegulAite backend.

## LLM Configuration

The `llm_config.py` file provides a `LLMConfig` class for configuring LLM models used by the agents. This allows for more flexible configuration of different LLM providers and model parameters.

### Basic Usage

```python
from config.llm_config import LLMConfig
from openai import OpenAI

# Create an LLM configuration
llm_config = LLMConfig(
    provider="openai",
    model="gpt-4",
    temperature=0.7,
    max_tokens=2048,
    api_key="your-api-key",  # Optional, will use environment variable if not provided
    api_url=None,  # Optional, for custom API endpoints
)

# Use the configuration with OpenAI client
client = OpenAI(
    api_key=llm_config.api_key,
    base_url=llm_config.api_url or None
)

# Make a request
response = client.chat.completions.create(
    model=llm_config.model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=llm_config.temperature,
    max_tokens=llm_config.max_tokens,
    **llm_config.additional_params
)
```

### Available Configuration Options

The `LLMConfig` class supports the following parameters:

- `provider`: LLM provider (e.g., "openai", "anthropic", "cohere")
- `model`: Model name to use (e.g., "gpt-4", "claude-3-opus")
- `api_key`: API key (optional, will use environment variable if not provided)
- `api_url`: Custom API URL endpoint (optional, for self-hosted models or proxies)
- `temperature`: Temperature for generation (0-1)
- `max_tokens`: Maximum tokens to generate
- `top_p`: Top-p sampling parameter (optional)
- `frequency_penalty`: Frequency penalty parameter (optional)
- `presence_penalty`: Presence penalty parameter (optional)
- `stop_sequences`: Sequences that will stop generation (optional)
- `additional_params`: Additional provider-specific parameters (optional)

### Using Custom API Endpoints

For self-hosted models or API proxies, you can specify a custom API URL:

```python
llm_config = LLMConfig(
    provider="openai",
    model="gpt-4",
    api_url="https://your-custom-endpoint.com/v1",
)
```

### Using Different LLM Providers

The configuration system supports different LLM providers and automatically maps common parameters to their provider-specific equivalents:

```python
# Anthropic configuration
anthropic_config = LLMConfig(
    provider="anthropic",
    model="claude-3-opus-20240229",
    max_tokens=2048,  # Will be converted to max_tokens_to_sample for Anthropic
)

# Cohere configuration
cohere_config = LLMConfig(
    provider="cohere",
    model="command",
    temperature=0.7,
)
```

### Provider-Specific Parameters

You can specify additional provider-specific parameters using the `additional_params` field:

```python
llm_config = LLMConfig(
    provider="openai",
    model="gpt-4",
    additional_params={
        "logit_bias": {50256: -100},  # Example of OpenAI-specific parameter
    }
)
``` 