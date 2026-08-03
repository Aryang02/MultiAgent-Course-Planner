import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.exceptions import NotFoundError
from src.auth.auth import get_user
from src.core.models import User
from src.database.db import get_db
from src.repositories import DocumentRepository
from src.serializers.backend import DocumentListResponse, DocumentResponse

router = APIRouter(prefix="/v1", tags=["documents"])


@router.get("/documents", response_model=DocumentListResponse)
def list_documents(
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    docs = DocumentRepository(db)
    user_docs = docs.list_for_user(user.id)
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in user_docs]
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    user: User = Depends(get_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    docs = DocumentRepository(db)
    doc = docs.get_by_id(user.id, document_id)
    if not doc:
        raise NotFoundError("Document not found")
    return DocumentResponse.model_validate(doc)
