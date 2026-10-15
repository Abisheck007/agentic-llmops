import logging
from functools import lru_cache
from time import perf_counter

from openai import AsyncAzureOpenAI
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from backend.app.core.config import settings
from backend.app.api.schemas import SourceDocument
from backend.app.observability.metrics import (
    llm_completion_tokens,
    llm_duration,
    llm_prompt_tokens,
    llm_requests,
)

logger = logging.getLogger(__name__)

tracer = trace.get_tracer(__name__)


@lru_cache(maxsize=1)
def get_azure_openai_client() -> AsyncAzureOpenAI:
    """Create and cache the Azure OpenAI client."""

    required_settings = {
        "AZURE_OPENAI_ENDPOINT": settings.azure_openai_endpoint,
        "AZURE_OPENAI_API_KEY": settings.azure_openai_api_key,
        "AZURE_OPENAI_DEPLOYMENT": settings.azure_openai_deployment,
        "AZURE_OPENAI_API_VERSION": settings.azure_openai_api_version,
    }

    missing = [
        name
        for name, value in required_settings.items()
        if not value or not value.strip()
    ]

    if missing:
        raise ValueError("Missing Azure OpenAI configuration: " + ", ".join(missing))

    return AsyncAzureOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        api_version=settings.azure_openai_api_version,
        timeout=30.0,
        max_retries=2,
    )


async def generate_answer(
    question: str,
    sources: list[SourceDocument],
) -> str:
    """Generate a grounded answer and record LLM telemetry."""

    client = get_azure_openai_client()

    # Build context from retrieved Azure AI Search documents.
    if sources:
        context_parts = []

        for index, source in enumerate(sources, start=1):
            context_parts.append(
                f"[{index}] Title: {source.title}\n"
                f"Document ID: {source.document_id}\n"
                f"Content: {source.content}"
            )

        context = "\n\n".join(context_parts)
    else:
        context = "No relevant documents were found."

    system_prompt = f"""
You are an assistant in a Retrieval-Augmented Generation application.

Answer the user's question using the retrieved context.

Rules:
- Prefer information supported by the retrieved documents.
- Do not invent facts.
- If the context is insufficient, say so clearly.
- Cite supporting documents using [1], [2], and so on.
- If no documents were found, say that the knowledge base
  did not provide relevant information.

Retrieved context:
{context}
"""

    start = perf_counter()
    outcome = "error"

    with tracer.start_as_current_span("llm.generate_answer") as span:
        span.set_attribute(
            "gen_ai.request.model",
            settings.azure_openai_deployment or "unknown",
        )
        span.set_attribute(
            "rag.source_count",
            len(sources),
        )

        try:
            response = await client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": question,
                    },
                ],
                max_completion_tokens=settings.llm_max_tokens,
            )

            if not response.choices:
                raise RuntimeError("The model returned no response choices.")

            choice = response.choices[0]
            message = choice.message
            answer = message.content

            # Record safe diagnostic metadata.
            logger.info(
                "Model response metadata: finish_reason=%s, "
                "completion_tokens=%s, prompt_tokens=%s, refusal=%s",
                choice.finish_reason,
                (response.usage.completion_tokens if response.usage else None),
                (response.usage.prompt_tokens if response.usage else None),
                bool(message.refusal),
            )

            span.set_attribute(
                "gen_ai.response.finish_reasons",
                [choice.finish_reason or "unknown"],
            )

            # Record token usage when the API supplies it.
            if response.usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens

                span.set_attribute(
                    "gen_ai.usage.input_tokens",
                    prompt_tokens,
                )
                span.set_attribute(
                    "gen_ai.usage.output_tokens",
                    completion_tokens,
                )

                llm_prompt_tokens.add(prompt_tokens)
                llm_completion_tokens.add(completion_tokens)

            if message.refusal:
                raise RuntimeError("The model refused to answer the question.")

            if not answer or not answer.strip():
                raise RuntimeError(
                    "The model returned no text. "
                    f"Finish reason: {choice.finish_reason}"
                )

            outcome = "success"
            return answer.strip()

        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise

        finally:
            elapsed_ms = (perf_counter() - start) * 1000

            span.set_attribute(
                "operation.duration_ms",
                elapsed_ms,
            )
            span.set_attribute(
                "operation.outcome",
                outcome,
            )

            # Record each request exactly once.
            llm_requests.add(1, {"outcome": outcome})

            llm_duration.record(
                elapsed_ms,
                {"outcome": outcome},
            )
