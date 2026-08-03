from src.database.data_ingestion import DataIngestion
from src.settings import settings


def search_documents(
    user_id: str,
    query: str,
    top_k: int = 5,
    index_name: str | None = None,
) -> list[str]:
    """Search a user's uploaded documents in Pinecone."""
    if not settings.PINECONE_API_KEY or not settings.GOOGLE_API_KEY:
        return []

    ingestion = DataIngestion(index_name=index_name)
    return ingestion.search_documents(user_id, query, top_k=top_k)
