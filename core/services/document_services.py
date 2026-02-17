
from sqlalchemy.orm import Session
from typing import List
import logging

from core.RAG.main import ingest_document
from database.db_access import document_access
from database import models


logger = logging.getLogger(__name__)


def upload_document(user_id: int, filename: str, file_bytes: bytes, db: Session) -> dict:

    logger.info(f"Service: uploading document '{filename}' for user {user_id}")
    doc = ingest_document(user_id, filename, file_bytes, db)

    return {
        "id": doc.id,
        "user_id": doc.user_id,
        "filename": doc.filename,
        "upload_date": str(doc.upload_date),
        "processing_status": doc.processing_status.value,
    }


def get_user_documents(user_id: int, db: Session) -> List[dict]:

    docs = document_access.get_documents_for_user(user_id, db)
    return [
        {
            "id": doc.id,
            "user_id": doc.user_id,
            "filename": doc.filename,
            "upload_date": str(doc.upload_date),
            "processing_status": doc.processing_status.value,
        }
        for doc in docs
    ]


def delete_user_document(user_id: int, doc_id: int, db: Session) -> bool:
    doc = document_access.get_document_by_id(doc_id, db)
    if not doc or doc.user_id != user_id:
        return False
    return document_access.delete_document(doc_id, db)
