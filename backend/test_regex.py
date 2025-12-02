import re

text = "genera una factura con ruc 20202020202 para anderson de 2 routers cisco de 5 mil dolares cada uno, con direccion en arica 1234 y correo ejemplo@hotmail.com"

print(f"Texto a analizar: {text}\n")

# 1. Test Address Regex
print("--- Test Dirección ---")
# Regex actual
addr_pattern = r'(?:direccion|dirección)(?:\s+fiscal)?\s+en\s+([A-Za-z0-9\s,.-]+?)(?=\s+y\s+correo|\s*,|$)'
match = re.search(addr_pattern, text, re.IGNORECASE)
if match:
    print(f"✅ Dirección encontrada: '{match.group(1).strip()}'")
else:
    print("❌ Dirección NO encontrada con el patrón actual")
    
    # Intento de patrón más flexible
    flexible_pattern = r'(?:direccion|dirección)(?:.*?)en\s+([A-Za-z0-9\s,.-]+?)(?=\s+y\s+correo|\s+correo|$)'
    match2 = re.search(flexible_pattern, text, re.IGNORECASE)
    if match2:
        print(f"💡 Sugerencia encontrada: '{match2.group(1).strip()}'")

# 2. Test Email Regex
print("\n--- Test Email ---")
email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
match = re.search(email_pattern, text)
if match:
    print(f"✅ Email encontrado: '{match.group(0)}'")
else:
    print("❌ Email NO encontrado")

# 3. Test Client Regex
print("\n--- Test Cliente ---")
client_patterns = [
    r'(?:para\s+el\s+cliente|para\s+cliente)\s+([A-Za-z0-9\s]+?)(?=\s+con\s+ruc|\s+por|\s+con\s+dirección|\s+$)',
    r'cliente\s+([A-Za-z0-9\s]+?)(?=\s+con\s+ruc|\s+por|\s+con\s+dirección|\s+$)',
    r'(?:nombre\s+social|con\s+el\s+nombre|nombre)\s+([A-Za-z0-9\s]+?)(?=\s*,|\s+direccion|\s+ruc|\s+por|\s+$)',
    r'para\s+([A-Za-z0-9\s]+?)\s+de', # Patrón que añadí antes
    r'(?:para|a)\s+([A-Za-z0-9\s]+?)(?=\s+con\s+ruc|\s+por|\s+con\s+dirección|\s+$)'
]

found = False
for i, pat in enumerate(client_patterns):
    m = re.search(pat, text, re.IGNORECASE)
    if m:
        print(f"✅ Cliente encontrado con patrón {i}: '{m.group(1).strip()}'")
        found = True
        break
if not found:
    print("❌ Cliente NO encontrado")
