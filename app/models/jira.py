from pydantic import BaseModel
from typing import Any


class JiraUser(BaseModel):
    accountId: str | None = None
    displayName: str | None = None
    emailAddress: str | None = None


class JiraIssue(BaseModel):
    id: str
    key: str
    fields: dict[str, Any] = {}


class JiraWebhookPayload(BaseModel):
    webhookEvent: str
    timestamp: int | None = None
    issue: JiraIssue | None = None
    user: JiraUser | None = None
    changelog: dict[str, Any] | None = None
    comment: dict[str, Any] | None = None
