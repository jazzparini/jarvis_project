from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field


class LLMResponseSchema(BaseModel):
    intent: Literal["answer", "tool_call", "clarify", "confirm", "refuse"] = Field(
        ..., description="La intención del modelo"
    )
    message: str = Field(..., description="Mensaje explicativo o respuesta directa para el usuario")
    tool: Optional[str] = Field(default=None, description="Nombre de la herramienta a invocar si aplica")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Argumentos para la herramienta")
    risk: Literal["low", "medium", "high"] = Field(default="low", description="Nivel de riesgo de la acción")
    requires_confirmation: bool = Field(default=False, description="Indica si se requiere confirmación humana explícita")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confianza en la respuesta")
