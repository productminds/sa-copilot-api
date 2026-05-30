from abc import ABC, abstractmethod

from app.services.ai.schemas import AIAnalysis, AIContext, AIResponse


class AIService(ABC):
    """Standard contract every AI provider must implement.

    Lifecycle hooks (`setup`/`teardown`) are optional and default to no-ops,
    so providers without external resources don't need to override them.
    Providers like Agno override them to manage tool connections.
    """

    async def setup(self) -> None:
        """Acquire external resources at application startup. No-op by default."""
        return None

    async def teardown(self) -> None:
        """Release external resources at application shutdown. No-op by default."""
        return None

    @abstractmethod
    async def generate_response(self, context: AIContext, prompt: str) -> AIResponse: ...

    @abstractmethod
    async def analyze(self, context: AIContext, analysis_type: str) -> AIAnalysis: ...
