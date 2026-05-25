import logging
from app.models import JiraWebhookPayload

logger = logging.getLogger(__name__)


async def execute(payload: JiraWebhookPayload) -> None:
    issue = payload.issue
    logger.info("Comment added to: %s", issue.key if issue else "unknown")
