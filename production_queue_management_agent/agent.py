import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a Production Queue Management Agent specialized in managing production schedules and order processing. "
    "Your primary responsibilities include: "
    "1. Recording and organizing incoming purchase orders in the production system "
    "2. Managing production schedules and priorities based on order requirements "
    "3. Generating confirmation emails for accepted orders "
    "4. Coordinating with suppliers and customers regarding order status "
    "5. Optimizing production workflow and resource allocation "
    "Use the available tools to record orders and generate email responses. "
    "Focus on efficient production planning and maintaining clear communication with all stakeholders."
)


def create_agent() -> LlmAgent:
    """Constructs the ADK production queue management agent."""
    logger.info("--- 🔧 Loading MCP tools from MCP Server... ---")
    logger.info("--- 🤖 Creating ADK Production Queue Management Agent... ---")
    return LlmAgent(
        model="gemini-2.5-flash",
        name="production_queue_management_agent",
        description="An agent that manages production schedules and order processing workflows",
        instruction=SYSTEM_INSTRUCTION,
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=os.getenv("MCP_SERVER_URL", "http://localhost:8080")
                ),
                tool_filter=["manage_po_records","send_response_email"]
            )
        ],
    )


root_agent = create_agent()
