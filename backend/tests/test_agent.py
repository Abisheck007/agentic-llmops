from backend.app.agent.nodes import is_context_relevant


class FakeSource:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content


def test_relevant_context_is_accepted():
    sources = [
        FakeSource(
            "Agentic RAG",
            "Agentic RAG uses agent orchestration and retrieval "
            "to answer questions using Azure AI Search.",
        )
    ]

    assert is_context_relevant(
        "What is Agentic RAG and how does it use Azure AI Search?",
        sources,
    )


def test_unrelated_context_is_rejected():
    sources = [
        FakeSource(
            "Introduction to RAG",
            "Retrieval augmented generation combines retrieval "
            "with language model generation.",
        )
    ]

    assert not is_context_relevant(
        "What is the weather on planet Zorblax?",
        sources,
    )


def test_empty_sources_are_rejected():
    assert not is_context_relevant(
        "What is Agentic RAG?",
        [],
    )
