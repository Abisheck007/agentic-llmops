from time import perf_counter

from opentelemetry import trace

from backend.app.api.schemas import SourceDocument
from backend.app.observability.metrics import (
    retrieved_documents,
    retrieval_duration,
)
from backend.app.rag.search_client import get_search_client

tracer = trace.get_tracer(__name__)


def retrieve_documents(
    question: str,
    top_k: int = 5,
) -> list[SourceDocument]:
    start = perf_counter()
    outcome = "error"

    with tracer.start_as_current_span("rag.retrieve") as span:
        try:
            client = get_search_client()

            results = client.search(
                search_text=question,
                top=top_k,
                select=[
                    "document_id",
                    "title",
                    "content",
                    "page_number",
                    "source_url",
                ],
            )

            sources: list[SourceDocument] = []

            for result in results:
                sources.append(
                    SourceDocument(
                        document_id=result["document_id"],
                        title=result.get("title") or "Untitled",
                        content=result.get("content") or "",
                        page_number=result.get("page_number"),
                        source_url=result.get("source_url"),
                    )
                )

            outcome = "success"
            span.set_attribute(
                "rag.retrieved_document_count",
                len(sources),
            )
            retrieved_documents.record(len(sources))

            return sources

        except Exception:
            span.set_attribute("operation.outcome", "error")
            raise

        finally:
            elapsed_ms = (perf_counter() - start) * 1000
            span.set_attribute("operation.duration_ms", elapsed_ms)
            span.set_attribute("operation.outcome", outcome)
            retrieval_duration.record(
                elapsed_ms,
                {"outcome": outcome},
            )
