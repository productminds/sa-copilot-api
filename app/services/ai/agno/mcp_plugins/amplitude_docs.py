from agno.tools.mcp import MCPTools

from app.config import Settings
from app.services.ai.agno.mcp_plugins.plugin import McpPluginDefinition

INSTRUCTIONS = """\
## amplitude_docs_*
English only. Skip if ticket is answerable without docs.
- search_docs: 2-4 English keywords (e.g. `engagement surveys`). Map product names
  (Guides & Surveys -> engagement/surveys). Zero results -> list_pages, do not rephrase.
- list_pages: when search fails or slug unknown. Pick one slug, then get_page.
- get_page: full markdown; requires exact slug from search or list_pages.
Paths: search->get | list->get | search->list->get. Sequential only."""

BUDGET_HINT = "Amplitude: if search_docs empty, use list_pages then get_page."


def _is_enabled(settings: Settings) -> bool:
    return settings.mcp_docs_enabled


def _build_tool(settings: Settings) -> MCPTools:
    return MCPTools(
        url=settings.amplitude_docs_mcp_url,
        transport="streamable-http",
        timeout_seconds=settings.mcp_timeout_seconds,
        tool_name_prefix="amplitude_docs",
    )


PLUGIN = McpPluginDefinition(
    id="amplitude_docs",
    prefix="amplitude_docs",
    is_enabled=_is_enabled,
    build_tool=_build_tool,
    instructions=INSTRUCTIONS,
    budget_hint=BUDGET_HINT,
)
