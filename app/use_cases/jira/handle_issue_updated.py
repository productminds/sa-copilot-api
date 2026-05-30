import logging

from app.models import JiraWebhookPayload
from app.services.ai import AIContext, get_ai_service

logger = logging.getLogger(__name__)


async def execute(payload: JiraWebhookPayload) -> None:
    issue = payload.issue
    logger.info("Issue updated: %s", issue.key if issue else "unknown")

    if not issue:
        return

    context = AIContext(
        issue_key=issue.key,
        summary=issue.fields.get("summary"),
        description=issue.fields.get("description"),
        metadata={"changelog": payload.changelog or {}},
    )
    analysis = await get_ai_service().analyze(context, "sentiment")
    logger.debug("[DEBUG] - AI sentiment analysis for %s (confidence=%.2f): %s", issue.key, analysis.confidence, analysis.result)
