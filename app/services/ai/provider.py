import logging

from app.config import get_settings
from app.services.ai.agno_service import AgnoService
from app.services.ai.base import AIService
from app.services.ai.mock import MockAIService

logger = logging.getLogger(__name__)


def _build_ai_service() -> AIService:
    settings = get_settings()
    if settings.ai_provider == "agno":
        logger.info("Initializing AgnoService with BigQuery tools")
        return AgnoService.from_settings(settings)
    return MockAIService()


_service: AIService = _build_ai_service()


def get_ai_service() -> AIService:
    return _service


def set_ai_service(service: AIService) -> None:
    global _service
    _service = service
