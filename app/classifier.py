import os # Reads environment variables
from dotenv import load_dotenv # Loads values from the .env file
from anthropic import Anthropic # Claude API client
from app.models import TicketClassification  # Imports the Pydantic model from the app package
from app.tools import check_application_status
import json

load_dotenv() # Loads ANTHROPIC_API_KEY from.env

client = Anthropic() # Creates the Claude client using the API key

# This is called tool schema acts as a description of tools for claude.
# Tool schema: describes the available tool and its expected input to Claude.
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
# This acts like a dispatcher between claude's requested tool name and your actual python implementations
def execute_tool(tool_name: str, tool_input: dict):
    if tool_name == "check_application_status":
        return check_application_status(
            tool_input["application"]
        )
    return {
        "error": f"Unknown tool: {tool_name}"
    }


SYSTEM_PROMPT = """
You are an AI assistant responsible for classifying enterprise automation support tickets.

Classify severity using these business rules:

LOW:
No active production incident remains.

Use LOW for enhancements, warnings, future risks, informational issues, or incidents that automatically recovered completely and require no operational intervention.

MEDIUM:
A real production issue occurred and requires follow-up, investigation, correction, or manual action, but the business process is not currently urgent or severely blocked.

If a production automation failed and someone must still investigate or correct the issue, do not classify it as LOW merely because the business impact is small.

HIGH:
The issue currently blocks an automation or part of a business process and requires intervention, but there is no immediate deadline or major enterprise-wide impact.

CRITICAL:
A time-sensitive or business-critical process is currently blocked, multiple automations or users are significantly affected, or delay could cause immediate serious financial, compliance, customer, or operational impact.

Additional rules:

- Base severity primarily on current business impact and urgency.
- Do not classify an issue as HIGH or CRITICAL only because an error occurred.
- A future risk with no current business impact should normally be LOW.
- An isolated production failure that requires investigation should normally be at least MEDIUM.
- The existence of an SLA does not automatically mean CRITICAL.
- CRITICAL requires immediate or near-term business impact.
- If an automation recovered successfully with no remaining impact, severity should normally be LOW.
- If manual intervention is required but there is no urgent deadline, consider MEDIUM or HIGH based on whether the business process is blocked.

Examples:

Ticket:
"The bot password expired. The process can be completed tomorrow."
Severity: MEDIUM

Ticket:
"The bot automatically recovered from a temporary network error and completed successfully."
Severity: LOW

Ticket:
"The claims API is unavailable. Claims are accumulating, but the SLA is tomorrow."
Severity: HIGH

Ticket:
"Payroll submission is blocked and must be completed within 20 minutes."
Severity: CRITICAL

Ticket:
"A credential will expire next week, but the automation is currently running normally."
Severity: LOW
"""

def classify_ticket(ticket_txt: str):
    response = client.messages.parse(
        model="claude-sonnet-4-6",
        #model="unknown model",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role":"user",
                "content": f"""
Classify the following automation support ticket.

Ticket: {ticket_txt}


"""
            }
        ],
        output_format = TicketClassification
    )

   # print(response.parsed_output)

    return response.parsed_output



def test_tool_calling(ticket_txt: str):
    response = client.messages.create(
        model = "claude-sonnet-4-5",
        max_tokens=5000,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=[
            {
                "role":"user",
                "content":  f"""
Investigate the following automation support ticket.

Use the available tools when additional information would help you understand the incident.

Ticket: {ticket_txt}
"""
            }
        ]
    )
    print(response)
# Now we get the tool name from claude's response and execute the tool
    for block in response.content:
        if block.type == "tool_use":
            print("Tool requested:", block.name)
            print("Tool input:", block.input)
            result = execute_tool(
                block.name,
                block.input
            )
            print("Tool result:",result)
            # Sending tool information back to claude
            second_response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=500,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=[
                    {
                        "role": "user",
                        "content": f"""
            Investigate the following automation support ticket.

            Use the available tools when additional information would help you understand the incident.

            Ticket: {ticket_txt}
            """
                },

                {
                    "role": "assistant",
                    "content": response.content
                },

                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id, # This is important because imagine claude
                            # requests for 3 tools, Claude needs to know which result belongs to which request.
                            "content": json.dumps(result) # This serializes python dictionary to JSON
                        }
                    ]
                }
            ]
        )

            print("Claude after tool result:")
            print(second_response)


test_tool_calling(
    "SAP is not responding and the invoice automation failed."
)

result = execute_tool("check_application_status",{"application":"SAP"})
print(result)

"""

Agent loop logic :
 while True:

    response = ask_claude()

    if response wants a tool:
        execute_tool()
        add_result_to_messages

    else:
        return response """

def run_agent(ticket_txt: str):

    messages = [
        {
            "role": "user",
            "content": f"""
Investigate the following automation support ticket.

Use the available tools when additional information would help you understand the incident.

Only classify an incident as CRITICAL when the available evidence shows immediate or near-term serious business impact.
Do not assume deadlines, financial impact, compliance impact, affected users, or affected transaction volumes unless they are provided by the ticket or tool results.

Ticket: {ticket_txt}
"""
        }
    ]

    while True:

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=700,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        print("\nClaude response:")
        print(response)

        # Save Claude's response in conversation history
        messages.append(
            {
                "role": "assistant",
                "content": response.content
            }
        )

        # If Claude is finished, return its answer
        if response.stop_reason != "tool_use":
            return response

        # Otherwise execute every tool Claude requested
        tool_results = []

        for block in response.content:

            if block.type == "tool_use":

                print("\nTool requested:", block.name)
                print("Tool input:", block.input)

                result = execute_tool(
                    block.name,
                    block.input
                )

                print("Tool result:", result)

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result)
                    }
                )

        # Give the tool results back to Claude
        messages.append(
            {
                "role": "user",
                "content": tool_results
            }
        )
final_response = run_agent(
        "SAP is not responding and the invoice automation failed."
    )

print("\nFINAL RESPONSE:")

for block in final_response.content:
    if block.type == "text":
        print(block.text)