import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a Purchase Order Agent specialized in generating purchase orders and managing supplier communications. "
    "Your primary responsibilities include: "
    "1. Processing purchase requests from the purchase queue "
    "2. Generating formal purchase order documents "
    "3. Creating and sending purchase order emails to suppliers "
    "4. Managing supplier communication workflows "
    "5. Tracking purchase order status and delivery schedules "
    "Use the available tools to access the purchase queue, generate documents, and send emails. "
    "Focus on maintaining clear communication with suppliers and ensuring timely order processing."
    "List of suppliers with email addresses:"
    "\n1. Supplier Tech Hardware - agent1.0.email@gmail.com"
    "etc. Take the email address from the purchase request and use it to send the email."
)


def create_agent() -> LlmAgent:
    """Constructs the ADK purchase order agent."""
    logger.info("--- 🔧 Loading MCP tools from MCP Server... ---")
    logger.info("--- 🤖 Creating ADK Purchase Order Agent... ---")
    return LlmAgent(
        model="gemini-2.5-flash",
        name="purchase_order_agent",
        description="An agent that generates purchase orders and manages supplier communications",
        instruction=SYSTEM_INSTRUCTION,
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=os.getenv("MCP_SERVER_URL", "http://localhost:8080")
                ),
                tool_filter=["manage_approval_process","generate_purchase_order","generate_po_email"]
            )
        ],
    )


root_agent = create_agent()
