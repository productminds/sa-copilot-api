from app.services.ai.base import AIService
from app.services.ai.mock import MockAIService

_service: AIService = MockAIService()


def get_ai_service() -> AIService:
    return _service


def set_ai_service(service: AIService) -> None:
    global _service
    _service = service
