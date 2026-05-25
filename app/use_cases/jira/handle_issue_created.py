import logging
from app.models import JiraWebhookPayload
from app.services.ai import get_ai_service, AIContext

logger = logging.getLogger(__name__)


async def execute(payload: JiraWebhookPayload) -> None:
    issue = payload.issue
    logger.info("Issue created: %s", issue.key if issue else "unknown")

    if not issue:
        return

    context = AIContext(
        issue_key=issue.key,
        summary=issue.fields.get("summary"),
        description=issue.fields.get("description"),
    )
    analysis = await get_ai_service().analyze(context, "priority")
    logger.info("AI priority analysis for %s (confidence=%.2f): %s", issue.key, analysis.confidence, analysis.result)
