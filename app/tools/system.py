from datetime import datetime
import platform
import psutil
from typing import Any, Dict
from app.tools.base import BaseTool, ToolResult


class SystemInfoTool(BaseTool):
    name = "system_info"
    description = "Obtiene métricas básicas y estado del sistema (CPU, memoria, disco y OS)."
    risk_level = "low"
    requires_confirmation = False

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        }

    async def execute(self, **kwargs) -> ToolResult:
        try:
            cpu_usage = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            info = {
                "os": platform.platform(),
                "cpu_percent": cpu_usage,
                "memory_used_percent": mem.percent,
                "memory_available_gb": round(mem.available / (1024**3), 2),
                "disk_used_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "timestamp": datetime.utcnow().isoformat(),
            }
            return ToolResult(success=True, output=info)
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))
