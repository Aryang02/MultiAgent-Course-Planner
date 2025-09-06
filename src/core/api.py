from fastapi import FastAPI, Depends
from langchain.prompts import PromptTemplate
from core.llm import LLM
from src.database.data_ingestion import DataIngestion
from fastapi.responses import JSONResponse
from typing import List
from fastapi import UploadFile, File
from core.models import Base, User, Document, AuthToken, ChatHistory
from database.db import engine, get_db
from auth.auth import create_token, get_user
from sqlalchemy.orm import Session
import uuid
import datetime

def start_app():
    app = FastAPI(title="MCP API", version="1.0.0", debug=True)
    create_tables()
    return app

def create_tables():
    Base.metadata.create_all(bind=engine)

app = start_app()

@app.post("/v1/generate")
def generate(query, context, chat_id, chat_history, image_urls = [], input_files = [], user_id=Depends(get_user)):
    try:
        llm_instance = LLM()
        context = llm_instance.retrieve_context(query) or []
        chat_history = llm_instance.retrieve_chat_history(user_id, chat_id) or []
        payload = {
            "prompt": query,
            "context": context,
            "chat_history": chat_history,
        }
        if image_urls:
            payload["image_urls"] = image_urls
        if input_files:
            payload["input_files"] = input_files
        response = llm_instance.call(
            **payload
        )
        llm_instance.update_history(chat_history, query, response)
        return JSONResponse(status_code=200, content={"response": response})
    except Exception as e:
        return JSONResponse(status=400, content={"detail": f"Failed to generate response: {str(e)}"})

@app.post("/v1/upload")
def upload(documents : List[UploadFile] = File(...), index_name: str = "vector_db_index", user_id=Depends(get_user)):
    try:
        if not documents:
            return JSONResponse(status=400, content={"detail": "No documents provided"})
        
        data_ingestion = DataIngestion()
        file_paths = data_ingestion.save_files()
        data_ingestion.upsert_data(user_id, file_paths, index_name=index_name)
        
        return JSONResponse(status_code=200, content= {"detail" :"Documents ingested successfully"})
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": f"Failed to upload docs {str(e)}"})
    
@app.get('/v1/chats')
def fetch_chats(chat_id: str, user_id=Depends(get_user)):
    try:
        llm = LLM()
        return llm.retrieve_chat_history(user_id, chat_id)
    except Exception as e:
        return JSONResponse(status=400, content={"detail": f"Failed to fetch chats: {str(e)}"})
    
@app.post('/v1/login')
def login(username: str, password: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user or not user.verify_password(password):
            return JSONResponse(status_code=400, content={"detail":"Invalid username or password"})
        access, refresh = create_token({"sub": user.id, "username": user.username, "email": user.email})
        return JSONResponse(status=200, content={"access_token": access, "refresh_token": refresh, "token_type": "bearer", "user": {"id": str(user.id), "username": user.username, "email": user.email}})
    except Exception as e:
        return JSONResponse(status=400, content={"detail": f"Login failed: {str(e)}"})
    
@app.post('/v1/register')
def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            raise Exception("Username or email already exists")
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        new_user.created_at = datetime.utcnow()
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return JSONResponse(status=201, content={"id": str(new_user.id), "username": new_user.username, "email": new_user.email})
    except Exception as e:
        return JSONResponse(status=400, content={"detail": f"Registration failed: {str(e)}"})
    
@app.get("v1/new_chat")
def new_chat(user_id=Depends(get_user), db: Session = Depends(get_db)):
    try:
        chat_id = str(uuid.uuid4())
        db.add(ChatHistory(id=chat_id, user_id=user_id.id, history=[], created_at=datetime.datetime.utcnow()))
        db.commit()
        db.refresh(ChatHistory)
        return JSONResponse(status=200, content={"chat_id": chat_id})
    except Exception as e:
        return JSONResponse(status=400, content={"detail": f"Failed to create new chat: {str(e)}"})