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
        "address": "",
        "items": []
    }
    
    # 1. Extract RUC (11 digits, optionally preceded by "RUC" keyword)
    # Pattern 1: "RUC 12345678901" or "RUC: 12345678901" or just "12345678901"
    ruc_match = re.search(r'(?:ruc[:\s]+)?(\d{11})\b', text, re.IGNORECASE)
    if ruc_match:
        data["ruc"] = ruc_match.group(1)
    else:
        # Pattern 2: Any 11-digit number starting with 10 or 20 (standard RUC format)
        ruc_match = re.search(r'\b(10|20)\d{9}\b', text)
        if ruc_match:
            data["ruc"] = ruc_match.group(0)
    
    # 2. Extract Client Name
    # Pattern: "nombre social [Name]" or "con el nombre [Name]" or "a [Name]" or "para [Name]"
    client_patterns = [
        r'(?:nombre\s+social|con\s+el\s+nombre|nombre)\s+([a-zA-Z0-9\s]+?)(?=\s*,|\s+direccion|\s+ruc|\s+por)',
        r'(?:a|para)\s+([A-Z][a-zA-Z0-9\s]+?)(?=\s+(?:con|por|de|ruc|direccion|$))',
    ]
    
    for pattern in client_patterns:
        client_match = re.search(pattern, text, re.IGNORECASE)
        if client_match:
            data["client"] = client_match.group(1).strip()
            break
    
    # 3. Extract Address
    # Pattern: "direccion [Address]" or "dirección [Address]"
    address_match = re.search(r'direcci[oó]n\s+([a-zA-Z0-9\s,.-]+?)(?=\s+por|\s+ruc|$)', text, re.IGNORECASE)
    if address_match:
        data["address"] = address_match.group(1).strip()
        
    # 4. Extract Items (Quantity x Description x Price)
    # Patterns like: "2 laptops a 1500", "5 mouse por 20", "2 routers de 10 mil dolares en total"
    
    # Pattern 1: Standard "X items a/por/c/u Y"
    item_pattern = r'(\d+)\s+([a-zA-Z0-9\s]+?)\s+(?:a|por|cuesta|c\/u|de)\s+(\d+(?:\.\d{1,2})?)'
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
    
    # Pattern 2: "X items de Y en total" (divide total by quantity)
    total_pattern = r'(\d+)\s+([a-zA-Z0-9\s]+?)\s+de\s+(\d+(?:\s*mil)?)\s+(?:dolares|soles|pesos)?\s+en\s+total'
    total_matches = re.finditer(total_pattern, text, re.IGNORECASE)
    
    for match in total_matches:
        qty = int(match.group(1))
        desc = match.group(2).strip()
        total_str = match.group(3).strip()
        
        # Handle "10 mil" -> 10000
        if 'mil' in total_str.lower():
            total = float(total_str.split()[0]) * 1000
        else:
            total = float(total_str)
        
        unit_price = total / qty
        
        data["items"].append({
            "description": desc,
            "quantity": qty,
            "unit_price": unit_price
        })
        
    return data
