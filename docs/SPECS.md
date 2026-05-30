# SA Copilot API — Project Specifications

Living specification for this **MVP**. When in doubt, read this before adding code.

---

## 0. MVP mindset (read first)

This is an **MVP**, not a platform. Default to the simplest thing that works.

**Ask before abstracting:**

- Does this scope (e.g. prompts, a use case) justify more than one file?
- Will this change often enough to need a plugin/registry, or is a plain function enough?
- Am I building for a hypothetical future or for the next ticket?

**Where abstraction is warranted today:**

| Area | Why |
| --- | --- |
| `AIService` + `provider.py` | AI backend may change (mock → agno → other) |
| `mcp_plugins/` | Tools are added/removed via env; prompt travels with tool |
| Layering (router → use case → service) | Keeps webhook flow testable |

**Where to stay flat:**

| Area | Current shape |
| --- | --- |
| Prompts | Single `agno/prompts.py` (core + builder + user templates) |
| Jira use cases | One file per event, no base class |
| Config | One frozen dataclass |

Split a file only when it exceeds ~150 lines or has a second independent reason to change.

---

## 1. Purpose

FastAPI service: **Jira webhooks** → ticket context → **AI draft** for Solutions Architects
(Amplitude, Braze, Martech).

MVP scope: receive events, call AI, log results. No Jira write-back, auth, or DB yet.

---

## 2. Architecture

```
HTTP (routers) → controllers → use_cases → services → AI / MCP
```

| Layer | Does | Must not |
| --- | --- | --- |
| `routers` | Routes, validation | Business logic |
| `controllers` | Event dispatch | AI calls |
| `use_cases` | Orchestration, `AIContext` | HTTP details |
| `services` | AI contract, Agno, MCP | Webhook parsing |

### Jira flow

| Event | Use case | AI |
| --- | --- | --- |
| `jira:issue_created` | `handle_issue_created` | `generate_response(ctx, "priority")` |
| `jira:issue_updated` | `handle_issue_updated` | `analyze(ctx, "sentiment")` |
| `comment_created` | `handle_comment_created` | `generate_response(ctx, comment)` |

`main.py` lifespan: `get_ai_service().setup()` / `teardown()` for MCP.

---

## 3. AI layer

### Contract (`AIService`)

- `setup()` / `teardown()` — optional
- `generate_response(context, prompt) -> AIResponse`
- `analyze(context, analysis_type) -> AIAnalysis`

DTOs: `app/services/ai/schemas.py`. Provider switch: `AI_PROVIDER=mock|agno`.

### Agno (`AgnoService`)

Two agents, created **once**, reused:

- **Response agent** — MCP tools, markdown output
- **Analysis agent** — no tools, `output_schema=AnalysisOutput`

---

## 4. MCP plugins

Tool + prompt live together. Core prompts never mention specific tool names.

```
mcp_plugins/
├── plugin.py          # McpPluginDefinition dataclass only
├── registry.py        # MCP_PLUGINS tuple + build_mcp_tools()
├── amplitude_docs.py  # PLUGIN export
└── braze_docs.py
```

Add a plugin: new file + register in `MCP_PLUGINS` + env flag. Disable via env removes tool and prompt.

| Plugin | Env | Prefix |
| --- | --- | --- |
| Amplitude Docs | `MCP_DOCS_ENABLED` | `amplitude_docs_*` |
| Braze (Context7) | `BRAZE_DOCS_MCP_ENABLED` | `braze_docs_*` |

---

## 5. Prompts

Single file: `app/services/ai/agno/prompts.py`

- **Core fragments** — role, governance, response rules (no tool names)
- **`build_agent_instructions(settings)`** — core + enabled plugin blocks
- **`TicketResponsePrompt` / `TicketAnalysisPrompt`** — user-side task, context, budget

Plugin-specific instructions stay in each `mcp_plugins/*.py`.

### Prompt rules (compact)

1. Skip tools when ticket context is enough
2. When/when-not per tool → in plugin module
3. Sequential tool paths, not parallel
4. Doc queries in English; SA response in ticket language
5. Stop after one useful doc fetch; no tool mentions in SA output

### Amplitude paths

| Path | Steps |
| --- | --- |
| A | `search_docs` → `get_page` |
| B | `list_pages` → `get_page` (when search empty) |
| C | `search_docs` → `list_pages` → `get_page` |

Keywords: 2-4 English words. G&S → engagement/surveys.

---

## 6. Configuration

| Variable | Default |
| --- | --- |
| `LOG_LEVEL` | `INFO` |
| `AI_PROVIDER` | `mock` |
| `ANTHROPIC_API_KEY` / `CLAUDE_DEV_API_KEY` | — |
| `CLAUDE_MODEL_ID` | `claude-3-5-haiku-20241022` |
| `AGENT_MAX_TOOL_CALLS` | `3` |
| `MCP_DOCS_ENABLED` | `true` |
| `BRAZE_DOCS_MCP_ENABLED` | `true` |
| `MCP_TIMEOUT_SECONDS` | `30` |

---

## 7. Code standards

- Python 3.11+, FastAPI, Pydantic v2, Ruff (100 cols)
- Minimal diffs; no new layers without reason
- No secrets in git; no emojis in logs

---

## 8. Logging

- Summarize `run.tools` instead of dumping full `RunOutput`
- `debug_mode=False` on agents in normal use
- Silence `httpcore`, `httpx`, `mcp` at WARNING

---

## 9. Extension checklist

**New Jira event:** use case file + controller branch + `AIContext`

**New AI provider:** subclass `AIService`, register in `provider.py`

**New MCP plugin:** one file in `mcp_plugins/` + registry + env flag

**Do not add (MVP):** DB, Jira write-back, webhook auth, Agno Team/Workflow, agents in loops

---

## 10. Key paths

```
main.py
app/config.py
app/controllers/jira.py
app/use_cases/jira/
app/services/ai/base.py
app/services/ai/provider.py
app/services/ai/agno/service.py
app/services/ai/agno/prompts.py
app/services/ai/agno/mcp_plugins/
docs/SPECS.md
.cursor/skills/sa-copilot-api/SKILL.md
.cursor/skills/critique-sa-copilot/SKILL.md
```