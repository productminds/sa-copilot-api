from fastapi import APIRouter, Request
from app.controllers import handle_webhook

router = APIRouter(prefix="/webhooks/jira", tags=["jira"])


@router.post("")
async def jira_webhook(payload: JiraWebhookPayload):
    return await handle_webhook(payload)
