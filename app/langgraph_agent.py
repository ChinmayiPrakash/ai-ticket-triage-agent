
from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from anthropic import Anthropic
from dotenv import load_dotenv

from app.tools import check_application_status


# ============================================================
# 1. SETUP
# ============================================================

load_dotenv()

client = Anthropic()


# ============================================================
# 2. TOOL SCHEMA
# ============================================================

"""
Tool schema     → tells Claude what tools exist
Python function → actually performs the work

Claude knows that check_application_status exists because
we provide this schema.

However, Claude does NOT execute the Python function itself.
"""

tools = [
    {
        "name": "check_application_status",
        "description": "Check whether an enterprise application is currently UP, DOWN, or UNKNOWN.",
        "input_schema": {
            "type": "object",
            "properties": {
                "application": {
                    "type": "string",
                    "description": "Name of the enterprise application to check"
                }
            },
            "required": ["application"]
        }
    }
]


# ============================================================
# 3. AGENT STATE
# ============================================================

class AgentState(TypedDict):

    # messages is a list.
    #
    # When a node returns updates for this field,
    # add_messages tells LangGraph to combine the new messages
    # with the existing messages instead of replacing them.

    messages: Annotated[list, add_messages]

    # These fields store information when Claude requests a tool.
    #
    # Example:
    #
    # {
    #     "tool_name": "check_application_status",
    #     "tool_input": {
    #         "application": "SAP"
    #     }
    # }

    tool_name: str | None
    tool_input: dict | None


# ============================================================
# 4. AGENT NODE
# ============================================================

def agent_node(state: AgentState):

    # Build the conversation history that will be sent to Claude.
    anthropic_messages = []

    for message in state["messages"]:

        # LangGraph represents user messages as HumanMessage.
        if message.type == "human":
            role = "user"

        # LangGraph represents assistant messages as AIMessage.
        elif message.type == "ai":
            role = "assistant"

        else:
            continue

        # Convert the LangGraph message into the format
        # expected by the Anthropic API.
        anthropic_messages.append(
            {
                "role": role,
                "content": message.content
            }
        )

    # Send the conversation history and available tools to Claude.
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        tools=tools,
        messages=anthropic_messages
    )

    """
    Previously we could simply do:

        claude_text = response.content[0].text

    But that is no longer enough because Claude can now return:

        1. A normal text response
        OR
        2. A tool_use request

    Therefore, we first check whether Claude requested a tool.
    """

    for block in response.content:

        if block.type == "tool_use":

            # Store the requested tool and its input in AgentState.
            return {
                "tool_name": block.name,
                "tool_input": block.input
            }

    # If Claude did NOT request a tool,
    # retrieve Claude's normal text response.
    claude_text = response.content[0].text

    return {
        "messages": [
            {
                "role": "assistant",
                "content": claude_text
            }
        ],

        # No tool is currently waiting to be executed.
        "tool_name": None,
        "tool_input": None
    }


# ============================================================
# 5. ROUTING FUNCTION
# ============================================================

def route_agent(state: AgentState):

    """
    This function does NOT execute the tool.

    Its only responsibility is to tell LangGraph
    where execution should go next.

    If Claude requested a tool:
        Agent → Tool

    Otherwise:
        Agent → END
    """

    if state.get("tool_name"):
        return "tool"

    return "end"


# ============================================================
# 6. TOOL NODE
# ============================================================

def tool_node(state: AgentState):

    """
    For now, this node only proves that LangGraph
    successfully routed execution to the tool node.

    In the next step, we will actually execute
    check_application_status().
    """

    print("\nTool node reached!")

     # Get the tool information from AgentState
    tool_name = state["tool_name"]
    tool_input = state["tool_input"]

    print("Tool:", tool_name)
    print("Input:", tool_input)

    if tool_name == "check_application_status":

        result = check_application_status(
            tool_input["application"]
        )

        print("Tool result:", result)

        return {
            "messages": [
                {
                    "role": "user",
                    "content": f"Tool result: {result}"
                }
            ],
            "tool_name": None,
            "tool_input": None
        }

    return {
        "tool_name": None,
        "tool_input": None
    }


# ============================================================
# 7. BUILD THE GRAPH
# ============================================================

# StateGraph defines the workflow.
# AgentState defines the information that travels through it.
builder = StateGraph(AgentState)


# Add nodes to the graph.
#
# "agent" is the node's name inside the graph.
# agent_node is the actual Python function LangGraph executes.
builder.add_node("agent", agent_node)

# "tool" is the graph node name.
# tool_node is the Python function that will run.
builder.add_node("tool", tool_node)


# ============================================================
# 8. ADD EDGES
# ============================================================

# An edge tells LangGraph where execution should go next.

# Start the workflow by going to the agent.
builder.add_edge(START, "agent")


# After agent_node finishes, call route_agent().
#
# route_agent returns:
#
# "tool" → go to the tool node
# "end"  → finish execution
builder.add_conditional_edges(
    "agent",
    route_agent,
    {
        "tool": "tool",
        "end": END
    }
)


# TEMPORARY:
#
# After reaching the tool node, stop the graph.
#
# Later this will change because we want:
#
# Agent → Tool → Agent
#
# instead of:
#
# Agent → Tool → END
#builder.add_edge("tool", END)
builder.add_edge("tool", "agent")

# ============================================================
# 9. COMPILE THE GRAPH
# ============================================================

# builder is the definition / blueprint of the workflow.
#
# compile() turns that blueprint into an executable graph.
graph = builder.compile()


# ============================================================
# 10. TEST THE GRAPH
# ============================================================

if __name__ == "__main__":

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "SAP is not responding."
                }
            ],
            "tool_name": None,
            "tool_input": None
        }
    )

    print("\nFinal messages:")

    for message in result["messages"]:
        print(message)
