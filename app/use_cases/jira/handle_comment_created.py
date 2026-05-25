import logging
from app.models import JiraWebhookPayload
from app.services.ai import get_ai_service, AIContext

logger = logging.getLogger(__name__)


async def execute(payload: JiraWebhookPayload) -> None:
    issue = payload.issue
    logger.info("Comment added to: %s", issue.key if issue else "unknown")

    if not issue or not payload.comment:
        return

    comment_body = payload.comment.get("body", "")
    context = AIContext(
        issue_key=issue.key,
        summary=issue.fields.get("summary"),
        description=issue.fields.get("description"),
        comments=[comment_body],
    )
    response = await get_ai_service().generate_response(context, comment_body)
    logger.info("AI suggested response for %s (model=%s): %s", issue.key, response.model, response.content)
