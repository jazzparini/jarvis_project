import json
import structlog
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

from app.config import settings
from app.tools.registry import tool_registry

logger = structlog.get_logger()


class TaskScheduler:
    def __init__(self, bot: Bot = None):
        self.scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)
        self.bot = bot

    def set_bot(self, bot: Bot):
        self.bot = bot

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("task_scheduler_started", timezone=settings.TIMEZONE)

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("task_scheduler_stopped")

    def add_cron_job(
        self,
        task_id: str,
        chat_id: int,
        tool_name: str,
        cron_expr: str,
        arguments: dict = None,
    ):
        """Agrega un job con expresión cron (ej: '*/30 * * * *' o 5 campos)."""
        args = arguments or {}

        async def _job():
            logger.info("executing_scheduled_task", task_id=task_id, tool_name=tool_name)
            tool = tool_registry.get(tool_name)
            if not tool:
                logger.error("scheduled_task_tool_not_found", tool_name=tool_name)
                return

            result = await tool.execute(**args)
            if self.bot and chat_id:
                status_emoji = "✅" if result.success else "❌"
                msg = (
                    f"⏰ **Reporte Programado: `{task_id}`**\n"
                    f"Herramienta: `{tool_name}` {status_emoji}\n\n"
                    f"```json\n{json.dumps(result.output or result.error, indent=2)}\n```"
                )
                try:
                    await self.bot.send_message(chat_id=chat_id, text=msg)
                except Exception as e:
                    logger.error("error_sending_scheduled_notification", error=str(e))

        # Soporte para formato estándar de 5 campos de cron
        parts = cron_expr.strip().split()
        if len(parts) == 5:
            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
                timezone=settings.TIMEZONE,
            )
        else:
            trigger = CronTrigger.from_crontab(cron_expr, timezone=settings.TIMEZONE)

        self.scheduler.add_job(_job, trigger=trigger, id=task_id, replace_existing=True)
        logger.info("cron_job_scheduled", task_id=task_id, cron_expr=cron_expr)

    def list_jobs(self):
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        return jobs


task_scheduler = TaskScheduler()
