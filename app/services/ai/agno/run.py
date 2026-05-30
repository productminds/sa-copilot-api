from agno.run.agent import RunOutput


def usage_from_run(run: RunOutput) -> dict[str, int]:
    metrics = run.metrics
    if metrics is None:
        return {}
    return {
        "prompt_tokens": metrics.input_tokens or 0,
        "completion_tokens": metrics.output_tokens or 0,
        "total_tokens": metrics.total_tokens or 0,
    }
