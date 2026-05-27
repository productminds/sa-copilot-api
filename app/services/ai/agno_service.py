import logging

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.run.agent import RunOutput
from agno.tools.google.bigquery import GoogleBigQueryTools

from app.config import Settings, get_settings
from app.services.ai.base import AIContext, AIResponse, AIService

logger = logging.getLogger(__name__)


def _content_to_str(content: object) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    return str(content)


def _usage_from_run(run: RunOutput) -> dict[str, int]:
    metrics = run.metrics
    if metrics is None:
        return {}
    return {
        "prompt_tokens": metrics.input_tokens or 0,
        "completion_tokens": metrics.output_tokens or 0,
        "total_tokens": metrics.total_tokens or 0,
    }


def _build_user_query(
    context: AIContext,
    user_prompt: str,
    *,
    analysis_type: str | None = None,
) -> str:
    lines = [
        "Use Google BigQuery tools to answer this request.",
        "Prefer read-only SELECT queries. Summarize results for a Jira stakeholder.",
    ]
    if context.issue_key:
        lines.append(f"Issue key: {context.issue_key}")
    if context.summary:
        lines.append(f"Summary: {context.summary}")
    if context.description:
        lines.append(f"Description: {context.description}")
    if context.comments:
        lines.append("Comments:")
        lines.extend(f"- {comment}" for comment in context.comments)
    if analysis_type:
        lines.append(f"Analysis type: {analysis_type}")
    if user_prompt:
        lines.append(f"Request: {user_prompt}")
    return "\n".join(lines)


class AgnoService(AIService):
    def __init__(
        self,
        *,
        anthropic_api_key: str,
        model_id: str,
        bigquery_dataset: str,
        google_cloud_project: str,
        google_cloud_location: str,
    ) -> None:
        self._model_id = model_id
        qualified_dataset = f"{google_cloud_project}.{bigquery_dataset}"

        self._agent = Agent(
            name="SA Copilot Data Agent",
            model=Claude(id=model_id, api_key=anthropic_api_key),
            tools=[
                GoogleBigQueryTools(
                    dataset=bigquery_dataset,
                    project=google_cloud_project,
                    location=google_cloud_location,
                )
            ],
            instructions=[
                "You are a data analyst assistant for the SA Copilot Jira integration.",
                f"BigQuery scope: `{qualified_dataset}`.",
                "Prepend project and dataset to table names in SQL.",
                "Use list_tables and describe_table when schema is unknown.",
                "Run read-only SELECT queries",
                "Return a concise answer with the key findings.",
            ],
            markdown=True,
            debug_mode=True,
        )

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "AgnoService":
        settings = settings or get_settings()
        missing = [
            name
            for name, value in (
                ("ANTHROPIC_API_KEY or CLAUDE_DEV_API_KEY", settings.anthropic_api_key),
                ("GOOGLE_CLOUD_PROJECT", settings.google_cloud_project),
                ("BIGQUERY_DATASET", settings.bigquery_dataset),
            )
            if not value
        ]
        if missing:
            raise ValueError(f"AgnoService requires environment variables: {', '.join(missing)}")

        assert settings.anthropic_api_key is not None
        assert settings.google_cloud_project is not None
        assert settings.bigquery_dataset is not None

        return cls(
            anthropic_api_key=settings.anthropic_api_key,
            model_id=settings.claude_model_id,
            bigquery_dataset=settings.bigquery_dataset,
            google_cloud_project=settings.google_cloud_project,
            google_cloud_location=settings.google_cloud_location,
        )

    async def _run_agent(self, query: str) -> RunOutput:
        try:
            run = await self._agent.arun(input=query)
        except Exception:
            logger.exception("Agno agent run failed")
            raise

        if not isinstance(run, RunOutput):
            msg = "Expected RunOutput from agent.arun()"
            raise TypeError(msg)
        return run

    async def generate_response(self, context: AIContext, prompt: str) -> AIResponse:
        query = _build_user_query(context, prompt)
        print("USER QUERY: ", query)
        run = await self._run_agent(query)
        content = _content_to_str(run.content)

        return AIResponse(
            content=content,
            model=self._model_id,
            usage=_usage_from_run(run),
        )
