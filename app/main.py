#from app.classifier import classify_ticket  # Imports the reusable classifier function

#ticket_text = input("Enter the support ticket: ")  # Reads ticket text from the user

#ticket = classify_ticket(ticket_text)

#print(ticket.model_dump_json(indent=2))
import logging
from fastapi import FastAPI,HTTPException
from app.classifier import classify_ticket
from app.models import TicketRequest, TicketClassification
from app.tools import check_application_status

app = FastAPI()

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

@app.get("/")
def home():
    return {"message": "AI Ticket Triage API is running"}

@app.post("/classify", response_model=TicketClassification) #FastAPI uses it as the 
#API response contract/validation and documentation.
def classify(ticket: TicketRequest):
    try:
        logger.info("Ticket classification started")
        result = classify_ticket(ticket.ticket_text) #FastAPI uses it as the 
#Input data contract/validation and documentation.
        logger.info("Ticket classification completed")
        return result

    except Exception as e:
        logger.error(f"Ticket classification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Ticket classification failed"
        )