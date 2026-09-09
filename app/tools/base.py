import abc
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    success: bool
    output: Any
    error: Optional[str] = None


class BaseTool(abc.ABC):
    name: str
    description: str
    risk_level: Literal["low", "medium", "high"] = "low"
    requires_confirmation: bool = False

    @abc.abstractmethod
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Retorna el esquema JSON de los parámetros que requiere la herramienta."""
        pass

    @abc.abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Ejecuta la herramienta de forma asíncrona y segura."""
        pass
