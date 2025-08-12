# Google ADK Agent Core

A minimal AI agent implementation that provides chat capabilities using OpenRouter API gateway. This core library is consumed by the FastAPI application to handle AI interactions.

## Overview

The ADK Agent Core is a lightweight Python library that:
- Connects to AI models via OpenRouter API
- Handles configuration loading from YAML files  
- Provides simple chat interface
- Manages API authentication and requests

## Directory Structure

```
google-adk/
├── requirements.txt          # Python dependencies (httpx, pyyaml)
├── README.md                # This file
└── src/
    └── adk_agent/
        ├── __init__.py      # Package marker
        ├── agents/
        │   └── core_agent.py    # Main agent implementation
        └── config/
            ├── loader.py        # Configuration loader
            └── runtime.yaml     # Agent configuration
```

## Configuration

### runtime.yaml
```yaml
provider: openrouter
model: anthropic/claude-opus-4.1
```

### Environment Variables

Required in `.env` file:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

Optional:
```bash
MODEL_SLUG=anthropic/claude-opus-4.1    # Override model from config
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1  # Default API base
```

## Core Components

### CoreAgent Class
- **Purpose**: Main chat agent that communicates with AI models
- **Key Methods**:
  - `run(system_prompt, user_input)` - Send chat message and get response
- **Dependencies**: Requires OpenRouter API key and model configuration

### Configuration Loader  
- **Purpose**: Load and validate agent configuration
- **Features**: YAML file parsing, environment variable overrides
- **Usage**: `load_runtime_config(config_path)`

## Usage by API

The FastAPI application consumes this agent core as follows:

1. **Import**: Direct Python imports from `/deps` path in Docker container
2. **Configuration**: Loads config via `ADK_CONFIG_PATH` environment variable
3. **Instantiation**: Creates agent instance using `create_core_agent(config)`  
4. **Communication**: Calls `agent.run(system_prompt, user_input)` for each request

## Architecture Flow

```
API Request → FastAPI → load_runtime_config() → create_core_agent() → CoreAgent.run() → OpenRouter API
```

## Dependencies

- **httpx**: HTTP client for OpenRouter API communication
- **pyyaml**: YAML configuration file parsing

## Development

To modify agent behavior:
1. Update `runtime.yaml` for configuration changes
2. Modify `core_agent.py` for logic changes  
3. Update environment variables in `.env` file
4. API will automatically pick up changes on next request

## Environment Setup

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Add your OpenRouter API key:**
   ```bash
   echo "OPENROUTER_API_KEY=your_key_here" >> .env
   ```

3. **Optional model override:**
   ```bash
   echo "MODEL_SLUG=openai/gpt-4o-mini" >> .env
   ``` 