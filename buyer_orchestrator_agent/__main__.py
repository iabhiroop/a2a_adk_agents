import asyncio
import logging
import os
import traceback
from collections.abc import AsyncIterator
from pprint import pformat

import click
from dotenv import load_dotenv
import gradio as gr
import uvicorn

from agent import root_agent
from agent_executor import ADKAgentExecutor

from google.adk.artifacts import InMemoryArtifactService
from google.adk.events import Event
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

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

# Constants for the agent interaction
APP_NAME = 'buyer_orchestrator_app'
USER_ID = 'default_user'
SESSION_ID = 'default_session'


async def get_response_from_agent(
    message: str,
    history: list[gr.ChatMessage],
    runner: Runner,
) -> AsyncIterator[gr.ChatMessage]:
    """Get response from buyer orchestrator agent."""
    try:
        event_iterator: AsyncIterator[Event] = runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=types.Content(
                role='user', parts=[types.Part(text=message)]
            ),
        )

        async for event in event_iterator:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        formatted_call = f'```python\n{pformat(part.function_call.model_dump(exclude_none=True), indent=2, width=80)}\n```'
                        yield gr.ChatMessage(
                            role='assistant',
                            content=f'🛠️ **Tool Call: {part.function_call.name}**\n{formatted_call}',
                        )
                    elif part.function_response:
                        response_content = part.function_response.response
                        if (
                            isinstance(response_content, dict)
                            and 'response' in response_content
                        ):
                            formatted_response_data = response_content[
                                'response'
                            ]
                        else:
                            formatted_response_data = response_content
                        formatted_response = f'```json\n{pformat(formatted_response_data, indent=2, width=80)}\n```'
                        yield gr.ChatMessage(
                            role='assistant',
                            content=f'⚡ **Tool Response from {part.function_response.name}**\n{formatted_response}',
                        )
            if event.is_final_response():
                final_response_text = ''
                if event.content and event.content.parts:
                    final_response_text = ''.join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif event.actions and event.actions.escalate:
                    final_response_text = f'Agent escalated: {event.error_message or "No specific message."}'
                if final_response_text:
                    yield gr.ChatMessage(
                        role='assistant', content=final_response_text
                    )
                break
    except Exception as e:
        print(f'Error in get_response_from_agent (Type: {type(e)}): {e}')
        traceback.print_exc()  # This will print the full traceback
        yield gr.ChatMessage(
            role='assistant',
            content='An error occurred while processing your request. Please check the server logs for details.',
        )


async def run_gradio_interface(host: str, port: int, runner: Runner, session_service: InMemorySessionService):
    """Run the Gradio interface for the buyer orchestrator agent."""
    print('Creating ADK session...')
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print('ADK session created successfully.')

    # Predefined prompt for buyer workflow
    BUYER_WORKFLOW_PROMPT = "Analyze inventory levels and validate purchase requirements. Create PO documents as required and send to respective supplier email."

    async def trigger_buyer_workflow():
        """Trigger the buyer workflow and return the response."""
        try:
            event_iterator: AsyncIterator[Event] = runner.run_async(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=types.Content(
                    role='user', parts=[types.Part(text=BUYER_WORKFLOW_PROMPT)]
                ),
            )

            log_messages = []
            async for event in event_iterator:
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.function_call:
                            formatted_call = f'🛠️ **Tool Call: {part.function_call.name}**\n```python\n{pformat(part.function_call.model_dump(exclude_none=True), indent=2, width=80)}\n```'
                            log_messages.append(formatted_call)
                        elif part.function_response:
                            response_content = part.function_response.response
                            if (
                                isinstance(response_content, dict)
                                and 'response' in response_content
                            ):
                                formatted_response_data = response_content['response']
                            else:
                                formatted_response_data = response_content
                            formatted_response = f'⚡ **Tool Response from {part.function_response.name}**\n```json\n{pformat(formatted_response_data, indent=2, width=80)}\n```'
                            log_messages.append(formatted_response)
                            
                if event.is_final_response():
                    final_response_text = ''
                    if event.content and event.content.parts:
                        final_response_text = ''.join(
                            [p.text for p in event.content.parts if p.text]
                        )
                    elif event.actions and event.actions.escalate:
                        final_response_text = f'Agent escalated: {event.error_message or "No specific message."}'
                    if final_response_text:
                        log_messages.append(f'✅ **Final Response:**\n{final_response_text}')
                    break
                    
            return '\n\n'.join(log_messages) if log_messages else "No response received from agent."
            
        except Exception as e:
            error_msg = f'❌ **Error:** {e}'
            print(f'Error in trigger_buyer_workflow: {e}')
            traceback.print_exc()
            return error_msg

    with gr.Blocks(
        theme=gr.themes.Ocean(), title='Buyer Orchestrator Agent'
    ) as demo:
        gr.Markdown("# 🛒 Buyer Orchestrator Agent")
        gr.Markdown("This agent orchestrates and coordinates the workflow between buyer agents including inventory management, validation, and purchase order processing.")
        gr.Markdown("---")
        gr.Markdown("### Workflow: Analyze inventory → Validate requirements → Create PO documents → Send to suppliers")
        
        with gr.Row():
            trigger_btn = gr.Button(
                "🚀 Execute Buyer Workflow", 
                variant="primary", 
                size="lg"
            )
        
        with gr.Row():
            output_display = gr.Markdown(
                value="Click the button above to execute the buyer workflow. Logs and responses will appear here.",
                label="Workflow Logs & Output"
            )
        
        # Button click handler
        trigger_btn.click(
            fn=trigger_buyer_workflow,
            inputs=[],
            outputs=[output_display]
        )

    print(f'Launching Gradio interface on {host}:{port}...')
    demo.queue().launch(
        server_name=host,
        server_port=port,
    )
    print('Gradio application has been shut down.')

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=8093, help="Port to bind the server to")
@click.option("--interface", default="fastapi", type=click.Choice(['fastapi', 'gradio', 'text']), help="Interface to use: fastapi, gradio, or text")
def main(host: str, port: int, interface: str):
    """Run the buyer orchestrator agent server."""
    logger.info("--- 🚀 Starting Buyer Orchestrator Agent Server... ---")
    
    # Create agent skill
    skill = AgentSkill(
        id='buyer_orchestration',
        name='Buyer Workflow Orchestration',
        description='Orchestrates and coordinates workflow between inventory, validation, and purchase order agents',
        tags=['orchestration', 'buyer', 'workflow', 'coordination'],
        examples=['Execute buyer workflow', 'Check inventory and create purchase orders', 'Coordinate purchasing process'],
    )

    # Create agent card
    agent_card = AgentCard(
        name='Buyer Orchestrator Agent',
        description='Orchestrates and coordinates the workflow between buyer agents',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    # Create session service
    session_service = InMemorySessionService()

    # Create runner
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
        memory_service=InMemoryMemoryService(),
        artifact_service=InMemoryArtifactService(),
    )

    if interface == "gradio":
        # Run Gradio interface
        asyncio.run(run_gradio_interface(host, port, runner, session_service))
    elif interface == "text":
        # Run simple text client
        asyncio.run(run_text_client(runner, session_service))
    else:
        # Run FastAPI server (default)
        executor = ADKAgentExecutor(runner, agent_card)
        
        app = A2AFastAPIApplication(
            agent_card=agent_card,
            http_handler=DefaultRequestHandler(
                agent_executor=executor,
                task_store=InMemoryTaskStore(),
            )
        )
        uvicorn.run(app.build(), host=host, port=port)


async def send_text_to_agent(text: str, runner: Runner, session_service: InMemorySessionService) -> str:
    """
    Simple function to send text input to the agent and get a response.
    
    Args:
        text: The text message to send to the agent
        runner: The ADK runner instance
        session_service: The session service instance
    
    Returns:
        The agent's response as a string
    """
    try:
        # Ensure session exists
        try:
            await session_service.create_session(
                app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
            )
        except Exception:
            # Session might already exist, continue
            pass

        event_iterator: AsyncIterator[Event] = runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=types.Content(
                role='user', parts=[types.Part(text=text)]
            ),
        )

        responses = []
        async for event in event_iterator:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        responses.append(f"Tool Call: {part.function_call.name}")
                    elif part.function_response:
                        responses.append(f"Tool Response: {part.function_response.name}")
                        
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_text = ''.join([p.text for p in event.content.parts if p.text])
                    if final_text:
                        responses.append(final_text)
                elif event.actions and event.actions.escalate:
                    responses.append(f'Agent escalated: {event.error_message or "No specific message."}')
                break
                
        return '\n'.join(responses) if responses else "No response received from agent."
        
    except Exception as e:
        error_msg = f'Error in send_text_to_agent: {e}'
        print(error_msg)
        traceback.print_exc()
        return error_msg


async def run_text_client(runner: Runner, session_service: InMemorySessionService):
    """Run a simple text-based client for the agent."""
    print("🛒 Buyer Orchestrator Agent - Text Client")
    print("=" * 50)
    print("Type your messages below. Type 'quit' to exit.")
    print()

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            if not user_input:
                continue

            print("Agent: ", end="", flush=True)
            
            # Send to agent and get response
            response = await send_text_to_agent(user_input, runner, session_service)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
