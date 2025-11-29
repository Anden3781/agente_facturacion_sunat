import json
from datetime import date, datetime
from typing import Any, Dict, List, Tuple

import streamlit as st
import streamlit.components.v1 as components

DEFAULT_EMITTER = {
    "name": "Empresa Demo S.A.C.",
    "ruc": "20123456789",
    "address": "Av. Ficticia 123, Lima, Perú",
}


def init_session_state() -> None:
    if "invoice" not in st.session_state:
        st.session_state.invoice = {
            "invoice_type": "Factura",
            "serie": "F001",
            "number": "000001",
            "currency": "PEN",
            "issue_date": date.today().isoformat(),
            "emitter": DEFAULT_EMITTER.copy(),
            "customer": {
                "name": "Cliente Demo",
                "tax_id": "00000000000",
                "address": "",
                "email": "",
            },
            "items": [],
            "igv_rate": 0.18,  # 18%
            "notes": "",
        }
    if "nl_input" not in st.session_state:
        st.session_state.nl_input = ""


def reset_invoice() -> None:
    st.session_state.pop("invoice", None)
    init_session_state()


def load_example_invoice() -> None:
    """Carga una factura de ejemplo para la demo."""
    st.session_state.invoice = {
        "invoice_type": "Factura",
        "serie": "F001",
        "number": "000123",
        "currency": "PEN",
        "issue_date": date.today().isoformat(),
        "emitter": DEFAULT_EMITTER.copy(),
        "customer": {
            "name": "ACME S.A.",
            "tax_id": "20123456789",
            "address": "Av. Industrial 456, Lima",
            "email": "facturas@acme.com",
        },
        "items": [
            {"description": "Laptop empresarial", "quantity": 3.0, "unit_price": 2500.0},
            {"description": "Monitor 24\"", "quantity": 2.0, "unit_price": 800.0},
        ],
        "igv_rate": 0.18,
        "notes": "Pago contra entrega.",
    }


# ----------------- Cálculos y helpers -----------------


def compute_totals(items: List[Dict[str, Any]], igv_rate: float) -> Tuple[float, float, float]:
    subtotal = 0.0
    for item in items:
        qty = float(item.get("quantity", 0) or 0)
        price = float(item.get("unit_price", 0) or 0)
        subtotal += qty * price
    subtotal = round(subtotal, 2)
    igv_amount = round(subtotal * igv_rate, 2)
    total = round(subtotal + igv_amount, 2)
    return subtotal, igv_amount, total


def parse_issue_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return date.today()


def build_invoice_json(invoice: Dict[str, Any]) -> Dict[str, Any]:
    subtotal, igv_amount, total = compute_totals(invoice["items"], invoice["igv_rate"])
    return {
        "invoice_type": invoice["invoice_type"],
        "serie": invoice["serie"],
        "number": invoice["number"],
        "currency": invoice["currency"],
        "issue_date": invoice["issue_date"],
        "emitter": invoice["emitter"],
        "customer": invoice["customer"],
        "items": invoice["items"],
        "igv_rate": invoice["igv_rate"],
        "subtotal": subtotal,
        "igv_amount": igv_amount,
        "total": total,
        "notes": invoice.get("notes", ""),
    }


def build_invoice_html(invoice_json: Dict[str, Any]) -> str:
    items_rows = ""
    for idx, item in enumerate(invoice_json["items"], start=1):
        subtotal_item = item["quantity"] * item["unit_price"]
        items_rows += f"""
        <tr>
            <td style="padding:4px; border:1px solid #ddd; text-align:center;">{idx}</td>
            <td style="padding:4px; border:1px solid #ddd;">{item['description']}</td>
            <td style="padding:4px; border:1px solid #ddd; text-align:right;">{item['quantity']}</td>
            <td style="padding:4px; border:1px solid #ddd; text-align:right;">{item['unit_price']:.2f}</td>
            <td style="padding:4px; border:1px solid #ddd; text-align:right;">{subtotal_item:.2f}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8" />
<title>{invoice_json['invoice_type']} {invoice_json['serie']}-{invoice_json['number']}</title>
<style>
body {{
    font-family: Arial, sans-serif;
    font-size: 12px;
    margin: 24px;
}}
h1 {{
    font-size: 20px;
    margin-bottom: 4px;
}}
h3 {{
    margin-bottom: 4px;
    margin-top: 16px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
}}
th {{
    background-color: #f2f2f2;
}}
</style>
</head>
<body>
  <h1>{invoice_json['invoice_type']} {invoice_json['serie']}-{invoice_json['number']}</h1>
  <p><strong>Fecha:</strong> {invoice_json['issue_date']}</p>

  <h3>Emisor</h3>
  <p>
    <strong>{invoice_json['emitter']['name']}</strong><br/>
    RUC: {invoice_json['emitter']['ruc']}<br/>
    {invoice_json['emitter']['address']}
  </p>

  <h3>Cliente</h3>
  <p>
    <strong>{invoice_json['customer']['name']}</strong><br/>
    Documento: {invoice_json['customer']['tax_id']}<br/>
    {invoice_json['customer']['address']}
  </p>

  <h3>Detalle</h3>
  <table>
    <thead>
      <tr>
        <th style="padding:4px; border:1px solid #ddd;">#</th>
        <th style="padding:4px; border:1px solid #ddd;">Descripción</th>
        <th style="padding:4px; border:1px solid #ddd;">Cantidad</th>
        <th style="padding:4px; border:1px solid #ddd;">Precio unitario</th>
        <th style="padding:4px; border:1px solid #ddd;">Subtotal</th>
      </tr>
    </thead>
    <tbody>
      {items_rows}
    </tbody>
  </table>

  <table style="width: 40%; float: right; margin-top: 12px;">
    <tr>
      <td style="padding:4px;">Op. gravada</td>
      <td style="padding:4px; text-align:right;">{invoice_json['subtotal']:.2f}</td>
    </tr>
    <tr>
      <td style="padding:4px;">IGV ({int(invoice_json['igv_rate']*100)}%)</td>
      <td style="padding:4px; text-align:right;">{invoice_json['igv_amount']:.2f}</td>
    </tr>
    <tr>
      <td style="padding:4px;"><strong>Total</strong></td>
      <td style="padding:4px; text-align:right;"><strong>{invoice_json['total']:.2f}</strong></td>
    </tr>
  </table>

  <div style="clear: both;"></div>

  <p style="margin-top: 48px; font-size: 10px; color: #666;">
    Documento generado por un MVP de demostración. No tiene validez tributaria.
  </p>
</body>
</html>
"""
    return html


# ----------------- UI: header -----------------


def render_header() -> None:
    invoice = st.session_state.invoice

    col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])
    with col1:
        invoice_type = st.selectbox(
            "Tipo de comprobante",
            ["Factura", "Boleta"],
            index=0 if invoice["invoice_type"] == "Factura" else 1,
        )
    with col2:
        igv_percent = st.number_input(
            "IGV (%)",
            min_value=0.0,
            max_value=30.0,
            value=float(invoice["igv_rate"] * 100),
            step=0.5,
        )
    with col3:
        if st.button("Nueva factura"):
            reset_invoice()
            st.stop()
    with col4:
        if st.button("Cargar ejemplo"):
            load_example_invoice()
            st.stop()

    invoice["invoice_type"] = invoice_type
    invoice["igv_rate"] = igv_percent / 100.0
    st.session_state.invoice = invoice

    st.caption("Datos ficticios. No conectado a SUNAT. Funciones de IA pendientes.")


# ----------------- UI: panel de lenguaje natural -----------------


def render_natural_language_panel() -> None:
    st.subheader("Entrada en lenguaje natural")

    st.session_state.nl_input = st.text_area(
        "Describe la factura (IA aún no implementada)",
        value=st.session_state.nl_input,
        height=180,
        placeholder=(
            "Ejemplo: genera una factura a ACME S.A. con RUC 20123456789 "
            "por 3 laptops a 2500 cada una y 2 monitores a 800. Fecha de hoy. "
            "Moneda soles."
        ),
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("Ejemplo 1 ítem"):
            st.session_state.nl_input = (
                "Genera una factura a Cliente Uno con RUC 20111111111 por 1 "
                "servicio de consultoría a 1500 soles. Fecha 01/12/2025."
            )
            st.experimental_rerun()
    with col_b:
        if st.button("Ejemplo varios ítems"):
            st.session_state.nl_input = (
                "Genera una factura a ACME S.A. con RUC 20123456789 por 3 laptops a "
                "2500 cada una y 2 monitores a 800 cada uno. Moneda PEN, fecha de hoy."
            )
            st.experimental_rerun()
    with col_c:
        if st.button("Limpiar descripción"):
            st.session_state.nl_input = ""
            st.experimental_rerun()

    if st.button("Generar borrador (IA pendiente)", type="primary"):
        st.info("La extracción automática con IA todavía no está implementada en este MVP.")


# ----------------- UI: tabla de ítems -----------------


def render_items_table(invoice: Dict[str, Any]) -> None:
    st.markdown("#### Ítems")

    items = invoice.get("items", [])
    if st.button("Agregar ítem"):
        items.append(
            {
                "description": "Nuevo ítem",
                "quantity": 1.0,
                "unit_price": 0.0,
            }
        )
        invoice["items"] = items
        st.session_state.invoice = invoice

    updated_items: List[Dict[str, Any]] = []
    for idx, item in enumerate(invoice.get("items", [])):
        cols = st.columns([4, 1, 1, 1])
        with cols[0]:
            desc = st.text_input(
                "Descripción",
                value=item["description"],
                key=f"item_desc_{idx}",
            )
        with cols[1]:
            qty = st.number_input(
                "Cantidad",
                min_value=0.0,
                value=float(item["quantity"]),
                key=f"item_qty_{idx}",
            )
        with cols[2]:
            unit_price = st.number_input(
                "Precio unitario",
                min_value=0.0,
                value=float(item["unit_price"]),
                key=f"item_price_{idx}",
            )
        with cols[3]:
            delete = st.button("Eliminar", key=f"item_del_{idx}")

        if not delete:
            updated_items.append(
                {"description": desc, "quantity": qty, "unit_price": unit_price}
            )

    invoice["items"] = updated_items
    st.session_state.invoice = invoice


# ----------------- UI: panel de factura estructurada -----------------


def render_structured_invoice_panel() -> None:
    invoice = st.session_state.invoice

    st.subheader("Factura estructurada")

    st.markdown("#### Datos del comprobante y emisor")
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            serie = st.text_input("Serie", value=invoice["serie"])
        with col2:
            number = st.text_input("Número", value=invoice["number"])
        with col3:
            issue_date_val = parse_issue_date(invoice["issue_date"])
            issue_date_ui = st.date_input("Fecha de emisión", value=issue_date_val)

        invoice["serie"] = serie
        invoice["number"] = number
        invoice["issue_date"] = issue_date_ui.isoformat()

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Emisor (fijo demo)**")
            st.text_input(
                "Razón social emisor",
                value=invoice["emitter"]["name"],
                disabled=True,
            )
            st.text_input(
                "RUC emisor",
                value=invoice["emitter"]["ruc"],
                disabled=True,
            )
            st.text_input(
                "Dirección emisor",
                value=invoice["emitter"]["address"],
                disabled=True,
            )

        with col2:
            st.markdown("**Cliente**")
            customer_name = st.text_input(
                "Razón social / Nombre",
                value=invoice["customer"]["name"],
            )
            customer_tax_id = st.text_input(
                "RUC / DNI",
                value=invoice["customer"]["tax_id"],
                max_chars=11,
            )
            customer_address = st.text_input(
                "Dirección",
                value=invoice["customer"]["address"],
            )
            customer_email = st.text_input(
                "Correo (opcional)",
                value=invoice["customer"]["email"],
            )
            invoice["customer"].update(
                {
                    "name": customer_name,
                    "tax_id": customer_tax_id,
                    "address": customer_address,
                    "email": customer_email,
                }
            )

    render_items_table(invoice)

    subtotal, igv_amount, total = compute_totals(invoice["items"], invoice["igv_rate"])
    st.markdown("#### Totales")
    col1, col2, col3 = st.columns(3)
    col1.metric("Op. gravada (subtotal)", f"{subtotal:,.2f}")
    col2.metric(f"IGV ({int(invoice['igv_rate'] * 100)}%)", f"{igv_amount:,.2f}")
    col3.metric("Total a pagar", f"{total:,.2f}")

    invoice["notes"] = st.text_area(
        "Notas / Observaciones",
        value=invoice.get("notes", ""),
        height=60,
    )
    st.session_state.invoice = invoice

    st.markdown("---")

    invoice_json = build_invoice_json(invoice)
    tab_json, tab_html = st.tabs(["Vista JSON", "Vista HTML"])

    with tab_json:
        json_str = json.dumps(invoice_json, ensure_ascii=False, indent=2)
        st.code(json_str, language="json")

    with tab_html:
        html = build_invoice_html(invoice_json)
        components.html(html, height=600, scrolling=True)


# ----------------- Main -----------------


def main() -> None:
    st.set_page_config(
        page_title="Agente de Facturación SUNAT-like",
        layout="wide",
    )
    init_session_state()

    st.title("Agente de Facturación estilo SUNAT")
    render_header()

    col_left, col_right = st.columns([1, 1.3])
    with col_left:
        render_natural_language_panel()
    with col_right:
        render_structured_invoice_panel()


if __name__ == "__main__":
    main()
