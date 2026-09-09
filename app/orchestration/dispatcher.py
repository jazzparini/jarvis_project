import json
import structlog
from typing import Optional, Dict
from app.llm.client import get_llm_client
from app.llm.schemas import LLMResponseSchema
from app.security.auth import is_user_authorized, is_chat_authorized
from app.tools.registry import tool_registry

logger = structlog.get_logger()


class RequestOrchestrator:
    def __init__(self):
        self.llm_client = get_llm_client()
        self.pending_confirmations: Dict[int, dict] = {}

    async def handle_user_message(
        self,
        telegram_user_id: int,
        telegram_chat_id: int,
        message_text: str,
        provider: Optional[str] = None,
    ) -> str:
        log = logger.bind(user_id=telegram_user_id)

        # 1. Autorización
        if not is_user_authorized(telegram_user_id) or not is_chat_authorized(telegram_chat_id):
            log.warning("unauthorized_access_attempt")
            return "⛔ Acceso no autorizado. Tu usuario o chat no se encuentra en la lista de permisos."

        # 2. Contexto de herramientas disponibles para el prompt
        available_tools = tool_registry.list_tools()
        system_context = f"Herramientas disponibles:\n{json.dumps(available_tools, ensure_ascii=False)}"

        # 3. Invocación al LLM
        try:
            client = get_llm_client(provider) if provider else self.llm_client
            llm_response: LLMResponseSchema = await client.generate_response(
                messages=[
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": message_text},
                ]
            )
            log.info("llm_response_received", intent=llm_response.intent, tool=llm_response.tool)

            # 4. Procesamiento de intención
            if llm_response.intent == "tool_call" and llm_response.tool:
                tool = tool_registry.get(llm_response.tool)
                if not tool:
                    return f"❌ La herramienta '{llm_response.tool}' no está disponible en el catálogo."

                # Si requiere confirmación o es de riesgo alto/medio
                if tool.requires_confirmation or llm_response.requires_confirmation or tool.risk_level in ["medium", "high"]:
                    self.pending_confirmations[telegram_user_id] = {
                        "tool": tool.name,
                        "arguments": llm_response.arguments,
                    }
                    return (
                        f"⚠️ **Confirmación requerida** (Riesgo: `{tool.risk_level}`)\n"
                        f"¿Confirmas ejecutar `{tool.name}` con argumentos `{json.dumps(llm_response.arguments)}`?\n\n"
                        f"Usa `/confirm` para autorizar o `/cancel` para abortar."
                    )

                # Ejecutar herramienta directa de bajo riesgo
                result = await tool.execute(**llm_response.arguments)
                if result.success:
                    return f"⚙️ **{tool.name} ejecutado con éxito:**\n```json\n{json.dumps(result.output, indent=2)}\n```\n\n{llm_response.message}"
                else:
                    return f"❌ Error ejecutando `{tool.name}`: {result.error}"

            return llm_response.message

        except Exception as e:
            log.error("error_handling_request", error=str(e))
            return f"❌ Error procesando solicitud: {str(e)}"

    async def confirm_action(self, telegram_user_id: int) -> str:
        pending = self.pending_confirmations.pop(telegram_user_id, None)
        if not pending:
            return "ℹ️ No tienes ninguna acción pendiente de confirmación."

        tool = tool_registry.get(pending["tool"])
        if not tool:
            return "❌ Herramienta no encontrada."

        result = await tool.execute(**pending["arguments"])
        if result.success:
            return f"✅ Acción confirmada y ejecutada:\n```json\n{json.dumps(result.output, indent=2)}\n```"
        return f"❌ Error ejecutando acción: {result.error}"

    async def cancel_action(self, telegram_user_id: int) -> str:
        pending = self.pending_confirmations.pop(telegram_user_id, None)
        if not pending:
            return "ℹ️ No tienes ninguna acción pendiente de cancelación."
        return f"🚫 Acción sobre `{pending['tool']}` cancelada exitosamente."
