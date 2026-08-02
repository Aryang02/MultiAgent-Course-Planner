import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from src.api.exceptions import AppError
from src.auth.auth import get_user
from src.core.models import Document, User
from src.database.data_ingestion import DataIngestion
from src.database.db import get_db
from src.serializers.backend import UploadResponse
from src.settings import settings
from src.worker.task_ownership import register_task_owner
from src.worker.tasks.ingestion import ingest_documents

router = APIRouter(prefix="/v1", tags=["upload"])


@router.post("/upload", response_model=UploadResponse, status_code=202)
def upload(
    documents: list[UploadFile] = File(...),
    index_name: str | None = None,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
) -> UploadResponse:
    if not documents:
        raise AppError("No documents provided", status_code=400)

    index_name = index_name or settings.DEFAULT_VECTOR_INDEX
    data_ingestion = DataIngestion(index_name=index_name)

    try:
        file_records = data_ingestion.save_uploaded_files(
            documents, upload_dir=f"data/{user.id}"
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc

    document_ids: list[uuid.UUID] = []
    file_items: list[dict] = []

    for file_path, original_name, _size in file_records:
        doc_id = uuid.uuid4()
        record = Document(
            id=doc_id,
            user_id=user.id,
            file_name=original_name,
            file_path=file_path,
            status="pending",
            index_name=index_name,
        )
        db.add(record)
        document_ids.append(doc_id)
        file_items.append({"file_path": file_path, "document_id": str(doc_id)})

    db.commit()

    task = ingest_documents.delay(
        user_id=str(user.id),
        file_items=file_items,
        index_name=index_name,
    )
    register_task_owner(task.id, str(user.id))

    return UploadResponse(
        task_id=task.id,
        detail="Document ingestion started",
        files_uploaded=len(documents),
        document_ids=document_ids,
        status="pending",
    )
