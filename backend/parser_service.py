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
    """Use Google Gemini to extract the required fields.

    The prompt forces Gemini to return ONLY a JSON object with the keys:
    client, ruc, address, email, items (list of {description, quantity, unit_price}).
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""Eres un asistente especializado en extraer información de facturas desde texto en lenguaje natural.

IMPORTANTE: Solo debes procesar solicitudes relacionadas con facturación.

Extrae la siguiente información del texto y devuelve SOLO un JSON válido (sin markdown, sin explicaciones):
{{
  \"client\": \"nombre del cliente\",
  \"ruc\": \"RUC de 11 dígitos (si no hay, usa '00000000000')\",
  \"address\": \"dirección del cliente (si no hay, deja vacío)\",
  \"email\": \"correo electrónico (si no hay, deja vacío)\",
  \"items\": [
    {{
      \"description\": \"descripción del producto/servicio\",
      \"quantity\": número (float),
      \"unit_price\": precio unitario (float)
    }}
  ]
}}

REGLAS:
1. NO DUPLIQUES items. Si dice "2 routers de 10 mil en total", son 2 routers a 5000 cada uno.
2. Si dice "X de Y en total", divide Y entre X para obtener el precio unitario.
3. Convierte "mil" a 1000 (ej: "10 mil" = 10000).
4. Si no encuentras información, usa valores por defecto.
5. SOLO responde con el JSON, nada más.

Texto a procesar:
{text}
"""
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=500,
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
    # Ensure all keys exist
    data.setdefault('client', 'Cliente General')
    data.setdefault('ruc', '00000000000')
    data.setdefault('address', '')
    data.setdefault('email', '')
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
        r'(?:para|a)\s+([A-Za-z0-9\s]+?)(?=\s+con\s+ruc|\s+por|\s+con\s+dirección|\s+$)'
    ]
    for pat in client_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            data["client"] = m.group(1).strip()
            break
    # ---- Address ----
    addr_match = re.search(r'(?:direccion|dirección)(?:\s+fiscal)?\s+en\s+([A-Za-z0-9\s,.-]+?)(?=\s+y\s+correo|\s*,|$)', text, re.IGNORECASE)
    if addr_match:
        data["address"] = addr_match.group(1).strip()
    # ---- Email ----
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        data["email"] = email_match.group(0).strip()
    # ---- Items ----
    items_found = []
    # Pattern 1: "X items de Y cada uno"
    # Capture quantity but ensure it's not an 11-digit number (RUC)
    pat1 = r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+(?:de|a)\s+(\d+(?:\s*mil)?)\s+(?:dolares|soles|pesos)?\s+cada\s+uno'
    for m in re.finditer(pat1, text, re.IGNORECASE):
        qty = int(m.group(1))
        desc = m.group(2).strip()
        price_str = m.group(3).strip()
        price = float(price_str.split()[0]) * 1000 if 'mil' in price_str.lower() else float(price_str)
        items_found.append({"description": desc, "quantity": qty, "unit_price": price})
    
    # Pattern 2: "X items a/por Y"
    pat2 = r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+(?:a|por|cuesta|c\/u)\s+(\d+(?:\.\d{1,2})?)'
    for m in re.finditer(pat2, text, re.IGNORECASE):
        qty = int(m.group(1))
        desc = m.group(2).strip()
        price = float(m.group(3))
        items_found.append({"description": desc, "quantity": qty, "unit_price": price})
    
    # Pattern 3: "X items de Y en total"
    pat3 = r'\b(?!(?:10|20)\d{9}\b)(\d+)\s+([a-zA-Z0-9\s]+?)\s+de\s+(\d+(?:\s*mil)?)\s+(?:dolares|soles|pesos)?\s+en\s+total'
    for m in re.finditer(pat3, text, re.IGNORECASE):
        qty = int(m.group(1))
        desc = m.group(2).strip()
        total_str = m.group(3).strip()
        total = float(total_str.split()[0]) * 1000 if 'mil' in total_str.lower() else float(total_str)
        unit_price = total / qty
        items_found.append({"description": desc, "quantity": qty, "unit_price": unit_price})
    # Deduplicate (keep first occurrence)
    seen = set()
    for it in items_found:
        key = it["description"].lower()
        if key not in seen:
            data["items"].append(it)
            seen.add(key)
    print(f"Regex parsed: {data}")
    return data
