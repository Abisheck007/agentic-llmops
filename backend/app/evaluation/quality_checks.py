import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from backend.app.agent.graph import run_agent

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = PROJECT_ROOT / "evals" / "test_questions.jsonl"
REPORT_PATH = PROJECT_ROOT / "evals" / "results" / "latest_report.json"

# Initial baseline thresholds, not comprehensive semantic metrics.
MIN_RETRIEVAL_KEYWORD_COVERAGE = 0.34
MIN_ANSWER_KEYWORD_COVERAGE = 0.34


def normalize_text(text: str) -> str:
    """Normalize text for simple, deterministic keyword checks."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def get_field(item: Any, field: str, default: Any = "") -> Any:
    """Read a field from a Pydantic object or dictionary."""
    if isinstance(item, dict):
        return item.get(field, default)
    return getattr(item, field, default)


def keyword_coverage(
    text: str,
    expected_keywords: list[str],
) -> float:
    """Return the fraction of expected keywords found in text."""
    if not expected_keywords:
        return 1.0

    normalized = normalize_text(text)

    matched = sum(
        1 for keyword in expected_keywords if normalize_text(keyword) in normalized
    )

    return matched / len(expected_keywords)


def load_dataset() -> list[dict[str, Any]]:
    """Load and validate the JSONL evaluation dataset."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Evaluation dataset not found: {DATASET_PATH}")

    cases = []

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on dataset line {line_number}") from exc

            required_fields = {
                "id",
                "question",
                "expected_keywords",
            }

            if not required_fields.issubset(case):
                raise ValueError(f"Missing required fields on line {line_number}")

            if not isinstance(case["expected_keywords"], list) or not all(
                isinstance(keyword, str) for keyword in case["expected_keywords"]
            ):
                raise ValueError(
                    f"expected_keywords must be a list of strings "
                    f"on line {line_number}"
                )

            cases.append(case)

    if not cases:
        raise ValueError("The evaluation dataset is empty.")

    return cases


async def evaluate_case(
    case: dict[str, Any],
) -> dict[str, Any]:
    """Run one agent evaluation case and return its measurements."""
    started = perf_counter()

    question = case["question"]
    expected_keywords = case["expected_keywords"]

    try:
        result = await run_agent(question=question)

        elapsed_ms = round(
            (perf_counter() - started) * 1000,
            2,
        )

        sources = result.get("sources", [])
        answer = result.get("answer", "") or ""
        steps = result.get("steps", [])

        source_text = " ".join(
            f"{get_field(source, 'title', '')} " f"{get_field(source, 'content', '')}"
            for source in sources
        )

        retrieval_score = keyword_coverage(
            source_text,
            expected_keywords,
        )

        answer_score = keyword_coverage(
            answer,
            expected_keywords,
        )

        has_answer = bool(answer.strip())
        has_sources = len(sources) > 0

        # This is a basic citation-presence check, not a
        # verification that every citation is factually correct.
        has_citation = bool(re.search(r"\[\d+\]", answer))

        has_retrieval_step = any("retriev" in str(step).lower() for step in steps)

        checks = {
            "answer_present": has_answer,
            "retrieval_step_present": has_retrieval_step,
            "retrieval_keyword_coverage": (
                retrieval_score >= MIN_RETRIEVAL_KEYWORD_COVERAGE
            ),
            "answer_keyword_coverage": (answer_score >= MIN_ANSWER_KEYWORD_COVERAGE),
            "citation_present": (has_citation if has_sources else True),
        }

        return {
            "id": case["id"],
            "question": question,
            "status": ("passed" if all(checks.values()) else "failed"),
            "latency_ms": elapsed_ms,
            "retrieved_document_count": len(sources),
            "retrieval_keyword_coverage": round(retrieval_score, 3),
            "answer_keyword_coverage": round(answer_score, 3),
            "citation_present": has_citation,
            "agent_steps": steps,
            "checks": checks,
        }

    except Exception as exc:
        elapsed_ms = round(
            (perf_counter() - started) * 1000,
            2,
        )

        logger.exception(
            "Evaluation case %s failed",
            case["id"],
        )

        return {
            "id": case["id"],
            "question": question,
            "status": "error",
            "latency_ms": elapsed_ms,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


async def run_evaluations() -> dict[str, Any]:
    """Run all cases and save a machine-readable report."""
    cases = load_dataset()
    results = []

    for case in cases:
        result = await evaluate_case(case)
        results.append(result)

        print(
            f"[{result['status'].upper()}] "
            f"{result['id']} - "
            f"{result['latency_ms']} ms"
        )

    passed = sum(result["status"] == "passed" for result in results)

    failed = sum(result["status"] == "failed" for result in results)

    errors = sum(result["status"] == "error" for result in results)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": str(DATASET_PATH.relative_to(PROJECT_ROOT)),
        "total_cases": len(results),
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": round(passed / len(results), 3),
        "results": results,
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\nEvaluation summary")
    print(f"Total cases: {len(results)}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")
    print(f"Errors:      {errors}")
    print(f"Report:      {REPORT_PATH}")

    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    evaluation_report = asyncio.run(run_evaluations())

    # Non-zero exit code if the suite has failures or errors.
    if evaluation_report["failed"] > 0 or evaluation_report["errors"] > 0:
        raise SystemExit(1)
