import structlog
from app.config import settings

logger = structlog.get_logger()


def is_user_authorized(telegram_user_id: int) -> bool:
    allowed = settings.allowed_users
    if not allowed:
        # Si la lista está vacía en development, loguear advertencia
        logger.warning("No allowed users configured in TELEGRAM_ALLOWED_USER_IDS")
        return False
    return telegram_user_id in allowed


def is_chat_authorized(telegram_chat_id: int) -> bool:
    allowed = settings.allowed_chats
    if not allowed:
        return True  # Si no se restringen chats específicos, permitir chats de usuarios autorizados
    return telegram_chat_id in allowed
