"""
Buyer Orchestrator Agent

This agent orchestrates and coordinates the workflow between the three buyer agents using the ADK agent pattern.

Capabilities:
- Orchestrate the buyer workflow: inventory analysis → purchase validation → purchase order generation
- Manage communication between inventory management, purchase validation, and purchase order agents via A2A client
- Ensure proper data flow and context sharing between agents
- Monitor the overall buyer process and handle coordination issues
- Provide comprehensive reports on buyer workflow execution
- Make decisions on workflow routing based on agent responses

Tools:
- send_message: Send tasks to individual buyer agents
- execute_buyer_workflow: Execute the complete sequential buyer workflow

Workflow:
1. Inventory Management Agent: Analyzes current stock levels and demand patterns
2. Purchase Validation Agent: Validates purchase requirements based on inventory analysis
3. Purchase Order Agent: Processes and generates purchase orders if validation passes

Communication:
This agent uses A2AClient to communicate with the three buyer agents via HTTP:
- Inventory Management Agent (port 8001)
- Purchase Validation Agent (port 8002) 
- Purchase Order Agent (port 8003)

Environment Variables:
- INVENTORY_AGENT_URL: URL for inventory management agent (default: http://localhost:8001)
- PURCHASE_VALIDATION_AGENT_URL: URL for purchase validation agent (default: http://localhost:8002)
- PURCHASE_ORDER_AGENT_URL: URL for purchase order agent (default: http://localhost:8003)

Usage:
The agent will automatically detect and connect to available buyer agents on startup.
Use the tools to either send individual tasks or execute the complete workflow.
"""
