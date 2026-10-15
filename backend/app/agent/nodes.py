import asyncio

from backend.app.agent.state import AgentState
from backend.app.llm.client import generate_answer
from backend.app.rag.retrieval import retrieve_documents
import re

from backend.app.agent.state import AgentState

STOP_WORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "what",
    "how",
    "why",
    "when",
    "where",
    "who",
    "does",
    "do",
    "did",
    "can",
    "could",
    "would",
    "should",
    "and",
    "or",
    "but",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "by",
    "from",
    "about",
    "it",
    "its",
    "use",
    "used",
    "using",
    "explain",
    "tell",
    "me",
    "please",
}


def extract_keywords(text: str) -> set[str]:
    """Extract informative terms from text."""
    words = re.findall(r"[a-z0-9]+", text.lower())

    return {word for word in words if word not in STOP_WORDS and len(word) > 1}


def is_context_relevant(
    question: str,
    sources: list,
    threshold: float = 0.20,
) -> bool:
    """Estimate whether retrieved documents overlap the question."""
    question_keywords = extract_keywords(question)

    if not question_keywords or not sources:
        return False

    source_text = " ".join(f"{source.title} {source.content}" for source in sources)

    source_keywords = extract_keywords(source_text)

    matched_keywords = question_keywords & source_keywords

    score = len(matched_keywords) / len(question_keywords)

    return score >= threshold


def evaluate_context_node(state: AgentState) -> dict:
    """Route the agent based on basic context relevance."""

    question = state.get("question", "")
    sources = state.get("sources", [])

    context_sufficient = is_context_relevant(
        question=question,
        sources=sources,
    )

    if context_sufficient:
        step = "Retrieved context appears relevant to the question."
    else:
        step = (
            "Retrieved context is missing or appears insufficiently "
            "relevant to the question."
        )

    return {
        "context_sufficient": context_sufficient,
        "steps": state.get("steps", []) + [step],
    }


async def retrieve_node(state: AgentState) -> dict:
    """Retrieve relevant documents from Azure AI Search."""

    sources = await asyncio.to_thread(
        retrieve_documents,
        state["question"],
    )

    return {
        "sources": sources,
        "steps": state.get("steps", [])
        + [f"Retrieved {len(sources)} document(s) from Azure AI Search."],
    }


async def generate_answer_node(state: AgentState) -> dict:
    """Generate an answer grounded in retrieved documents."""

    answer = await generate_answer(
        question=state["question"],
        sources=state.get("sources", []),
    )

    return {
        "answer": answer,
        "steps": state.get("steps", [])
        + ["Generated an answer using the retrieved context."],
    }


def no_context_node(state: AgentState) -> dict:
    """Return a safe fallback when retrieval finds no usable context."""

    return {
        "answer": (
            "I couldn't find relevant information in the current "
            "knowledge base to answer that question. Please try a "
            "different question or add relevant documents."
        ),
        "steps": state.get("steps", [])
        + ["Returned a fallback because no usable context was available."],
    }
