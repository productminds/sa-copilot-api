from pydantic import BaseModel
from typing import Any, Optional


class JiraUser(BaseModel):
    accountId: Optional[str] = None
    displayName: Optional[str] = None
    emailAddress: Optional[str] = None


class JiraIssue(BaseModel):
    id: str
    key: str
    fields: dict[str, Any] = {}


class JiraWebhookPayload(BaseModel):
    webhookEvent: str
    timestamp: Optional[int] = None
    issue: Optional[JiraIssue] = None
    user: Optional[JiraUser] = None
    changelog: Optional[dict[str, Any]] = None
    comment: Optional[dict[str, Any]] = None
