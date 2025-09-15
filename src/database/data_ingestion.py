# from langchain_google_genai import GoogleGenerativeAIEmbeddings 
# import os
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_pinecone import PineconeVectorStore
# from pinecone import ServerlessSpec
# from dotenv import load_dotenv
# from pinecone import Pinecone
# from src.settings import settings

# load_dotenv()

# class DataIngestion:
#     def __init__(self, index_name="vector_db_index"):
#         # Initialize embeddings first
#         self.embeddings = GoogleGenerativeAIEmbeddings(google_api_key=settings.GOOGLE_API_KEY, model='gemini-embedding-1024')

#         # Initialize Pinecone client
#         self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

#         # Ensure index exists
#         self.create_or_update_index(index_name)

#         # Now create LangChain’s vector store wrapper
#         self.vectorstore = PineconeVectorStore(
#             index_name=index_name,
#             embedding=self.embeddings,
#             pinecone_api_key=os.getenv("PINECONE_API_KEY")  # optional if already in env
#         )

#     def embed_docs(self, documents):
#         # Process and embed documents
#         try:
#             embedded_docs = [self.embeddings.embed(doc) for doc in documents]
#             return embedded_docs
#         except Exception as e:
#             raise Exception(f"Failed to embed documents: {str(e)}")
    
#     def create_or_update_index(self, index_name="vector_db_index"):
#         try:
#             if index_name not in self.pc.list_indexes().names():
#                 self.pc.create_index(
#                     name=index_name,
#                     dimension=1024,
#                     metric="cosine",
#                     spec=ServerlessSpec(cloud="aws", region="us-east-1"),
#                 )
#             return self.pc.Index(index_name)
#         except Exception as e:
#             raise Exception(f"Failed to create or connect to index: {str(e)}")
    
#     def load_docs(self, user_id, documents):
#         # Load documents from the specified file path
#         try:
#             pages = []
#             for doc in documents:
#                 loader = PyPDFLoader(file_path=doc)
#                 for page in loader.load_and_split():
#                     page.metadata['user_id'] = user_id
#                     pages.append(page)
#             return pages
#         except Exception as e:
#             raise Exception(f"Failed to load documents: {str(e)}")
    
#     def upsert_data(self, user_id, documents, index_name = "vector_db_index"):
#         # Upsert embedded documents into Pinecone index
#         try:
#             documents = self.load_docs(user_id, documents)
#             self.pc.add_documents(index_name=index_name, documents=documents)
#         except Exception as e:
#             raise Exception(f"Failed to upsert data: {str(e)}")
        
#     def save_files(self, upload_dir='data'):
#         # Save uploaded files to the specified directory
#         try:
#             if not os.path.exists(os.path.join(os.getcwd(), upload_dir)):
#                 os.makedirs(os.path.join(os.getcwd(), upload_dir))
#             file_paths = [os.path.join(upload_dir, f) for f in os.listdir(upload_dir) if f.endswith(('.pdf', '.txt', '.docx', '.png', '.jpg'))]
#             return file_paths
#         except Exception as e:
#             raise Exception(f"Failed to save files: {str(e)}")
from langchain_google_genai import GoogleGenerativeAIEmbeddings 
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_pinecone import PineconeVectorStore
from pinecone import ServerlessSpec
from dotenv import load_dotenv
from pinecone import Pinecone
from src.settings import settings
import uuid

load_dotenv()

class DataIngestion:
    def __init__(self, index_name="vector_db_index"):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GOOGLE_API_KEY, 
            model='gemini-embedding-1024' 
        )

        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

        self.index = self.create_or_update_index(index_name)

        self.vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings,
            pinecone_api_key=os.getenv("PINECONE_API_KEY")
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def create_or_update_index(self, index_name="vector_db_index"):
        try:
            existing_indexes = [idx['name'] for idx in self.pc.list_indexes()]
            
            if index_name not in existing_indexes:
                self.pc.create_index(
                    name=index_name,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
            return self.pc.Index(index_name)
        except Exception as e:
            raise Exception(f"Failed to create or connect to index: {str(e)}")
    
    def save_uploaded_files(self, documents, upload_dir='data'):
        """Save uploaded files to disk and return file paths"""
        try:
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file_paths = []
            for doc in documents:
                file_id = str(uuid.uuid4())
                file_extension = os.path.splitext(doc.filename)[1]
                file_path = os.path.join(upload_dir, f"{file_id}{file_extension}")
                
                with open(file_path, "wb") as f:
                    content = doc.file.read()
                    f.write(content)
                
                file_paths.append(file_path)
                
            return file_paths
        except Exception as e:
            raise Exception(f"Failed to save uploaded files: {str(e)}")
    
    def load_docs(self, user_id, file_paths):
        """Load and process documents from file paths"""
        try:
            all_docs = []
            for file_path in file_paths:
                if file_path.endswith('.pdf'):
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    
                    chunked_docs = self.text_splitter.split_documents(docs)
                    
                    for doc in chunked_docs:
                        doc.metadata['user_id'] = user_id
                        doc.metadata['source_file'] = os.path.basename(file_path)
                    
                    all_docs.extend(chunked_docs)
                    
            return all_docs
        except Exception as e:
            raise Exception(f"Failed to load documents: {str(e)}")
    
    def upsert_data(self, user_id, documents, index_name="vector_db_index"):
        """Process uploaded files and upsert to vector store"""
        try:
            file_paths = self.save_uploaded_files(documents, upload_dir=f'data/{user_id}')
            
            processed_docs = self.load_docs(user_id, file_paths)
            
            if not processed_docs:
                raise Exception("No documents were processed")
            
            self.vectorstore.add_documents(processed_docs)
            
            for file_path in file_paths:
                try:
                    os.remove(file_path)
                except:
                    pass
                    
            return len(processed_docs)
            
        except Exception as e:
            raise Exception(f"Failed to upsert data: {str(e)}")