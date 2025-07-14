"""
Supplier Orchestrator Agent

This agent orchestrates and coordinates the workflow between the two supplier agents using
the ADK (Agent Development Kit) framework with A2A (Agent-to-Agent) communication protocol.

Architecture:
- Built on google.adk.Agent with LLM capabilities
- Uses A2AClient and A2ACardResolver for agent discovery and communication
- Implements RemoteAgentConnections for managing supplier agent connections
- Integrates with MCP (Model Context Protocol) server for specialized tools

Capabilities:
- Orchestrate the supplier workflow: order intelligence → production queue management
- Manage A2A communication between order intelligence and production queue management agents
- Ensure proper data flow and context sharing between supplier agents using structured messaging
- Monitor the overall supplier process and handle coordination issues
- Provide comprehensive reports on supplier workflow execution
- Manage both order processing workflows and continuous order monitoring
- Coordinate production schedules and order confirmations

A2A Agent Connections:
- Order Intelligence Agent (localhost:8091): Processes incoming orders and extracts details
- Production Queue Management Agent (localhost:8092): Records orders and manages production queue

Workflows:
1. Standard Supplier Workflow:
   - Order Intelligence Agent: Processes incoming orders and extracts details
   - Production Queue Management Agent: Records orders and manages production queue

2. Order Monitoring Workflow:
   - Continuous monitoring of incoming orders
   - Real-time processing and production queue updates

Tools Available:
- send_message: Send structured messages to other agents
- execute_supplier_workflow: Orchestrate the complete supplier process
- execute_order_monitoring_workflow: Execute continuous order monitoring

Environment Variables:
- ORDER_INTELLIGENCE_AGENT_URL: URL for Order Intelligence Agent (default: http://localhost:8091)
- PRODUCTION_QUEUE_AGENT_URL: URL for Production Queue Agent (default: http://localhost:8092)
- MCP_SERVER_URL: MCP server endpoint (default: http://localhost:8080/mcp)
- GOOGLE_API_KEY: API key for Google Gemini model
- MODEL_NAME: Model name (default: gemini-2.0-flash-exp)

Usage:
Run this agent on port 8094 to coordinate supplier operations through A2A protocol.
"""
