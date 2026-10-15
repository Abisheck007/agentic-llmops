from typing import TypedDict

from backend.app.api.schemas import SourceDocument


class AgentState(TypedDict, total=False):
    question: str
    session_id: str | None
    sources: list[SourceDocument]
    context_sufficient: bool
    answer: str
    steps: list[str]
