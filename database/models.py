from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, ARRAY, Float, Enum, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

from pgvector.sqlalchemy import Vector

import datetime
import enum

from .database import Base


class ProcessingStatus(enum.Enum):
    READY = "ready"
    PROCESSING = "processing"
    FAILED = "failed"


class Role(enum.Enum):
    USER = "user"
    AI = "ai"


# Association table: links chats to documents (many-to-many)
chat_documents = Table(
    "chat_documents",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True),
    Column("document_id", Integer, ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    # id, email, hased_password
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    # relationships
    documents = relationship("Document", back_populates="owner")
    query_logs = relationship("QueryLog", back_populates="user")


class Document(Base):
    # id, user_id(FK), filename, upload_data, processing status
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    upload_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    processing_status = Column(
        Enum(ProcessingStatus), 
        default=ProcessingStatus.PROCESSING, nullable=False
    )

    # relationships
    owner = relationship("User", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    # id, document_id(FK), content, embedding
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    embedding = Column(Vector(384))  # 384 dims for all-MiniLM-L6-v2

    # relationships
    document = relationship("Document", back_populates="chunks")


class Chat(Base):
    # id, user_id (FK), title, created_at
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False, default="New Chat")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))

    # relationships
    documents = relationship("Document", secondary=chat_documents, backref="chats")
    messages = relationship("Message", backref="chat", cascade="all, delete-orphan")


class Message(Base):
    # id, conversation_id(FK), role, content, created_at
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    role = Column(Enum(Role), nullable=False)
    content = Column(String, nullable=False)
    parent_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


class QueryLog(Base):
    # id, user_id(FK), query text, retrieved_chunks, timestamp, latency_ms
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_text = Column(String, nullable=False)
    retrieved_chunks = Column(ARRAY(Integer), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    latency_ms = Column(Integer)

    # relationships
    user = relationship("User", back_populates="query_logs")