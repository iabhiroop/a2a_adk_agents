from collections.abc import AsyncGenerator
import logging

from google.adk import Runner
from google.adk.events import Event
from google.genai import types

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    AgentCard,
    FilePart,
    FileWithBytes,
    FileWithUri,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils.errors import ServerError


logger = logging.getLogger(__name__)


class ADKAgentExecutor(AgentExecutor):
    """An AgentExecutor that runs an ADK supplier orchestrator agent."""

    def __init__(self, runner: Runner, card: AgentCard):
        self.runner = runner
        self._card = card
        self._running_sessions = {}

    def _run_agent(
        self, session_id, new_message: types.Content
    ) -> AsyncGenerator[Event, None]:
        return self.runner.run_async(
            session_id=session_id, user_id="self", new_message=new_message
        )

    async def _process_request(
        self,
        new_message: types.Content,
        session_id: str,
        task_updater: TaskUpdater,
    ) -> None:
        session = await self._upsert_session(
            session_id,
        )

        logger.info(f"Running supplier orchestrator agent for session {session_id}")

        async for event in self._run_agent(session_id, new_message):
            if event.agent_turn_started:
                await task_updater.update_task(
                    state=TaskState.IN_PROGRESS,
                )
            elif event.agent_content_delta:
                await task_updater.add_content_delta(event.agent_content_delta)
            elif event.agent_turn_finished:
                await task_updater.update_task(
                    state=TaskState.COMPLETE,
                )
            elif event.error:
                logger.error(f"Error in supplier orchestrator agent: {event.error}")
                await task_updater.update_task(
                    state=TaskState.FAILED,
                    result="Agent execution failed",
                )

    async def _upsert_session(self, session_id: str):
        """Create or retrieve a session for the supplier orchestrator agent."""
        if session_id not in self._running_sessions:
            self._running_sessions[session_id] = await self.runner.create_session(
                session_id=session_id, user_id="self"
            )
        return self._running_sessions[session_id]

    async def execute_request(
        self, request_context: RequestContext, task_updater: TaskUpdater
    ) -> None:
        """Execute a request for the supplier orchestrator agent."""
        try:
            parts = []
            for part in request_context.request.content.parts:
                if isinstance(part, TextPart):
                    parts.append(types.Part.from_text(part.text))
                elif isinstance(part, FilePart):
                    if isinstance(part.file, FileWithBytes):
                        # Handle file with bytes
                        parts.append(
                            types.Part.from_bytes(
                                part.file.contents, mime_type=part.file.mime_type
                            )
                        )
                    elif isinstance(part.file, FileWithUri):
                        # Handle file with URI
                        parts.append(
                            types.Part.from_uri(
                                part.file.uri, mime_type=part.file.mime_type
                            )
                        )
                    else:
                        logger.warning(f"Unsupported file type: {type(part.file)}")
                else:
                    logger.warning(f"Unsupported part type: {type(part)}")

            new_message = types.Content(parts=parts)
            await self._process_request(
                new_message, request_context.task.session_id, task_updater
            )

        except Exception as e:
            logger.error(f"Error executing supplier orchestrator agent request: {e}")
            await task_updater.update_task(
                state=TaskState.FAILED,
                result=f"Failed to execute request: {str(e)}",
            )

    def get_card(self) -> AgentCard:
        """Return the agent card for the supplier orchestrator agent."""
        return self._card

    async def check_files_access(self, file_uris: list[str]) -> dict[str, bool]:
        """Check if the agent can access the given files."""
        # For now, assume all files are accessible
        return {uri: True for uri in file_uris}

    async def cancel_request(self, session_id: str, task_id: str) -> None:
        """Cancel a request for the supplier orchestrator agent."""
        logger.info(f"Cancelling request for session {session_id}, task {task_id}")
        # Implementation for cancelling requests
        pass

    async def execute(self, request_context: RequestContext, task_updater: TaskUpdater) -> None:
        """Implements the abstract execute method."""
        await self.execute_request(request_context, task_updater)

    async def cancel(self, session_id: str, task_id: str) -> None:
        """Implements the abstract cancel method."""
        await self.cancel_request(session_id, task_id)
