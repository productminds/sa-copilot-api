import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    log_level: str
    ai_provider: str
    anthropic_api_key: str | None
    claude_model_id: str
    agent_max_tool_calls: int
    mcp_docs_enabled: bool
    amplitude_docs_mcp_url: str
    braze_docs_mcp_enabled: bool
    braze_docs_context7_command: str
    mcp_timeout_seconds: int


@lru_cache
def get_settings() -> Settings:
    return Settings(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        ai_provider=os.getenv("AI_PROVIDER", "mock").lower(),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_DEV_API_KEY"),
        claude_model_id=os.getenv("CLAUDE_MODEL_ID", "claude-3-5-haiku-20241022"),
        agent_max_tool_calls=int(os.getenv("AGENT_MAX_TOOL_CALLS", "3")),
        mcp_docs_enabled=os.getenv("MCP_DOCS_ENABLED", "true").lower() == "true",
        amplitude_docs_mcp_url=os.getenv(
            "AMPLITUDE_DOCS_MCP_URL",
            "https://amplitude.com/docs/api/mcp",
        ),
        braze_docs_mcp_enabled=os.getenv("BRAZE_DOCS_MCP_ENABLED", "true").lower() == "true",
        braze_docs_context7_command=os.getenv(
            "BRAZE_DOCS_CONTEXT7_COMMAND",
            "npx -y @upstash/context7-mcp@latest",
        ),
        mcp_timeout_seconds=int(os.getenv("MCP_TIMEOUT_SECONDS", "30")),
    )
