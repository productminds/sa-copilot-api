from collections.abc import Callable
from dataclasses import dataclass

from agno.tools.mcp import MCPTools

from app.config import Settings


@dataclass(frozen=True)
class McpPluginDefinition:
    """MCP tool factory + prompt fragment. One module per plugin."""

    id: str
    prefix: str
    is_enabled: Callable[[Settings], bool]
    build_tool: Callable[[Settings], MCPTools]
    instructions: str
    budget_hint: str | None = None
