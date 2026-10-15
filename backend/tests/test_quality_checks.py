from backend.app.evaluation.quality_checks import (
    get_field,
    keyword_coverage,
    normalize_text,
)


def test_normalize_text():
    assert normalize_text("  Azure   AI Search  ") == ("azure ai search")


def test_keyword_coverage_all_keywords_found():
    score = keyword_coverage(
        "RAG combines retrieval with generation.",
        ["retrieval", "generation"],
    )

    assert score == 1.0


def test_keyword_coverage_partial_match():
    score = keyword_coverage(
        "RAG uses retrieval.",
        ["retrieval", "generation"],
    )

    assert score == 0.5


def test_keyword_coverage_no_match():
    score = keyword_coverage(
        "Azure cloud services",
        ["retrieval", "generation"],
    )

    assert score == 0.0


def test_keyword_coverage_empty_expected_keywords():
    assert keyword_coverage("Any answer", []) == 1.0


def test_get_field_from_dictionary():
    assert (
        get_field(
            {"title": "Agentic RAG"},
            "title",
        )
        == "Agentic RAG"
    )


def test_get_field_default_when_missing():
    assert get_field({}, "missing", "unknown") == "unknown"
