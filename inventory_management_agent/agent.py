import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are an Inventory Management Agent specialized in monitoring stock levels and demand forecasting. "
    "Your primary responsibilities include: "
    "1. Monitoring inventory levels across all products "
    "2. Analyzing demand patterns and trends "
    "3. Identifying items that need restocking "
    "4. Generating inventory reports and analytics "
    "5. Recommending optimal stock levels based on historical data "
    "Use the available tools to restock inventory and generate comprehensive reports. "
    "Focus on maintaining optimal inventory levels to prevent stockouts while minimizing carrying costs."
    "Final response should have the expected report."
)


def create_agent() -> LlmAgent:
    """Constructs the ADK inventory management agent."""
    logger.info("--- 🔧 Loading MCP tools from MCP Server... ---")
    logger.info("--- 🤖 Creating ADK Inventory Management Agent... ---")
    return LlmAgent(
        model="gemini-2.5-flash",
        name="inventory_management_agent",
        description="An agent that monitors stock levels and handles demand forecasting for inventory management",
        instruction=SYSTEM_INSTRUCTION,
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=os.getenv("MCP_SERVER_URL", "http://localhost:8080")
                ),
                tool_filter=["analyze_inventory","save_report"]
            )
        ],
    )


root_agent = create_agent()
