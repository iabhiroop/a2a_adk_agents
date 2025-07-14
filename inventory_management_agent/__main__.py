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
@click.option("--port", default=8088, help="Port to bind the server to")
def main(host: str, port: int):
    """Run the inventory management agent server."""
    logger.info("--- 🚀 Starting Inventory Management Agent Server... ---")
    
    # Create agent skill
    skill = AgentSkill(
        id='inventory_management',
        name='Inventory Management',
        description='Monitors stock levels, handles demand forecasting, and manages inventory restocking',
        tags=['inventory', 'stock', 'forecasting', 'management'],
        examples=['Check inventory levels', 'Analyze stock trends', 'Generate restock recommendations'],
    )

    # Create agent card
    agent_card = AgentCard(
        name='Inventory Management Agent',
        description='Monitors stock levels and handles demand forecasting for inventory management',
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
