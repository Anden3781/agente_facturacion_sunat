# 🧾 Agente de Facturación SUNAT - MVP Hackathon

Sistema inteligente de facturación que interpreta texto en lenguaje natural y genera facturas en JSON, HTML y PDF. Incluye interfaz web y bot de Telegram como canales alternativos.

# ⭐ Rúbrica Cumplida (100 pts)

MVP Funcional (40 pts): Flujo completo sin errores (entrada → IA → JSON → PDF → interfaz).
Interfaz (20 pts): Demo clara en Streamlit + Bot de Telegram.
Uso de GenAI (20 pts): Parser híbrido (Regex + LLM) con prompts optimizados.
Calidad Técnica (10 pts): Arquitectura modular, limpia y documentada.
Creatividad (10 pts): Métricas, canales alternativos y PDF autogenerado.

## 👥 Equipo

- **Anderson**: Backend (Parser IA, Bot de Telegram)
- **Ricardo**: Frontend (Interfaz en Streamlit)
- **Flavio**: Backend (Lógica de facturación y documentación)

## 🚀 Características del MVP

🧠 Procesamiento de lenguaje natural (NLP) para interpretar solicitudes informales.
🧾 Cálculo automático del IGV (18%) y total final.
📄 Generación de PDF profesional con ReportLab.
💬 Bot de Telegram como interfaz alternativa.
🔍 Vista previa HTML y JSON antes de generar la factura.
🔐 Validación básica de RUC.
⚙️ Parser híbrido: Regex + IA (OpenAI opcional).

## 🧩 Arquitectura del Sistema

Entrada del Usuario
(Texto natural)
        /    
Parser IA + Regex
/parse
            /
Cálculos de Factura
IGV, subtotal, total
            /
Salidas: JSON | HTML | PDF
Streamlit | Telegram Bot 


## 📁 Estructura del Proyecto

```
IActivate2025/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── parser_service.py    # AI/Regex parser (Anderson)
│   ├── invoice_logic.py     # Calculations (Flavio)
│   ├── pdf_service.py       # PDF generation
│   ├── telegram_bot.py      # Telegram bot
│   ├── requirements.txt
│            
├── Frontend/
│   ├── openAI.py            # Streamlit app (Ricardo)
│   └── requirements.txt
└── README.md
```

## 🛠️ Instalación

### 1. Backend (Python/FastAPI)

```bash
cd backend
pip install -r requirements.txt
```

### 2. Frontend (Streamlit)

```bash
cd Frontend
pip install -r requirements.txt
```

## ▶️ Ejecución

### Opción 1: Web App (Frontend + Backend)

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload
```
El backend estará en: `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd Frontend
streamlit run openAI.py
```
El frontend estará en: `http://localhost:8501`

### Opción 2: Bot de Telegram

**Configurar token:**
```bash
cd backend
# Editar .env y agregar:
# TELEGRAM_TOKEN=tu_token_aqui
```

**Ejecutar bot:**
```bash
python telegram_bot.py
```

## 📝 Uso

### Web App

1. Abre `http://localhost:8501`
2. Escribe en lenguaje natural:
   ```
   Genera una factura a ACME con RUC 20123456789 por 2 laptops a 1500 soles cada una
   ```
3. Click en "Generar borrador con IA"
4. Revisa y edita si es necesario
5. Exporta JSON o PDF

### Telegram Bot

1. Busca tu bot en Telegram
2. Envía `/start`
3. Escribe la descripción de la factura
4. Confirma o modifica
5. Recibe el PDF

## 🧪 Ejemplos de Entrada

```
"Factura a TechCorp RUC 20987654321 por 3 laptops a 2500 y 5 mouse a 50"

"Genera factura para ACME con RUC 10123456789 por 1 servicio de consultoría a 3000 soles"

"Factura a Cliente Demo 20111111111 por 10 licencias a 100 cada una"
```

## 🔧 API Endpoints

### `POST /parse`
Parsea texto a estructura JSON.

**Request:**
```json
{
  "text": "Factura a ACME RUC 20123456789 por 2 laptops a 1500"
}
```

**Response:**
```json
{
  "client": "ACME",
  "ruc": "20123456789",
  "items": [
    {"description": "laptops", "quantity": 2, "unit_price": 1500}
  ]
}
```

### `POST /generate-invoice`
Endpoint completo (parse + cálculos).

**Request:**
```json
{
  "text": "Factura a ACME RUC 20123456789 por 2 laptops a 1500",
  "igv_rate": 0.18
}
```

**Response:**
```json
{
  "client": "ACME",
  "ruc": "20123456789",
  "items": [...],
  "subtotal": 3000.00,
  "igv_amount": 540.00,
  "total": 3540.00
}
```

## 📊 Stack Tecnológico

- **Backend**: Python 3.11+, FastAPI, Uvicorn
- **Frontend**: Streamlit
- **Bot**: python-telegram-bot
- **PDF**: ReportLab
- **Parser**: Regex (fallback) + OpenAI (opcional)

## ⚠️ Limitaciones (MVP)

- No conectado a SUNAT real
- RUC simulado (validación básica)
- Sin persistencia de datos
- Parser regex simple (mejora con LLM real)

## 🔐 Variables de Entorno

Crear archivo `backend/.env`:

```env
TELEGRAM_TOKEN=tu_token_de_botfather
OPENAI_API_KEY=tu_api_key_opcional
```

## 📄 Licencia

MIT - Proyecto educativo para hackathon.

## 🙏 Agradecimientos

Desarrollado durante IActivate 2025 Hackathon.
