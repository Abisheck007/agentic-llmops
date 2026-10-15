from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
)

from backend.app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def create_search_index() -> None:
    endpoint = settings.azure_ai_search_endpoint
    api_key = settings.azure_ai_search_api_key
    index_name = settings.azure_ai_search_index

    if not endpoint or not api_key or not index_name:
        raise ValueError(
            "Configure Azure AI Search endpoint, API key, " "and index name in .env."
        )

    index_client = SearchIndexClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
    )

    fields = [
        SimpleField(
            name="document_id",
            type=SearchFieldDataType.String,
            key=True,
        ),
        SearchableField(
            name="title",
            type=SearchFieldDataType.String,
        ),
        SearchableField(
            name="content",
            type=SearchFieldDataType.String,
        ),
        SimpleField(
            name="page_number",
            type=SearchFieldDataType.Int32,
        ),
        SimpleField(
            name="source_url",
            type=SearchFieldDataType.String,
        ),
    ]

    index = SearchIndex(
        name=index_name,
        fields=fields,
    )

    result = index_client.create_or_update_index(index)

    print(f"Search index ready: {result.name}")


if __name__ == "__main__":
    create_search_index()
