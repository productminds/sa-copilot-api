from agno.tools.mcp import MCPTools

from app.config import Settings
from app.services.ai.agno.mcp_plugins.amplitude_docs import PLUGIN as AMPLITUDE_DOCS
from app.services.ai.agno.mcp_plugins.braze_docs import PLUGIN as BRAZE_DOCS
from app.services.ai.agno.mcp_plugins.plugin import McpPluginDefinition

MCP_PLUGINS: tuple[McpPluginDefinition, ...] = (
    AMPLITUDE_DOCS,
    BRAZE_DOCS,
)


def get_enabled_plugins(settings: Settings) -> list[McpPluginDefinition]:
    return [plugin for plugin in MCP_PLUGINS if plugin.is_enabled(settings)]


def build_mcp_tools(settings: Settings) -> list[MCPTools]:
    return [plugin.build_tool(settings) for plugin in get_enabled_plugins(settings)]
