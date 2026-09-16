import os # Reads environment variables
from dotenv import load_dotenv # Loads values from the .env file
from anthropic import Anthropic # Claude API client
from app.models import TicketClassification  # Imports the Pydantic model from the app package


load_dotenv() # Loads ANTHROPIC_API_KEY from.env

client = Anthropic() # Creates the Claude client using the API key

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


#ticket = classify_ticket(
 #   "SAP application is unavailable. Bot failed 3 times with HTTP 503."
#)

#print(ticket)
#print(ticket.model_dump_json(indent=2))