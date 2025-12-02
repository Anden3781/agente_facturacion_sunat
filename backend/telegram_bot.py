import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from parser_service import parse_input
from pdf_service import generate_invoice_pdf
from invoice_logic import calculate_totals

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# States
WAITING_INPUT, CONFIRM_PREVIEW = range(2)

# Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")  # User will set this

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation."""
    await update.message.reply_text(
        "¡Hola! Soy tu Agente de Facturación. 🤖\n"
        "Dime qué quieres facturar (ej: 'Factura a ACME RUC 20123456789 por 2 laptops a 1500')."
    )
    return WAITING_INPUT

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Parses the input and shows a preview."""
    text = update.message.text
    user_data = context.user_data
    
    # 1. Parse Input
    parsed_data = parse_input(text)
    
    # Calculate totals
    totals = calculate_totals(parsed_data['items'])
    parsed_data.update(totals) # Add subtotal, igv_amount, total to parsed_data
    
    user_data['invoice_data'] = parsed_data # Save to context
    
    # 2. Format Preview
    currency_symbol = "$" if parsed_data.get('currency') == 'USD' else "S/"
    items_str = "\n".join([f"- {i['quantity']} x {i['description']} ({currency_symbol} {i['unit_price']})" for i in parsed_data['items']])
    
    preview = (
        f"🧾 **Vista Previa**\n\n"
        f"👤 **Cliente:** {parsed_data['client']}\n"
        f"🆔 **RUC:** {parsed_data['ruc']}\n"
        f"📍 **Dirección:** {parsed_data['address']}\n"
        f"📧 **Correo:** {parsed_data['email']}\n\n"
        f"📦 **Ítems:**\n{items_str}\n\n"
        f"💰 **Subtotal:** {currency_symbol} {parsed_data['subtotal']}\n"
        f"💵 **IGV (18%):** {currency_symbol} {parsed_data['igv_amount']}\n"
        f"💳 **TOTAL:** {currency_symbol} {parsed_data['total']}\n\n"
        f"¿Está correcto? Responde 'Sí' para generar el PDF o escribe los cambios."
    )
    
    await update.message.reply_text(preview, parse_mode='Markdown')
    return CONFIRM_PREVIEW

async def confirm_or_modify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles confirmation or modification."""
    text = update.message.text.lower()
    user_data = context.user_data
    
    if text in ['si', 'sí', 'correcto', 'ok', 'confirmar']:
        # Generate PDF
        await update.message.reply_text("Generando PDF... ⏳")
        
        pdf_path = generate_invoice_pdf(user_data['invoice_data'], filename="factura_temp.pdf")
        
        # Send PDF
        await update.message.reply_document(document=open(pdf_path, 'rb'), filename="factura.pdf")
        
        # Cleanup
        # os.remove(pdf_path) 
        
        await update.message.reply_text("¡Listo! ¿Deseas crear otra factura? Dime los detalles.")
        return WAITING_INPUT
        
    else:
        # Modification Logic (Simplified: Just re-parse the new text combined with old context? 
        # For MVP, we'll just treat it as a new input or a refinement request. 
        # Ideally, we'd merge, but for now let's re-parse the *modification* instruction or ask to re-state).
        
        # Heuristic: If it looks like a correction, we might need a smarter merger.
        # For this MVP, let's assume the user re-states or adds info.
        # Let's try to parse the new text.
        
        # NOTE: A real "modification" agent needs stateful merging. 
        # Here we will just re-run the parser on the new text for simplicity, 
        # assuming the user might say "Factura a ACME... pero con 3 laptops".
        # Or we can just loop back to handle_input.
        
        await update.message.reply_text("Entendido, actualizando... (Procesando nuevo texto)")
        return await handle_input(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operación cancelada. /start para empezar de nuevo.")
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    if not TELEGRAM_TOKEN:
        print("ERROR: TELEGRAM_TOKEN environment variable not set.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input)],
            CONFIRM_PREVIEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_or_modify)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
