import structlog
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from app.config import settings
from app.orchestration.dispatcher import RequestOrchestrator
from app.orchestration.scheduler import task_scheduler
from app.tools.registry import tool_registry

logger = structlog.get_logger()
orchestrator = RequestOrchestrator()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hola {user.first_name}. Soy **JARVIS**, tu asistente operativo seguro.\n\n"
        "Comandos disponibles:\n"
        "/help - Lista de capacidades y herramientas\n"
        "/status - Estado del sistema y métricas\n"
        "/tasks - Tareas programadas activas\n"
        "/confirm - Confirmar acción pendiente\n"
        "/cancel - Cancelar acción pendiente"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tools = tool_registry.list_tools()
    tools_desc = "\n".join([f"- `{t['name']}`: {t['description']} (Riesgo: {t['risk_level']})" for t in tools])
    await update.message.reply_text(
        f"🛠 **JARVIS - Capacidades**\n\n"
        f"**Herramientas registradas:**\n{tools_desc}\n\n"
        f"Escribe cualquier mensaje de consulta u orden para que JARVIS la gestione."
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = task_scheduler.list_jobs()
    await update.message.reply_text(
        f"🟢 **JARVIS Estado:** Operacional\n"
        f"- Entorno: `{settings.APP_ENV}`\n"
        f"- Proveedor LLM: `{settings.DEFAULT_LLM_PROVIDER}`\n"
        f"- Modelo Gemini: `{settings.GEMINI_MODEL}`\n"
        f"- Modelo Anthropic: `{settings.ANTHROPIC_MODEL}`\n"
        f"- Herramientas activas: `{len(tool_registry.list_tools())}`\n"
        f"- Tareas programadas (cron): `{len(jobs)}`"
    )


async def tasks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = task_scheduler.list_jobs()
    if not jobs:
        await update.message.reply_text("📋 No hay tareas programadas activas.")
        return

    text = "📋 **Tareas Programadas Activas:**\n\n"
    for j in jobs:
        text += f"- **ID:** `{j['id']}`\n  Trigger: `{j['trigger']}`\n  Próxima ejecución: `{j['next_run_time'] or 'N/A'}`\n\n"
    await update.message.reply_text(text)


async def confirm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = await orchestrator.confirm_action(update.effective_user.id)
    await update.message.reply_text(res)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = await orchestrator.cancel_action(update.effective_user.id)
    await update.message.reply_text(res)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text

    response = await orchestrator.handle_user_message(
        telegram_user_id=user_id,
        telegram_chat_id=chat_id,
        message_text=text,
    )
    await update.message.reply_text(response)


def create_bot_app():
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN no configurado.")
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("tasks", tasks_command))
    app.add_handler(CommandHandler("confirm", confirm_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    return app
