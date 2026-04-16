"""
Document entity module for the Adaptive Second Brain application.
"""

from dataclasses import dataclass
from datetime import datetime
import enum


class ProcessingStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"


@dataclass
class DocumentCreate:
    user_id: int
    r2_key: str
    file_name: str
    file_size: int
    content_type: str


@dataclass
class DocumentUpload:
    user_id: int
    file_name: str
    file_size: int
    content_type: str
    file_bytes: bytes


@dataclass
class DocumentRetrieve:
    id: int
    user_id: int
    file_name: str
    file_size: int
    content_type: str
    r2_key: str
    created_at: datetime
    processing_status: ProcessingStatus