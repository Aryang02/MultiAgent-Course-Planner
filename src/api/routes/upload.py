import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from src.api.exceptions import AppError
from src.auth.auth import get_user
from src.core.models import Document, User
from src.database.data_ingestion import DataIngestion
from src.database.db import get_db
from src.serializers.backend import UploadResponse

router = APIRouter(prefix="/v1", tags=["upload"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}


@router.post("/upload", response_model=UploadResponse)
def upload(
    documents: List[UploadFile] = File(...),
    index_name: str = "vector_db_index",
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
) -> UploadResponse:
    if not documents:
        raise AppError("No documents provided", status_code=400)

    for doc in documents:
        file_ext = os.path.splitext(doc.filename or "")[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise AppError(f"Unsupported file type: {file_ext}", status_code=400)

    data_ingestion = DataIngestion(index_name=index_name)
    file_records = data_ingestion.save_uploaded_files(documents, upload_dir=f"data/{user.id}")

    document_ids: list[uuid.UUID] = []
    for file_path, original_name in file_records:
        record = Document(
            id=uuid.uuid4(),
            user_id=user.id,
            file_name=original_name,
            file_path=file_path,
        )
        db.add(record)
        document_ids.append(record.id)
    db.commit()

    num_chunks = data_ingestion.ingest_saved_files(user.id, [path for path, _ in file_records])

    return UploadResponse(
        detail="Documents ingested successfully",
        chunks_processed=num_chunks,
        files_uploaded=len(documents),
        document_ids=document_ids,
    )
