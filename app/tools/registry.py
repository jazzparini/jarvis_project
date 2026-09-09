import structlog
from typing import Dict, List, Optional
from app.tools.base import BaseTool
from app.tools.system import SystemInfoTool

logger = structlog.get_logger()


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        # Registrar herramientas integradas por defecto
        self.register(SystemInfoTool())

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            logger.warning("overwriting_tool", tool_name=tool.name)
        self._tools[tool.name] = tool
        logger.info("tool_registered", tool_name=tool.name, risk_level=tool.risk_level)

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "risk_level": tool.risk_level,
                "requires_confirmation": tool.requires_confirmation,
                "parameters": tool.get_parameters_schema(),
            }
            for tool in self._tools.values()
        ]


tool_registry = ToolRegistry()
