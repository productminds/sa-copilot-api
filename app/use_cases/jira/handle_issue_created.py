import logging

from app.models import JiraWebhookPayload
from app.services.ai import AIContext, get_ai_service

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
    response = await get_ai_service().generate_response(context, "priority")
    logger.info("AI priority analysis for %s (model=%s): %s", issue.key, response.model, response.content)
