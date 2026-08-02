import os
import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from src.settings import settings


class DataIngestion:
    def __init__(self, index_name: str = "vector_db_index"):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GOOGLE_API_KEY,
            model="gemini-embedding-1024",
        )
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.create_or_update_index(index_name)
        self.vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings,
            pinecone_api_key=settings.PINECONE_API_KEY,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

    def create_or_update_index(self, index_name: str = "vector_db_index"):
        existing_indexes = [idx["name"] for idx in self.pc.list_indexes()]
        if index_name not in existing_indexes:
            self.pc.create_index(
                name=index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        return self.pc.Index(index_name)

    def save_uploaded_files(self, documents, upload_dir: str = "data") -> list[tuple[str, str]]:
        """Save uploaded files and return list of (file_path, original_filename)."""
        os.makedirs(upload_dir, exist_ok=True)
        file_records: list[tuple[str, str]] = []
        for doc in documents:
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(doc.filename or "")[1]
            file_path = os.path.join(upload_dir, f"{file_id}{file_extension}")
            with open(file_path, "wb") as f:
                f.write(doc.file.read())
            file_records.append((file_path, doc.filename or f"{file_id}{file_extension}"))
        return file_records

    def _load_file(self, user_id, file_path: str):
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
        return chunked_docs

    def load_docs(self, user_id, file_paths: list[str]):
        all_docs = []
        for file_path in file_paths:
            all_docs.extend(self._load_file(user_id, file_path))
        return all_docs

    def ingest_saved_files(self, user_id, file_paths: list[str]) -> int:
        processed_docs = self.load_docs(user_id, file_paths)
        if not processed_docs:
            raise Exception("No documents were processed")
        self.vectorstore.add_documents(processed_docs)
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except OSError:
                pass
        return len(processed_docs)

    def upsert_data(self, user_id, documents, index_name: str = "vector_db_index"):
        file_records = self.save_uploaded_files(documents, upload_dir=f"data/{user_id}")
        file_paths = [path for path, _ in file_records]
        return self.ingest_saved_files(user_id, file_paths)
