from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from parser_service import parse_input
# from invoice_logic import calculate_totals # Flavio's part (commented out for now)

app = FastAPI(title="Billing Agent API")

class ParseRequest(BaseModel):
    text: str
    api_key: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Billing Agent API is running"}

@app.post("/parse")
def parse_invoice_text(request: ParseRequest):
    """
    Endpoint to parse natural language text into invoice data.
    """
    try:
        data = parse_input(request.text, request.api_key)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Placeholder for Flavio's part
# @app.post("/calculate")
# def calculate_invoice(items: List[Item]):
#     ...
