import logging

from azure.core.exceptions import AzureError
from fastapi import APIRouter, HTTPException
from openai import APIError

from backend.app.agent.graph import run_agent
from backend.app.api.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
)
from backend.app.core.config import settings
from time import perf_counter

from opentelemetry import trace

from backend.app.observability.metrics import (
    api_request_duration,
    api_requests,
)
from backend.app.observability.tracing import get_current_trace_id

tracer = trace.get_tracer(__name__)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
)
async def health_check():
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        environment=settings.app_env,
    )


@router.post(
    f"{settings.api_prefix}/query",
    response_model=QueryResponse,
    tags=["Agentic RAG"],
)
async def query_agent(request: QueryRequest):
    start = perf_counter()
    outcome = "error"

    try:
        with tracer.start_as_current_span("api.query") as span:
            span.set_attribute("app.name", settings.app_name)
            span.set_attribute("agent.session_present", bool(request.session_id))

            result = await run_agent(
                question=request.question,
                session_id=request.session_id,
            )

            trace_id = get_current_trace_id()
            outcome = "success"

            return QueryResponse(
                status="completed",
                answer=result["answer"],
                session_id=request.session_id,
                sources=result.get("sources", []),
                trace_id=trace_id,
                agent_steps=result.get("steps", []),
            )

    except ValueError as exc:
        logger.error("Agent configuration error: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Azure service configuration is incomplete.",
        ) from exc

    except APIError as exc:
        logger.exception("Azure OpenAI request failed.")
        raise HTTPException(
            status_code=502,
            detail="The Azure OpenAI service request failed.",
        ) from exc

    except AzureError as exc:
        logger.exception("Azure AI Search request failed.")
        raise HTTPException(
            status_code=502,
            detail="The Azure AI Search request failed.",
        ) from exc

    except RuntimeError as exc:
        logger.exception("Agent execution failed.")
        raise HTTPException(
            status_code=502,
            detail="The agent could not complete the request.",
        ) from exc

    finally:
        elapsed_ms = (perf_counter() - start) * 1000
        api_requests.add(1, {"outcome": outcome})
        api_request_duration.record(
            elapsed_ms,
            {"outcome": outcome},
        )
