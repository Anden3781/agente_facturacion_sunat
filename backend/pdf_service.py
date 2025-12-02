from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_invoice_pdf(data: dict, filename: str = "invoice.pdf") -> str:
    """
    Generates a detailed PDF invoice from the data dictionary.
    Returns the path to the generated PDF.
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # --- Header ---
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "FACTURA ELECTRÓNICA")
    
    c.setFont("Helvetica", 10)
    # Emitter (Demo data)
    c.drawString(50, height - 70, "Empresa Demo S.A.C.")
    c.drawString(50, height - 82, "RUC: 20123456789")
    c.drawString(50, height - 94, "Av. Ficticia 123, Lima, Perú")

    # Invoice Details (Right side)
    c.drawString(400, height - 70, f"Fecha: {data.get('issue_date', 'Hoy')}")
    c.drawString(400, height - 82, f"Moneda: {data.get('currency', 'PEN')}")
    c.drawString(400, height - 94, f"Pago: {data.get('payment_method', 'Contado')}")

    # Separator
    c.line(50, height - 110, 550, height - 110)

    # --- Client Info ---
    y_client = height - 130
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_client, "Datos del Cliente:")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, y_client - 15, f"Razón Social: {data.get('client', 'N/A')}")
    c.drawString(50, y_client - 27, f"RUC: {data.get('ruc', 'N/A')}")
    c.drawString(50, y_client - 39, f"Dirección: {data.get('address', '')}")
    c.drawString(300, y_client - 39, f"Email: {data.get('email', '')}")

    # --- Items Table ---
    y = height - 190
    c.setFont("Helvetica-Bold", 10)
    # Headers
    c.drawString(50, y, "Descripción")
    c.drawString(300, y, "Cant.")
    c.drawString(340, y, "Und.")
    c.drawString(380, y, "P.Unit")
    c.drawString(450, y, "Total")
    
    c.line(50, y - 5, 550, y - 5)
    
    # Rows
    y -= 20
    c.setFont("Helvetica", 10)
    total_neto = 0
    
    for item in data.get('items', []):
        desc = item.get('description', '')[:45] # Truncate long descriptions
        qty = item.get('quantity', 0)
        unit = item.get('unit_measure', 'NIU')
        price = item.get('unit_price', 0.0)
        subtotal = qty * price
        total_neto += subtotal
        
        c.drawString(50, y, desc)
        c.drawString(300, y, str(qty))
        c.drawString(340, y, unit)
        c.drawString(380, y, f"{price:,.2f}")
        c.drawString(450, y, f"{subtotal:,.2f}")
        y -= 15
        
        if y < 100: # New page if needed (basic handling)
            c.showPage()
            y = height - 50

    # --- Totals ---
    igv_rate = data.get('igv_rate', 0.18)
    igv = total_neto * igv_rate
    total = total_neto + igv
    currency_symbol = "S/" if data.get('currency') == 'PEN' else "$"
    
    y -= 10
    c.line(50, y, 550, y)
    y -= 20
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, y, "Op. Gravada:")
    c.drawRightString(500, y, f"{currency_symbol} {total_neto:,.2f}")
    y -= 15
    c.drawString(350, y, f"IGV ({int(igv_rate*100)}%):")
    c.drawRightString(500, y, f"{currency_symbol} {igv:,.2f}")
    y -= 15
    c.setFont("Helvetica-Bold", 12)
    c.drawString(350, y, "TOTAL A PAGAR:")
    c.drawRightString(500, y, f"{currency_symbol} {total:,.2f}")

    # --- Footer / Notes ---
    y -= 40
    c.setFont("Helvetica", 9)
    notes = data.get('notes', '')
    if notes:
        c.drawString(50, y, "Observaciones:")
        c.drawString(50, y - 12, notes[:100]) # Basic truncation

    c.save()
    return filename
