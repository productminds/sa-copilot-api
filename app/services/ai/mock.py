import random
from collections.abc import Callable
from typing import Any

from .base import AIService
from .schemas import AIAnalysis, AIContext, AIResponse

_MODEL = "mock-ai-v1"

_RESPONSE_TEMPLATES = [
    "Based on {key} — {summary} — I recommend addressing this promptly with the relevant team.",
    "Reviewing {key}: '{summary}'. The context suggests a clear resolution path is available.",
    "For {key}, this looks actionable. Suggest triaging '{summary}' in the next sprint.",
]

_ANALYSIS_HANDLERS: dict[str, Callable[[AIContext], dict[str, Any]]] = {
    "sentiment": lambda ctx: {
        "sentiment": "neutral",
        "score": 0.5,
        "signals": ["no strong sentiment detected in mock mode"],
    },
    "priority": lambda ctx: {
        "recommended_priority": "medium",
        "reasoning": (
            f"Issue {ctx.issue_key} assessed as medium priority. "
            f"Summary: '{ctx.summary or 'N/A'}'. No urgent keywords detected."
        ),
    },
    "summary": lambda ctx: {
        "brief": ctx.summary or "No summary available.",
        "key_points": [
            ctx.description[:120].strip() + "..." if ctx.description else "No description.",
        ],
        "comment_count": len(ctx.comments),
    },
    "action_items": lambda ctx: {
        "items": [
            f"Review and triage {ctx.issue_key}",
            "Assign to the appropriate team member",
            "Set a target resolution date",
            "Notify stakeholders if high-impact",
        ]
    },
}


class MockAIService(AIService):
    async def generate_response(self, context: AIContext, prompt: str) -> AIResponse:
        template = random.choice(_RESPONSE_TEMPLATES)
        content = template.format(
            key=context.issue_key or "N/A",
            summary=context.summary or "no summary",
        )
        if prompt:
            truncated = prompt[:80] + ("..." if len(prompt) > 80 else "")
            content = f"{content}\n\nRegarding: '{truncated}' — further investigation recommended."
        return AIResponse(
            content=content,
            model=_MODEL,
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(content.split()),
            },
        )

    async def analyze(self, context: AIContext, analysis_type: str) -> AIAnalysis:
        handler = _ANALYSIS_HANDLERS.get(analysis_type)
        if handler is None:
            return AIAnalysis(
                analysis_type=analysis_type,
                result={"error": f"unsupported analysis type: '{analysis_type}'"},
                confidence=0.0,
                model=_MODEL,
            )
        return AIAnalysis(
            analysis_type=analysis_type,
            result=handler(context),
            confidence=0.85,
            model=_MODEL,
        )
