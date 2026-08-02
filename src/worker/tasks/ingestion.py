import logging

from src.database.data_ingestion import DataIngestion
from src.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="src.worker.tasks.ingestion.ingest_documents", bind=True)
def ingest_documents(
    self,
    user_id: str,
    file_paths: list[str],
    document_ids: list[str],
    index_name: str = "vector_db_index",
) -> dict:
    logger.info(
        "Starting ingestion task_id=%s user_id=%s files=%d",
        self.request.id,
        user_id,
        len(file_paths),
    )
    ingestion = DataIngestion(index_name=index_name)
    chunks_processed = ingestion.ingest_saved_files(user_id, file_paths)
    return {
        "chunks_processed": chunks_processed,
        "files_uploaded": len(file_paths),
        "document_ids": document_ids,
        "index_name": index_name,
    }
