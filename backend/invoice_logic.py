def calculate_totals(items: list, igv_rate: float = 0.18) -> dict:
    """
    Calculates invoice totals (Net, IGV, Total).
    
    Args:
        items: List of items with 'quantity' and 'unit_price'
        igv_rate: IGV rate (default 18% = 0.18)
        
    Returns:
        Dictionary with subtotal, igv_amount, and total
    """
    subtotal = 0.0
    
    for item in items:
        qty = float(item.get('quantity', 0))
        price = float(item.get('unit_price', 0))
        subtotal += qty * price
    
    subtotal = round(subtotal, 2)
    igv_amount = round(subtotal * igv_rate, 2)
    total = round(subtotal + igv_amount, 2)
    
    return {
        "subtotal": subtotal,
        "igv_amount": igv_amount,
        "total": total
    }
