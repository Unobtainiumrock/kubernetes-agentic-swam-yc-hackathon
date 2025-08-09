# ADK Agent API

A minimal FastAPI application that provides REST endpoints for AI agent interactions using the Google ADK agent core.

## Architecture

The API serves as a HTTP gateway to the AI agent, providing two simple endpoints:
- **Health Check**: System status endpoint
- **AI Agent**: Chat interface to the AI agent

```
┌─────────────┐    HTTP    ┌─────────────┐    Python    ┌─────────────┐
│   Client    │ ────────── │  FastAPI    │ ───────────  │  AI Agent   │
│             │            │     API     │              │    Core     │
└─────────────┘            └─────────────┘              └─────────────┘
```

## Directory Structure

```
api/
├── Dockerfile              # Container configuration
├── Makefile               # Build and run commands
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── app/
    ├── __init__.py       # Package marker
    ├── app.py           # FastAPI application factory
    ├── server.py        # Uvicorn server entry point
    ├── schemas.py       # Pydantic data models
    └── routers/
        ├── __init__.py  # Package marker
        └── agent.py     # API endpoints implementation
```

## Quick Start

1. **Build the container:**
   ```bash
   make api-build
   ```

2. **Run the API:**
   ```bash
   make api-run
   ```

3. **Test the endpoints:**
   ```bash
   # Health check
   curl http://localhost:8080/health
   
   # AI agent chat
   curl -X POST http://localhost:8080/v1/agent/run \
     -H "Content-Type: application/json" \
     -d '{"input": "Hello, how are you?"}'
   ```

## Available Commands

| Command | Description |
|---------|-------------|
| `make api-build` | Build Docker image |
| `make api-run` | Run API container (port 8080) |
| `make api-logs` | View container logs |
| `make api-stop` | Stop API container |
| `make api-clean` | Remove Docker image |

## API Endpoints

### Health Check
- **GET** `/health`
- **Response**: `{"status": "ok", "service": "adk-agent-api", "version": "0.0.1"}`

### AI Agent Chat
- **POST** `/v1/agent/run`
- **Request**: `{"input": "your message here"}`
- **Response**: `{"run_id": "uuid", "output": "agent response", "metadata": {}}`

## Integration with Google ADK

The API integrates with the Google ADK agent core located in `../google-adk/`:

1. **Configuration**: Loads agent config from `/deps/adk_agent/config/runtime.yaml`
2. **Dependencies**: Agent core is mounted at runtime via Docker volumes
3. **Communication**: Direct Python imports and function calls
4. **Environment**: Requires `OPENROUTER_API_KEY` environment variable

## Environment Setup

Required environment variables (via `.env` file in `google-adk/` directory):
```bash
OPENROUTER_API_KEY=your_api_key_here
MODEL_SLUG=openai/gpt-5-mini  # Optional override
```

## Development

The API automatically reloads the agent configuration on each request, making development and testing easier. No restart required for config changes.