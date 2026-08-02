from fastapi import Depends, FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import traceback
import uuid
from datetime import datetime
from typing import List

from src.auth.auth import create_token, get_user
from src.core.models import Base, ChatHistory, User
from src.database.data_ingestion import DataIngestion
from src.database.db import engine, get_db
from src.utils.email_helper import email_helper


def create_app() -> FastAPI:
    app = FastAPI(title="MCP API", version="1.0.0", debug=True)

    @app.on_event("startup")
    def on_startup() -> None:
        create_tables()

    register_routes(app)
    return app


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def register_routes(app: FastAPI) -> None:
    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/v1/generate")
    def generate(query, chat_id, user_id=Depends(get_user)):
        try:
            # RUN AGENTS — wired in Phase 4
            return JSONResponse(status_code=501, content={"detail": "Not implemented yet"})
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(
                status_code=400,
                content={"detail": f"Failed to generate response: {str(e)}"},
            )

    @app.post("/v1/upload")
    def upload(
        documents: List[UploadFile] = File(...),
        index_name: str = "vector_db_index",
        user_id=Depends(get_user),
    ):
        try:
            if not documents:
                return JSONResponse(status_code=400, content={"detail": "No documents provided"})

            allowed_extensions = {".pdf", ".txt", ".docx"}
            for doc in documents:
                file_ext = os.path.splitext(doc.filename)[1].lower()
                if file_ext not in allowed_extensions:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": f"Unsupported file type: {file_ext}"},
                    )

            data_ingestion = DataIngestion(index_name=index_name)
            num_chunks = data_ingestion.upsert_data(user_id, documents, index_name=index_name)

            return JSONResponse(
                status_code=200,
                content={
                    "detail": "Documents ingested successfully",
                    "chunks_processed": num_chunks,
                    "files_uploaded": len(documents),
                },
            )
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(status_code=400, content={"detail": f"Failed to upload docs: {str(e)}"})

    @app.get("/v1/chats")
    def fetch_chats(chat_id: str, user_id=Depends(get_user)):
        try:
            # Implemented in Phase 2
            return JSONResponse(status_code=501, content={"detail": "Not implemented yet"})
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(status_code=400, content={"detail": f"Failed to fetch chats: {str(e)}"})

    @app.post("/v1/login")
    def login(user_email: str, password: str, db: Session = Depends(get_db)):
        try:
            user = db.query(User).filter(User.email == user_email).first()
            if not user or not user.verify_password(password):
                return JSONResponse(status_code=400, content={"detail": "Invalid username or password"})
            access, refresh = create_token(
                {"sub": str(user.id), "username": user.username, "email": user.email}
            )
            return JSONResponse(
                status_code=200,
                content={
                    "access_token": access,
                    "refresh_token": refresh,
                    "token_type": "bearer",
                    "user": {
                        "id": str(user.id),
                        "username": user.username,
                        "email": user.email,
                    },
                },
            )
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(status_code=400, content={"detail": f"Login failed: {str(e)}"})

    @app.post("/v1/register")
    def register(username: str, user_email: str, password: str, db: Session = Depends(get_db)):
        try:
            existing_user = (
                db.query(User)
                .filter((User.username == username) | (User.email == user_email))
                .first()
            )
            if existing_user:
                raise Exception("Username or email already exists")
            new_user = User(username=username, email=user_email)
            new_user.set_password(password)
            new_user.created_at = datetime.now()
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            link = new_user.generate_link()
            email_helper(
                [user_email],
                f"Welcome to MCP! Your account has been successfully created.\n\nPlease use the following {link} to login.",
                "Welcome to MCP",
            )
            return JSONResponse(
                status_code=201,
                content={
                    "id": str(new_user.id),
                    "username": new_user.username,
                    "email": new_user.email,
                },
            )
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(status_code=400, content={"detail": f"Registration failed: {str(e)}"})

    @app.get("/v1/new_chat")
    def new_chat(user=Depends(get_user), db: Session = Depends(get_db)):
        try:
            chat_id = uuid.uuid4()
            chat = ChatHistory(
                id=uuid.uuid4(),
                user_id=user.id,
                chat_id=chat_id,
                messages=[],
            )
            db.add(chat)
            db.commit()
            db.refresh(chat)
            return JSONResponse(status_code=200, content={"chat_id": str(chat_id)})
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(status_code=400, content={"detail": f"Failed to create new chat: {str(e)}"})


app = create_app()
