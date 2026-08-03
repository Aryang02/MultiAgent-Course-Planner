import os
import re
import uuid
from typing import Any

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from src.settings import settings

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}


def sanitize_filename(filename: str) -> str:
    name = os.path.basename(filename or "upload")
    return re.sub(r"[^\w.\- ]", "_", name)[:255]


class DataIngestion:
    def __init__(self, index_name: str | None = None):
        self.index_name = index_name or settings.DEFAULT_VECTOR_INDEX
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GOOGLE_API_KEY,
            model="gemini-embedding-1024",
        )
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.create_or_update_index(self.index_name)
        self.vectorstore = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings,
            pinecone_api_key=settings.PINECONE_API_KEY,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

    def create_or_update_index(self, index_name: str):
        existing_indexes = [idx["name"] for idx in self.pc.list_indexes()]
        if index_name not in existing_indexes:
            self.pc.create_index(
                name=index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        return self.pc.Index(index_name)

    def _user_namespace(self, user_id) -> str:
        return str(user_id)

    def _max_file_bytes(self) -> int:
        return settings.MAX_UPLOAD_FILE_SIZE_MB * 1024 * 1024

    def _max_request_bytes(self) -> int:
        return settings.MAX_UPLOAD_REQUEST_SIZE_MB * 1024 * 1024

    def save_uploaded_files(
        self, documents, upload_dir: str = "data"
    ) -> list[tuple[str, str, int]]:
        """Save uploaded files; return (file_path, original_filename, byte_size)."""
        os.makedirs(upload_dir, exist_ok=True)
        file_records: list[tuple[str, str, int]] = []
        total_size = 0

        for doc in documents:
            content = doc.file.read()
            size = len(content)
            total_size += size

            if size > self._max_file_bytes():
                raise ValueError(
                    f"File '{doc.filename}' exceeds {settings.MAX_UPLOAD_FILE_SIZE_MB}MB limit"
                )
            if total_size > self._max_request_bytes():
                raise ValueError(
                    f"Total upload exceeds {settings.MAX_UPLOAD_REQUEST_SIZE_MB}MB limit"
                )

            file_id = str(uuid.uuid4())
            safe_name = sanitize_filename(doc.filename or "upload")
            file_extension = os.path.splitext(safe_name)[1].lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                raise ValueError(f"Unsupported file type: {file_extension}")

            file_path = os.path.join(upload_dir, f"{file_id}{file_extension}")
            with open(file_path, "wb") as f:
                f.write(content)
            file_records.append((file_path, safe_name, size))

        return file_records

    def _load_file(self, user_id, file_path: str, document_id: str | None = None):
        lower_path = file_path.lower()
        if lower_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif lower_path.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
        elif lower_path.endswith(".docx"):
            from langchain_community.document_loaders import Docx2txtLoader

            loader = Docx2txtLoader(file_path)
        else:
            return []

        docs = loader.load()
        chunked_docs = self.text_splitter.split_documents(docs)
        for doc in chunked_docs:
            doc.metadata["user_id"] = str(user_id)
            doc.metadata["source_file"] = os.path.basename(file_path)
            if document_id:
                doc.metadata["document_id"] = document_id
        return chunked_docs

    def ingest_file(self, user_id, file_path: str, document_id: str | None = None) -> int:
        processed_docs = self._load_file(user_id, file_path, document_id=document_id)
        if not processed_docs:
            raise ValueError(f"No content extracted from {file_path}")

        namespace = self._user_namespace(user_id)
        self.vectorstore.add_documents(processed_docs, namespace=namespace)

        try:
            os.remove(file_path)
        except OSError:
            pass

        return len(processed_docs)

    def ingest_saved_files(
        self,
        user_id,
        file_items: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Ingest multiple files; file_items = [{file_path, document_id}, ...]."""
        results = []
        total_chunks = 0

        for item in file_items:
            file_path = item["file_path"]
            document_id = item.get("document_id")
            try:
                chunks = self.ingest_file(user_id, file_path, document_id=document_id)
                total_chunks += chunks
                results.append(
                    {
                        "document_id": document_id,
                        "status": "completed",
                        "chunks_processed": chunks,
                    }
                )
            except Exception as exc:
                results.append(
                    {
                        "document_id": document_id,
                        "status": "failed",
                        "error": str(exc),
                    }
                )

        return {
            "chunks_processed": total_chunks,
            "files_processed": len(file_items),
            "results": results,
        }

    def search_documents(self, user_id, query: str, top_k: int = 5) -> list[str]:
        namespace = self._user_namespace(user_id)
        filter_dict = {"user_id": str(user_id)}
        docs = self.vectorstore.similarity_search(
            query,
            k=top_k,
            namespace=namespace,
            filter=filter_dict,
        )
        return [doc.page_content for doc in docs]
