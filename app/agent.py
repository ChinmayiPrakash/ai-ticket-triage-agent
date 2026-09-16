from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()
# this is only a description of the tool for claude.
tools = [
    {
        "name": "check_application_status",
        "description": "Check whether an enterprise application is currently UP, DOWN, or UNKNOWN.",
        "input_schema": {
            "type": "object",
            "properties": {
                "application": {
                    "type": "string",
                    "description": "Name of the application to check"
                }
            },
            "required": ["application"]
        }
    }
]

def investigate_ticket(ticket_text: str):

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        tools=tools,
        messages=[
            {
                "role": "user",
                "content": f"""
Investigate this automation incident.

Ticket:
{ticket_text}

Use available tools when they would help diagnose the incident.
"""
            }
        ]
    )

    return response