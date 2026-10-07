# AI Triage Agent

An AI-powered enterprise support ticket triage and incident investigation system built with **Python, FastAPI, Claude, and LangGraph**.

The application analyzes automation support tickets, classifies incidents, and uses an agentic workflow to gather additional evidence through tools before producing a response.

## Project Overview

Traditional ticket classification systems make decisions using only the information provided in the ticket.

This project extends ticket classification into an **agentic incident investigation workflow**.

Instead of immediately generating a response, the AI agent can:

- Analyze an incoming support ticket
- Decide whether additional information is required
- Select an appropriate tool
- Generate tool arguments
- Execute the tool through the application
- Observe the tool result
- Continue reasoning using the new evidence
- Produce an evidence-based response

## Current Architecture

```text
Incoming Support Ticket
        |
        v
      FastAPI
        |
        v
   LangGraph Agent
        |
        v
     Claude LLM
        |
        v
  Need more evidence?
      /       \
    Yes        No
     |          |
     v          v
  Tool Node    END
     |
     v
Application Status Tool
     |
     v
 Tool Result
     |
     +--------> Agent
```

The graph allows the agent to follow a:

**Reason → Act → Observe → Reason**

execution cycle.

## Current Features

- FastAPI REST API
- Pydantic data validation
- Claude LLM integration
- Structured ticket classification
- Severity classification
- LangGraph state management
- Conditional graph routing
- LLM tool selection
- Dynamic tool argument generation
- Application-status investigation tool
- Agent → Tool → Agent execution loop
- Evidence-based incident investigation
- Environment-variable based API key management

## Severity Levels

The ticket classifier uses four severity levels:

**LOW**  
Enhancements, informational requests, future risks, or issues that automatically recovered.

**MEDIUM**  
Production issues requiring investigation or manual intervention but without urgent business impact.

**HIGH**  
Issues currently blocking an automation or business process and requiring intervention.

**CRITICAL**  
Time-sensitive or business-critical incidents where delay may cause immediate serious operational, financial, compliance, or customer impact.

The agent is instructed not to assume deadlines, financial impact, affected users, or transaction volumes without supporting evidence.

## Agent Tools

### Application Status Tool

The current agent can call:

```text
check_application_status(application)
```

The tool returns the availability of supported enterprise applications.

Example:

```text
Ticket:
SAP is not responding.

Agent decision:
Check SAP application status.

Tool:
check_application_status("SAP")

Tool result:
{
    "application": "SAP",
    "status": "DOWN"
}

Agent:
SAP is confirmed to be unavailable and recommends appropriate incident-response actions.
```

The current application-status implementation is a mock service used to demonstrate agent tool calling. It can later be replaced with integrations such as monitoring platforms, enterprise APIs, UiPath Orchestrator, or ServiceNow.

## Project Structure

```text
app/
├── main.py
├── models.py
├── classifier.py
├── agent.py
├── langgraph_agent.py
└── tools.py

tests/
├── test_classifier.py
└── evaluate_classifier.py
```

### Main Components

`main.py`  
FastAPI application and API endpoints.

`models.py`  
Pydantic models and severity definitions.

`classifier.py`  
Claude-based ticket classification logic.

`agent.py`  
Initial/manual tool-calling agent implementation.

`langgraph_agent.py`  
LangGraph-based agent orchestration, state, nodes, routing, and tool execution.

`tools.py`  
Python tools available to the agent.

## Running the Project

Create and activate a Python virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file and configure the required API key:

```text
ANTHROPIC_API_KEY=your_api_key
```

Do not commit `.env` to source control.

Run the FastAPI application:

```powershell
python -m uvicorn app.main:app --reload
```

Run the LangGraph agent:

```powershell
python -m app.langgraph_agent
```

## Current Development Status

The current version supports:

```text
Ticket
  ↓
Claude
  ↓
Tool Decision
  ↓
Conditional Routing
  ↓
Tool Execution
  ↓
Observation
  ↓
Claude
  ↓
Final Response
```

The LangGraph tool loop is functional.

## Planned Improvements

The next iterations will include:

- Native Anthropic `tool_use` / `tool_result` handling
- Integration of structured classification into the LangGraph workflow
- Knowledge retrieval / RAG
- Human-in-the-loop approval
- Improved exception handling and retries
- Agent evaluation
- Automated tests
- Logging and observability
- Docker containerization
- Production API integration

Future versions may replace mock tools with real enterprise integrations.

## Technology Stack

- Python
- FastAPI
- Pydantic
- Anthropic Claude
- LangGraph
- REST APIs
- Pytest
- Git/GitHub

Planned:

- Vector database / RAG
- Docker
- Agent observability and evaluation
- Cloud deployment

## Project Goal

The goal of this project is to demonstrate how traditional enterprise automation can be extended with agentic AI.

Instead of relying only on static ticket classification, the system can gather evidence from enterprise systems, reason over the evidence, and determine an appropriate response while maintaining controlled tool execution.