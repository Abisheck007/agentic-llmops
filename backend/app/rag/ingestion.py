import json
from pathlib import Path

from backend.app.rag.search_client import get_search_client


def load_documents() -> list[dict]:
    # Project root / data / documents.json
    project_root = Path(__file__).resolve().parents[3]
    file_path = project_root / "data" / "documents.json"

    if not file_path.exists():
        raise FileNotFoundError(f"Knowledge file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError("documents.json must contain a JSON array.")

    required_fields = {"document_id", "title", "content"}

    for document in documents:
        missing = required_fields - document.keys()

        if missing:
            raise ValueError(f"Document is missing fields: {sorted(missing)}")

    return documents


def ingest_documents() -> None:
    client = get_search_client()
    documents = load_documents()

    if not documents:
        print("No documents to upload.")
        return

    results = client.upload_documents(documents=documents)

    succeeded = sum(1 for result in results if result.succeeded)
    failed = len(results) - succeeded

    print(f"Documents submitted: {len(results)}")
    print(f"Successful uploads: {succeeded}")
    print(f"Failed uploads: {failed}")

    if failed:
        failures = [
            {
                "key": result.key,
                "error": result.error_message,
            }
            for result in results
            if not result.succeeded
        ]
        raise RuntimeError(f"Some documents failed to upload: {failures}")
