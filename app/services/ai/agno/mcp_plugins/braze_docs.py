from agno.tools.mcp import MCPTools

from app.config import Settings
from app.services.ai.agno.mcp_plugins.plugin import McpPluginDefinition

INSTRUCTIONS = """\
## braze_docs_* (Context7)
Braze tickets only. Never mix with amplitude_docs in the same request.
resolve-library-id (libraryName: braze) -> query-docs (libraryId + short English query)."""

BUDGET_HINT = "Braze: resolve-library-id before query-docs."


def _is_enabled(settings: Settings) -> bool:
    return settings.braze_docs_mcp_enabled


def _build_tool(settings: Settings) -> MCPTools:
    return MCPTools(
        command=settings.braze_docs_context7_command,
        transport="stdio",
        timeout_seconds=settings.mcp_timeout_seconds,
        tool_name_prefix="braze_docs",
    )


PLUGIN = McpPluginDefinition(
    id="braze_docs",
    prefix="braze_docs",
    is_enabled=_is_enabled,
    build_tool=_build_tool,
    instructions=INSTRUCTIONS,
    budget_hint=BUDGET_HINT,
)
