import logging
import uuid

from src.database.data_ingestion import DataIngestion
from src.database.session import get_db_session
from src.repositories import DocumentRepository
from src.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="src.worker.tasks.ingestion.ingest_documents",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=3,
)
def ingest_documents(
    self,
    user_id: str,
    file_items: list[dict],
    index_name: str = "vector_db_index",
) -> dict:
    logger.info(
        "Starting ingestion task_id=%s user_id=%s files=%d",
        self.request.id,
        user_id,
        len(file_items),
    )

    document_ids = [
        uuid.UUID(item["document_id"])
        for item in file_items
        if item.get("document_id")
    ]

    with get_db_session() as db:
        DocumentRepository(db).mark_processing(document_ids)

    ingestion = DataIngestion(index_name=index_name)
    result = ingestion.ingest_saved_files(user_id, file_items)

    with get_db_session() as db:
        docs_repo = DocumentRepository(db)
        for item in result["results"]:
            doc_id_str = item.get("document_id")
            if not doc_id_str:
                continue
            doc_id = uuid.UUID(doc_id_str)
            if item["status"] == "completed":
                docs_repo.update_status(
                    doc_id,
                    "completed",
                    chunk_count=item.get("chunks_processed", 0),
                )
            else:
                docs_repo.update_status(
                    doc_id,
                    "failed",
                    error_message=item.get("error", "Ingestion failed"),
                )

    result["task_id"] = self.request.id
    return result
