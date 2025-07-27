# Purchase Order Agent A2A ADK Framework

An Agent-to-Agent (A2A) ADK (Agent Development Kit) based automation system for supply chain ordering and documentation processes using a custom MCP (Model Context Protocol) server. This implementation transforms traditionally manual supply chain processes through intelligent multi-agent coordination.

## 🚀 Overview

This repository demonstrates how A2A ADK agents can revolutionize supply chain automation by replacing manual inventory analysis, purchase validation, and order documentation with intelligent agent coordination through MCP tools.

**Current Implementation**: 7 specialized ADK agents working through Agent-to-Agent communication patterns:

- **Buyer Agent Cluster** (3 agents + 1 orchestrator):  
  Automates purchasing workflows through coordinated agent interactions, eliminating manual spreadsheet analysis and streamlining purchase order generation via MCP tool integration.

- **Supplier Agent Cluster** (2 agents + 1 orchestrator):  
  Processes incoming orders and manages production through intelligent agent coordination, leveraging MCP tools for email monitoring and document processing.

**A2A Architecture Benefits**: 
- Direct agent-to-agent communication reduces coordination overhead
- MCP server provides standardized tool access across all agents
- Modular ADK design enables seamless scaling and agent specialization
- Event-driven workflows through HTTP-based agent communication

## 📹 Video Demonstration

Watch the complete buyer workflow automation in action:


https://github.com/user-attachments/assets/0d190085-7a68-407b-aab4-1c82e7ff9870



## 🏗️ A2A ADK Architecture

### ADK Agent Structure
Each agent follows the ADK pattern:
- **agent.py**: Agent configuration and system instructions
- **agent_executor.py**: Request processing and MCP tool integration
- **__main__.py**: HTTP server for A2A communication
- **__init__.py**: Agent metadata and documentation

### Agent Communication Flow
```
Buyer Orchestrator
    ↓ HTTP Requests
├── Inventory Agent ←→ MCP Tools
├── Validation Agent ←→ MCP Tools  
└── Purchase Order Agent ←→ MCP Tools

Supplier Orchestrator
    ↓ HTTP Requests
├── Order Intelligence Agent ←→ MCP Tools
└── Production Queue Agent ←→ MCP Tools
```

### MCP Tool Integration
All agents access specialized tools through the MCP server:
- **RestockInventoryTool**: Inventory monitoring and analysis
- **FinancialDataTool**: Budget validation and cost analysis
- **DocumentGeneratorTool**: Purchase order and report generation
- **EmailMonitoringTool**: Automated email processing
- **PORecordTool**: Order tracking and production management

## 🎯 ADK Agents Overview

### Orchestrator Agents

#### 0. Buyer Orchestrator Agent 🎯
- **Purpose**: Coordinates workflow between buyer agents via A2A communication
- **Tools**: MCP tools + Direct HTTP communication with buyer agents
- **A2A Pattern**: Sequential orchestration (Inventory → Validation → Purchase Orders)
- **MCP Integration**: Workflow coordination through standardized tool access

#### 6. Supplier Orchestrator Agent 🏭
- **Purpose**: Manages supplier agent workflows through A2A coordination
- **Tools**: MCP tools + Direct HTTP communication with supplier agents
- **A2A Pattern**: Parallel processing with order monitoring workflows
- **MCP Integration**: Production coordination and email monitoring

### Specialized Worker Agents

#### 1. Inventory Management Agent 📦
- **ADK Role**: Inventory analysis and demand forecasting
- **MCP Tools**: RestockInventoryTool, ReportFileTool
- **A2A Interface**: Responds to orchestrator requests with inventory insights

#### 2. Purchase Validation Agent ✅
- **ADK Role**: Budget validation and compliance checking
- **MCP Tools**: FinancialDataTool, PurchaseQueueTool
- **A2A Interface**: Validates purchase requests from orchestrator

#### 3. Purchase Order Agent 📄
- **ADK Role**: Document generation and supplier communication
- **MCP Tools**: PurchaseQueueTool, DocumentGeneratorTool, PoEmailGeneratorTool
- **A2A Interface**: Creates and distributes purchase orders

#### 4. Order Intelligence Agent 🧠
- **ADK Role**: Email processing and order extraction
- **MCP Tools**: EmailMonitoringTool, DocumentParserTool
- **A2A Interface**: Processes incoming orders for production queue

#### 5. Production Queue Management Agent 🏭
- **ADK Role**: Production scheduling and order tracking
- **MCP Tools**: PORecordTool, EmailResponseGeneratorTool
- **A2A Interface**: Manages production workflows and notifications

## 🛠️ Technology Stack

### A2A ADK Framework
- **ADK Pattern**: Agent Development Kit with standardized structure
- **MCP Protocol**: Model Context Protocol for tool standardization
- **HTTP Communication**: RESTful A2A agent communication
- **JSON Messaging**: Standardized agent-to-agent message format

### AI & Integration
- **Gemini 2.5 Flash**: LLM for agent intelligence
- **Custom MCP Server**: Centralized tool access and coordination
- **Email Integration**: IMAP/SMTP through MCP tools
- **Document Processing**: OCR and parsing via MCP tools

### Infrastructure
- **Python 3.8+**: Agent runtime environment
- **HTTP Servers**: Individual agent endpoints
- **MCP Server**: Tool coordination hub
- **Environment Configuration**: Shared .env for all agents

## 🚀 Quick Start - A2A Deployment

### Prerequisites
- Python 3.8 or higher
- Custom MCP Server running on port 8099
- Gmail accounts for email integration
- Google API key for Gemini integration

### MCP Server Setup
1. **Start the MCP Server:**
   ```bash
   # Ensure your custom MCP server is running
   # Default: http://localhost:8099/mcp
   ```

2. **Environment Configuration:**
   Create `.env` file in the root directory:
   ```env
   # MCP Server Configuration
   MCP_SERVER_URL=http://localhost:8099/mcp

   # Model Configuration  
   MODEL=gemini-2.5-flash
   GEMINI_API_KEY=your_api_key_here

   # Email Configuration
   EMAIL=buyer_email
   PASSWORD=your_app_password
   SUPEMAIL=supplier_email
   SUPPASSWORD=your_supplier_app_password
   ```

### A2A Agent Deployment

#### Buyer Workflow Only
```bash
# Start buyer agents + orchestrator
start_buyer_workflow.bat      # Windows
start_buyer_workflow.ps1      # PowerShell
```

#### Individual Agent Deployment
```bash
# Buyer Orchestrator
cd buyer_orchestrator_agent
python -m __main__ --host localhost --port 8000

# Individual agents (ports 8001-8005)
cd inventory_management_agent
python -m __main__ --host localhost --port 8001
# ... repeat for other agents
```

### Testing A2A Communication

#### Orchestrator Usage Examples
```bash
# Buyer workflow coordination
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "Execute complete buyer workflow for office supplies"}'

# Supplier workflow coordination  
curl -X POST http://localhost:8006/execute \
  -H "Content-Type: application/json" \
  -d '{"message": "Process incoming purchase orders"}'
```

## 📁 ADK Project Structure

```
a2a_adk_agents/
├── .env                        # Shared environment configuration
├── README.md                   # This file
├── start_*.bat/ps1            # Automated startup scripts
├── buyer_orchestrator_agent/   # Buyer workflow coordinator
│   ├── agent.py               # ADK agent configuration
│   ├── agent_executor.py      # MCP tool integration
│   ├── __main__.py            # HTTP server for A2A
│   └── __init__.py            # Agent metadata
├── inventory_management_agent/ # Stock monitoring ADK agent
├── purchase_validation_agent/  # Budget validation ADK agent
├── purchase_order_agent/      # Document generation ADK agent
├── order_intelligence_agent/  # Email processing ADK agent
├── production_queue_management_agent/ # Production ADK agent
└── supplier_orchestrator_agent/ # Supplier workflow coordinator
```

## 🔧 A2A Configuration

### Agent Communication Patterns
- **Sequential Flow**: Orchestrator → Agent1 → Agent2 → Agent3
- **Parallel Processing**: Multiple agents handling concurrent requests
- **Event-Driven**: Agents responding to HTTP triggers from orchestrators

### MCP Tool Configuration
All tools are accessed through the centralized MCP server, ensuring:
- **Consistent Tool Access**: Standardized interfaces across agents
- **Resource Management**: Centralized tool lifecycle management
- **Cross-Agent Coordination**: Shared tool state and coordination

## 📊 A2A Workflow Examples

### Buyer Workflow
1. **Orchestrator Request**: "Execute buyer workflow"
2. **A2A Coordination**: Orchestrator → Inventory Agent (analysis)
3. **Sequential Processing**: Results → Validation Agent (approval)
4. **Final Step**: Approved requests → Purchase Order Agent (generation)

### Supplier Workflow  
1. **Orchestrator Request**: "Process incoming orders"
2. **A2A Coordination**: Orchestrator → Order Intelligence (email parsing)
3. **Production Flow**: Parsed orders → Production Queue Agent (scheduling)
4. **Notification**: Status updates via email automation

## ⚠️ A2A Considerations

### Agent Communication
- **Network Latency**: HTTP-based A2A communication introduces network overhead
- **Error Handling**: Robust retry mechanisms for failed agent communications
- **Load Balancing**: Consider agent scaling for high-throughput scenarios

### MCP Server Dependency
- **Single Point of Failure**: MCP server availability affects all agents
- **Tool Versioning**: Ensure MCP tool compatibility across agent updates
- **Performance**: MCP server performance impacts overall system responsiveness

## 🤝 Contributing

1. Fork the repository
2. Follow ADK patterns for new agents
3. Ensure MCP tool integration compliance
4. Test A2A communication workflows
5. Submit pull request with agent documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*This A2A ADK implementation demonstrates the power of agent coordination through standardized MCP tools and HTTP-based communication patterns.*
