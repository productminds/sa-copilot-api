from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class AIContext(BaseModel):
    issue_key: str | None = None
    summary: str | None = None
    description: str | None = None
    comments: list[str] = []
    metadata: dict[str, Any] = {}


class AIResponse(BaseModel):
    content: str
    model: str
    usage: dict[str, int] = {}


class AIAnalysis(BaseModel):
    analysis_type: str
    result: dict[str, Any]
    confidence: float
    model: str


class AIService(ABC):
    @abstractmethod
    async def generate_response(self, context: AIContext, prompt: str) -> AIResponse: ...

    @abstractmethod
    async def analyze(self, context: AIContext, analysis_type: str) -> AIAnalysis: ...
