from typing import Any

from pydantic import BaseModel


class AnalysisOutput(BaseModel):
    """Structured output schema returned by the analysis agent."""

    result: dict[str, Any]
    confidence: float
