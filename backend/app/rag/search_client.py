from functools import lru_cache

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from backend.app.core.config import settings


@lru_cache(maxsize=1)
def get_search_client() -> SearchClient:
    required_settings = {
        "AZURE_AI_SEARCH_ENDPOINT": settings.azure_ai_search_endpoint,
        "AZURE_AI_SEARCH_INDEX": settings.azure_ai_search_index,
        "AZURE_AI_SEARCH_API_KEY": settings.azure_ai_search_api_key,
    }

    missing = [
        name
        for name, value in required_settings.items()
        if not value or not value.strip()
    ]

    if missing:
        raise ValueError("Missing Azure AI Search configuration: " + ", ".join(missing))

    return SearchClient(
        endpoint=settings.azure_ai_search_endpoint,
        index_name=settings.azure_ai_search_index,
        credential=AzureKeyCredential(settings.azure_ai_search_api_key),
    )
