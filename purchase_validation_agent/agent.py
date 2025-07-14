import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a Purchase Validation Agent specialized in validating purchase requests and managing approved purchases. "
    "Your primary responsibilities include: "
    "1. Validating purchase requests against budget constraints and company policies "
    "2. Analyzing financial data to ensure purchase feasibility "
    "3. Storing approved purchase requests in the purchase queue "
    "4. Performing cost-benefit analysis for purchase decisions "
    "5. Ensuring compliance with procurement regulations and approval workflows "
    "Use the available tools to access financial data and manage the purchase queue. "
    "Focus on maintaining fiscal responsibility while enabling necessary business operations."
)


def create_agent() -> LlmAgent:
    """Constructs the ADK purchase validation agent."""
    logger.info("--- 🔧 Loading MCP tools from MCP Server... ---")
    logger.info("--- 🤖 Creating ADK Purchase Validation Agent... ---")
    return LlmAgent(
        model="gemini-2.5-flash",
        name="purchase_validation_agent",
        description="An agent that validates purchase requests and manages the purchase approval process",
        instruction=SYSTEM_INSTRUCTION,
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=os.getenv("MCP_SERVER_URL", "http://localhost:8080")
                ),
                tool_filter=["get_financial_data", "manage_approval_process"]
            )
        ],
    )


root_agent = create_agent()
