import pytest
from app.orchestration.scheduler import TaskScheduler


def test_scheduler_add_and_list_jobs():
    sched = TaskScheduler()
    sched.add_cron_job(
        task_id="daily_system_check",
        chat_id=123456789,
        tool_name="system_info",
        cron_expr="0 9 * * *",
    )

    jobs = sched.list_jobs()
    assert len(jobs) == 1
    assert jobs[0]["id"] == "daily_system_check"
    assert "cron" in jobs[0]["trigger"]
