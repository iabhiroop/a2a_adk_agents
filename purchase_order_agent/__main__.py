import logging
import os

import click
from dotenv import load_dotenv
import uvicorn

from agent import root_agent
from agent_executor import ADKAgentExecutor

from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)


logger = logging.getLogger(__name__)

load_dotenv()


@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=8090, help="Port to bind the server to")
def main(host: str, port: int):
    """Run the purchase order agent server."""
    logger.info("--- 🚀 Starting Purchase Order Agent Server... ---")
    
    # Create agent skill
    skill = AgentSkill(
        id='purchase_order_generation',
        name='Purchase Order Generation',
        description='Generates purchase orders, manages supplier communications, and handles order documentation',
        tags=['purchase_order', 'generation', 'supplier', 'communication'],
        examples=['Generate purchase order', 'Send order to supplier', 'Create order documentation'],
    )

    # Create agent card
    agent_card = AgentCard(
        name='Purchase Order Agent',
        description='Generates purchase orders and manages supplier communications',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    # Create runner
    runner = Runner(
        app_name=agent_card.name,
        agent=root_agent,
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        artifact_service=InMemoryArtifactService(),
    )

    # Create executor
    executor = ADKAgentExecutor(runner=runner, card=agent_card)

    # Create app
    app = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )
    )
    uvicorn.run(app.build(), host=host, port=port)


if __name__ == "__main__":
    main()
