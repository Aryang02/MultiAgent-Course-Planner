from langchain_google_genai import GoogleGenerativeAIEmbeddings 
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

class DataIngestion:
    def __init__(self, index_name="vector_db_index"):
        self.index = self.create_or_update_index(index_name)
        if not self.index:
            raise Exception("Failed to create or connect to Pinecone index")
        self.embeddings = GoogleGenerativeAIEmbeddings()
        self.pc = PineconeVectorStore(api_key = os.getenv("PINECONE_API_KEY"), index=self.index, embeddings = self.embeddings)

    def embed_docs(self, documents):
        # Process and embed documents
        try:
            embedded_docs = [self.embeddings.embed(doc) for doc in documents]
            return embedded_docs
        except Exception as e:
            raise Exception(f"Failed to embed documents: {str(e)}")
    
    def create_or_update_index(self, index_name="vector_db_index"):
        try:
            if not self.pc.has_index(index_name):
                self.pc.create_index_for_model(
                    name=index_name,
                    dimension=1024,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
            index = self.pc.Index(index_name)
            return index
        except Exception as e:
            raise Exception(f"Failed to create or connect to index: {str(e)}")
    
    def load_docs(self, user_id, documents):
        # Load documents from the specified file path
        try:
            pages = []
            for doc in documents:
                loader = PyPDFLoader(file_path=doc)
                for page in loader.load_and_split():
                    page.metadata['user_id'] = user_id
                    pages.append(page)
            return pages
        except Exception as e:
            raise Exception(f"Failed to load documents: {str(e)}")
    
    def upsert_data(self, user_id, documents, index_name = "vector_db_index"):
        # Upsert embedded documents into Pinecone index
        try:
            documents = self.load_docs(user_id, documents)
            self.pc.add_documents(index_name=index_name, documents=documents)
        except Exception as e:
            raise Exception(f"Failed to upsert data: {str(e)}")
        
    def save_files(self, upload_dir='data'):
        # Save uploaded files to the specified directory
        try:
            if not os.path.exists(os.path.join(os.getcwd(), upload_dir)):
                os.makedirs(os.path.join(os.getcwd(), upload_dir))
            file_paths = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if f.endswith(('.pdf', '.txt', '.docx', '.png', '.jpg'))]
            return file_paths
        except Exception as e:
            raise Exception(f"Failed to save files: {str(e)}")