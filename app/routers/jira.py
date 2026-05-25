from fastapi import APIRouter
from app.controllers import handle_webhook
from app.models import JiraWebhookPayload

router = APIRouter(prefix="/webhooks/jira", tags=["jira"])


@router.post("")
async def jira_webhook(payload: JiraWebhookPayload):
    return await handle_webhook(payload)
