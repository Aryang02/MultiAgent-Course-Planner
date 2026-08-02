import uuid
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from src.database.data_ingestion import DataIngestion, sanitize_filename
from src.repositories.base import DocumentRepository


def test_sanitize_filename():
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert " " in sanitize_filename("my file.pdf") or "_" in sanitize_filename("my file.pdf")


def test_save_uploaded_files_rejects_oversized():
    ingestion = DataIngestion.__new__(DataIngestion)
    ingestion._max_file_bytes = lambda: 10
    ingestion._max_request_bytes = lambda: 100

    mock_file = MagicMock()
    mock_file.filename = "big.pdf"
    mock_file.file = BytesIO(b"x" * 20)

    with pytest.raises(ValueError, match="exceeds"):
        ingestion.save_uploaded_files([mock_file], upload_dir="/tmp/test_upload")


def test_search_documents_returns_chunks():
    ingestion = DataIngestion.__new__(DataIngestion)
    ingestion._user_namespace = lambda user_id: str(user_id)
    ingestion.vectorstore = MagicMock()
    ingestion.vectorstore.similarity_search.return_value = [
        MagicMock(page_content="chunk one"),
        MagicMock(page_content="chunk two"),
    ]

    chunks = ingestion.search_documents("user-1", "linear algebra", top_k=2)
    assert chunks == ["chunk one", "chunk two"]
    ingestion.vectorstore.similarity_search.assert_called_once()
    call_kwargs = ingestion.vectorstore.similarity_search.call_args.kwargs
    assert call_kwargs["namespace"] == "user-1"
    assert call_kwargs["filter"] == {"user_id": "user-1"}


def test_document_repository_update_status():
    db = MagicMock()
    doc = MagicMock()
    doc.id = uuid.uuid4()
    db.query.return_value.filter.return_value.first.return_value = doc

    repo = DocumentRepository(db)
    updated = repo.update_status(doc.id, "completed", chunk_count=12)

    assert updated.status == "completed"
    assert updated.chunk_count == 12
