import sys
import os

# Add the current directory to sys.path to ensure we can import parser_service
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser_service import parse_with_regex

def run_test(name, text, expected_checks):
    print(f"\n--- Test: {name} ---")
    print(f"Input: {text}")
    
    print("Testing Regex Fallback...")
    result = parse_with_regex(text)
    
    all_passed = True
    for key, expected_value in expected_checks.items():
        if key == "items":
            # Check item count
            if len(result["items"]) != len(expected_value):
                 print(f"❌ Items count: Expected {len(expected_value)}, got {len(result['items'])}")
                 all_passed = False
            
            # Check each expected item
            for i, expected_item in enumerate(expected_value):
                if i >= len(result["items"]):
                    break
                actual_item = result["items"][i]
                for item_key, item_val in expected_item.items():
                    if actual_item.get(item_key) != item_val:
                        print(f"❌ Item {i} {item_key}: Expected {item_val}, got {actual_item.get(item_key)}")
                        all_passed = False
                    else:
                        print(f"✅ Item {i} {item_key}: {item_val}")
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

# Case 1: The reported duplicate issue
text1 = "creame una factura para anderson con ruc 10345678912, dirección fiscal avenida arica 1234 y correo test@test.com por 5 routers cisco con un precio unitario de 5 mil dolares cada uno"
checks1 = {
    "client": "anderson",
    "ruc": "10345678912",
    "address": "avenida arica 1234",
    "email": "test@test.com",
    "currency": "USD",
    "items": [
        {
            "description": "routers cisco",
            "quantity": 5,
            "unit_price": 5000.0
        }
    ]
}

if __name__ == "__main__":
    run_test("Duplicate Issue Fix", text1, checks1)
