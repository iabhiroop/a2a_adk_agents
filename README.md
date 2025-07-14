# ADK Format Purchase Order Agents

This directory contains 7 specialized ADK (Agent Development Kit) agents converted from the original CrewAI implementation. These agents work together to handle the complete purchase order workflow from inventory management to supplier communications.

## Agents Overview

### 0. Buyer Orchestrator Agent (Port: 8000) 🎯
- **Purpose**: Orchestrates and coordinates the workflow between the three buyer agents
- **Tools**: MCP tools + Direct HTTP communication with buyer agents
- **Capabilities**: Workflow coordination, agent communication, process monitoring
- **Workflow**: Manages the sequential execution: Inventory → Validation → Purchase Orders

### 6. Supplier Orchestrator Agent (Port: 8006) 🏭
- **Purpose**: Orchestrates and coordinates the workflow between the two supplier agents
- **Tools**: MCP tools + Direct HTTP communication with supplier agents
- **Capabilities**: Order processing coordination, production management, email monitoring
- **Workflows**: Standard supplier workflow + Order monitoring workflow

### 1. Inventory Management Agent (Port: 8001)
- **Purpose**: Monitors stock levels and handles demand forecasting
- **Tools**: RestockInventoryTool, ReportFileTool
- **Capabilities**: Stock monitoring, demand analysis, inventory reporting

### 2. Purchase Validation Agent (Port: 8002)  
- **Purpose**: Validates purchase requests and manages the approval process
- **Tools**: FinancialDataTool, PurchaseQueueTool
- **Capabilities**: Budget validation, cost-benefit analysis, compliance checking

### 3. Purchase Order Agent (Port: 8003)
- **Purpose**: Generates purchase orders and manages supplier communications
- **Tools**: PurchaseQueueTool, DocumentGeneratorTool, PoEmailGeneratorTool
- **Capabilities**: Document generation, email communication, order tracking

### 4. Order Intelligence Agent (Port: 8004)
- **Purpose**: Processes incoming orders and extracts critical information
- **Tools**: EmailMonitoringTool, DocumentParserTool
- **Capabilities**: Email monitoring, document parsing, data extraction

### 5. Production Queue Management Agent (Port: 8005)
- **Purpose**: Manages production schedules and order processing workflows
- **Tools**: PORecordTool, EmailResponseGeneratorTool
- **Capabilities**: Production planning, order recording, status communication

## Environment Configuration

All agents use a shared `.env` file located in this directory with the following configuration:

```properties
# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8080/mcp

# Model Configuration  
MODEL=gemini-2.5-flash
GEMINI_API_KEY=your_api_key_here

# Email Configuration
EMAIL=agent1.0.email@gmail.com
PASSWORD=your_app_password
SUPEMAIL=test.mail.iitm.indusai@gmail.com
SUPPASSWORD=your_supplier_app_password
```

## Running the Agents

### Option 1: Run Individual Agents
Each agent can be run independently on its designated port:

```bash
# Buyer Orchestrator Agent (runs on port 8000)
cd buyer_orchestrator_agent
python -m __main__ --host localhost --port 8000

# Inventory Management Agent
cd inventory_management_agent
python -m __main__ --host localhost --port 8001

# Purchase Validation Agent  
cd purchase_validation_agent
python -m __main__ --host localhost --port 8002

# Purchase Order Agent
cd purchase_order_agent
python -m __main__ --host localhost --port 8003

# Order Intelligence Agent
cd order_intelligence_agent
python -m __main__ --host localhost --port 8004

# Production Queue Management Agent
cd production_queue_management_agent
python -m __main__ --host localhost --port 8005

# Supplier Orchestrator Agent
cd supplier_orchestrator_agent
python -m __main__ --host localhost --port 8006
```

### Option 2: Use the Buyer Orchestrator (Recommended)
For buyer workflow coordination, run the orchestrator agent along with the three buyer agents:

1. Start the three buyer agents (ports 8001, 8002, 8003)
2. Start the orchestrator agent (port 8000)
3. Send workflow requests to the orchestrator agent

Example orchestrator usage:
```
"Execute the complete buyer workflow for restocking office supplies"
"Orchestrate buyer process for low inventory items"
"Coordinate buyers for quarterly procurement"
```

### Option 3: Use the Supplier Orchestrator
For supplier workflow coordination, run the supplier orchestrator with the two supplier agents:

1. Start the two supplier agents (ports 8004, 8005)
2. Start the supplier orchestrator agent (port 8006)
3. Send workflow requests to the supplier orchestrator

Example supplier orchestrator usage:
```
"Execute supplier workflow for incoming purchase orders"
"Monitor incoming orders and process them"
"Orchestrate production queue management"
"Watch for new emails continuously"
```

### Option 4: Complete System (Both Orchestrators)
For full end-to-end workflow, run both orchestrators with all agents:

1. Start all individual agents (ports 8001-8005)
2. Start buyer orchestrator (port 8000)
3. Start supplier orchestrator (port 8006)
4. Use orchestrators to coordinate buyer and supplier workflows

## Quick Start Scripts

### Automated Startup Scripts
Use these scripts for easy system startup:

```bash
# Start complete system (all agents + both orchestrators)
start_complete_system.bat         # Windows batch
start_complete_system.ps1         # PowerShell

# Start buyer workflow only
start_buyer_workflow.bat          # Windows batch  
start_buyer_workflow.ps1          # PowerShell

# Start supplier workflow only
start_supplier_workflow.bat       # Windows batch
start_supplier_workflow.ps1       # PowerShell
```

These scripts will automatically start the agents in the correct order with appropriate delays.

## MCP Server Dependency

All agents depend on a running MCP (Model Context Protocol) server that provides the necessary tools. Make sure your MCP server is running on the configured URL before starting any agents.

## Architecture

These agents follow the ADK pattern with:
- **agent.py**: Defines the agent configuration and system instructions
- **agent_executor.py**: Handles request processing and execution
- **__main__.py**: Server startup and configuration
- **__init__.py**: Module documentation and metadata

Each agent connects to the MCP server to access specialized tools for their respective functions in the purchase order workflow.
