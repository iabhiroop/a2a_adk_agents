import asyncio
import json
import logging
import os
import uuid
from typing import Any

import httpx

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    Part,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from remote_agent_connection import (
    RemoteAgentConnections,
    TaskUpdateCallback,
)
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext

# ruff: noqa: E501
# pylint: disable=logging-fstring-interpolation
import asyncio
import json
import os
import uuid

from typing import Any

import httpx

from a2a.client import A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    Part,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from remote_agent_connection import (
    RemoteAgentConnections,
    TaskUpdateCallback,
)
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools.tool_context import ToolContext


load_dotenv()


def convert_part(part: Part, tool_context: ToolContext):
    """Convert a part to text. Only text parts are supported."""
    if part.type == 'text':
        return part.text

    return f'Unknown type: {part.type}'


def convert_parts(parts: list[Part], tool_context: ToolContext):
    """Convert parts to text."""
    rval = []
    for p in parts:
        rval.append(convert_part(p, tool_context))
    return rval


def create_send_message_payload(
    text: str, task_id: str | None = None, context_id: str | None = None
) -> dict[str, Any]:
    """Helper function to create the payload for sending a task."""
    payload: dict[str, Any] = {
        'message': {
            'role': 'user',
            'parts': [{'type': 'text', 'text': text}],
            'messageId': uuid.uuid4().hex,
        },
    }

    if task_id:
        payload['message']['taskId'] = task_id

    if context_id:
        payload['message']['contextId'] = context_id
    return payload


class BuyerOrchestratorAgent:
    """The Buyer Orchestrator agent.

    This is the agent responsible for choosing which remote buyer agents to send
    tasks to and coordinate their work in the buyer workflow.
    """

    def __init__(
        self,
        task_callback: TaskUpdateCallback | None = None,
    ):
        self.task_callback = task_callback
        self.remote_agent_connections: dict[str, RemoteAgentConnections] = {}
        self.cards: dict[str, AgentCard] = {}
        self.agents: str = ''

    async def _async_init_components(
        self, remote_agent_addresses: list[str]
    ) -> None:
        """Asynchronous part of initialization."""
        # Use a single httpx.AsyncClient for all card resolutions for efficiency
        async with httpx.AsyncClient(timeout=30) as client:
            for address in remote_agent_addresses:
                card_resolver = A2ACardResolver(
                    client, address
                )  # Constructor is sync
                try:
                    card = (
                        await card_resolver.get_agent_card()
                    )  # get_agent_card is async

                    remote_connection = RemoteAgentConnections(
                        agent_card=card, agent_url=address
                    )
                    self.remote_agent_connections[card.name] = remote_connection
                    self.cards[card.name] = card
                except httpx.ConnectError as e:
                    print(
                        f'ERROR: Failed to get agent card from {address}: {e}'
                    )
                except Exception as e:  # Catch other potential errors
                    print(
                        f'ERROR: Failed to initialize connection for {address}: {e}'
                    )

        # Populate self.agents using the logic from original __init__ (via list_remote_agents)
        agent_info = []
        for agent_detail_dict in self.list_remote_agents():
            agent_info.append(json.dumps(agent_detail_dict))
        self.agents = '\n'.join(agent_info)

    @classmethod
    async def create(
        cls,
        remote_agent_addresses: list[str],
        task_callback: TaskUpdateCallback | None = None,
    ) -> 'BuyerOrchestratorAgent':
        """Create and asynchronously initialize an instance of the BuyerOrchestratorAgent."""
        instance = cls(task_callback)
        await instance._async_init_components(remote_agent_addresses)
        return instance

    def create_agent(self) -> Agent:
        """Create an instance of the BuyerOrchestratorAgent."""
        model_id = 'gemini-2.5-flash'
        print(f'Using model: {model_id}')
        return Agent(
            model=model_id,
            name='Buyer_Orchestrator_Agent',
            instruction=self.root_instruction,
            before_model_callback=self.before_model_callback,
            description=(
                'This Buyer Orchestrator agent orchestrates the workflow between buyer agents for inventory management, purchase validation, and purchase order generation'
            ),
            tools=[
                self.send_message,
                self.execute_buyer_workflow,
            ],
        )

    def root_instruction(self, context: ReadonlyContext) -> str:
        """Generate the root instruction for the BuyerOrchestratorAgent."""
        current_agent = self.check_active_agent(context)
        return f"""
        **Role:** You are an expert Buyer Workflow Orchestrator. Your primary function is to coordinate and manage the buyer workflow across three specialized agents.

        **Core Directives:**

        * **Workflow Coordination:** Use the `execute_buyer_workflow` function to run the complete buyer workflow sequence.
        * **Task Delegation:** Use the `send_message` function to assign specific tasks to individual buyer agents.
        * **Sequential Processing:** Ensure the buyer workflow follows the correct sequence: Inventory Management → Purchase Validation → Purchase Order Generation.
        * **Contextual Awareness:** Provide each agent with relevant context from previous steps in the workflow.
        * **Autonomous Execution:** Execute workflows without requiring user confirmation between steps.
        * **Comprehensive Reporting:** Present detailed results from each stage of the buyer workflow.
        * **Error Handling:** Handle failures gracefully and provide clear error reporting.
        * **Tool Reliance:** Use available tools to address user requests. Do not generate responses based on assumptions.
        * **Active Agent Tracking:** Track which agent is currently active and route follow-up requests appropriately.

        **Buyer Workflow Sequence:**
        1. **Inventory Management Agent**: Analyzes stock levels and demand patterns
        2. **Purchase Validation Agent**: Validates purchase requirements based on inventory analysis  
        3. **Purchase Order Agent**: Generates purchase orders based on validated requirements

        **Available Buyer Agents:**
        {self.agents}

        **Currently Active Agent:** {current_agent['active_agent']}

        **Usage Instructions:**
        - For complete workflow: Use `execute_buyer_workflow` with the overall request
        - For individual agent tasks: Use `send_message` with specific agent name and task
        - Always provide comprehensive context when delegating tasks
        """

    def check_active_agent(self, context: ReadonlyContext):
        state = context.state
        if (
            'session_id' in state
            and 'session_active' in state
            and state['session_active']
            and 'active_agent' in state
        ):
            return {'active_agent': f'{state["active_agent"]}'}
        return {'active_agent': 'None'}

    def before_model_callback(
        self, callback_context: CallbackContext, llm_request
    ):
        state = callback_context.state
        if 'session_active' not in state or not state['session_active']:
            if 'session_id' not in state:
                state['session_id'] = str(uuid.uuid4())
            state['session_active'] = True

    def list_remote_agents(self):
        """List the available remote buyer agents you can use to delegate tasks."""
        if not self.cards:
            return []

        remote_agent_info = []
        for card in self.cards.values():
            print(f'Found buyer agent card: {card.model_dump(exclude_none=True)}')
            print('=' * 100)
            remote_agent_info.append(
                {'name': card.name, 'description': card.description}
            )
        return remote_agent_info

    async def send_message(
        self, agent_name: str, task: str, tool_context: ToolContext
    ):
        """Sends a task to a specific remote buyer agent.

        This will send a message to the remote buyer agent named agent_name.

        Args:
            agent_name: The name of the buyer agent to send the task to.
            task: The comprehensive task description and context for the agent.
            tool_context: The tool context this method runs in.

        Yields:
            A dictionary of JSON data.
        """
        if agent_name not in self.remote_agent_connections:
            raise ValueError(f'Buyer agent {agent_name} not found')
        
        state = tool_context.state
        state['active_agent'] = agent_name
        client = self.remote_agent_connections[agent_name]

        if not client:
            raise ValueError(f'Client not available for {agent_name}')
        
        task_id = state['task_id'] if 'task_id' in state else str(uuid.uuid4())

        if 'context_id' in state:
            context_id = state['context_id']
        else:
            context_id = str(uuid.uuid4())

        message_id = ''
        metadata = {}
        if 'input_message_metadata' in state:
            metadata.update(**state['input_message_metadata'])
            if 'message_id' in state['input_message_metadata']:
                message_id = state['input_message_metadata']['message_id']
        if not message_id:
            message_id = str(uuid.uuid4())

        payload = {
            'message': {
                'role': 'user',
                'parts': [
                    {'type': 'text', 'text': task}
                ],
                'messageId': message_id,
            },
        }

        if task_id:
            payload['message']['taskId'] = task_id

        if context_id:
            payload['message']['contextId'] = context_id

        message_request = SendMessageRequest(
            id=message_id, params=MessageSendParams.model_validate(payload)
        )
        send_response: SendMessageResponse = await client.send_message(
            message_request=message_request
        )
        print(
            'send_response',
            send_response.model_dump_json(exclude_none=True, indent=2),
        )

        if not isinstance(send_response.root, SendMessageSuccessResponse):
            print('received non-success response. Aborting get task ')
            return None

        if not isinstance(send_response.root.result, Task):
            print('received non-task response. Aborting get task ')
            return None

        return send_response.root.result

    async def execute_buyer_workflow(
        self, workflow_request: str, tool_context: ToolContext
    ):
        """Executes the complete buyer workflow across all three buyer agents.

        This orchestrates the sequential execution of:
        1. Inventory Management Agent - analyzes stock levels and demand
        2. Purchase Validation Agent - validates purchase requirements  
        3. Purchase Order Agent - generates purchase orders

        Args:
            workflow_request: The overall workflow request and context.
            tool_context: The tool context this method runs in.

        Yields:
            A dictionary of workflow results.
        """
        workflow_results = {
            'workflow_id': str(uuid.uuid4()),
            'status': 'starting',
            'steps': []
        }
        
        try:
            # Step 1: Inventory Management
            print("Executing Step 1: Inventory Management")
            inventory_task = f"Analyze current inventory levels and demand patterns. Context: {workflow_request}"
            inventory_result = await self.send_message(
                "Inventory Management Agent", 
                inventory_task, 
                tool_context
            )
            workflow_results['steps'].append({
                'step': 1,
                'agent': 'Inventory Management Agent',
                'task': inventory_task,
                'result': inventory_result
            })

            # Step 2: Purchase Validation
            print("Executing Step 2: Purchase Validation")
            validation_task = f"Validate purchase requirements based on inventory analysis: {inventory_result}. Original request: {workflow_request}"
            validation_result = await self.send_message(
                "Purchase Validation Agent",
                validation_task,
                tool_context
            )
            workflow_results['steps'].append({
                'step': 2,
                'agent': 'Purchase Validation Agent',
                'task': validation_task,
                'result': validation_result
            })

            # Step 3: Purchase Order Generation
            print("Executing Step 3: Purchase Order Generation")
            po_task = f"Generate purchase orders based on validation results: {validation_result}. Inventory context: {inventory_result}"
            po_result = await self.send_message(
                "Purchase Order Agent",
                po_task,
                tool_context
            )
            workflow_results['steps'].append({
                'step': 3,
                'agent': 'Purchase Order Agent',
                'task': po_task,
                'result': po_result
            })

            workflow_results['status'] = 'completed'
            workflow_results['summary'] = 'Buyer workflow completed successfully across all three agents'

        except Exception as e:
            print(f"Buyer workflow execution failed: {e}")
            workflow_results['status'] = 'failed'
            workflow_results['error'] = str(e)

        return workflow_results


def _get_initialized_buyer_orchestrator_sync() -> Agent:
    """Synchronously creates and initializes the BuyerOrchestratorAgent."""

    async def _async_main() -> Agent:
        buyer_orchestrator_instance = await BuyerOrchestratorAgent.create(
            remote_agent_addresses=[
                os.getenv('INVENTORY_AGENT_URL', 'http://localhost:8001'),
                os.getenv('PURCHASE_VALIDATION_AGENT_URL', 'http://localhost:8002'),
                os.getenv('PURCHASE_ORDER_AGENT_URL', 'http://localhost:8003'),
            ]
        )
        return buyer_orchestrator_instance.create_agent()

    try:
        return asyncio.run(_async_main())
    except RuntimeError as e:
        if 'asyncio.run() cannot be called from a running event loop' in str(e):
            print(
                f'Warning: Could not initialize BuyerOrchestratorAgent with asyncio.run(): {e}. '
                'This can happen if an event loop is already running (e.g., in Jupyter). '
                'Consider initializing BuyerOrchestratorAgent within an async function in your application.'
            )
        raise


root_agent = _get_initialized_buyer_orchestrator_sync()
