import asyncio
import structlog
from app.config import settings
from app.storage.database import init_db
from app.telegram.bot import create_bot_app
from app.orchestration.scheduler import task_scheduler

logger = structlog.get_logger()


async def main():
    logger.info("starting_jarvis", env=settings.APP_ENV)
    
    # 1. Inicializar base de datos
    logger.info("initializing_database")
    await init_db()

    # 2. Inicializar Bot de Telegram
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("missing_telegram_token", msg="Por favor define TELEGRAM_BOT_TOKEN en tu archivo .env")
        return

    bot_app = create_bot_app()

    # 3. Inicializar y enlazar Scheduler
    task_scheduler.set_bot(bot_app.bot)
    task_scheduler.start()

    logger.info("bot_polling_started")
    try:
        await bot_app.run_polling()
    finally:
        task_scheduler.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("jarvis_shutdown_cleanly")
