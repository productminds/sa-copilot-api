import logging

from fastapi import FastAPI

from app.config import get_settings
from app.routers import jira

logging.basicConfig(level=get_settings().log_level)

app = FastAPI(title="SA Copilot API")

app.include_router(jira.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
