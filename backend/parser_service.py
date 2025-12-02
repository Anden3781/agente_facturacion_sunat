import re
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def parse_input(text: str, api_key: str = None) -> dict:
    """Parse natural language invoice description into a structured dict.

    Tries Gemini first (if API key is available). If Gemini fails or is not configured,
    falls back to a deterministic regex‑based parser.
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            print("Attempting Gemini parsing...")
            return parse_with_gemini(text, gemini_key)
        except Exception as e:
            print(f"Gemini parsing failed: {e}. Falling back to regex.")
    print("Using regex fallback...")
    return parse_with_regex(text)

def parse_with_gemini(text: str, api_key: str) -> dict:
    """Use Google Gemini (Flash model) to extract the required fields quickly."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""Extrae datos de facturación de este texto a JSON.
    Campos: client, ruc (11 dígitos o '00000000000'), address, email, currency (PEN/USD), payment_method, notes, items (description, quantity, unit_measure, unit_price).
    Reglas:
    - No inventes datos.
    - Items: No duplicar. Si dice '5 cajas de X a 10 c/u', son 5 items.
    - Moneda: Si menciona dólares/usd -> USD, sino PEN.
    - Unidad: Si dice 'cajas', 'litros', etc. úsalo. Defecto: NIU.
    - Extrae TODOS los datos mencionados, incluso si no siguen un orden específico.
    - Si menciona 'dolares', establece currency como 'USD'.
    - Extrae dirección fiscal si se menciona 'dirección fiscal' o 'direccion fiscal'.
    - Extrae correo electrónico si se menciona 'correo' o 'email'.
    Texto: {text}
    JSON:"""
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.0,
            max_output_tokens=1000,
        ),
        request_options={'timeout': 15}
    )
    response_text = response.text.strip()
    if response_text.startswith('```'):
        response_text = response_text.split('```')[1]
        if response_text.startswith('json'):
            response_text = response_text[4:]
        response_text = response_text.strip()
    data = json.loads(response_text)
    # Ensure defaults
    data.setdefault('client', 'Cliente General')
    data.setdefault('ruc', '00000000000')
    data.setdefault('address', '')
    data.setdefault('email', '')
    data.setdefault('currency', 'PEN')
    data.setdefault('payment_method', 'Contado')
    data.setdefault('notes', '')
    data.setdefault('items', [])
    print(f"Gemini parsed successfully: {data}")
    return data

def parse_with_regex(text: str) -> dict:
    """Heuristic regex parser (fallback)."""
    data = {
        "client": "Cliente General",
        "ruc": "00000000000",
        "address": "",
        "email": "",
        "items": []
    }
    # ---- RUC ----
    ruc_match = re.search(r'(?:ruc[:\s]+)?(\d{11})\b', text, re.IGNORECASE)
    if ruc_match:
        data["ruc"] = ruc_match.group(1)
    else:
        ruc_match = re.search(r'\b(10|20)\d{9}\b', text)
        if ruc_match:
            data["ruc"] = ruc_match.group(0)
    # ---- Client ----
    client_patterns = [
        r'(?:para\s+el\s+cliente|para\s+cliente)\s+([A-Za-z0-9\s]+?)(?=\s+con\s+ruc|\s+por|\s+con\s+dirección|\s+$)',
        r'cliente\s+([A-Za-z0-9\s]+?)(?=\s+con\s+ruc|\s+por|\s+con\s+dirección|\s+$)',
        r'(?:nombre\s+social|con\s+el\s+nombre|nombre)\s+([A-Za-z0-9\s]+?)(?=\s*,|\s+direccion|\s+ruc|\s+por|\s+$)',
        r'para\s+([A-Za-z0-9\s]+?)\s+de',
        r'\b(?:para|a)\s+([A-Za-z0-9\s]+?)(?=\s+con\s+ruc|\s+por|\s+con\s+dirección|\s+$)',
        r'\b(?:para|a)\s+([A-Za-z0-9\s]+?)\s+(?:con\s+ruc|\s+por|\s+con\s+dirección|\s+$)'
    ]
    for pat in client_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            data["client"] = m.group(1).strip()
            break
            
    # Set client name based on text if still default
    if data["client"] == "Cliente General":
        client_match = re.search(r'(?:para|a)\s+([A-Za-z0-9\s]+?)(?=\s+con\s+ruc|\s+por|\s+con\s+dirección|\s+$)', text, re.IGNORECASE)
        if client_match:
            data["client"] = client_match.group(1).strip()
        else:
            # Try to find client name with "para" pattern
            client_match = re.search(r'para\s+([A-Za-z0-9\s]+?)\s+(?:con\s+ruc|\s+por|\s+con\s+dirección|\s+$)', text, re.IGNORECASE)
            if client_match:
                data["client"] = client_match.group(1).strip()

    # ---- Address ----
    # Updated address regex to accept 'de' or 'en' and common misspellings
    addr_match = re.search(r'(?:direccion|diracci\u00f3n|dir|dirección)(?:\s+fiscal)?\s+(?:de|en)\s+([A-Za-z0-9\s,.-]+?)(?=\s+(?:con|y)\s+correo|\s*,|$)', text, re.IGNORECASE)
    if addr_match:
        data["address"] = addr_match.group(1).strip()
    else:
        # Try simpler address pattern
        addr_match = re.search(r'(?:direccion|diracci\u00f3n|dir|dirección)\s+([A-Za-z0-9\s,.-]+?)(?=\s*,|\s+$)', text, re.IGNORECASE)
        if addr_match:
            data["address"] = addr_match.group(1).strip()
        else:
            # Try to find address with "fiscal" pattern
            addr_match = re.search(r'(?:direccion|diracci\u00f3n|dir|dirección)\s+fiscal\s+([A-Za-z0-9\s,.-]+?)(?=\s*,|\s+$)', text, re.IGNORECASE)
            if addr_match:
                data["address"] = addr_match.group(1).strip()
            else:
                # Try to find address with "fiscal" pattern and "y" separator
                addr_match = re.search(r'(?:direccion|diracci\u00f3n|dir|dirección)\s+fiscal\s+([A-Za-z0-9\s,.-]+?)\s+y\s+correo', text, re.IGNORECASE)
                if addr_match:
                    data["address"] = addr_match.group(1).strip()

    # ---- Email ----
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        data["email"] = email_match.group(0).strip()
    else:
        # Try to find email mentioned in text
        email_match = re.search(r'(?:correo|email)\s+([\w\.-]+@[\w\.-]+\.\w+)', text, re.IGNORECASE)
        if email_match:
            data["email"] = email_match.group(1).strip()
        else:
             # Try to find email mentioned in text with "correo" pattern
            email_match = re.search(r'correo\s+([\w\.-]+@[\w\.-]+\.\w+)', text, re.IGNORECASE)
            if email_match:
                data["email"] = email_match.group(1).strip()

    # ---- Items ----
    items_found = []
    matched_ranges = []

    def is_overlapping(start, end, ranges):
        for s, e in ranges:
            # Check for any overlap
            if max(start, s) < min(end, e):
                return True
        return False

    # List of patterns in order of priority (Specific -> General)
    # Format: (Regex Pattern, Price Type ['unit' or 'total'])
    item_patterns = [
        # 1. Specific: "con un precio unitario de"
        (r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+con\s+un\s+precio\s+unitario\s+de\s+(\d+(?:\s*mil)?)\s+(?:dolares|soles|pesos)?', 'unit'),
        # 2. Specific: "valorizados en ... cada uno"
        (r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+valorizados\s+en\s+(\d+(?:\s*mil)?)\s+cada\s+uno', 'unit'),
        # 3. Specific: "de ... cada uno"
        (r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+(?:de|a)\s+(\d+(?:\s*mil)?)\s+(?:dolares|soles|pesos)?\s+cada\s+uno', 'unit'),
        # 4. Specific: "de ... en total"
        (r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+de\s+(\d+(?:\s*mil)?)\s+(?:dolares|soles|pesos)?\s+en\s+total', 'total'),
        # 5. Medium: "de ... dolares" (Explicit currency)
        (r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+de\s+(\d+(?:\s*mil)?)\s+(?:dolares|soles|pesos)', 'unit'),
        # 6. Medium: "a/por ... dolares" (Explicit currency)
        (r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+(?:a|por|cuesta|c\/u)\s+(\d+(?:\.\d{1,2})?)\s+(?:dolares|soles|pesos)', 'unit'),
        # 7. General: "a/por ..."
        (r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+(?:a|por|cuesta|c\/u)\s+(\d+(?:\.\d{1,2})?)', 'unit'),
        # 8. General: "de ..." (Can be risky, matches "5 items de color rojo") - keep it lower priority
        (r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+de\s+(\d+(?:\s*mil)?)\s+(?:dolares|soles|pesos)?', 'unit'),
        # 9. General: "por ..."
        (r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+por\s+(\d+(?:\s*mil)?)\s+(?:dolares|soles|pesos)?', 'unit'),
        # 10. Most General: "X items Y" (Very risky, must be last)
        (r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+(\d+(?:\s*mil)?)\s+(?:dolares|soles|pesos)?', 'unit')
    ]

    for pat, price_type in item_patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            start, end = m.span()
            
            # Skip if this match overlaps with a previously found (higher priority) item
            if is_overlapping(start, end, matched_ranges):
                continue
            
            qty = int(m.group(1))
            desc = m.group(2).strip()
            price_str = m.group(3).strip()
            
            # Handle "mil" in price
            if 'mil' in price_str.lower():
                price_val = float(price_str.split()[0]) * 1000
            else:
                price_val = float(price_str)
            
            if price_type == 'total':
                unit_price = price_val / qty if qty > 0 else 0
            else:
                unit_price = price_val

            items_found.append({
                "description": desc,
                "quantity": qty,
                "unit_price": unit_price,
                "unit_measure": "NIU"
            })
            matched_ranges.append((start, end))

    # Deduplicate by description (just in case)
    seen = set()
    for it in items_found:
        key = it["description"].lower()
        if key not in seen:
            data["items"].append(it)
            seen.add(key)

    # Set currency based on text
    if re.search(r'\bdolares\b', text, re.IGNORECASE):
        data["currency"] = "USD"
    elif re.search(r'\b(?:soles|pesos)\b', text, re.IGNORECASE):
        data["currency"] = "PEN"

    print(f"Regex parsed: {data}")
    return data
