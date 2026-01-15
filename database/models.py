from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, ARRAY, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text

from pgvector.sqlalchemy import Vector

from datetime import datetime

from enum import Enum
import enum

from .database import Base


class ProcessingStatus(str, enum.Enum):
    READY = "ready"
    PROCESSING = "processing"
    FAILED = "failed"


class User(Base):
    # id, email, hased_password
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hased_password = Column(String, nullable=False)

    # relationships
    docuemnts = relationship("Document", back_populates="owner")
    query_logs = relationship("QueryLog", back_populates="user")


class Document(Base):
    # id, user_id(FK), filename, upload_data, processing status
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    upload_date = Column(TIMESTAMP(timezone=True), nunllable=False, server_default=text('now()'))
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PROCESSING, nullable=False)

    # relationships
    owner = relationship("User", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    # id, document_id(FK), content, embedding
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(String, nullable=False)
    embedding = Column(Vector)

    # relationships
    document = relationship("Document", back_populates="chunks")


class QueryLog(Base):
    # id, user_id(FK), query text, retrieved_chunks, timestamp, latency_ms
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_text = Column(String, nullable=False)
    retrieved_chunks = Column(ARRAY(Integer), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(datetime.timezone.utc))
    latency_ms = Column(Integer)

    # relationships
    user = relationship("User", back_populates="query_logs")