from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from parser_service import parse_input
from invoice_logic import calculate_totals

app = FastAPI(title="Billing Agent API")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ParseRequest(BaseModel):
    text: str
    api_key: Optional[str] = None

class Item(BaseModel):
    description: str
    quantity: float
    unit_price: float

class CalculateRequest(BaseModel):
    items: List[Item]
    igv_rate: Optional[float] = 0.18

class InvoiceRequest(BaseModel):
    text: str
    igv_rate: Optional[float] = 0.18
    api_key: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Billing Agent API is running", "version": "1.0"}

@app.post("/parse")
def parse_invoice_text(request: ParseRequest):
    """
    Endpoint to parse natural language text into invoice data.
    Returns: client, ruc, items
    """
    try:
        data = parse_input(request.text, request.api_key)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate")
def calculate_invoice(request: CalculateRequest):
    """
    Endpoint to calculate invoice totals.
    Returns: subtotal, igv_amount, total
    """
    try:
        items_dict = [item.dict() for item in request.items]
        totals = calculate_totals(items_dict, request.igv_rate)
        return totals
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-invoice")
def generate_full_invoice(request: InvoiceRequest):
    """
    Complete endpoint: Parse text + Calculate totals.
    Returns: Full invoice data ready for frontend.
    """
    try:
        # 1. Parse input
        parsed_data = parse_input(request.text, request.api_key)
        
        # 2. Calculate totals
        totals = calculate_totals(parsed_data['items'], request.igv_rate)
        
        # 3. Combine everything
        result = {
            "client": parsed_data['client'],
            "ruc": parsed_data['ruc'],
            "address": parsed_data.get('address', ''),
            "email": parsed_data.get('email', ''),
            "currency": parsed_data.get('currency', 'PEN'),
            "payment_method": parsed_data.get('payment_method', 'Contado'),
            "notes": parsed_data.get('notes', ''),
            "items": parsed_data['items'],
            "igv_rate": request.igv_rate,
            **totals
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
