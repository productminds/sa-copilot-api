import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.routers import jira
from app.services.ai import get_ai_service

logging.basicConfig(level=get_settings().log_level)

for name in ('httpcore', 'httpx', 'mcp', 'watchfiles'):
    logging.getLogger(name).setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    service = get_ai_service()
    try:
        await service.setup()
        yield
    finally:
        await service.teardown()


app = FastAPI(title="SA Copilot API", lifespan=lifespan)

app.include_router(jira.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
