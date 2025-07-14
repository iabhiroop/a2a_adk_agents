import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are an Order Intelligence Agent specialized in processing incoming orders and extracting critical information. "
    "Your primary responsibilities include: "
    "1. Monitoring incoming emails for new purchase orders "
    "2. Parsing and extracting order details from various document formats "
    "3. Validating order information for completeness and accuracy "
    "4. Categorizing orders by priority, product type, and delivery requirements "
    "5. Preparing structured order data for production planning "
    "Use the available tools to monitor emails and parse documents. "
    "Focus on accurate data extraction and ensuring all order details are properly captured."
)


def create_agent() -> LlmAgent:
    """Constructs the ADK order intelligence agent."""
    logger.info("--- 🔧 Loading MCP tools from MCP Server... ---")
    logger.info("--- 🤖 Creating ADK Order Intelligence Agent... ---")
    return LlmAgent(
        model="gemini-2.5-flash",
        name="order_intelligence_agent",
        description="An agent that processes incoming orders and extracts critical information",
        instruction=SYSTEM_INSTRUCTION,
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=os.getenv("MCP_SERVER_URL", "http://localhost:8080")
                ),
                tool_filter=["fetch_emails","parse_document"]
            )
        ],
    )


root_agent = create_agent()
