# JARVIS 🤖

Asistente operativo conversacional seguro para Telegram.

## 🚀 Puesta en marcha rápida

### 1. Requisitos
- Python 3.11+
- Token de Bot de Telegram (obtenido con [@BotFather](https://t.me/BotFather))
- API Key de Gemini (`GEMINI_API_KEY`) y/o Anthropic (`ANTHROPIC_API_KEY`)

### 2. Instalación de dependencias
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -e .
```

### 3. Configuración
Copia el archivo `.env.example` a `.env` y completa tus credenciales:
```bash
cp .env.example .env
```
Asegúrate de colocar tu ID de usuario de Telegram en `TELEGRAM_ALLOWED_USER_IDS` para tener acceso autorizado.

### 4. Ejecución
```bash
python -m app.main
```
