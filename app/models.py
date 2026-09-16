from enum import Enum  # Used to define a fixed set of allowed severity values
from pydantic import BaseModel  # Used to validate the structure and data types


class Severity(Enum):  # Restricts severity to these four values
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TicketClassification(BaseModel):  # Defines and validates the AI classification output
    category: str  # Type of issue
    severity: Severity  # Severity level of the issue
    application: str  # Application affected
    retryable: bool  # Whether the issue can be retried
    recommended_action: str  # Suggested action to resolve the issue


class TicketRequest(BaseModel):
    ticket_text: str
    
#ticket = TicketClassification(
#    category="Application Failure",
#    severity=Severity.HIGH,
#    application="SAP",
#    retryable=True,
#    recommended_action="Check SAP server availability"
#)

#print(ticket)