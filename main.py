from fastapi import FastAPI, Request, HTTPException
from app.routers import jira

app = FastAPI(title="SA Copilot API")

app.include_router(jira.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
