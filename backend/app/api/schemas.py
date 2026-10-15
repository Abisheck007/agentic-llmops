from typing import Literal

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request body for an Agentic RAG query."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Question to answer using the knowledge base.",
    )

    session_id: str | None = Field(
        default=None,
        max_length=128,
        description="Optional identifier for a conversation session.",
    )


class SourceDocument(BaseModel):
    """A source used to support an answer."""

    document_id: str
    title: str
    content: str
    page_number: int | None = None
    source_url: str | None = None


class QueryResponse(BaseModel):
    status: Literal["completed", "not_implemented"]
    answer: str
    session_id: str | None = None
    sources: list[SourceDocument] = Field(default_factory=list)
    trace_id: str | None = None
    agent_steps: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Basic application health information."""

    status: Literal["healthy"]
    app_name: str
    environment: str
