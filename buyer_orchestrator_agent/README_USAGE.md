# Buyer Orchestrator Agent - Usage Guide

This document explains how to use the different interfaces available for the Buyer Orchestrator Agent.

## Overview

The Buyer Orchestrator Agent can be run with three different interfaces:

1. **FastAPI Server** (default) - REST API interface
2. **Gradio Web Interface** - Interactive web-based chat interface
3. **Text Client** - Command-line text interface

## Prerequisites

Make sure you have installed the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Agent

### 1. FastAPI Server (Default)

```bash
python __main__.py
```

Or explicitly specify the FastAPI interface:

```bash
python __main__.py --interface fastapi --host localhost --port 8093
```

This starts a REST API server that you can interact with using HTTP requests.

### 2. Gradio Web Interface

```bash
python __main__.py --interface gradio --host localhost --port 8083
```

This launches a web-based chat interface accessible at `http://localhost:8083`. You can:
- Chat with the agent in a user-friendly web interface
- See tool calls and responses formatted nicely
- View the conversation history

### 3. Text Client

```bash
python __main__.py --interface text
```

This starts a command-line interface where you can type messages directly and receive responses. Type 'quit' to exit.

## Using the Text Function Programmatically

You can also use the `send_text_to_agent` function directly in your Python code:

```python
import asyncio
from __main__ import send_text_to_agent, APP_NAME
from agent import root_agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

async def example():
    # Set up the agent
    session_service = InMemorySessionService()
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
        memory_service=InMemoryMemoryService(),
        artifact_service=InMemoryArtifactService(),
    )
    
    # Send a message
    response = await send_text_to_agent(
        "Check inventory status for product ABC123", 
        runner, 
        session_service
    )
    print(response)

# Run the example
asyncio.run(example())
```

## Example Commands

Here are some example commands you can try with the agent:

- "Execute buyer workflow for product XYZ"
- "Check inventory status"
- "Create a purchase order for 100 units of ABC123"
- "Coordinate purchasing process"
- "Validate purchase requirements"

## Configuration Options

- `--host`: Host to bind the server to (default: localhost)
- `--port`: Port to bind the server to (default: 8093 for FastAPI, can be changed for Gradio)
- `--interface`: Interface type (fastapi, gradio, or text)

## Troubleshooting

1. **Import errors**: Make sure all dependencies are installed using `pip install -r requirements.txt`
2. **Port conflicts**: If the default port is in use, specify a different port with `--port`
3. **Agent errors**: Check the console output for detailed error messages and stack traces

## Files

- `__main__.py`: Main application file with all interfaces
- `simple_text_client.py`: Standalone example of using the text function
- `requirements.txt`: Python dependencies
- `agent.py`: Agent implementation
- `agent_executor.py`: Agent executor implementation
