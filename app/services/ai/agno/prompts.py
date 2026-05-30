import json
from dataclasses import dataclass

from app.config import Settings, get_settings
from app.services.ai.agno.mcp_plugins.registry import get_enabled_plugins
from app.services.ai.schemas import AIContext

# --- Core system prompt fragments (tool-agnostic) ---

_ROLE = """\
## Role
SA Copilot - brief Jira guidance for Solutions Architects (Amplitude, Braze, Martech)."""

_OBJECTIVE = """\
## Objective
Fast, actionable draft. Prefer ticket context."""

_TOOL_GOVERNANCE = """\
## Tools
Use docs MCP only for official SDK/API/product guidance. One MCP family per request.
Max one page/doc fetch. Stop when you have enough. Under 250 words unless SA asks detail."""

_RESPONSE_RULES = """\
## Response
Same language as ticket/SA request. One doc URL/title or N/A. No mention of tools/MCP."""

ANALYSIS_INSTRUCTIONS = """\
Structured Jira analysis. Return JSON for analysis_type using ticket context only.
Types: sentiment | priority | summary | action_items.
Same language as ticket. confidence 0.0-1.0 from context completeness. No external tools."""

_RESPONSE_OUTPUT_FORMAT = (
    "1-3 short lines per section. Headings:\n"
    "- Summary: issue + client need\n"
    "- Likely cause: one hypothesis; mark uncertainty\n"
    "- Next steps: max 3 numbered actions\n"
    "- Doc reference: one URL/title or N/A\n"
    "- Open questions: max 2 bullets or N/A"
)


def build_agent_instructions(settings: Settings) -> str:
    """Core rules + enabled MCP plugin prompt blocks."""
    sections = [_ROLE, _OBJECTIVE]
    enabled = get_enabled_plugins(settings)
    if enabled:
        sections.append(_TOOL_GOVERNANCE)
        sections.extend(plugin.instructions for plugin in enabled)
    sections.append(_RESPONSE_RULES)
    return "\n\n".join(sections)


def build_tool_budget_hint(max_tool_calls: int, settings: Settings) -> str:
    base = f"Max {max_tool_calls} tool calls. Prefer 0-2."
    hints = [p.budget_hint for p in get_enabled_plugins(settings) if p.budget_hint]
    return f"{base} {' '.join(hints)}" if hints else base


def _render_sections(sections: dict[str, str]) -> str:
    return "\n\n".join(
        f"## {title}\n{body.strip()}" for title, body in sections.items() if body.strip()
    )


def _format_ticket_context(context: AIContext) -> str:
    scalar_fields = {
        "Issue key": context.issue_key,
        "Summary": context.summary,
        "Description": context.description,
    }
    parts = [f"{label}: {value}" for label, value in scalar_fields.items() if value]
    if context.comments:
        parts.append("Comments:\n" + "\n".join(f"- {c}" for c in context.comments))
    if context.metadata:
        parts.append(f"Metadata: {json.dumps(context.metadata, ensure_ascii=False)}")
    return "\n".join(parts) if parts else "No ticket fields provided."


@dataclass(frozen=True)
class TicketResponsePrompt:
    """User prompt for drafting a full SA response to a ticket."""

    context: AIContext
    user_request: str
    max_tool_calls: int = 3
    settings: Settings | None = None

    def render(self) -> str:
        settings = self.settings or get_settings()
        return _render_sections(
            {
                "Task": (
                    "Draft a short SA response. Docs MCP only if official guidance needed. "
                    "Same language as ticket."
                ),
                "Ticket context": _format_ticket_context(self.context),
                "SA request": (
                    self.user_request.strip() or "Analyze the ticket and draft a brief response."
                ),
                "Tool budget": build_tool_budget_hint(self.max_tool_calls, settings),
                "Output format": _RESPONSE_OUTPUT_FORMAT,
            }
        )


@dataclass(frozen=True)
class TicketAnalysisPrompt:
    """User prompt for a structured analysis of a ticket."""

    context: AIContext
    analysis_type: str

    def render(self) -> str:
        return _render_sections(
            {
                "Task": f"Run '{self.analysis_type}' analysis on the ticket below.",
                "Ticket context": _format_ticket_context(self.context),
                "Analysis type": self.analysis_type,
            }
        )
