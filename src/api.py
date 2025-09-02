from fastapi import FastAPI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from server import LLM
from data_ingestion import DataIngestion
from http import Response

app = FastAPI()

@app.post("/v1/generate")
def generate(request: dict):
    try:
        query = request.get("query")
        context = request.get("context", "")
        chat_id = request.get("chat_id", "default_chat")
        chat_history = request.get("chat_history", [])
        image_urls = request.get("image_urls", [])
        input_files = request.get("input_files", [])
        
        llm_instance = LLM()
        
        context = llm_instance.retrieve_context(query)
        chat_history = llm_instance.retrieve_chat_history(request.user.id, chat_id)
        response = llm_instance.call(
            prompt=query,
            context=context,
            chat_history=chat_history,
            image_urls=image_urls,
            input_files=input_files
        )
        
        return {"response": response}
    except Exception as e:
        return Response(status=400, message={"detail": f"Failed to generate response: {str(e)}"})

@app.post("/v1/upload")
def upload(request: dict):
    try:
        documents = request.get("documents", [])
        index_name = request.get("index_name", "vector_db_index")
        
        if not documents:
            return Response(status=400, message={"detail": "No documents provided"})
        
        data_ingestion = DataIngestion()
        file_paths = data_ingestion.save_files()
        data_ingestion.upsert_data(file_paths, index_name=index_name)
        
        return Response(status=200 , message = {"detail" :"Documents ingested successfully"})
    except Exception as e:
        return Response(status=400, message={"detail": f"Failed to upload docs {str(e)}"})
    
@app.get('/v1/chats')
def fetch_chats(request: dict):
    try:
        chat_id = request.get("chat_id", "default_chat")
        llm = LLM()
        return llm.retrieve_chat_history(request.user.id, chat_id)
    except Exception as e:
        return Response(status=400, message={"detail": f"Failed to fetch chats: {str(e)}"})