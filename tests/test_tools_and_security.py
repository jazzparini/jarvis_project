import pytest
from app.tools.registry import tool_registry
from app.tools.system import SystemInfoTool
from app.security.auth import is_user_authorized
from app.config import settings


def test_tool_registry_has_system_info():
    tool = tool_registry.get("system_info")
    assert tool is not None
    assert isinstance(tool, SystemInfoTool)
    assert tool.risk_level == "low"


@pytest.mark.asyncio
async def test_system_info_tool_execution():
    tool = SystemInfoTool()
    result = await tool.execute()
    assert result.success is True
    assert "cpu_percent" in result.output
    assert "memory_used_percent" in result.output


def test_user_authorization():
    settings.TELEGRAM_ALLOWED_USER_IDS = "111,222"
    assert is_user_authorized(111) is True
    assert is_user_authorized(222) is True
    assert is_user_authorized(999) is False
