import logging

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.run.agent import RunOutput

from app.config import Settings, get_settings
from app.services.ai.agno.prompts import (
    ANALYSIS_INSTRUCTIONS,
    TicketAnalysisPrompt,
    TicketResponsePrompt,
    build_agent_instructions,
)
from app.services.ai.agno.run import usage_from_run
from app.services.ai.agno.schemas import AnalysisOutput
from app.services.ai.agno.mcp_plugins import build_mcp_tools
from app.services.ai.base import AIService
from app.services.ai.schemas import AIAnalysis, AIContext, AIResponse
from app.utils.content import content_to_str

logger = logging.getLogger(__name__)


class AgnoService(AIService):
    """Agno implementation of the AIService contract.

    Adds MCP-backed documentation tools and structured analysis on top of the
    standard `setup`/`teardown` lifecycle defined by `AIService`.
    """

    def __init__(
        self,
        *,
        anthropic_api_key: str,
        model_id: str,
        max_tool_calls: int,
        settings: Settings,
    ) -> None:
        self._model_id = model_id
        self._max_tool_calls = max_tool_calls
        self._settings = settings
        self._mcp_tools = build_mcp_tools(settings)

        self._agent = Agent(
            name="SA Copilot Agent",
            model=Claude(id=model_id, api_key=anthropic_api_key),
            tools=self._mcp_tools,
            instructions=build_agent_instructions(settings),
            tool_call_limit=max_tool_calls,
            markdown=True,
            debug_mode=True,
        )

        self._analysis_agent = Agent(
            name="SA Copilot Analysis Agent",
            model=Claude(id=model_id, api_key=anthropic_api_key),
            instructions=ANALYSIS_INSTRUCTIONS,
            output_schema=AnalysisOutput,
            debug_mode=False,
        )

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "AgnoService":
        settings = settings or get_settings()
        if not settings.anthropic_api_key:
            raise ValueError("AgnoService requires ANTHROPIC_API_KEY or CLAUDE_DEV_API_KEY")

        return cls(
            anthropic_api_key=settings.anthropic_api_key,
            model_id=settings.claude_model_id,
            max_tool_calls=settings.agent_max_tool_calls,
            settings=settings,
        )

    async def setup(self) -> None:
        for tool in self._mcp_tools:
            try:
                await tool.connect()
                logger.debug("[DEBUG] - Connected MCP (prefix=%s)", tool.tool_name_prefix)
            except Exception:
                logger.exception("Failed to connect MCP (prefix=%s)", tool.tool_name_prefix)

    async def teardown(self) -> None:
        for tool in self._mcp_tools:
            try:
                await tool.close()
                logger.debug("[DEBUG] - Closed MCP (prefix=%s)", tool.tool_name_prefix)
            except Exception:
                logger.exception("Failed to close MCP (prefix=%s)", tool.tool_name_prefix)

    async def generate_response(self, context: AIContext, prompt: str) -> AIResponse:
        run = await self._arun(
            self._agent,
            TicketResponsePrompt(
                context, prompt, self._max_tool_calls, settings=self._settings
            ).render(),
        )
        return AIResponse(
            content=content_to_str(run.content),
            model=self._model_id,
            usage=usage_from_run(run),
        )

    async def analyze(self, context: AIContext, analysis_type: str) -> AIAnalysis:
        run = await self._arun(
            self._analysis_agent, TicketAnalysisPrompt(context, analysis_type).render()
        )
        output = run.content
        if not isinstance(output, AnalysisOutput):
            raise TypeError(f"Expected AnalysisOutput, got {type(output)}")

        return AIAnalysis(
            analysis_type=analysis_type,
            result=output.result,
            confidence=output.confidence,
            model=self._model_id,
        )

    async def _arun(self, agent: Agent, prompt: str) -> RunOutput:
        try:
            run = await agent.arun(input=prompt)
        except Exception:
            logger.exception("Agno agent run failed (agent=%s)", agent.name)
            raise

        if not isinstance(run, RunOutput):
            raise TypeError("Expected RunOutput from agent.arun()")
        return run
