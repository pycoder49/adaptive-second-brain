
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from database import models


logger = logging.getLogger(__name__)


def create_document(user_id: int, filename: str, db: Session) -> models.Document:

    logger.info(f"Creating document record for user {user_id}: {filename}")
    new_doc = models.Document(
        user_id=user_id,
        filename=filename,
        processing_status=models.ProcessingStatus.PROCESSING,
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


def update_document_status(doc_id: int, status: models.ProcessingStatus, db: Session) -> None:
    logger.info(f"Updating document {doc_id} status to {status.value}")
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if doc:
        doc.processing_status = status
        db.commit()


def get_documents_for_user(user_id: int, db: Session) -> List[models.Document]:

    logger.info(f"Fetching all documents for user {user_id}")
    return (
        db.query(models.Document)
        .filter(models.Document.user_id == user_id)
        .order_by(models.Document.upload_date.desc())
        .all()
    )


def get_document_by_id(doc_id: int, db: Session) -> Optional[models.Document]:

    return db.query(models.Document).filter(models.Document.id == doc_id).first()


def delete_document(doc_id: int, db: Session) -> bool:

    logger.info(f"Deleting document {doc_id}")
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        return False
    db.delete(doc)
    db.commit()
    return True
