from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_invoice_pdf(data: dict, filename: str = "invoice.pdf") -> str:
    """
    Generates a simple PDF invoice from the data dictionary.
    Returns the path to the generated PDF.
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "FACTURA ELECTRÓNICA (Borrador)")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Cliente: {data.get('client', 'N/A')}")
    c.drawString(50, height - 100, f"RUC: {data.get('ruc', 'N/A')}")
    
    # Items Header
    y = height - 140
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Descripción")
    c.drawString(300, y, "Cant.")
    c.drawString(350, y, "P.Unit")
    c.drawString(450, y, "Total")
    
    # Items
    y -= 20
    c.setFont("Helvetica", 12)
    total_neto = 0
    
    for item in data.get('items', []):
        desc = item.get('description', '')
        qty = item.get('quantity', 0)
        price = item.get('unit_price', 0.0)
        subtotal = qty * price
        total_neto += subtotal
        
        c.drawString(50, y, desc)
        c.drawString(300, y, str(qty))
        c.drawString(350, y, f"{price:.2f}")
        c.drawString(450, y, f"{subtotal:.2f}")
        y -= 20
        
    # Totals
    igv = total_neto * 0.18
    total = total_neto + igv
    
    y -= 20
    c.line(50, y, 500, y)
    y -= 20
    c.drawString(350, y, "Subtotal:")
    c.drawString(450, y, f"{total_neto:.2f}")
    y -= 20
    c.drawString(350, y, "IGV (18%):")
    c.drawString(450, y, f"{igv:.2f}")
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y, "TOTAL:")
    c.drawString(450, y, f"{total:.2f}")
    
    c.save()
    return filename
