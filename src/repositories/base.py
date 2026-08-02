import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.core.models import AgentMessage, AgentRun, AuthToken, ChatHistory, Document, StudyPlan, User


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID, document_id: uuid.UUID) -> Document | None:
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id, Document.id == document_id)
            .first()
        )

    def list_for_user(self, user_id: uuid.UUID) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.user_id == user_id)
            .order_by(Document.uploaded_at.desc())
            .all()
        )

    def update_status(
        self,
        document_id: uuid.UUID,
        status: str,
        chunk_count: int | None = None,
        error_message: str | None = None,
    ) -> Document | None:
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return None
        doc.status = status
        if chunk_count is not None:
            doc.chunk_count = chunk_count
        if error_message is not None:
            doc.error_message = error_message[:1024]
        self.db.flush()
        return doc

    def mark_processing(self, document_ids: list[uuid.UUID]) -> None:
        for doc_id in document_ids:
            self.update_status(doc_id, "processing")


class AuthTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: uuid.UUID,
        access_token: str,
        refresh_token: str,
        expires_at: datetime,
        refresh_expires_at: datetime,
    ) -> AuthToken:
        record = AuthToken(
            user_id=user_id,
            token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            refresh_expires_at=refresh_expires_at,
            refresh_expired=False,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def get_active_by_refresh_token(self, refresh_token: str) -> AuthToken | None:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(AuthToken)
            .filter(
                AuthToken.refresh_token == refresh_token,
                AuthToken.refresh_expired.is_(False),
                AuthToken.refresh_expires_at > now,
            )
            .first()
        )

    def mark_refresh_expired(self, record: AuthToken) -> None:
        record.refresh_expired = True
        self.db.flush()

    def get_user(self, user_id: uuid.UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, username: str, email: str, password_hash: bytes) -> User:
        user = User(username=username, email=email, password=password_hash)
        self.db.add(user)
        self.db.flush()
        return user


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_chat(self, user_id: uuid.UUID) -> ChatHistory:
        chat_id = uuid.uuid4()
        chat = ChatHistory(
            id=uuid.uuid4(),
            user_id=user_id,
            chat_id=chat_id,
            messages=[],
        )
        self.db.add(chat)
        self.db.flush()
        return chat

    def get_by_chat_id(self, user_id: uuid.UUID, chat_id: uuid.UUID) -> ChatHistory | None:
        return (
            self.db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id, ChatHistory.chat_id == chat_id)
            .first()
        )

    def list_for_user(self, user_id: uuid.UUID) -> list[ChatHistory]:
        return self.db.query(ChatHistory).filter(ChatHistory.user_id == user_id).all()


class StudyPlanRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        user_id: uuid.UUID,
        topic: str,
        study_topics: list[str],
        notes: dict | None,
        test: dict | None,
    ) -> StudyPlan:
        plan = StudyPlan(
            user_id=user_id,
            topic=topic,
            study_topics=study_topics,
            notes=notes,
            test=test,
        )
        self.db.add(plan)
        self.db.flush()
        return plan

    def get_latest_for_topic(self, user_id: uuid.UUID, topic: str) -> StudyPlan | None:
        return (
            self.db.query(StudyPlan)
            .filter(StudyPlan.user_id == user_id, StudyPlan.topic == topic)
            .order_by(StudyPlan.updated_at.desc())
            .first()
        )

    def get_by_id(self, user_id: uuid.UUID, plan_id: uuid.UUID) -> StudyPlan | None:
        return (
            self.db.query(StudyPlan)
            .filter(StudyPlan.user_id == user_id, StudyPlan.id == plan_id)
            .first()
        )

    def list_for_user(self, user_id: uuid.UUID) -> list[StudyPlan]:
        return (
            self.db.query(StudyPlan)
            .filter(StudyPlan.user_id == user_id)
            .order_by(StudyPlan.created_at.desc())
            .all()
        )


class AgentRunRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_run(
        self, user_id: uuid.UUID, agents_involved: list[str], input_data: dict
    ) -> AgentRun:
        run = AgentRun(
            user_id=user_id,
            agents_involved=agents_involved,
            input=input_data,
        )
        self.db.add(run)
        self.db.flush()
        return run

    def complete_run(self, run_id: uuid.UUID, output: dict) -> AgentRun | None:
        run = self.db.query(AgentRun).filter(AgentRun.run_id == run_id).first()
        if run:
            run.final_output = output
            run.completed_at = datetime.utcnow()
            self.db.flush()
        return run

    def log_message(
        self,
        run_id: uuid.UUID,
        sender: str,
        content: dict,
        receiver: str | None = None,
    ) -> AgentMessage:
        message = AgentMessage(
            run_id=run_id,
            sender_agent=sender,
            receiver_agent=receiver,
            content=content,
        )
        self.db.add(message)
        self.db.flush()
        return message

    def get_messages(self, run_id: uuid.UUID) -> list[AgentMessage]:
        return (
            self.db.query(AgentMessage)
            .filter(AgentMessage.run_id == run_id)
            .order_by(AgentMessage.timestamp)
            .all()
        )

    def get_run_for_user(self, user_id: uuid.UUID, run_id: uuid.UUID) -> AgentRun | None:
        return (
            self.db.query(AgentRun)
            .filter(AgentRun.run_id == run_id, AgentRun.user_id == user_id)
            .first()
        )
