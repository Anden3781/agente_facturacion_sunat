import sys
import os

# Add the current directory to sys.path to ensure we can import parser_service
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser_service import parse_with_regex, parse_input

def run_test(name, text, expected_checks):
    print(f"\n--- Test: {name} ---")
    print(f"Input: {text}")
    
    # We test regex fallback explicitly first to ensure the logic works
    # even if Gemini is not available or fails.
    print("Testing Regex Fallback...")
    result = parse_with_regex(text)
    
    all_passed = True
    for key, expected_value in expected_checks.items():
        if key == "items":
            # Check if at least one item matches criteria
            if not result["items"]:
                print(f"❌ Items: Expected items but got empty list")
                all_passed = False
                continue
                
            item = result["items"][0]
            for item_key, item_val in expected_value.items():
                if item.get(item_key) != item_val:
                    print(f"❌ Item {item_key}: Expected {item_val}, got {item.get(item_key)}")
                    all_passed = False
                else:
                    print(f"✅ Item {item_key}: {item_val}")
        else:
            if result.get(key) != expected_value:
                print(f"❌ {key}: Expected '{expected_value}', got '{result.get(key)}'")
                all_passed = False
            else:
                print(f"✅ {key}: {expected_value}")
    
    if all_passed:
        print("🎉 TEST PASSED (Regex)")
    else:
        print("💥 TEST FAILED (Regex)")

# Case 1: The reported failing case
text1 = "creame una factura con nombre anderson RUC 20212223241, diracción fiscal de avenida arica 1234 con correo ejemplo@hotmail.com para 10 routers d ecisco valorizados en 5000 cada uno"
checks1 = {
    "client": "anderson",
    "ruc": "20212223241",
    "address": "avenida arica 1234",
    "email": "ejemplo@hotmail.com",
    "items": {
        "quantity": 10,
        "unit_price": 5000.0
    }
}

# Case 2: Standard case
text2 = "factura para Juan Perez con RUC 10123456789 direccion en Calle Lima 123 y correo juan@test.com por 5 laptops a 2000 soles cada uno"
checks2 = {
    "client": "Juan Perez",
    "ruc": "10123456789",
    "address": "Calle Lima 123",
    "email": "juan@test.com",
    "items": {
        "quantity": 5,
        "unit_price": 2000.0
    }
}

if __name__ == "__main__":
    run_test("Reported Issue", text1, checks1)
    run_test("Standard Case", text2, checks2)
