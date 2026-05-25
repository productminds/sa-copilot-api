import logging
from app.models import JiraWebhookPayload
from app.use_cases.jira import (
    handle_issue_created,
    handle_issue_updated,
    handle_comment_created,
)

logger = logging.getLogger(__name__)


async def handle_webhook(payload: JiraWebhookPayload) -> dict:
    logger.info("Received Jira event: %s", payload.webhookEvent)

    if payload.webhookEvent == "jira:issue_created":
        await handle_issue_created.execute(payload)
    elif payload.webhookEvent == "jira:issue_updated":
        await handle_issue_updated.execute(payload)
    elif payload.webhookEvent == "comment_created":
        await handle_comment_created.execute(payload)
    else:
        logger.debug("Unhandled event type: %s", payload.webhookEvent)

    return {"received": True, "event": payload.webhookEvent}
