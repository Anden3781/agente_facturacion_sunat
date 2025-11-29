import re
import json

def parse_input(text: str, api_key: str = None) -> dict:
    """
    Parses natural language text into structured invoice data.
    
    Args:
        text: The natural language description of the invoice.
        api_key: Optional API key for LLM service (not implemented yet).
        
    Returns:
        A dictionary containing:
        - client: Name of the client
        - ruc: RUC number (11 digits)
        - items: List of items (description, quantity, unit_price)
    """
    # TODO: Implement LLM integration here if api_key is provided.
    
    # Fallback: Regex/Heuristic parsing
    return parse_with_regex(text)

def parse_with_regex(text: str) -> dict:
    """
    Heuristic parser using Regex for demo purposes.
    """
    data = {
        "client": "Cliente General",
        "ruc": "00000000000",
        "items": []
    }
    
    # 1. Extract RUC (11 digits)
    ruc_match = re.search(r'\b(10|20)\d{9}\b', text)
    if ruc_match:
        data["ruc"] = ruc_match.group(0)
        
    # 2. Extract Client (Heuristic: "a [Client Name]" or "para [Client Name]")
    client_match = re.search(r'(?:a|para)\s+([A-Z][a-zA-Z0-9\s]+?)(?=\s+(?:con|por|de|ruc|$))', text, re.IGNORECASE)
    if client_match:
        data["client"] = client_match.group(1).strip()
        
    # 3. Extract Items (Quantity x Description x Price)
    # Patterns like: "2 laptops a 1500", "5 mouse por 20", "1 servicio de consultoria 500"
    # Regex logic: Number + text + (a/por/cuesta) + Number
    
    item_pattern = r'(\d+)\s+([a-zA-Z0-9\s]+?)\s+(?:a|por|cuesta|c\/u)\s+(\d+(?:\.\d{1,2})?)'
    matches = re.finditer(item_pattern, text, re.IGNORECASE)
    
    for match in matches:
        qty = int(match.group(1))
        desc = match.group(2).strip()
        price = float(match.group(3))
        
        data["items"].append({
            "description": desc,
            "quantity": qty,
            "unit_price": price
        })
        
    return data
